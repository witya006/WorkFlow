#pragma once

// Authored extension shaders. Skinning and clip position keep the original matrix
// registers; all lighting vectors below use world space consistently.
static const char RF455EnhancedActorVertex[] = R"HLSL(
float4x4 projection : register(c2);
float4x4 view : register(c6);
float4x4 bones[30] : register(c100);
struct Input {
    float3 position : POSITION;
    float3 weights : BLENDWEIGHT;
    int4 indices : BLENDINDICES;
    float3 normal : NORMAL0;
    float2 uv : TEXCOORD0;
    float3 tangent : TANGENT;
};
struct Output {
    float4 position : POSITION;
    float2 uv : TEXCOORD0;
    float3 worldPosition : TEXCOORD1;
    float3 normal : TEXCOORD2;
    float3 tangent : TEXCOORD3;
};
Output main(Input input) {
    Output output = (Output)0;
    float4 weights = float4(input.weights, 1 - dot(input.weights, 1));
    float4 p = float4(input.position, 1);
    float4 n = float4(input.normal, 0);
    float4 t = float4(input.tangent, 0);
    float4 worldPosition = mul(p, bones[input.indices.x]) * weights.x
        + mul(p, bones[input.indices.y]) * weights.y
        + mul(p, bones[input.indices.z]) * weights.z
        + mul(p, bones[input.indices.w]) * weights.w;
    output.normal = (mul(n, bones[input.indices.x]) * weights.x
        + mul(n, bones[input.indices.y]) * weights.y
        + mul(n, bones[input.indices.z]) * weights.z
        + mul(n, bones[input.indices.w]) * weights.w).xyz;
    output.tangent = (mul(t, bones[input.indices.x]) * weights.x
        + mul(t, bones[input.indices.y]) * weights.y
        + mul(t, bones[input.indices.z]) * weights.z
        + mul(t, bones[input.indices.w]) * weights.w).xyz;
    output.position = mul(mul(worldPosition, view), projection);
    output.worldPosition = worldPosition.xyz;
    output.uv = input.uv;
    return output;
}
)HLSL";

static const char RF455EnhancedActorPixel[] = R"HLSL(
sampler2D albedoMap : register(s0);
sampler2D normalMap : register(s3);
sampler2D specularMap : register(s4);
float4 materialDiffuse : register(c0);
float4 materialAmbient : register(c1);
float4 lightDirection : register(c2);
float4 cameraPosition : register(c3);
float4 materialSpecular : register(c4); // RGB tint, w exponent.
struct Input {
    float2 uv : TEXCOORD0;
    float3 worldPosition : TEXCOORD1;
    float3 normal : TEXCOORD2;
    float3 tangent : TEXCOORD3;
};
float3 safeUnit(float3 value) { return value * rsqrt(max(dot(value, value), 0.000001)); }
float4 main(Input input) : COLOR {
    float4 albedo = tex2D(albedoMap, input.uv);
    float3 normal = safeUnit(input.normal);
#if RF455_NORMAL_MAP
    float3 tangent = input.tangent - normal * dot(normal, input.tangent);
    float tangentLength = dot(tangent, tangent);
    if (tangentLength > 0.000001) {
        tangent *= rsqrt(tangentLength);
        float3 bitangent = safeUnit(cross(normal, tangent));
        float2 xy = tex2D(normalMap, input.uv).xy * 2 - 1;
        float3 mapped = safeUnit(float3(xy, sqrt(max(0, 1 - dot(xy, xy)))));
        normal = safeUnit(mapped.x * tangent + mapped.y * bitangent + mapped.z * normal);
    }
#endif
    float3 light = safeUnit(-lightDirection.xyz);
    float ndotl = saturate(dot(normal, light));
    // Keep map-derived material colour. Per-pixel normals provide the shape;
    // this is not a post-process brightness or contrast filter.
    float3 colour = albedo.rgb * (materialAmbient.rgb + materialDiffuse.rgb * ndotl);
#if RF455_SPECULAR_MAP
    float3 eye = safeUnit(cameraPosition.xyz - input.worldPosition);
    float3 halfVector = safeUnit(light + eye);
    float highlight = pow(saturate(dot(normal, halfVector)), materialSpecular.w) * ndotl;
    float3 mask = saturate(tex2D(specularMap, input.uv).rgb);
    colour += materialSpecular.rgb * mask * highlight;
#endif
    return float4(colour, albedo.a * materialDiffuse.a);
}
)HLSL";
