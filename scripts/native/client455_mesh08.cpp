#include "client455_mesh08.h"
#include <cstring>
#include <limits>

namespace {
constexpr std::size_t headerBytes=693,vertexBytes=64,boneBytes=404;
constexpr std::uint16_t indexLimit=64000;
const unsigned char magic[6]={'M','E','S','H','0','8'};
struct Reader {
    const unsigned char* data;std::size_t size,at;
    bool take(std::size_t count,const unsigned char*& value) {
        if(count>size-at)return false;
        value=data+at;at+=count;return true;
    }
    bool word(std::uint16_t& value) {
        const unsigned char* p;if(!take(2,p))return false;
        value=static_cast<std::uint16_t>(p[0]|(static_cast<unsigned>(p[1])<<8));return true;
    }
};
bool addSize(std::size_t& size,std::size_t count,std::size_t stride) {
    if(count>((std::numeric_limits<std::size_t>::max)()-size)/stride)return false;
    size+=count*stride;return true;
}
void putWord(unsigned char*& out,std::uint16_t value) {
    *out++=static_cast<unsigned char>(value);*out++=static_cast<unsigned char>(value>>8);
}
void putBytes(unsigned char*& out,const unsigned char* in,std::size_t count) {
    if(count)std::memmove(out,in,count);out+=count;
}
}

extern "C" RF455Mesh08Status RF455_DecodeMesh08(const void* bytes,std::size_t size,
    RF455Mesh08Part* records,std::size_t capacity,RF455Mesh08View* result) {
    if(!result || (!bytes && size))return RF_MESH08_ARGUMENT;
    if(size<8)return RF_MESH08_TRUNCATED;
    const auto* data=static_cast<const unsigned char*>(bytes);
    if(std::memcmp(data,magic,6))return RF_MESH08_MAGIC;
    Reader reader={data,size,6};std::uint16_t count=0;reader.word(count);
    if(count>capacity || (count && !records))return RF_MESH08_CAPACITY;
    if(count>(size-8)/(headerBytes+6))return RF_MESH08_TRUNCATED;
    for(unsigned n=0;n<count;++n) {
        RF455Mesh08Part record={};
        if(!reader.take(headerBytes,record.header) || !reader.word(record.vertexCount) ||
           !reader.take(vertexBytes*record.vertexCount,record.vertices) || !reader.word(record.indexCount))return RF_MESH08_TRUNCATED;
        if(record.indexCount>indexLimit)return RF_MESH08_INDEX_LIMIT;
        if(!reader.take(2u*record.indexCount,record.indices) || !reader.word(record.boneCount) ||
           !reader.take(boneBytes*record.boneCount,record.bones))return RF_MESH08_TRUNCATED;
        records[n]=record;
    }
    RF455Mesh08View value={records,data+reader.at,reader.at,size-reader.at,count};
    *result=value;return RF_MESH08_OK;
}

extern "C" RF455Mesh08Status RF455_EncodeMesh08(const RF455Mesh08View* view,void* bytes,
    std::size_t capacity,std::size_t* written) {
    if(!view || !written || (!view->parts && view->meshCount) || (!view->trailing && view->trailingBytes))return RF_MESH08_ARGUMENT;
    std::size_t size=8;
    for(unsigned n=0;n<view->meshCount;++n) {
        const RF455Mesh08Part& p=view->parts[n];
        if(!p.header || (!p.vertices && p.vertexCount) || (!p.indices && p.indexCount) || (!p.bones && p.boneCount))return RF_MESH08_ARGUMENT;
        if(p.indexCount>indexLimit)return RF_MESH08_INDEX_LIMIT;
        if(!addSize(size,1,headerBytes+6) || !addSize(size,p.vertexCount,vertexBytes) ||
           !addSize(size,p.indexCount,2) || !addSize(size,p.boneCount,boneBytes))return RF_MESH08_OVERFLOW;
    }
    if(!addSize(size,view->trailingBytes,1))return RF_MESH08_OVERFLOW;
    if(!bytes || size>capacity)return RF_MESH08_CAPACITY;
    auto* out=static_cast<unsigned char*>(bytes);putBytes(out,magic,6);putWord(out,view->meshCount);
    for(unsigned n=0;n<view->meshCount;++n) {
        const RF455Mesh08Part& p=view->parts[n];putBytes(out,p.header,headerBytes);putWord(out,p.vertexCount);
        putBytes(out,p.vertices,vertexBytes*p.vertexCount);putWord(out,p.indexCount);putBytes(out,p.indices,2u*p.indexCount);
        putWord(out,p.boneCount);putBytes(out,p.bones,boneBytes*p.boneCount);
    }
    putBytes(out,view->trailing,view->trailingBytes);*written=size;return RF_MESH08_OK;
}
