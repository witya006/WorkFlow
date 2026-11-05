#pragma once
#include "client455_character_draw.h"
#include <cstring>
namespace rf455draw {
template<class T>T get(const void* p,unsigned at){T v;std::memcpy(&v,static_cast<const unsigned char*>(p)+at,sizeof(v));return v;}
template<class T>void put(void* p,unsigned at,T v){std::memcpy(static_cast<unsigned char*>(p)+at,&v,sizeof(v));}
inline void unit(float* m){std::memset(m,0,64);m[0]=m[5]=m[10]=m[15]=1;}
float add(float,float);
float scale(float,double);
float mix(float,float);
float delta(unsigned,float,double);
float angle(float,float);
float absolute(float);
float advance(float,unsigned);
float ratio(unsigned,double);
float fourthWeight(const float*);
float weighted(const float*,const float*,bool);
bool equal(float,float);
bool less(float,float);
bool lessUnordered(float,float);
bool greater(float,float);
bool valid(const RF455CharacterDrawContext*);
void bindDeclaration(RF455CharacterDrawContext*);
void clearShaders(RF455CharacterDrawContext*);
void select(RF455CharacterDrawContext*,unsigned);
void projection(RF455CharacterDrawContext*);
void material(float*,const RF455CharacterStorage*,const RF455MeshStorage*);
void capturePalette(float*,const RF455MeshStorage*,const void*,const void*,const RF455MeshMatrixOps*);
RF455CharacterDrawStatus submit(RF455CharacterDrawContext*,RF455MeshStorage*,const void*,const float*,bool forceShared=false);
RF455CharacterDrawStatus batch(RF455CharacterDrawContext*,RF455MeshStorage*,const RF455CharacterStorage*,const void*);
RF455CharacterDrawStatus enqueue(RF455CharacterDrawContext*,RF455MeshStorage*,const RF455CharacterStorage*,unsigned,const void*,const void*,bool second);
bool immediate(const RF455MeshStorage*);
}
