#include "client455_tutorial_intro.h"
#include "client455_tutorial_intro_tables.h"
#include <stdexcept>

const RF455TutorialIntroSequence* RF455_GetTutorialIntroSequence(std::uint8_t race){
    static const RF455TutorialIntroSequence sequences[]={
        {".\\map\\bellato\\bellato.cam",bellatoSegments,sizeof(bellatoSegments)/sizeof(*bellatoSegments)},
        {".\\map\\cora\\cora.cam",coraSegments,sizeof(coraSegments)/sizeof(*coraSegments)},
        {".\\map\\accretia\\accretia.cam",accretiaSegments,sizeof(accretiaSegments)/sizeof(*accretiaSegments)}};
    return race/2<3?&sequences[race/2]:nullptr;
}

bool RF455TutorialIntro::load(std::uint8_t race,RF455TutorialIntroHost& host){
    const auto* sequence=RF455_GetTutorialIntroSequence(race);
    if(!sequence||!host.loadCamera(sequence->cameraPath)||host.cameraCount()!=sequence->count)return false;
    m_sequence=sequence;host.selectCamera(0,sequence->segments[0].start,sequence->segments[0].end,1);m_active=true;
    host.setEngineRenderFlag(0x80000000u);host.setEngineFloat8CE9D0(0.15f);
    host.setCameraControlFlags(host.cameraControlFlags()|1u);host.blockStageInput(true);host.showScreen(false);host.showMouse(false);
    return true;
}

void RF455TutorialIntro::frame(RF455TutorialIntroHost& host,bool& skipRequested){
    if(m_active&&m_ordinal>=host.cameraCount()){
        host.fadeOut(0,0,1);host.fadeIn(0,5,1);host.blockStageInput(false);host.showScreen(true);host.showMouse(true);
        host.startBoardScript();m_active=false;host.setEngineRenderFlag(0);host.setEngineFloat8CE9D0(0.25f);
        host.setCameraControlFlags(host.cameraControlFlags()&~1u);
    }
    if(m_active){
        if(!m_sequence||m_ordinal>=m_sequence->count)throw std::logic_error("455 Tutorial camera/table mismatch");
        float matrix[4][4];if(host.playCamera(matrix,1,false))host.applyCameraMatrix(matrix);
        const auto threshold=static_cast<std::int32_t>(m_sequence->segments[m_ordinal].end-70u);
        if(static_cast<double>(threshold)<=static_cast<double>(host.cameraSeconds())*30.0&&m_pending==m_ordinal){host.fadeOut(0,2,1);++m_pending;}
        if(!host.fading()&&m_ordinal!=m_pending){
            m_ordinal=m_pending;
            if(m_ordinal<host.cameraCount()){
                if(m_ordinal>=m_sequence->count)throw std::logic_error("455 Tutorial camera/table mismatch");
                host.fadeIn(0,3,1);const auto& segment=m_sequence->segments[m_ordinal];host.selectCamera(m_ordinal,segment.start,segment.end,1);
            }
        }
        if(skipRequested){m_ordinal=0xffff;skipRequested=false;}
    }else host.followAvatarCamera();
}
