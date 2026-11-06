#include "client455_nation_paths.h"
#include <windows.h>
#include <cstdio>
#include <cstring>
#include <string>
#include <vector>

int main(int argc,char**argv){
    if(argc!=3)return 200;FILE*f=std::fopen(argv[1],"rb");if(!f)return 201;
    char line[512];unsigned records=0;
    while(std::fgets(line,sizeof(line),f)){
        std::vector<std::string> cells;char*p=line,*start=p;for(;;++p)if(*p=='\t'||*p=='\n'||!*p){cells.emplace_back(start,p-start);if(*p!='\t')break;start=p+1;}
        if(cells.size()!=6)return 202;unsigned id=0,charset=0;std::sscanf(cells[0].c_str(),"%u",&id);std::sscanf(cells[5].c_str(),"%u",&charset);
        const auto& d=RF455_NationDescriptor(id);std::string hex;for(const unsigned char*c=reinterpret_cast<const unsigned char*>(d.font);*c;++c){char b[3];std::sprintf(b,"%02x",*c);hex+=b;}
        if(RF455_MapNation(cells[1].c_str())!=id||cells[1]!=d.setting||cells[2]!=d.folder||cells[3]!=d.crtLocale||cells[4]!=hex||charset!=d.charset)return 203;
        if(!WritePrivateProfileStringA("Setup","Language",cells[1].c_str(),argv[2]))return 204;
        RF455NationPaths state;if(!RF455_ReadNationPaths(argv[2],&state)||state.nation!=id||!state.configured||cells[2]!=state.folder||std::string(".\\DataTable\\")+cells[2]!=state.dataRoot)return 205;
        std::string lower=cells[1];lower[0]=static_cast<char>(lower[0]+32);if(RF455_MapNation(lower.c_str())!=0xffff)return 206;
        ++records;
    }std::fclose(f);if(records!=11)return 207;
    RF455NationPaths state;if(!RF455_ReadNationPaths(argv[2],&state))return 208;const auto saved=state;
    for(const auto& invalid:std::vector<std::string>{"","RussiaX","ru-ru","korea",std::string(200,'A')}){
        if(!WritePrivateProfileStringA("Setup","Language",invalid.c_str(),argv[2])||RF455_ReadNationPaths(argv[2],&state)||state.nation!=saved.nation||std::strcmp(state.dataRoot,saved.dataRoot))return 209;
    }
    WritePrivateProfileStringA("Setup",nullptr,nullptr,argv[2]);if(RF455_ReadNationPaths(argv[2],&state))return 210;
    if(std::strcmp(RF455_NationDescriptor(11).folder,"ko-kr")||std::strcmp(RF455_NationDescriptor(0xffff).folder,"ko-kr"))return 211;
    std::puts("PASS:11binary-derived country records,profile reads,case/invalid/truncation/missing/reload domains");return 0;
}
