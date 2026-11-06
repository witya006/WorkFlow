#include "client455_language.h"
#include "client455_nation_paths.h"
#include <windows.h>
#include <clocale>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <fstream>
#include <iterator>
#include <string>
#include <vector>

static std::vector<unsigned char>read(const char*p){std::ifstream f(p,std::ios::binary);return {std::istreambuf_iterator<char>(f),std::istreambuf_iterator<char>()};}
static void put(std::vector<unsigned char>&v,unsigned n){const auto*b=reinterpret_cast<const unsigned char*>(&n);v.insert(v.end(),b,b+4);}
int main(int argc,char**argv){
    if(argc!=3)return 200;std::ifstream manifest(argv[1]);if(!manifest)return 201;std::string line;unsigned files=0,total=0;
    while(std::getline(manifest,line)){
        std::vector<std::string>parts;std::size_t start=0;for(std::size_t i=0;i<=line.size();++i)if(i==line.size()||line[i]=='\t'){parts.push_back(line.substr(start,i-start));start=i+1;}
        if(parts.size()!=4)return 202;unsigned cp=std::strtoul(parts[0].c_str(),nullptr,10),expected=std::strtoul(parts[3].c_str(),nullptr,10);const auto raw=read(parts[1].c_str()),golden=read(parts[2].c_str());std::vector<unsigned char>decoded;
        if(!RF455_DecodeEdf(raw.data(),raw.size(),decoded)||decoded!=golden)return 203;RF455LanguagePack pack;
        if(!RF455_LoadLanguagePack(pack,parts[1].c_str(),cp)||pack.count!=expected||pack.codepage!=cp||pack.records.size()!=expected)return 204;
        std::vector<unsigned char>roundtrip;put(roundtrip,pack.count);
        for(unsigned i=0;i<pack.count;++i){const auto&r=pack.records[i];put(roundtrip,r.id);put(roundtrip,static_cast<unsigned>(r.text.size()));roundtrip.insert(roundtrip.end(),r.text.begin(),r.text.end());if(pack.get(i)!=reinterpret_cast<const char*>(r.text.data())||r.text.empty()||r.text.back())return 205;}
        if(roundtrip!=golden||std::strcmp(pack.get(pack.count),"")||std::strcmp(pack.get(0xffffffff),""))return 206;
        // Independent Windows character traversal versus the recovered index API.
        unsigned scanned=0;
        for(const auto&r:pack.records){
            const char*text=reinterpret_cast<const char*>(r.text.data());const auto length=std::strlen(text);if(length>300||scanned>=40)continue;
            for(const char*p=text;*p;){const char*next=CharNextExA(static_cast<WORD>(cp),p,0);const auto span=next-p;const int pos=static_cast<int>(p-text);
                if(pack.isLead(text,pos)!=(span==2)||pack.isTrail(text,pos))return 207;
                if(span==2&&(!pack.isTrail(text,pos+1)||pack.isLead(text,pos+1)))return 208;p=next;}
            if(pack.isLead(text,-1)||pack.isTrail(text,static_cast<int>(length))||pack.isLead(nullptr,0))return 209;++scanned;
        }
        const auto count=pack.count;pack.release();if(!pack.records.empty()||pack.count!=count||pack.codepage!=cp||std::strcmp(pack.get(0),""))return 210;
        total+=count;++files;
    }
    // Lookup is positional even with nonsequential/duplicate record IDs.
    std::vector<unsigned char>plain;put(plain,2);put(plain,900);put(plain,2);plain.push_back('A');plain.push_back(0);put(plain,900);put(plain,2);plain.push_back('B');plain.push_back(0);RF455LanguagePack pack;
    if(!RF455_ParseLanguagePayload(pack,plain.data(),plain.size(),1251)||std::strcmp(pack.get(0),"A")||std::strcmp(pack.get(1),"B")||std::strcmp(pack.get(900),""))return 211;
    for(std::size_t n:std::vector<std::size_t>{0,1,3,4,7,11,12,13,19,23}){RF455LanguagePack bad;if(RF455_ParseLanguagePayload(bad,plain.data(),n,949))return 212;}
    unsigned zero=0;if(RF455_ParseLanguagePayload(pack,&zero,4,949)||pack.count!=0||pack.codepage!=1251||std::strcmp(pack.get(0),""))return 213;pack.release();
    std::vector<unsigned char>shortEdf(288,0),decoded;if(RF455_DecodeEdf(shortEdf.data(),shortEdf.size(),decoded)||RF455_LoadLanguagePack(pack,"nonexistent-language.edf",949))return 214;
    // Country providers and CRT category agreement,independent expected file.
    std::ifstream countries(argv[2]);unsigned locales=0;while(std::getline(countries,line)){
        unsigned nation=0,cp=0;if(std::sscanf(line.c_str(),"%u %u",&nation,&cp)!=2||RF455_CountryCodePage(nation)!=cp)return 215;
        const char*locale=std::setlocale(LC_COLLATE,RF455_NationDescriptor(nation).crtLocale);const char*dot=locale?std::strchr(locale,'.'):nullptr;
        if(!dot||std::strtoul(dot+1,nullptr,10)!=cp)return 216;++locales;
    }
    if(files!=9||locales!=11)return 217;std::printf("{\"status\":\"PASS\",\"files\":%u,\"records\":%u,\"country_locales\":%u,\"byte_roundtrip\":true,\"indexed_lookup\":true,\"dbcs_boundaries\":true,\"release\":true,\"bounded_malformed_inputs\":true}\n",files,total,locales);return 0;
}
