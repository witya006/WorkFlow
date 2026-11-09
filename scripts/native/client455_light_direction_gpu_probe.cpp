class CEntity;struct D3DXMATRIX;
static void directionGPU131(CEntity&,D3DXMATRIX&);
#define RF455_LIGHT_EXTRA directionGPU131
#define RF455_LIGHTING_CONSUMERS_NO_MAIN
#include "client455_lighting_consumers_probe.cpp"

static void directionGPU131(CEntity& entity,D3DXMATRIX& base){
    FILE* trace=std::fopen("light-direction.jsonl","wb");check(trace!=nullptr,"light direction trace131");auto* d=GetD3dDevice();auto* state=GetR3State();
    const unsigned short saved=cw125();const float transforms[6][9]={
        {1,0,0,0,1,0,0,0,1},{0,1,0,-1,0,0,0,0,1},
        {1,0,0,0,0,1,0,-1,0},{2,0,0,0,.5f,0,0,0,4},
        {1,.25f,-.5f,.125f,1,.375f,-.25f,.5f,1},
        {1.25f,.125f,-.25f,.5f,2,.375f,-.125f,.25f,.75f}};
    for(unsigned pc:{0u,2u,3u})for(unsigned rc=0;rc<4;++rc)for(unsigned i=0;i<6;++i){
        const unsigned short wanted=(saved&~0xf00u)|(pc<<8)|(rc<<10)|0x3f;setCW125(wanted);D3DXMATRIX world=base;
        for(unsigned row=0;row<3;++row)for(unsigned col=0;col<3;++col)world.m[row][col]=transforms[i][row*3+col];
        entity.mFlag=0x62;_ENTITY_LIST list={};list.ShaderID=1;list.Factor[0]=.75f;list.Factor[1]=.25f;
        check(SUCCEEDED(d->BeginScene()),"direction scene131");samples125.clear();
        {Hook130 hook(d);check(entity.DrawEntityVS(&list,world.m,0xc0ffffff)!=0,"actual direction draw131");}
        check(SUCCEEDED(d->EndScene())&&!samples125.empty(),"direction submission131");float constants[4];check(SUCCEEDED(d->GetVertexShaderConstantF(19,constants,1)),"direction constants131");
        check(cw125()==wanted,"direction caller CW retained131");
        std::fprintf(trace,"{\"id\":%u,\"cw\":%u,\"world\":",i,wanted);floats130(trace,&world.m[0][0],16);std::fputs(",\"input\":",trace);floats130(trace,state->mMainLightNomal,3);std::fputs(",\"output\":",trace);floats130(trace,constants,3);
        std::fprintf(trace,",\"draws\":%u,\"shader_bytes\":%u,\"stride\":%u}\n",unsigned(samples125.size()),shaderBytes130,stride130);
    }
    setCW125(saved);std::fclose(trace);
}
int main(){try{return run130();}catch(const std::exception& e){std::fprintf(stderr,"direction131:%s\n",e.what());return 1;}}
