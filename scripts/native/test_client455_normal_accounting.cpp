#include "Character.h"
#include "client455_normal_accounting.h"
#include <cstdio>
#include <cstring>

#define REQUIRE(x) do{if(!(x)){std::fprintf(stderr,"Accounting failure line%d\n",__LINE__);return 1;}}while(0)
int main(int argc,char** argv){
    if(argc!=3)return 2;FILE* input=std::fopen(argv[1],"rb");REQUIRE(input);std::fseek(input,0,SEEK_END);const unsigned length=static_cast<unsigned>(std::ftell(input));std::fclose(input);REQUIRE(length>100);
    auto* accounting=RF455_GetNormalCharacterAccounting();const auto saved=*accounting;
    accounting->meshes={0xfffffffeu,0xfffffff0u};accounting->buffers={17,3};accounting->importedAnimationBytes=0xffffffffu-length+7;
    const auto before=RF455_GetCharacterMemoryInfo();REQUIRE(before.m_ObjectNum==0xfffffffeu && before.m_ObjectSize==0xfffffff0u && before.m_VertexSize==17 && before.m_VetexNum==3);
    const auto memory=RF455_CrtMeshMemoryOps();auto* meshes=RF455_AllocateMeshArray(2,&accounting->meshes,&memory);REQUIRE(meshes);
    const auto created=RF455_GetCharacterMemoryInfo();REQUIRE(created.m_ObjectNum==0 && created.m_ObjectSize==0xfffffff0u+2*5803u);
    RF455_DeleteMeshStorage(meshes,3,&memory);const auto deleted=RF455_GetCharacterMemoryInfo();REQUIRE(!std::memcmp(&created,&deleted,sizeof(created)));
    unsigned expected=before.m_AniSize;
    for(unsigned owner=0;owner<2;++owner){
        const auto ownerBefore=RF455_GetCharacterMemoryInfo();
        {ChInterface renderer;AnimationManager animations;const auto constructor=RF455_GetCharacterMemoryInfo();REQUIRE(!std::memcmp(&ownerBefore,&constructor,sizeof(constructor)));
            auto* animation=renderer.AddAnimationData(&animations,argv[1]);REQUIRE(animation && renderer.IsLoadAnimation(animation));expected+=length;
            const auto loaded=RF455_GetCharacterMemoryInfo();REQUIRE(loaded.m_AniSize==expected && loaded.m_ObjectNum==created.m_ObjectNum && loaded.m_ObjectSize==created.m_ObjectSize && loaded.m_VertexSize==17 && loaded.m_VetexNum==3);
            REQUIRE(renderer.IsLoadAnimation(animation));const auto cached=RF455_GetCharacterMemoryInfo();REQUIRE(!std::memcmp(&loaded,&cached,sizeof(loaded)));
        }
        const auto released=RF455_GetCharacterMemoryInfo();REQUIRE(released.m_AniSize==expected && released.m_ObjectSize==created.m_ObjectSize);
    }
    const auto textures=RF455_GetTextureAccounting();const auto final=RF455_GetCharacterMemoryInfo();REQUIRE(final.m_TextureSize==textures.estimatedBytes && final.m_TextureNum==textures.created);
    *accounting=saved;FILE* output=std::fopen(argv[2],"wb");REQUIRE(output);
    std::fprintf(output,"{\"status\":\"PASS\",\"real_ani_bytes\":%u,\"renderer_owners\":2,\"cumulative_after_release\":true,\"cached_load_unchanged\":true,\"dword_wrap\":true,\"real_mesh_lifetime\":true,\"snapshot_fields\":7}\n",length);std::fclose(output);return 0;
}
