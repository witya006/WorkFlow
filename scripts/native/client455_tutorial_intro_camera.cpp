#include "client455_tutorial_intro.h"
#include "core.h"
#include "commonutil.h"
#include "anicamera.h"
#include "r3enginekernel.h"
#include "r3move.h"
#include "r3util.h"
#include <cstring>
#include <string>

RF455TutorialIntroCameraHost::RF455TutorialIntroCameraHost():m_camera(new CAniCamera){}
RF455TutorialIntroCameraHost::~RF455TutorialIntroCameraHost(){m_camera->ReleaseAniCamera();}
bool RF455TutorialIntroCameraHost::loadCamera(const char* path){
    m_camera->ReleaseAniCamera();std::string name(path);m_camera->LoadAniCamera(&name[0]);return m_camera->IsLoadedAniCamera()!=FALSE;
}
std::uint32_t RF455TutorialIntroCameraHost::cameraCount(){return m_camera->GetCameraNum();}
void RF455TutorialIntroCameraHost::selectCamera(std::uint32_t id,std::uint32_t start,std::uint32_t end,std::uint32_t flag){m_camera->SetPrePlayCamera(id,start,end,flag);}
bool RF455TutorialIntroCameraHost::playCamera(float matrix[4][4],float speed,bool paused){return m_camera->PlayAniCamera(matrix,speed,paused?TRUE:FALSE)!=FALSE;}
void RF455TutorialIntroCameraHost::applyCameraMatrix(float matrix[4][4]){R3SetCameraMatrix(m_position,matrix);std::memcpy(m_matrix,&GetR3State()->mMatView,64);}
float RF455TutorialIntroCameraHost::cameraSeconds(){return m_camera->GetNowFrame();}
bool RF455TutorialIntroCameraHost::fading(){return IsFading()!=FALSE;}
void RF455TutorialIntroCameraHost::fadeIn(std::uint32_t color,float seconds,float density){SetFadeIn(color,seconds,density);}
void RF455TutorialIntroCameraHost::fadeOut(std::uint32_t color,float seconds,float density){SetFadeOut(color,seconds,density);}
