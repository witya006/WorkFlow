#pragma once
#include "client455_item_payloads.h"

// Owned before the game objects in CMainApp,so they release before the manager
// and its borrowed data owners. Automatic455 gameplay table-loading is open.
struct RF455ClientItems {
    RF455ItemDataStore data;
    RF455SkillForceData skillForce;
    RF455SourceItemManager manager;
    bool loadFiles(const char* item,const char* names,const char* quest,const char* character,
                   const char* sf,const char* sfNames);
    RF455ManagedItem* create(unsigned char selector,unsigned char type,unsigned index){
        return manager.createPayload(data,selector,type,index,&skillForce);
    }
};
RF455ClientItems& RF455_GameItems();
