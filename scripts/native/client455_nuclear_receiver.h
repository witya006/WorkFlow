#pragma once
#ifndef RF455_NUCLEAR_RECEIVER_H
#define RF455_NUCLEAR_RECEIVER_H
#include "network/netmsgprocessor/cnetmsgprocessor_base.h"
class CBoardObject;

class CNetMsgProcessor_Nuclear final:public CNetMsgProcessor_Base {
    void Result455(BYTE);
public:
    bool AnalysisServerPacket(_MSG_HEADER*,char*)override;
};

// This is the observed CInventoryBoard nuclear-use branch, not a generic
// replacement for every typed inventory-item use/side effect.
void RF455_CompleteNuclearInventoryUse(CBoardObject*);
#endif
