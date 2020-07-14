#include "types.h"
#include <tuple>

/* The iridescence_term method simulates the light interference caused by a very thin 
* dielectric layer (called film) on top of a rough conductor base. 
* These methods are taken from the supplementary code for Mitsuba 0.5 released for the paper
* https://blogs.unity3d.com/2017/05/09/a-practical-extension-to-microfacet-theory-for-the-modeling-of-varying-iridescence/
* I purposely left the former comments inside the code.
*/
using namespace types;


// fresnel_phase_exact and fresnel_conductor exact are helper functions 
std::pair<Spectrum, Spectrum>
    fresnel_phase_exact(const Spectrum &cos_theta, const Spectrum &eta1,
                        const Spectrum &eta2, const Spectrum &kappa2) {
        const Spectrum sin_theta_2 = Spectrum(1.0) - sqr(cos_theta);
        const Spectrum A =
            sqr(eta2) * (Spectrum(1.0) - sqr(kappa2)) - sqr(eta1) * sin_theta_2;
        const Spectrum B = sqrt(sqr(A) + sqr(2 * sqr(eta2) * kappa2));
        const Spectrum U = sqrt((A + B) / 2.0);
        const Spectrum V = sqrt((B - A) / 2.0);

        Spectrum phiS = atan2(2 * eta1 * V * cos_theta,
                              sqr(U) + sqr(V) - sqr(eta1 * cos_theta));
        Spectrum phiP =
            atan2(2 * eta1 * sqr(eta2) * cos_theta *
                      (2 * kappa2 * U - (Spectrum(1.0) - sqr(kappa2)) * V),
                  sqr(sqr(eta2) * (Spectrum(1.0) + sqr(kappa2)) * cos_theta) -
                      sqr(eta1) * (sqr(U) + sqr(V)));

        return std::pair(phiS, phiP);
    }

/* Polarized Fresnel Term
    */
std::pair<Spectrum, Spectrum> fresnel_conductor_exact(Spectrum cos_theta,
                                                        Spectrum eta,
                                                        Spectrum k)  {
    /* Modified from "Optics" by K.D. Moeller, University Science Books,
        * 1988 */

    Spectrum cos_theta_2 = cos_theta * cos_theta,
                sin_theta_2 = 1 - cos_theta_2,
                sin_theta_4 = sin_theta_2 * sin_theta_2;

    Spectrum temp1 = eta * eta - k * k - sin_theta_2,
                a2pb2 = safe_sqrt(temp1 * temp1 + 4 * k * k * eta * eta),
                a     = safe_sqrt(0.5f * (a2pb2 + temp1));

    Spectrum term1 = a2pb2 + cos_theta_2, term2 = 2 * a * cos_theta;

    Spectrum Rs2 = (term1 - term2) / (term1 + term2);

    Spectrum term3 = a2pb2 * cos_theta_2 + sin_theta_4,
                term4 = term2 * sin_theta_2;

    Spectrum Rp2 = Rs2 * (term3 - term4) / (term3 + term4);
    return std::pair(Rs2, Rp2);
}


/**
 * \brief Simulation of iridescence between thin film and conductor base
 *
 * \param cos_theta
 *     Angle between incoming direction and normal
 * \param eta
 *     Real part of the base conductor's IOR
 * \param k
 *     Imaginary part of the base conductor's IOR
 * \param ext_eta
 *     IOR of the exterior (usually 1 - air)
 * \param film_eta
 *     IOR of the film layer
 * \param height
 *     Height of the film layer (nm)
 * \param wavelengths
 *     Wavelengths that are sampled for the current interaction/rendering process
 */
/* Our iridescence term accounting for the interference of light reflected
    * by the layered structure.
    */
Spectrum iridescence_term(float cos_theta, 
                            const Spectrum &eta,
                            const Spectrum &k,
                            const Spectrum &ext_eta,
                            const Spectrum &film_eta,
                            const Spectrum &height,
                            const Spectrum &wavelengths) {
    /* Compute the Spectral versions of the Fresnel reflectance and
        * transmitance for each interface. */
    Spectrum R12p, T121p, R23p, R12s, T121s, R23s, ct2;

    // Reflected and transmitted parts in the thin film
    const Spectrum scale       = ext_eta / film_eta;
    const Spectrum cos_theta_2 = 1 - (1 - sqr(cos_theta)) * sqr(scale);

    /* Check for total internal reflection */
    if ((cos_theta_2 <= 0.0f) != 0.0) {
        R12s = 1.0;
        R12p = 1.0;

        // Compute the transmission coefficients
        T121p = 0.0;
        T121s = 0.0;
    } else {
        ct2                  = sqrt(cos_theta_2);
        std::tie(R12s, R12p) = fresnel_conductor_exact(
            Spectrum(cos_theta), film_eta / ext_eta, 0.0);

        // Reflected part by the base
        std::tie(R23s, R23p) =
            fresnel_conductor_exact(ct2, eta / film_eta, k / film_eta);

        // Compute the transmission coefficients
        T121p = 1.0 - R12p;
        T121s = 1.0 - R12s;
    }

    /* Optical Path Difference */
    const Spectrum D    = 2.0 * film_eta * height * ct2;
    const Spectrum Dphi = 2.0 * PI * D / wavelengths;

    /* Variables */
    Spectrum phi21p(0.), phi21s(0.), phi23p(0.), phi23s(0.), r123s, r123p,
        Rs, cosP, irid, I(0.);

    /* Evaluate the phase shift */
    std::tie(phi21s, phi21p) = fresnel_phase_exact(
        Spectrum(cos_theta), Spectrum(1.0), film_eta, Spectrum(0.0));
    std::tie(phi23s, phi23p) = fresnel_phase_exact(ct2, film_eta, eta, k);
    phi21p                   = Spectrum(PI) - phi21p;
    phi21s                   = Spectrum(PI) - phi21s;

    r123p = sqrt(R12p * R23p);
    r123s = sqrt(R12s * R23s);

    /* Iridescence term using Airy summation (Eq. 11) for Parallel
        * polarization */
    Rs   = (sqr(T121p) * R23p) / (Spectrum(1.0) - R12p * R23p);
    cosP = cos(Dphi + phi23p + phi21p);
    irid = (r123p * cosP - sqr(r123p)) /
            (Spectrum(1.0) - 2.0 * r123p * cosP + sqr(r123p));
    I = R12p + Rs + 2.0 * (Rs - T121p) * irid;

    /* Iridescence term using Airy summation (Eq. 11) for Perpendicular
        * polarization */
    Rs   = (sqr(T121s) * R23s) / (Spectrum(1.0) - R12s * R23s);
    cosP = cos(Dphi + phi23s + phi21s);
    irid = (r123s * cosP - sqr(r123s)) /
            (Spectrum(1.0) - 2.0 * r123s * cosP + sqr(r123s));
    I += R12s + Rs + 2.0 * (Rs - T121s) * irid;

    // Assure that the BRDF is non negative
    I = clamp_negative(I);
    return 0.5 * I;
}