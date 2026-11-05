#pragma once
#include "client455_renderer_owner.h"
#include <array>
#include <map>
#include <memory>
#include <string>
#include <vector>

// Own source record: the292-byte view supplies confirmed draw/particle fields.
// Text is held in modern strings,not transplanted into classic STL storage.
struct RF455EffectRecord {
    std::array<unsigned char,176> exported;
    std::array<unsigned char,292> draw;
    std::string file,mesh,texture[2],directory;
};
struct RF455EffectStore {std::map<std::string,std::map<std::string,std::unique_ptr<RF455EffectRecord>>> files;};
struct RF455EffectFileEntry {std::string file;int mode;};
struct RF455EffectFiles {std::map<unsigned,RF455EffectFileEntry> entries;};
enum RF455EffectStatus {RF_EFFECT_OK=0,RF_EFFECT_MISSING=1,RF_EFFECT_FORMAT=2,RF_EFFECT_NAME=3,RF_EFFECT_IO=4};
struct RF455EffectRead {RF455EffectStatus status;unsigned records,replaced,missing,ignored;};
RF455EffectRead RF455_ImportEffects(RF455EffectStore*,const char* file,const void*,std::size_t);
RF455EffectRead RF455_ParseEffects(const char* file,const void*,std::size_t,std::vector<RF455EffectRecord>*);
RF455EffectRead RF455_LoadEffects(RF455EffectStore*,const char* file);
RF455EffectRead RF455_LoadEffectFileTable(RF455EffectFiles*,RF455EffectStore*,const char* list,bool modeColumn);
RF455EffectRecord* RF455_FindEffect(RF455EffectStore*,const char* file,const char* uppercaseMesh);
// Actual textures use the existing source455manager. No successful fake backend.
void RF455_ApplyEffect(RF455CharacterRenderer*,RF455MeshStorage*,RF455EffectRecord*,int grade);
void RF455_ApplyInlineEffect(RF455CharacterRenderer*,RF455MeshStorage*,int grade);
int RF455_ApplyEffectFile(RF455EffectStore*,RF455CharacterRenderer*,RF455CharacterStorage*,const char* file,int grade);
unsigned RF455_EffectFactor(const void* intensityFloat,int grade);
RF455EffectStore& RF455_NormalEffects();
