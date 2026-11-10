#pragma once
#include "client455_item_payloads.h"
#include <array>
#include <cstring>
#include <new>
#include <stdexcept>

//461CC0 ->404BC0 ->405CE0 ->405E70. A detached clone is not inserted into the
//item manager and copies the reference byte without retaining the source.
//Only written fields are copied;the target does not memcpy all200bytes.
class RF455DetachedNormalItem final:public RF455ManagedItem {
    std::array<unsigned char,200> state;
    RF455ItemDataSpan data,metadata;
    const char* title;
public:
    explicit RF455DetachedNormalItem(RF455BasicItem& source):data(source.rawData()),metadata(source.rawMetadata()),title(source.name()){
        const auto from=source.recordBytes();
        if(from.size!=200||source.header().kind!=0)throw std::logic_error("455 normal clone requires CNormalItem payload");
        new(state.data()) RF455ItemHeader;
        RF455_CopyItemHeader(header(),source.header(),source.header().dispatch);
        for(unsigned offset:{96u,104u,108u,188u})std::memcpy(state.data()+offset,from.data+offset,4);
        for(unsigned offset:{92u,112u,113u,192u})state[offset]=from.data[offset];
        std::memcpy(state.data()+116,from.data+116,28);
        std::memcpy(state.data()+144,from.data+144,41);
    }
    RF455ItemHeader& header()override{return *reinterpret_cast<RF455ItemHeader*>(state.data());}
    const char* name()const override{return title;}
    RF455ItemDataSpan rawData()const{return data;}
    RF455ItemDataSpan rawMetadata()const{return metadata;}
    RF455ItemDataSpan recordBytes()const{return {state.data(),state.size()};}
};
