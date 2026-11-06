#include "gameobject/manager/ccharactermgr.h"
#include "gameobject/board/common/cboardmanager.h"
#include "cland.h"
#include "ccamera.h"
#include "datafile.h"
#include "datatable/cresourcedatamgr.h"
#include "item/citemmgr.h"
#include "input/imeedit.h"
#include "baseheader.h"
#include "gameprogress/cgameprogress.h"
#include "userinterface/spritemgr.h"
#include "mainapp.h"
#include <cstdio>
#include <cstring>
extern CMainApp g_MainApp;
// A compiler-typed pointer to the real normal member;no guessed byte offset.
template<class Tag,typename Tag::Type Member>struct MemberAccess{
    friend typename Tag::Type access(Tag){return Member;}
};
struct LandMember{using Type=CLand CMainApp::*;friend Type access(LandMember);};
template struct MemberAccess<LandMember,&CMainApp::m_cLand>;
#define REQUIRE(x) do{if(!(x)){std::fprintf(stderr,"Lifecycle line%d\n",__LINE__);return 1;}}while(0)

int main(int argc,char**argv){
    SetErrorMode(SEM_FAILCRITICALERRORS|SEM_NOGPFAULTERRORBOX|SEM_NOOPENFILEERRORBOX);
    if(argc!=3)return 200;
    const bool engine=std::strcmp(argv[1],"uncreated")!=0;
    const bool create=std::strcmp(argv[1],"created")==0;
    REQUIRE(create||engine&&std::strcmp(argv[1],"engine-only")==0||!engine);
    auto&land=g_MainApp.*access(LandMember{});
    REQUIRE(!land.GetLevel()&&!g_pLand&&!g_pLevel);
    // The actual owning global is uncreated. Before047 its destructor would
    // call ReleaseLevel with this==null after main returned.
    REQUIRE(land.UnloadLevel()==FALSE);
    REQUIRE(land.Destroy()==TRUE&&!land.GetLevel()&&!g_pLand&&!g_pLevel);
    REQUIRE(g_MainApp.Destroy()==FALSE);
    if(engine)InitR3Engine();
    if(create){
        REQUIRE(land.Create()==TRUE);
        REQUIRE(land.GetLevel()&&g_pLevel==land.GetLevel()&&g_pLand==&land);
        REQUIRE(land.Destroy()==TRUE);
        REQUIRE(!land.GetLevel()&&!g_pLevel&&!g_pLand);
        REQUIRE(land.UnloadLevel()==FALSE&&land.Destroy()==TRUE);
    }
    if(engine)ReleaseR3Engine();
    FILE*out=std::fopen(argv[2],"wb");REQUIRE(out);
    std::fprintf(out,"{\"status_before_crt_exit\":\"PASS\",\"mode\":\"%s\",\"normal_global_owner\":true,\"full_game_create_executed\":false}\n",argv[1]);
    std::fclose(out);
    // Let the real CRT invoke every normal global destructor. No debugger,
    // process termination, fake CLevel or branch/result override is used.
    return 0;
}
