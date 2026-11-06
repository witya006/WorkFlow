#pragma once
#include <cstddef>
#include <cstdint>
#include <memory>

struct RF455TutorialIntroSegment {std::uint32_t label,start,end;};
struct RF455TutorialIntroSequence {const char* cameraPath;const RF455TutorialIntroSegment* segments;std::size_t count;};
const RF455TutorialIntroSequence* RF455_GetTutorialIntroSequence(std::uint8_t avatarRace);

// Real dependencies are mandatory. The production Tutorial owner must bind these
// to its camera, screen, board and455 engine controls; none has a success default.
class RF455TutorialIntroHost {
public:
    virtual ~RF455TutorialIntroHost()=default;
    virtual bool loadCamera(const char*)=0;
    virtual std::uint32_t cameraCount()=0;
    virtual void selectCamera(std::uint32_t ordinal,std::uint32_t start,std::uint32_t end,std::uint32_t flag)=0;
    virtual bool playCamera(float matrix[4][4],float speed,bool paused)=0;
    virtual void applyCameraMatrix(float matrix[4][4])=0;
    virtual float cameraSeconds()=0;
    virtual bool fading()=0;
    virtual void fadeIn(std::uint32_t color,float seconds,float density)=0;
    virtual void fadeOut(std::uint32_t color,float seconds,float density)=0;
    virtual void setEngineRenderFlag(std::uint32_t)=0; //8CED70,additional consumers unported
    virtual void setEngineFloat8CE9D0(float)=0;
    virtual std::uint32_t cameraControlFlags()=0; //8D4CA0
    virtual void setCameraControlFlags(std::uint32_t)=0; //8D4C30
    virtual void blockStageInput(bool)=0;
    virtual void showScreen(bool)=0;
    virtual void showMouse(bool)=0;
    virtual void startBoardScript()=0;
    virtual void followAvatarCamera()=0;
};

// Source-owned state of558620/5594D0/intro branch5590B0. It is not an overlay.
class RF455TutorialIntro {
    const RF455TutorialIntroSequence* m_sequence=nullptr;
    std::uint32_t m_pending=0,m_ordinal=0;
    bool m_active=false;
public:
    void initCounters(){m_pending=m_ordinal=0;}
    bool load(std::uint8_t avatarRace,RF455TutorialIntroHost&);
    void frame(RF455TutorialIntroHost&,bool& skipRequested);
    bool active()const{return m_active;}
    std::uint32_t ordinal()const{return m_ordinal;}
    std::uint32_t pending()const{return m_pending;}
};

class CAniCamera;
// Shared real engine camera/fade backend. UI/stage/QBI/455 engine-state consumers
// remain mandatory abstract methods for the eventual CGP_Tutorial owner.
class RF455TutorialIntroCameraHost : public RF455TutorialIntroHost {
    std::unique_ptr<CAniCamera> m_camera;
    float m_matrix[4][4]={},m_position[3]={};
public:
    RF455TutorialIntroCameraHost();
    ~RF455TutorialIntroCameraHost()override;
    bool loadCamera(const char*)override;
    std::uint32_t cameraCount()override;
    void selectCamera(std::uint32_t,std::uint32_t,std::uint32_t,std::uint32_t)override;
    bool playCamera(float matrix[4][4],float,bool)override;
    void applyCameraMatrix(float matrix[4][4])override;
    float cameraSeconds()override;
    bool fading()override;
    void fadeIn(std::uint32_t,float,float)override;
    void fadeOut(std::uint32_t,float,float)override;
    const float* position()const{return m_position;}
    const float* viewMatrix()const{return &m_matrix[0][0];}
    CAniCamera& camera(){return *m_camera;}
};
