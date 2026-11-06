#include "client455_nation_paths.h"
#include <windows.h>
#include <mbstring.h>
#include <cstdio>
#include <cstring>

namespace {
const RF455NationDescriptor descriptors[]={
    {"Korea","ko-kr","Korean_Korea","\xb1\xbc\xb8\xb2\xc3\xbc",129},
    {"Brazil","pt-br","Portuguese_Brazil","Arial",1},
    {"China","zh-cn","Chinese_China","SimSun",134},
    {"Europe","en-gb","English_United Kingdom","Arial",1},
    {"Indonesia","en-id","English_Indonesia","Arial",1},
    {"Japan","ja-jp","Japanese_Japan","MS Gothic",128},
    {"Philippines","en-ph","English_Philippines","Tahoma",1},
    {"Russia","ru-ru","Russian_Russia","Lucida Console",204},
    {"Taiwan","zh-tw","Chinese_Taiwan","MingLiU",136},
    {"USA","en-us","English_United Kingdom","Arial",1},
    {"Thailand","th-th","Thai_Thailand","Tahoma",222}
};
RF455NationPaths normal;
}
std::uint16_t RF455_MapNation(const char* text){
    for(unsigned i=0;i<11;++i)if(!_mbscmp(reinterpret_cast<const unsigned char*>(text),reinterpret_cast<const unsigned char*>(descriptors[i].setting)))return static_cast<std::uint16_t>(i);
    return 0xffff;
}
const RF455NationDescriptor& RF455_NationDescriptor(unsigned nation){return descriptors[nation<11?nation:0];}
bool RF455_ReadNationPaths(const char* ini,RF455NationPaths* state){
    char setting[128]={};GetPrivateProfileStringA("Setup","Language","",setting,sizeof(setting),ini);
    const auto nation=RF455_MapNation(setting);if(nation>11)return false;
    const auto& descriptor=RF455_NationDescriptor(nation);RF455NationPaths next;
    next.nation=nation;next.configured=true;std::strcpy(next.folder,descriptor.folder);std::sprintf(next.dataRoot,".\\DataTable\\%s",descriptor.folder);*state=next;return true;
}
RF455NationPaths* RF455_GetNormalNationPaths(){return &normal;}
const char* RF455_GetClientDataRoot(){return normal.dataRoot;}
int RF455_InitializeNationPaths(){
    if(!RF455_ReadNationPaths(".\\R3Engine.ini",&normal)){MessageBoxA(nullptr,"Nation Setting Failure.","RF Online",0);return 0;}
    OutputDebugStringA(RF455_GetClientDataRoot());return 1;
}
