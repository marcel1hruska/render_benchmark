namespace types
{
    const float PI = 3.1415926535897932384;

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
