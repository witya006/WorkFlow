#pragma once
#include "client455_item_payloads.h"
#include <array>
#include <cstddef>
#include <cstdint>
#include <string>

struct RF455ItemTimer {
    std::uint8_t type;
    std::uint32_t durationSeconds;
};

struct RF455StorePreview {
    std::string name;
    RF455ItemTimer timer{};
    bool timed = false;
    std::uint8_t currency = 0xff;
    std::uint64_t basePrice = 0;
    std::uint8_t sockets = 0;
    std::uint8_t installedTalics = 0;
    std::array<std::uint8_t, 7> talicIds{};
};

struct RF455PremiumOfferSlot {
    std::uint8_t kind = 0xff;
    std::uint8_t quantity = 0;
    std::uint32_t catalogCode = 0;
    std::uint32_t itemOrdinal = 0;
    bool resolved = false;
};

struct RF455PremiumOffer {
    std::array<std::array<RF455PremiumOfferSlot, 10>, 6> pages{};
};

struct RF455StoreIngot {
    RF455ItemDataSpan row;
    std::uint8_t quantity;
};

struct RF455StoreBuyDiscount {
    float effect1 = 0.0f;
    float effect11 = 0.0f;
};

RF455StoreBuyDiscount RF455_StoreBuyDiscount(const RF455StoreIngot* ingots, std::size_t count,
                                             bool allowRestricted);
bool RF455_StoreBuyUnitPrice(const RF455StorePreview&, float tax, RF455StoreBuyDiscount discount,
                             std::uint64_t& price);
bool RF455_CurrentShopUnitPrice(const RF455StorePreview&, std::uint64_t& price);

// Owned before the game objects in CMainApp,so they release before the manager
// and its borrowed data owners. Initial item table loading is wired to Login;
// mixed legacy item consumers and the rest of the data bootstrap remain open.
struct RF455ClientItems {
    RF455ItemDataStore data;
    RF455SkillForceData skillForce;
    RF455SourceItemManager manager;
    RF455RawItemTable cash,setEffect;
    bool cashInitialized=false,setEffectInitialized=false;
    bool cashLoadResult=false,setEffectLoadResult=false;
    bool loadCashFiles(std::int32_t selector);
    bool loadSetEffectFile();
    bool loadItemTimerFile();
    bool findItemTimer(std::uint8_t kind, std::uint32_t catalogCode, RF455ItemTimer& value) const;
    bool makeStorePreview(std::uint8_t kind, std::uint32_t itemIndex, RF455StorePreview& out,
                          std::uint32_t upgradeCode = 0xffffffffu, std::uint32_t priceMultiplier = 1) const;
    bool loadItemPremiumFile();
    RF455ItemDataSpan itemPremiumRow(std::uint32_t ordinal) const;
    bool makePremiumOffer(std::uint32_t ordinal, RF455PremiumOffer& out) const;
    bool loadItemFiles();
    bool loadQuestFile(std::int32_t selector = -1);
    void selectQuestTextForRace(std::int32_t selector, unsigned race);
    bool loadFiles(const char* item,const char* names,const char* quest,const char* character,
                   const char* sf,const char* sfNames);
    RF455ManagedItem* create(unsigned char selector,unsigned char type,unsigned index){
        return manager.createPayload(data,selector,type,index,&skillForce);
    }
private:
    bool loadQuestFiles(std::int32_t selector, bool wide);
    RF455RawItemTable itemTimers;
    bool itemTimersLoaded = false;
    RF455RawItemTable itemPremium;
    bool itemPremiumLoaded = false;
    std::string itemNamesPath;
    std::string cashDataPath;
    std::string cashNamesPath;
    std::string questDataPath;
    std::string questNamesPath;
    bool questWideMode = false;
};
RF455ClientItems& RF455_GameItems();
