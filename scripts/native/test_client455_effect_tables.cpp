#include "Character.h"
#include <cstdio>
#include <cstring>
#include <memory>
#include <stdexcept>
#include <string>
#include <vector>

#define E_REQUIRE(x) do{if(!(x)){std::fprintf(stderr,"Effect table failure line%d\n",__LINE__);return 1;}}while(0)
static bool write(const char* path,const char* data){FILE* file=std::fopen(path,"wb");if(!file)return false;const bool ok=std::fwrite(data,1,std::strlen(data),file)==std::strlen(data);std::fclose(file);return ok;}
static int synthetic(){
    std::unique_ptr<RF455EffectPatterns> patterns(new RF455EffectPatterns);RF455_ConstructEffectPatterns(patterns.get());RF455EffectItems items;
    E_REQUIRE(write("patterns.txt","1 1 0 2 0 3 0 4 0 5\r\n2 0 0 0 0 0 0 0 0 0\r\n2299 7 7 7 7 7 7 7 7 7\r\n2300 8 8 8 8 8 8 8 8 8\r\n-1 9 9 9 9 9 9 9 9 9\r\n"));
    E_REQUIRE(write("items.txt","10203040 1 0 0 0 0 2\r\n10203040 2 2 2 2 2 2\r\nABCDEF01 2299 0 0 0 0 -1\r\n"));
    auto a=RF455_ReadEffectPatterns(patterns.get(),"patterns.txt");auto b=RF455_ReadEffectItems(&items,"items.txt");
    E_REQUIRE(a.status==RF_EFFECT_TABLE_OK && a.scanned==5 && a.stored==3 && b.status==RF_EFFECT_TABLE_OK && b.stored==2 && b.duplicates==1 && items.entries.size()==2);
    E_REQUIRE(patterns->known[1]==511 && patterns->known[0]==RF455_EFFECT_ALL_KNOWN && patterns->present[2299]==1);
    for(unsigned grade=0;grade<9;++grade){const auto selected=RF455_SelectItemEffect(patterns.get(),&items,0x10203040,grade,0);E_REQUIRE(selected.status==RF_EFFECT_QUERY_OK && selected.effect==(grade%2?0:1+grade/2));E_REQUIRE(!RF455_SelectItemEffect(patterns.get(),&items,0x10203040,grade,5).effect);}
    E_REQUIRE(RF455_SelectItemEffect(patterns.get(),&items,0x10203040,9,0).status==RF_EFFECT_QUERY_UNDEFINED && RF455_SelectItemEffect(patterns.get(),&items,0x10203040,35,5).status==RF_EFFECT_QUERY_UNDEFINED);
    E_REQUIRE(RF455_SelectItemEffect(patterns.get(),&items,0x10203040,36,999).status==RF_EFFECT_QUERY_OK && !RF455_SelectItemEffect(patterns.get(),&items,0x10203040,0xffffffff,0).effect);
    E_REQUIRE(RF455_SelectItemEffect(patterns.get(),&items,0x55555555,0,999).status==RF_EFFECT_QUERY_OK && RF455_SelectItemEffect(patterns.get(),&items,0x10203040,0,6).status==RF_EFFECT_QUERY_GROUP);
    E_REQUIRE(RF455_SelectItemEffect(patterns.get(),&items,0xabcdef01,0,5).status==RF_EFFECT_QUERY_PATTERN && RF455_SelectItemEffect(patterns.get(),&items,0x10203040,35,1).status==RF_EFFECT_QUERY_OK);
    // Missing file/reload retains rows; patterns overwrite, item maps keep first.
    E_REQUIRE(RF455_ReadEffectPatterns(patterns.get(),"missing.txt").status==RF_EFFECT_TABLE_MISSING && patterns->values[1][0]==1);
    E_REQUIRE(write("reload.txt","1 20 21 22 23 24 25 26 27 28\n"));a=RF455_ReadEffectPatterns(patterns.get(),"reload.txt");E_REQUIRE(a.duplicates==1 && patterns->values[1][0]==20 && patterns->values[2][0]==0);
    // Short reads retain earlier item selector values, initialized once to zero.
    E_REQUIRE(write("partial-items.txt","A1 1 2 3 4 5 6\nA2 8"));RF455EffectItems partial;b=RF455_ReadEffectItems(&partial,"partial-items.txt");const std::array<unsigned,6> expectedPartial={8,2,3,4,5,6};E_REQUIRE(b.partial==1 && partial.entries[0xa2]==expectedPartial);
    E_REQUIRE(write("partial-pattern.txt","7"));RF455_ConstructEffectPatterns(patterns.get());a=RF455_ReadEffectPatterns(patterns.get(),"partial-pattern.txt");E_REQUIRE(a.partial==1 && patterns->known[7]==0 && patterns->present[7]==1);
    E_REQUIRE(write("malformed.txt","NOT_A_NUMBER"));E_REQUIRE(RF455_ReadEffectPatterns(patterns.get(),"malformed.txt").status==RF_EFFECT_TABLE_FORMAT && RF455_ReadEffectItems(&partial,"malformed.txt").status==RF_EFFECT_TABLE_FORMAT);
    // The original finite pattern loop makes2299attempts,not2300.
    FILE* file=std::fopen("limit.txt","wb");E_REQUIRE(file);for(unsigned i=0;i<2300;++i)std::fprintf(file,"%u 1 1 1 1 1 1 1 1 1\n",i);std::fclose(file);RF455_ConstructEffectPatterns(patterns.get());a=RF455_ReadEffectPatterns(patterns.get(),"limit.txt");E_REQUIRE(a.scanned==2299 && patterns->present[2298] && !patterns->present[2299]);
    return 0;
}
int main(int argc,char** argv){
    if(argc!=3)return 2;E_REQUIRE(synthetic()==0);const std::string root=argv[1];
    auto pattern=root+"/PatternList.txt",item=root+"/ItemEffectList.txt",golden=root+"/selection.bin";
    g_PatternList.LoadEffectPatternList(const_cast<char*>(pattern.c_str()));g_EffectItemList.LoadItemListFile(const_cast<char*>(item.c_str()));
    E_REQUIRE(g_PatternList.lastRead.status==RF_EFFECT_TABLE_OK && g_EffectItemList.lastRead.status==RF_EFFECT_TABLE_OK);
    FILE* file=std::fopen(golden.c_str(),"rb");E_REQUIRE(file);unsigned header[4];E_REQUIRE(std::fread(header,4,4,file)==4 && !std::memcmp(header,"EFT1",4));
    E_REQUIRE(g_EffectItemList.native.entries.size()==header[3]);unsigned rows=0;for(auto present:g_PatternList.native.present)rows+=present!=0;E_REQUIRE(rows==header[2]);unsigned unknown=0;
    for(unsigned i=0;i<header[1];++i){unsigned record[5];E_REQUIRE(std::fread(record,4,5,file)==5);const auto selected=RF455_SelectItemEffect(&g_PatternList.native,&g_EffectItemList.native,record[0],record[1],record[2]);E_REQUIRE(static_cast<unsigned>(selected.status)==record[3] && selected.effect==record[4]);
        if(selected.status==RF_EFFECT_QUERY_OK)E_REQUIRE(IsHaveMeshEffect(nullptr,record[0],record[1],record[2])==(record[4]!=0));
        else{bool threw=false;try{IsHaveMeshEffect(nullptr,record[0],record[1],record[2]);}catch(const std::runtime_error&){threw=true;}catch(const std::out_of_range&){threw=true;}E_REQUIRE(threw);unknown+=selected.status==RF_EFFECT_QUERY_UNDEFINED;}}
    std::fclose(file);E_REQUIRE(unknown>0 && !IsHaveMeshEffect(nullptr,0xffffffffu,0) && !IsHaveMeshEffect(nullptr,0xffffffffu,36));
    E_REQUIRE(!GetModuleHandleA("mss32.dll") && !GetModuleHandleA("ABuse.dll") && !GetModuleHandleA("Adv.dll") && !GetModuleHandleA("PDLL.dll"));
    file=std::fopen(argv[2],"wb");E_REQUIRE(file);std::fprintf(file,"{\"status\":\"PASS\",\"pattern_records\":%u,\"item_records\":%u,\"real_selection_cases\":%u,\"undefined_queries_explicit\":%u,\"synthetic_boundaries\":true,\"normal_facade\":true,\"game_dlls_loaded\":false}\n",rows,header[3],header[1],unknown);std::fclose(file);return 0;
}
