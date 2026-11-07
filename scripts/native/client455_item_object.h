#pragma once
#include "cresobject.h"
#include "client455_client_items.h"

class CItemObject:public CResObject {
protected:
    RF455ManagedItem* m_pSharedItem455;
    DWORD m_dwItemField588455;
public:
    CItemObject();
    CItemObject(const CItemObject&);
    ~CItemObject();
    void Clear() override;
    virtual void SetItem455(RF455ManagedItem*);
    RF455ManagedItem* GetItem455()const{return m_pSharedItem455;}
    const void* GetItemData455()const;
    void RetainSharedItem455();
};
static_assert(sizeof(CItemObject)==592,"455 typed item resource owner");
