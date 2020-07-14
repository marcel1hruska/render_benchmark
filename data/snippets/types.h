namespace types
{
    const float PI = 3.1415926535897932384;
    const size_t SPECTRUM_SAMPLES = 4;

    // representation of a color spectrum - 4 pairs (wavelength,power value)
    using Spectrum = std::pair<float, float>[SPECTRUM_SAMPLES];

    struct vector3f
    {
        float x;
        float y;
        float z;
    };

    struct vector2f
    {
        float x;
        float y;
    };

    struct mask
    {
        float value;
        bool masked;
    };

    float sqr(float x)
    {
        return x*x;
    };

    Spectrum safe_sqrt(const Spectrum& s)
    {
        Spectrum result;
        for (size_t i = 0; i < SPECTRUM_SAMPLES; i++)
            result[i] = (s[i] < 0.f) ? 0.f : std::sqrt(s[i]);
        return result;
    };

    Spectrum clamp_negative(const Spectrum& s)
    {
        Spectrum result;
        for (size_t i = 0; i < SPECTRUM_SAMPLES; i++)
            result[i] = (std::isnan(s[i]) || s[i] < 0.f) ? 0.f : s[i];
        return result;
    };

    float dot(const vector3f& one, const vector3f& two)
    {
        one.x*two.x + one.y*two.y + one.z*two.z;
    }

    vector3f normalize(const vector3f& vec)
    {
        auto length = sqrt(sqr(vec.x) + sqr(vec.y) + sqr(vec.z));
        return vector3f{vec.x/length, vec.y/length, vec.z/length};
    }
}
