#pragma once
#include <cstddef>
#include <cstdint>
#include <vector>

struct RF455LanguageRecord {std::uint32_t id;std::vector<unsigned char> text;};
// Own source owner,not an overlay of the original12byte private C++ object.
struct RF455LanguagePack {
    std::uint32_t codepage=0,count=0;
    std::vector<RF455LanguageRecord> records;
    const char* get(std::uint32_t index)const;
    bool isLead(const char* text,int index)const;
    bool isTrail(const char* text,int index)const;
    void release(); // Original clears the record pointer,retains count/codepage.
};
bool RF455_DecodeEdf(const void*,std::size_t,std::vector<unsigned char>&);
bool RF455_ParseLanguagePayload(RF455LanguagePack&,const void*,std::size_t,unsigned codepage);
bool RF455_LoadLanguagePack(RF455LanguagePack&,const char* filename,unsigned codepage);
unsigned RF455_CountryCodePage(unsigned nation);
RF455LanguagePack* RF455_GetNormalLanguagePack();
// Country codepage/CRT agreement and real NDLanguage data only. Full font and
// ETCAction/launcher policies remain separate unfinished startup contracts.
int RF455_InitializeLanguageData();
