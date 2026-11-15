// Pinned 455 RVA 4DC32A..4DCA4D: advanced SPT input fields only.
// Rendering curves, distortion and azirang remains a separate contract.
#include <cerrno>
#include <cmath>
#include <cstdlib>
#include <cstring>
#include <limits>

namespace {
int particleRawToken455(RF455ResourceText& input, char (&token)[256]) {
    return input.readExact(token);
}
int particleRawToken455(FILE* file, char (&token)[256]) {
    return RF455ResourceText::readExact(file, token);
}
template<class Input>
bool particleToken455(Input& input, char (&token)[256]) {
    return particleRawToken455(input, token) == 1 && std::strcmp(token, "end") != 0;
}
template<class Input>
BOOL RF455_GetRandOrNum(Input& file, float* from, float* at, bool& valid) {
    const auto fail = [&]() -> BOOL {
        *from = *at = 0;
        valid = false;
        return FALSE;
    };
    if (!valid) return fail();
    char hole[256], temp[256];
    if (!particleToken455(file, hole)) return fail();
    if (std::strncmp(hole, "rand", 4) == 0) {
        while (!std::strchr(hole, ')')) {
            if (!particleToken455(file, temp)) return fail();
            const size_t used = std::strlen(hole), extra = std::strlen(temp);
            if (extra >= sizeof(hole) - used) return fail();
            std::memcpy(hole + used, temp, extra + 1);
        }
        const char* start = hole + 4;
        const char* comma = std::strchr(start, ',');
        const char* close = std::strchr(start, ')');
        if (*start != '(' || !comma || comma <= start + 1 || comma + 1 >= close)
            return fail();
        const DWORD consumed = GetTokenFloat(hole, from);
        GetTokenFloat(hole + consumed, at);
        return TRUE;
    }
    *from = static_cast<float>(std::atof(hole));
    return FALSE;
}
bool particleLong455(RF455ResourceText& file, char (&token)[256], long& value) {
    if (!particleToken455(file, token)) return false;
    char* end = nullptr;
    errno = 0;
    value = std::strtol(token, &end, 10);
    return end != token && *end == 0 && errno != ERANGE;
}
template<class Input>
bool particleFloat455(Input& file, char (&token)[256], float& value, double scale = 1.0) {
    if (!particleToken455(file, token)) return false;
    char* end = nullptr;
    errno = 0;
    const double parsed = std::strtod(token, &end) * scale;
    if (end == token || *end != 0 || errno == ERANGE || !std::isfinite(parsed) ||
        parsed > (std::numeric_limits<float>::max)() || parsed < -(std::numeric_limits<float>::max)()) return false;
    value = static_cast<float>(parsed);
    return true;
}
bool particleByte455(RF455ResourceText& file, char (&token)[256], BYTE& value) {
    long parsed;
    if (!particleLong455(file, token, parsed)) return false;
    value = static_cast<BYTE>(parsed); // Original signed atol narrowed to BYTE.
    return true;
}
bool particleCurve455(CParticle& particle, RF455ResourceText& file, char (&token)[256]) {
    BYTE count;
    if (!particleByte455(file, token, count)) return false;
    Vector3f* points = nullptr;
    if (count) {
        points = static_cast<Vector3f*>(Dmalloc(sizeof(Vector3f) * count));
        if (!points) return false;
        std::memset(points, 0, sizeof(Vector3f) * count);
    }
    if (particle.mCurvePoints) Dfree(particle.mCurvePoints);
    particle.mCurvePoints = points;
    particle.mTraceLength = count;
    return true;
}
bool RF455_ReadParticleFields(CParticle& p, RF455ResourceText& file, char (&hole)[256]) {
    if (!std::strcmp(hole, "tracelength") && !particleCurve455(p, file, hole)) return false;
    if (!std::strcmp(hole, "control_node")) {
        if (!particleCurve455(p, file, hole)) return false;
        for (unsigned i = 0; i < p.mTraceLength; ++i) {
            // The reference leaves malformed nodes uninitialized; reject them.
            if (!particleToken455(file, hole) || std::strcmp(hole, "control_pos")) return false;
            for (unsigned axis = 0; axis < 3; ++axis)
                if (!particleFloat455(file, hole, p.mCurvePoints[i][axis])) return false;
        }
        // Five ordered lookaheads are consumed even when their keyword differs.
        // Keep hole shared: the original later handlers see the final token.
        if (!particleToken455(file, hole)) return false;
        if ((!std::strcmp(hole, "curveknot_length") || !std::strcmp(hole, "control_radius")) &&
            !particleFloat455(file, hole, p.mCurveRadius)) return false;
        if (!particleToken455(file, hole)) return false;
        if (!std::strcmp(hole, "curveknot_num") && !particleByte455(file, hole, p.mCurveKnotNum)) return false;
        if (!particleToken455(file, hole)) return false;
        if (!std::strcmp(hole, "curve_speed") && !particleFloat455(file, hole, p.mCurveSpeed)) return false;
        if (!particleToken455(file, hole)) return false;
        if (!std::strcmp(hole, "curverepeate_num") && !particleByte455(file, hole, p.mCurveRepeatNum)) return false;
        if (!particleToken455(file, hole)) return false;
        if (!std::strcmp(hole, "curverepeate_rot") &&
            !particleFloat455(file, hole, p.mCurveRotation, 0.01745329238474369)) return false;
    }
    if (!std::strcmp(hole, "distort")) {
        p.mFlag |= 0x200000u;
        if (!particleFloat455(file, hole, p.mDistort)) return false;
    }
    if (!std::strcmp(hole, "distort_offset")) {
        p.mFlag |= 0x200000u;
        for (unsigned i = 0; i < 2; ++i)
            if (!particleFloat455(file, hole, p.mDistortOffset[i])) return false;
    }
    if (!std::strcmp(hole, "azirang_pos"))
        for (unsigned i = 0; i < 3; ++i)
            if (!particleFloat455(file, hole, p.mAzirangPos[i])) return false;
    if (!std::strcmp(hole, "azirang_width")) {
        long value;
        if (!particleLong455(file, hole, value)) return false;
        p.mAzirangWidth = static_cast<DWORD>(value);
    }
    if (!std::strcmp(hole, "azirang_height")) {
        long value;
        if (!particleLong455(file, hole, value)) return false;
        p.mAzirangHeight = static_cast<DWORD>(value);
    }
    if (!std::strcmp(hole, "azirang_amplitude") && !particleFloat455(file, hole, p.mAzirangAmplitude)) return false;
    if (!std::strcmp(hole, "azirang_time") && !particleFloat455(file, hole, p.mAzirangTime)) return false;
    if (!std::strcmp(hole, "azirang_variance") && !particleFloat455(file, hole, p.mAzirangVariance)) return false;
    if (!std::strcmp(hole, "use_combine_scale")) p.mUseCombineScale = 1;
    return true;
}
}

// Destination must be empty; entity ownership remains with the definition.
bool CParticle::CopyTemplate455(const CParticle& source) {
    if (this == &source || mElement || mCurvePoints || mEntity) return false;
    Vector3f* points = nullptr;
    if (source.mTraceLength) {
        if (!source.mCurvePoints) return false;
        const size_t bytes = sizeof(Vector3f) * source.mTraceLength;
        points = static_cast<Vector3f*>(Dmalloc(bytes));
        if (!points) return false;
        std::memcpy(points, source.mCurvePoints, bytes);
    }
    std::memcpy(this, &source, sizeof(CParticle));
    mCurvePoints = points;
    mElement = nullptr;
    return true;
}
