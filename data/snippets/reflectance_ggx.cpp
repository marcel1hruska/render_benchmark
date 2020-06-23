#include "types.h"
#include <cmath>
#include <utility>
#include <algorithm>

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
    // get tan_theta_m first - angle between microsurface normal m and macrosurface normal n
    float cos_theta_m = dot(m,n);
    float tan_theta_m = sqrt(1.f - sqr(cos_theta_m))/cos_theta_m;

    float alpha_2 = sqr(alpha);
    // rest of the equation
    float result = alpha_2 / 
        (PI * std::pow(cos_theta_m,4.f) * sqr(alpha_2 + sqr(tan_theta_m)));

    // Prevent potential numerical issues in other stages of the model
    return (result * dot(m,n) > 1e-20f) ? result : 0.f;
}


/**
 * \brief Evaluate the probability density function for isotropic GGX distrubution
 *
 * \param m
 *     The microfacet normal
 * \param n
 *     The macrosurface normal
 * \param alpha
 *     The surface roughness
 */
float pdf(const vector3f& m, const vector3f& n, float alpha)
{
    float result = eval(m,n,alpha);
    float cos_theta_m = dot(m,n);

    return result * cos_theta_m;
}


/**
 * \brief Draw a sample from the microfacet normal distribution
 *  and return the associated probability density
 *
 * \param samples
 *    A uniformly distributed 2D sample
 * \param alpha
 *    The surface roughness
 */
std::pair<vector3f,float> sample(const vector2f samples, float alpha)
{
    // azimuth
    float phi = (2.0 * PI) * samples.x;

    // polar
    float alpha_2 = sqr(alpha);

    float tan_theta_m_2 = alpha_2 * samples.x / (1.f - samples.x);
    float cos_theta = 1.0/(sqrt(1.0 + tan_theta_m_2));
    float cos_theta_2 = sqr(cos_theta);

    // Compute probability density of the sampled position
    float temp = 1.0 + tan_theta_m_2 / alpha_2;
    float cos_theta_3 = std::max(cos_theta_2 * cos_theta, 1e-20f);
    float sin_theta = sqrt(1.0 - cos_theta_2);

    float pdf = 1.0/ (PI * alpha_2 * cos_theta_3 * sqr(temp));

    // the resulting direction
    vector3f result = {sin_theta*cos(phi),
                        sin_theta*sin(phi),
                        cos_theta};

    return std::pair(result,pdf);
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
float smith_G1(const vector3f& v, const vector3f& m, const vector3f& n, float alpha)
{
    // get tan_theta_v first - angle between direction v and macrosurface normal n
    float cos_theta_v = dot(v,n);
    float tan_theta_v = sqrt(1.f - sqr(cos_theta_v))/cos_theta_v;

    // get tan of theta_v ^2 * alpha^2
    float tan_theta_alpha_2 = sqr(alpha)*sqr(tan_theta_v);

    // the rest of the equation
    float result = 2.f / (1.f + sqrt(1.f + tan_theta_alpha_2));

    /* Ensure consistent orientation (can't see the back
           of the microfacet from the front and vice versa) */
    return (dot(v, m) / cos_theta_v <= 0.f) ? 0.f : result;
}