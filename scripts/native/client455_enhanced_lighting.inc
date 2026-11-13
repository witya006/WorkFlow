#include "client455_enhanced_lighting_shader.h"
#include <cmath>
#include <algorithm>

namespace {
struct EnhancedActorLighting {
    RF455ShaderManager* manager = nullptr;
    unsigned programs[3] = {};
    bool available = false;
    bool enabled = false;
    bool protectedEffect = false;
} enhancedActorLighting;

void discardEnhancedFailure(RF455ShaderFailure& failure) {
    release(failure.orphan.vertex); release(failure.orphan.pixel);
    release(failure.orphan.vertexConstants); release(failure.orphan.pixelConstants);
    release(failure.code); release(failure.errors);
}

bool enhancedCameraPosition(const float* view, float* output) {
    if (!view) return false;
    for (unsigned i = 0; i < 16; ++i) if (!std::isfinite(view[i])) return false;
    // Invert the affine view basis; camera = -translation * inverse(basis).
    const double a=view[0], b=view[1], c=view[2], d=view[4], e=view[5], f=view[6],
                 g=view[8], h=view[9], i=view[10];
    const double determinant=a*(e*i-f*h)-b*(d*i-f*g)+c*(d*h-e*g);
    if (!std::isfinite(determinant) || std::fabs(determinant) < 1e-12 ||
        std::fabs(view[3]) > 1e-5 || std::fabs(view[7]) > 1e-5 ||
        std::fabs(view[11]) > 1e-5 || std::fabs(view[15]-1) > 1e-5) return false;
    const double inverse[9] = {(e*i-f*h)/determinant, (c*h-b*i)/determinant, (b*f-c*e)/determinant,
        (f*g-d*i)/determinant, (a*i-c*g)/determinant, (c*d-a*f)/determinant,
        (d*h-e*g)/determinant, (b*g-a*h)/determinant, (a*e-b*d)/determinant};
    for (unsigned axis=0; axis<3; ++axis) {
        output[axis] = static_cast<float>(-view[12]*inverse[axis]
            -view[13]*inverse[3+axis]-view[14]*inverse[6+axis]);
        if (!std::isfinite(output[axis])) return false;
    }
    output[3] = 1;
    return true;
}
}

bool RF455_EnhancedActorLightingAvailable() { return enhancedActorLighting.available; }
bool RF455_EnhancedActorLightingEnabled() {
    return enhancedActorLighting.available && enhancedActorLighting.enabled;
}
bool RF455_SetEnhancedActorLightingEnabled(bool enabled) {
    if (enabled && !enhancedActorLighting.available) return false;
    if (!WritePrivateProfileStringA("RenderState", "EnhancedActorLighting", enabled ? "1" : "0",
                                    ".\\R3Engine.ini")) return false;
    enhancedActorLighting.enabled = enabled;
    return true;
}
void RF455_SetEnhancedActorLightingProtected(bool protectedEffect) {
    enhancedActorLighting.protectedEffect = protectedEffect;
}
void RF455_ReleaseEnhancedActorLighting(RF455ShaderManager* manager) {
    if (enhancedActorLighting.manager == manager) enhancedActorLighting = EnhancedActorLighting{};
}
void RF455_InitializeEnhancedActorLighting(RF455ShaderManager* manager, const RF455ShaderApi* api) {
    if (enhancedActorLighting.manager == manager && enhancedActorLighting.available) return;
    enhancedActorLighting = EnhancedActorLighting{};
    if (!manager || !manager->device || !api || !api->compile || manager->count < 12) return;
    D3DCAPS9 caps{};
    if (FAILED(manager->device->GetDeviceCaps(&caps)) || caps.VertexShaderVersion < D3DVS_VERSION(2,0) ||
        caps.PixelShaderVersion < D3DPS_VERSION(3,0)) return;
    const unsigned originalCount = manager->count;
    EnhancedActorLighting next;
    next.manager = manager;
    for (unsigned kind = 0; kind < 3; ++kind) {
        const char* prefix = kind == 0 ? "#define RF455_NORMAL_MAP 0\n#define RF455_SPECULAR_MAP 0\n"
            : kind == 1 ? "#define RF455_NORMAL_MAP 1\n#define RF455_SPECULAR_MAP 0\n"
            : "#define RF455_NORMAL_MAP 1\n#define RF455_SPECULAR_MAP 1\n";
        RF455ShaderFailure failure;
        const int program = RF455_CreateShaderProgram(manager, api, RF455EnhancedActorVertex,
                                                       RF455EnhancedActorPixel, prefix, &failure);
        if (program < 0) {
            discardEnhancedFailure(failure);
            while (manager->count > originalCount) {
                auto& added = manager->programs[--manager->count];
                release(added.vertex); release(added.pixel);
                release(added.vertexConstants); release(added.pixelConstants);
            }
            OutputDebugStringA("RF455: optional enhanced actor lighting unavailable; classic retained\n");
            return;
        }
        next.programs[kind] = static_cast<unsigned>(program);
    }
    next.available = true;
    next.enabled = GetPrivateProfileIntA("RenderState", "EnhancedActorLighting", 0, ".\\R3Engine.ini") == 1;
    enhancedActorLighting = next;
}

bool RF455_BindEnhancedActorLighting(RF455ShaderManager* manager, const float* material,
                                    const float* view, const float* lightDirection,
                                    bool normalMap, bool specularMap, unsigned* selected) {
    if (!RF455_EnhancedActorLightingEnabled() || enhancedActorLighting.protectedEffect ||
        manager != enhancedActorLighting.manager || !material || !lightDirection || !selected ||
        (specularMap && !normalMap)) return false;
    float camera[4];
    if (!enhancedCameraPosition(view, camera)) return false;
    for (unsigned i=0; i<17; ++i) if (!std::isfinite(material[i])) return false;
    float direction[4] = {lightDirection[0], lightDirection[1], lightDirection[2], 0};
    double length = 0;
    for (unsigned i=0; i<3; ++i) {
        if (!std::isfinite(direction[i])) return false;
        length += double(direction[i])*direction[i];
    }
    if (length < 1e-12) return false;
    const unsigned index = enhancedActorLighting.programs[specularMap ? 2 : normalMap ? 1 : 0];
    if (index >= manager->count) return false;
    // Modest masked gloss, no artificial specular term for unmasked skin/cloth.
    float specular[4] = {(std::max)(0.f, material[8]), (std::max)(0.f, material[9]),
                         (std::max)(0.f, material[10]), (std::max)(1.f, (std::min)(128.f, material[16]))};
    auto* device = manager->device;
    if (FAILED(device->SetPixelShaderConstantF(0, material, 1)) ||
        FAILED(device->SetPixelShaderConstantF(1, material+4, 1)) ||
        FAILED(device->SetPixelShaderConstantF(2, direction, 1)) ||
        FAILED(device->SetPixelShaderConstantF(3, camera, 1)) ||
        FAILED(device->SetPixelShaderConstantF(4, specular, 1))) return false;
    if (FAILED(device->SetVertexShader(manager->programs[index].vertex)) ||
        FAILED(device->SetPixelShader(manager->programs[index].pixel))) {
        device->SetVertexShader(nullptr); device->SetPixelShader(nullptr); return false;
    }
    *selected = index;
    return true;
}
