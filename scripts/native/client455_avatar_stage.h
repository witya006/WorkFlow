#pragma once
#include <cstdint>

// Target stage IDs. Legacy0.7 MainGame still uses2 in its separate factory.
enum class RF455ClientStage : std::uint8_t {Title=0,Login=1,Tutorial=2,MainGame=3};
struct RF455AvatarStage {
    std::uint8_t current=0;
    std::uint32_t skipTutorial=0;
    bool is(std::uint8_t value)const{return current==value;}
    std::uint8_t select(std::uint8_t requested)const{return requested==2&&skipTutorial?3:requested;}
    bool handlesTutorialLocally()const{return current==2&&!skipTutorial;}
};
// Transitional source-ID bridge. Remove together with the legacy3stage factory.
std::uint8_t RF455_FromLegacyStage(std::uint8_t);
class CAvatar;
bool RF455_IsTutorialAvatarStage();
enum class RF455TutorialPacketRoute {Ignored,Transport,ClientHandler};
RF455TutorialPacketRoute RF455_TutorialPacketRoute(std::uint8_t group,std::uint8_t opcode);
