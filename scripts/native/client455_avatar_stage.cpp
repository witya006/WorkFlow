#include "client455_avatar_stage.h"

std::uint8_t RF455_FromLegacyStage(std::uint8_t value){return value==2?3:value;}
RF455TutorialPacketRoute RF455_TutorialPacketRoute(std::uint8_t group,std::uint8_t opcode){
    using Route=RF455TutorialPacketRoute;
    switch(group){
    case 1:return opcode==17?Route::Transport:Route::Ignored;
    case 4:return opcode==1||opcode==19||opcode==31?Route::ClientHandler:Route::Ignored;
    case 5:return Route::ClientHandler; // Even unknown opcodes can emit local attack failure feedback.
    case 7:return opcode==2||opcode==5||opcode==9||opcode==11||opcode==13?Route::ClientHandler:Route::Ignored;
    case 13:return opcode==2||opcode==21||opcode==26?Route::ClientHandler:Route::Ignored;
    case 17:return opcode==4?Route::ClientHandler:Route::Ignored;
    default:return Route::Ignored;
    }
}
