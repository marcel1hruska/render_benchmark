#include "types.h"
#include <cmath>
#include <utility>

using namespace types;

/**
 * \brief Evaluate the microfacet distribution function for isotropic GGX distrubution
 *
 * \param m
 *     The microfacet normal
 * \param n
 *     The macrosurface normal
 * \param alpha
 *     The surface roughness
 */
float eval(const vector3f& m, const vector3f& n, float alpha)
{
    float alpha_2 = sqr(alpha);
    float result = 1.f / (PI * alpha_2 *
                sqr(sqr(m.x / alpha) + sqr(m.y / alpha) + sqr(m.z)));

    // Prevent potential numerical issues in other stages of the model
    return (result * dot(m,n) > 1e-20f) ? result : 0.f;
}


/**
 * \brief Smith's shadowing-masking function for a single direction for isotropic GGX distrubution
 *
 * \param v
 *     An arbitrary direction
 * \param m
 *     The microfacet normal
 * \param n
 *     The macrosurface normal
 * \param alpha
 *     The surface roughness
 */
mask smith_G1(const vector3f& v, const vector3f& m, const vector3f& n, float alpha)
{
    mask result;
    // compute tan^2(theta_v)*alpha_g^2 term of the equation
    float xy_alpha_2 = sqr(alpha * v.x) + sqr(alpha * v.y);
    float tan_theta_alpha_2 = xy_alpha_2 / sqr(v.z);
    // the rest of the equation
    result.value = 2.f / (1.f + sqrt(1.f + tan_theta_alpha_2));

    /* Ensure consistent orientation (can't see the back
           of the microfacet from the front and vice versa) */
    if (dot(v, m) / dot(v,n) <= 0.f)
        result.masked = true;
    return result;
}