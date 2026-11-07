#include "client455_magic_control.h"

void RF455MagicControl::Add455(BYTE flags,float angle,float target,float curve){
    if(first){
        if(static_cast<int>(target)>=1||first==last){
            last->flags=flags;last->angle=angle;last->curve=curve;last->end=1;
        }else{
            auto* node=new RF455MagicCurveNode{};node->flags=flags;node->angle=angle;node->curve=curve;
            node->begin=last->begin;node->end=target;node->previous=last->previous;node->next=last;
            last->previous->next=node;last->begin=node->end;last->previous=node;++count;
        }
    }else{
        auto* node=new RF455MagicCurveNode{};node->flags=flags;node->angle=angle;node->curve=curve;node->begin=0;node->end=target;
        first=last=node;++count;
        if(static_cast<int>(node->end)<1){
            auto* tail=new RF455MagicCurveNode{};tail->flags=flags;tail->angle=.1f;tail->curve=0;
            tail->begin=target;tail->end=1;tail->previous=node;node->next=tail;last=tail;++count;
        }
    }
}
