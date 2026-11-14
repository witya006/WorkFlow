#pragma once
// Shared world-space lighting for lobby BSP and skinned actors. Shadow only
// modulates the direct sun; diffuse sky/bounce remains readable in all slots.
static const char RF455LobbyLightingShader[]=R"HLSL(
float3 LobbySun(){return normalize(float3(-.35,.8,-.45));}
float3 LobbyDecode(float3 c){c=max(c,0);return lerp(c/12.92,pow((c+.055)/1.055,2.4),step(.04045,c));}
float3 LobbyEncode(float3 c){c=max(c,0);return lerp(c*12.92,1.055*pow(c,1.0/2.4)-.055,step(.0031308,c));}
float3 LobbyFill(float3 n){
    // A readable floor for every actor slot, without a bright overhead dome
    // competing with the sun. The planet below contributes a cool broad bounce.
    float planet=saturate(-n.y),upper=saturate(n.y);
    return float3(.30,.32,.36)+float3(.025,.075,.12)*planet+float3(.04,.05,.06)*upper;
}
float LobbyShadow(sampler2D depthMap,float4 clip,float4 settings,float nl){
    if(settings.x<.5)return 1;
    float3 p=clip.xyz/clip.w;
    float2 uv=float2(p.x*.5+.5,.5-p.y*.5)+settings.y*.5;
    if(any(uv<.002)||any(uv>.998)||p.z<=0||p.z>=1)return 1;
    float z=p.z-(settings.z+settings.w*(1-nl));
    float sum=0;
    [unroll]for(int y=-1;y<=2;++y)[unroll]for(int x=-1;x<=2;++x){
        float depth=tex2D(depthMap,uv+(float2(x,y)-.5)*settings.y*1.15).r;
        sum+=step(z,depth);
    }
    return sum*(1.0/16.0);
}
float3 LobbySpecular(float3 n,float3 v,float3 l,float3 f0,float roughness){
    float3 h=normalize(v+l);float nl=saturate(dot(n,l)),nv=max(saturate(dot(n,v)),.001);
    float nh=saturate(dot(n,h)),vh=saturate(dot(v,h));
    float a=roughness*roughness,a2=a*a,den=nh*nh*(a2-1)+1;
    float D=a2/max(3.14159265*den*den,.0001),k=(roughness+1)*(roughness+1)/8;
    float G=(nl/(nl*(1-k)+k))*(nv/(nv*(1-k)+k));
    float3 F=f0+(1-f0)*pow(1-vh,5);
    return D*G*F/max(4*nl*nv,.001)*nl;
}
)HLSL";
