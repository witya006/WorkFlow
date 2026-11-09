#include "gameobject/manager/ccharactermgr.h"
#include "gameobject/board/common/cboardmanager.h"
#include "cland.h"
#include "ccamera.h"
#include "datafile.h"
#include "datatable/cresourcedatamgr.h"
#include "input/imeedit.h"
#include "gameprogress/cgameprogress.h"
#include "userinterface/spritemgr.h"
#include "mainapp.h"
#include "addcodebyjang/effectcore.h"
#include "client455_nuclear_aiming.h"
#include <cstring>
#include <stdexcept>

extern CMainApp g_MainApp;
namespace {
void cursor(float* out){
    // The target's menu-level dummy does not initialize this output. Keep that
    // unsafe domain explicit; the real loaded perspective level uses its BSP.
    auto* level=_GetLevel();
    if(!level||!level->IsLoadedBsp())throw std::logic_error("455 nuclear cursor requires an actual loaded level");
    if(GetR3State()->mMatProj._44!=0)throw std::logic_error("455 nuclear orthographic ray provider remains open");
    if(!level->GetPointFromScreenRay(gMouse.x,gMouse.y,reinterpret_cast<Vector3f*>(out)))
        throw std::logic_error("455 nuclear world cursor outside accepted BSP ray domain");
}
}
RF455NuclearAiming& RF455_NuclearAiming(){return g_MainApp.NuclearAiming455();}
void RF455NuclearAiming::SetPending(DWORD value){
    if(!pending)SetVisualState(value);
    pending=value;
}
void RF455NuclearAiming::SetVisualState(DWORD value){
    if(value==1){
        if(effectHandle){SetDisapearTimeMagicEffect(effectHandle,0);effectHandle=0;}
        float point[3];cursor(point);
        // Target StartMagicEffectType's null-character case preserves the
        // supplied position: GetCreatePos(null,create_type) returns false.
        effectHandle=StartMagicEffect(point,0,1358041136,nullptr,_EF_STATE_ALWAYS_LIVE);
        g_MainApp.TaggedAudio455().PlayAtListener(277034,1,1);
        GetR3State()->mDynamicLight=3;
    }else if(effectHandle){
        SetDisapearTimeMagicEffect(effectHandle,0);effectHandle=0;
        g_MainApp.TaggedAudio455().Stop(277034,1);
    }
}
void RF455NuclearAiming::SetPosition(const float* value){for(unsigned i=0;i<3;++i)position[i]=value[i];}
void RF455NuclearAiming::FrameMove(){
    if(effectHandle&&pending){float point[3];cursor(point);MovePosMagicEffect(effectHandle,point,0);}
}
void RF455NuclearAiming::Clear(){std::memset(position,0,sizeof(position));SetVisualState(0);pending=0;}
