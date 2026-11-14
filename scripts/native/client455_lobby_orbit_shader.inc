R"HLSL(
row_major float4x4 inverseProjection:register(c0);
row_major float4x4 inverseView:register(c4);
float4 eyeCloud:register(c8);
sampler2D spaceMap:register(s0);
sampler2D planetMap:register(s1);
sampler2D regionMap:register(s2);
struct Vertex {float4 position:POSITION0;float2 uv:TEXCOORD0;};
Vertex VS(Vertex v){return v;}
float3 decode(float3 c){return lerp(c/12.92,pow(max((c+.055)/1.055,0),2.4),step(.04045,c));}
float3 encode(float3 c){c=max(c,0);return lerp(c*12.92,1.055*pow(c,1.0/2.4)-.055,step(.0031308,c));}
float2 uvSphere(float3 n){return float2(atan2(n.z,n.x)*.15915494+.5,acos(clamp(n.y,-1,1))*.31830989);}
float3 starHash(float2 cell){
    // Integer celestial cells, never pixel coordinates or elapsed time.
    float3 p=frac(float3(cell.x,cell.y,cell.x)*float3(.1031,.1030,.0973));
    p+=dot(p,p.yxz+33.33);return frac((p.xxy+p.yzz)*p.zyx);
}
float3 stars(float3 ray,float2 uv,float footprint,float scale,float seed){
    float2 grid=float2(scale,scale*.5);
    float2 cell=floor(uv*grid);
    // Wrap longitude before hashing so the celestial meridian has no seam.
    cell.x=cell.x-floor(cell.x/grid.x)*grid.x;
    float3 h=starHash(cell+seed);
    float2 centre=.23+.54*h.xy;
    float latitude=sin(uv.y*3.14159265);
    float2 delta=(frac(uv*grid)-centre)/grid*float2(6.2831853*latitude,3.14159265);
    float distance2=dot(delta,delta);
    float bright=pow(h.x,4);
    float radius=lerp(.00024,.00070,bright);
    // Near the pole the cells converge. Fade the catalogue there rather than
    // stretching points into streaks or clipping them at cell boundaries.
    float polar=smoothstep(.08,.24,latitude);
    float presence=step(.956,h.z)*polar;
    float variance=radius*radius;
    float filtered=variance+footprint*footprint*.20;
    // Analytic pixel integration: stable subpixel energy through camera motion,
    // with a compact core and no animated jitter/twinkle or screen-space noise.
    float core=exp2(-2.88539*distance2/filtered)*(variance/filtered);
    float halo=exp2(-1.44270*distance2/(filtered*6))*.045*bright;
    float3 tint=lerp(float3(.66,.79,1),float3(1,.85,.66),h.x);
    return tint*(core+halo)*presence*lerp(1.8,5.0,bright);
}
float2 sphere(float3 origin,float3 ray,float3 center,float radius){
    float3 relative=origin-center;float b=dot(relative,ray),c=dot(relative,relative)-radius*radius;
    float h=b*b-c;if(h<0)return float2(-1,-1);h=sqrt(h);return float2(-b-h,-b+h);
}
float3 surfaceColor(float3 origin,float3 ray,float distance,float3 center,float radius,float3 sun){
    float3 p=origin+ray*distance,n=normalize(p-center);
    float3 mapped=float3(n.x,n.y*.5-n.z*.8660254,n.y*.8660254+n.z*.5);
    float2 uv=uvSphere(mapped);
    // A diffuse map on a real sphere, lit in the same world space as the station.
    float3 albedo=decode(tex2D(planetMap,uv+float2(.13,0)).rgb);
    // High-detail regional imagery belongs to a fixed spherical cap. It moves
    // with the planet, not the camera, and blends into the global map at its edge.
    const float3 capFront=float3(.619,.687,-.379);
    const float3 capRight=float3(-.522,0,-.853);
    const float3 capUp=float3(-.586,.726,.359);
    float facing=dot(n,capFront);
    float2 regionUV=.5+float2(dot(n,capRight),-dot(n,capUp))*.55/max(facing,.05);
    float border=max(abs(regionUV.x-.5),abs(regionUV.y-.5));
    float regionWeight=(1-smoothstep(.35,.49,border))*smoothstep(.3,.5,facing);
    albedo=lerp(albedo,decode(tex2D(regionMap,saturate(regionUV)).rgb),regionWeight);
    float nl=dot(n,sun),light=saturate(nl);
    float sea=1-smoothstep(.06,.23,albedo.r);
    float3 reflected=reflect(ray,n);
    float glint=pow(saturate(dot(reflected,sun)),120)*sea;
    float3 lit=albedo*(float3(.055,.095,.17)+float3(1.35,1.19,.99)*light);
    lit+=float3(1.0,.78,.48)*glint*.65;
    float edge=pow(1-saturate(dot(n,-ray)),3.3);
    lit=lerp(lit,float3(.13,.36,.70)*( .35+1.1*light),edge*.72);
    return lit;
}
float4 PS(Vertex i):COLOR0{
    float4 viewPoint=mul(float4(i.uv.x*2-1,1-i.uv.y*2,1,1),inverseProjection);
    float3 ray=normalize(mul(float4(viewPoint.xyz/viewPoint.w,0),inverseView).xyz);
    float3 origin=eyeCloud.xyz;
    float3 sun=normalize(float3(-.35,.8,-.45));
    float2 uv=uvSphere(ray);uv.x+=.17;
    // Fixed celestial directions; camera translation never drags the galaxy.
    // The 1774x887 panorama supplies nebula structure, not magnified star discs.
    // Suppress isolated bright map texels while retaining dark dust filaments.
    float3 nebula=decode(tex2Dlod(spaceMap,float4(uv,0,3)).rgb);
    float3 detail=decode(tex2Dlod(spaceMap,float4(uv,0,1.5)).rgb);
    detail=min(detail,nebula*1.12+.008);
    float3 sky=lerp(nebula,detail,.40)*1.25+float3(.0025,.004,.008);
    float footprint=max(length(ddx(ray)),length(ddy(ray)));
    sky+=stars(ray,uv,footprint,512,17);
    sky+=stars(ray,uv+float2(.317,0),footprint,768,83)*.55;
    float sunDot=saturate(dot(ray,sun));
    sky+=float3(1.0,.63,.30)*pow(sunDot,30)*.28;
    sky+=float3(1.6,1.11,.62)*pow(sunDot,260)*.45;
    sky+=float3(10,8.2,5.7)*smoothstep(.99982,.99996,sunDot);
    // Small remote moon: an independent body with its own parallax/terminator.
    const float3 moonCenter=float3(22,11,-34);const float moonRadius=4.8;
    float2 moonHit=sphere(origin,ray,moonCenter,moonRadius);
    if(moonHit.x>0){
        float3 n=normalize(origin+ray*moonHit.x-moonCenter);
        float3 moonAlbedo=decode(tex2D(planetMap,uvSphere(n)+float2(.51,0)).rgb);
        float rock=dot(moonAlbedo,float3(.4,.3,.3));
        sky=float3(.34,.39,.49)*(rock*.85+.10)*(.12+saturate(dot(n,sun))*1.5);
        sky+=float3(.04,.11,.23)*pow(1-saturate(dot(n,-ray)),4);
    }
    // Novus beneath the orbital station. World units are kilometres here;
    // the fixed centre preserves curvature and translation parallax.
    const float3 center=float3(-6.8,-7.6,3.7);const float radius=7.25;
    const float atmosphereThickness=.13;
    float2 ground=sphere(origin,ray,center,radius);
    float2 atmosphere=sphere(origin,ray,center,radius+atmosphereThickness);
    if(ground.x>0)sky=surfaceColor(origin,ray,ground.x,center,radius,sun);
    if(atmosphere.x>0){
        float end=ground.x>0?ground.x:atmosphere.y;
        float lengthInside=max(0,end-atmosphere.x);
        float3 p=origin+ray*((atmosphere.x+end)*.5),n=normalize(p-center);
        float light=saturate(dot(n,sun)*2+.28);
        float optical=0;
        [unroll]for(int sampleIndex=0;sampleIndex<8;++sampleIndex){
            float3 samplePosition=origin+ray*(atmosphere.x+lengthInside*(sampleIndex+.5)/8);
            float height=saturate((length(samplePosition-center)-radius)/atmosphereThickness);
            optical+=exp(-height*4.5)*(1-smoothstep(.75,1,height));
        }
        float density=1-exp(-optical*lengthInside*.65);
        float forward=pow(saturate(dot(ray,sun)),12);
        float3 air=lerp(float3(.10,.30,.68),float3(1.0,.44,.14),forward*.8)*(light*.85+.12);
        sky=lerp(sky,air,density*.78);
    }
    return float4(eyeCloud.w>.5?sky:encode(sky),1);
}
)HLSL"
