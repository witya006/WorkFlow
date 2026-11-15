#include "client455_edf_input.h"
#include <cmath>
#include <limits>
#include <set>

namespace {
bool itemTableFile455(const char* name, RF455RawItemTable& output, std::uint32_t minimumStride = 0,
                      std::uint32_t exactStride = 0){
    return RF455_ReadEdfInput(name, [&](const unsigned char* raw, std::size_t size) {
        std::vector<unsigned char> plain;
        if (!RF455_DecodeEdf(raw, size, plain) || plain.size() < 8) return false;
        RF455RawItemTable next;
        std::memcpy(&next.count, plain.data(), 4);
        std::memcpy(&next.stride, plain.data() + 4, 4);
        if (exactStride && (next.stride != exactStride || (plain.size() - 8) % exactStride ||
                            next.count != (plain.size() - 8) / exactStride)) return false;
        if (next.count && next.stride < minimumStride) return false;
        if (next.count && next.stride) {
            if (next.count > (plain.size() - 8) / next.stride) return false;
            const auto bytes = std::size_t(next.count) * next.stride;
            next.bytes.assign(plain.data() + 8, plain.data() + 8 + bytes);
        }
        output = std::move(next);
        return true;
    });
}

constexpr std::size_t ingotEffectStart455 = 156;
constexpr std::size_t ingotEffectStride455 = 12;
constexpr unsigned ingotEffectSlots455 = 10;

template<class T>
T storeField455(RF455ItemDataSpan row, std::size_t offset)
{
    T value;
    std::memcpy(&value, row.data + offset, sizeof(value));
    return value;
}

bool storeIngotRow455(RF455ItemDataSpan row)
{
    return row.data && row.size >= 288 && row.data[88] == 17;
}

struct StoreIngotEffect455 {
    std::uint32_t id;
    float perUnit;
    float maximum;
};

bool storeIngotEffect455(RF455ItemDataSpan row, unsigned ordinal, StoreIngotEffect455& out)
{
    if (ordinal >= ingotEffectSlots455) return false;
    const auto offset = ingotEffectStart455 + ordinal * ingotEffectStride455;
    out = {storeField455<std::uint32_t>(row, offset), storeField455<float>(row, offset + 4),
           storeField455<float>(row, offset + 8)};
    return std::isfinite(out.perUnit) && std::isfinite(out.maximum);
}

float storeIngotGroup455(const RF455StoreIngot* ingots, std::size_t count, std::uint32_t group,
                        unsigned ordinal)
{
    float total = 0.0f, maximum = 0.0f;
    struct Stack {
        std::uint32_t code;
        std::uint64_t quantity;
        StoreIngotEffect455 effect;
    };
    std::vector<Stack> stacks;
    for (std::size_t i = 0; i < count; ++i) {
        const auto& ingot = ingots[i];
        if (!storeIngotRow455(ingot.row) || storeField455<std::uint32_t>(ingot.row, 284) != group)
            continue;
        StoreIngotEffect455 effect;
        if (!storeIngotEffect455(ingot.row, ordinal, effect)) continue;
        if (maximum < effect.maximum) maximum = effect.maximum;
        const auto code = storeField455<std::uint32_t>(ingot.row, 4);
        bool found = false;
        for (auto& stack : stacks) {
            if (stack.code != code) continue;
            stack.quantity += ingot.quantity;
            found = true;
            break;
        }
        if (!found) stacks.push_back({code, ingot.quantity, effect});
    }
    for (const auto& stack : stacks) {
        const auto& effect = stack.effect;
        if (effect.id == 255) continue;
        // RVA 0x077998 spills the product to float before comparing the cap.
        const float contribution = static_cast<float>(double(stack.quantity) * effect.perUnit);
        total += contribution < effect.maximum ? contribution : effect.maximum;
    }
    return total < maximum ? total : maximum;
}

bool storeBasisPoints455(double value, std::int32_t& out)
{
    value = std::trunc(value * 10000.0);
    if (!std::isfinite(value) || value < (std::numeric_limits<std::int32_t>::min)() ||
        value > (std::numeric_limits<std::int32_t>::max)()) return false;
    out = static_cast<std::int32_t>(value);
    return true;
}
}

RF455StoreBuyDiscount RF455_StoreBuyDiscount(const RF455StoreIngot* ingots, std::size_t count,
                                             bool allowRestricted)
{
    RF455StoreBuyDiscount result;
    if (!ingots) return result;
    const std::uint32_t effectIds[] = {1, 11};
    std::set<std::uint32_t> groups[2];
    float* totals[] = {&result.effect1, &result.effect11};
    // The first applicable item fixes the ordinal for each effect and group.
    // Repeated matching ordinals on that item still contribute independently.
    for (std::size_t i = 0; i < count; ++i) {
        const auto row = ingots[i].row;
        if (!storeIngotRow455(row) || (!allowRestricted && storeField455<std::uint32_t>(row, 280) == 1))
            continue;
        const auto effects = row.data[152];
        if (effects > ingotEffectSlots455) continue;
        const auto group = storeField455<std::uint32_t>(row, 284);
        for (unsigned lane = 0; lane < 2; ++lane) {
            if (groups[lane].count(group)) continue;
            for (unsigned ordinal = 0; ordinal < effects; ++ordinal) {
                StoreIngotEffect455 effect;
                if (storeIngotEffect455(row, ordinal, effect) && effect.id == effectIds[lane]) {
                    *totals[lane] += storeIngotGroup455(ingots, count, group, ordinal);
                    groups[lane].insert(group);
                }
            }
        }
    }
    return result;
}

bool RF455_StoreBuyUnitPrice(const RF455StorePreview& preview, float tax, RF455StoreBuyDiscount discount,
                             std::uint64_t& price)
{
    constexpr std::uint64_t basis = 10000;
    const auto currency = preview.currency;
    if (currency > 6) return false;
    auto payable = preview.basePrice;
    if (currency == 0) {
        std::int32_t factor;
        if (!storeBasisPoints455(1.0 - double(discount.effect1) - double(discount.effect11), factor) ||
            factor < 0) return false;
        payable = payable * static_cast<std::uint32_t>(factor) / basis;
    }
    if (currency <= 3 || currency == 6) {
        std::int32_t points;
        if (!storeBasisPoints455(double(tax), points)) return false;
        const auto factor = 10000ll + points;
        if (factor < 0 || factor > (std::numeric_limits<std::int32_t>::max)()) return false;
        if (currency == 6) {
            const auto product = static_cast<std::uint32_t>(payable) * static_cast<std::uint32_t>(factor);
            payable = product / basis;
        } else {
            payable = payable * static_cast<std::uint32_t>(factor) / basis;
            if (currency == 2 || currency == 3) payable = static_cast<std::uint32_t>(payable);
        }
    }
    price = payable;
    return true;
}

bool RF455ClientItems::loadCashFiles(std::int32_t selector){
    const auto* nation=RF455_GetNormalNationPaths();if(!nation->configured)return false;
    auto paths=RF455_ItemCashPaths(nation->folder,selector);
    const bool sameBase=cashInitialized&&cashDataPath==paths.data;
    if(sameBase&&cashNamesPath==paths.names)return true;
    if(!sameBase||!cashNamesPath.empty()){
        // Reset localized fields when changing the language. A failed base
        // read leaves the previous table intact.
        RF455RawItemTable next;
        if(!itemTableFile455(paths.data.c_str(),next))return false;
        cash=std::move(next);
        cashDataPath.swap(paths.data);
        cashNamesPath.clear();
        cashInitialized=true;
    }
    // The target keeps its base table even when the localized count mismatches.
    if (!RF455_ReadEdfInput(paths.names.c_str(), [&](const unsigned char* raw, std::size_t size) {
        std::vector<unsigned char> plain;
        if (!RF455_DecodeEdf(raw, size, plain) || plain.size() < 8) return false;
        std::uint32_t count;
        std::memcpy(&count, plain.data(), 4);
        if (count != cash.count || count > (plain.size() - 8) / 4 || (count && cash.stride < 20))
            return false;
        for (std::uint32_t i = 0; i < count; ++i)
            std::memcpy(cash.bytes.data() + std::size_t(i) * cash.stride + 16, plain.data() + 8 + 4 * i, 4);
        return true;
    })) return false;
    cashNamesPath.swap(paths.names);
    return true;
}
bool RF455ClientItems::loadSetEffectFile(){
    if(setEffectInitialized)return true;
    if(!itemTableFile455(".\\DataTable\\ItemSetEffect.edf",setEffect))return false;
    setEffectInitialized=true;return true;
}

bool RF455ClientItems::loadItemTimerFile()
{
    // Client 455 x86 RVA 0x209C60 loads this table from the common DataTable root.
    if (!itemTimersLoaded) {
        itemTimersLoaded = itemTableFile455(".\\DataTable\\ItemTimer.edf", itemTimers, 24);
    }
    return itemTimersLoaded;
}

bool RF455ClientItems::findItemTimer(std::uint8_t kind, std::uint32_t catalogCode, RF455ItemTimer& value) const
{
    // RVA 0x209DF0 uses the first matching kind and code in file order.
    for (std::uint32_t index = 0; index < itemTimers.count; ++index) {
        const auto row = itemTimers.get(index);
        if (row.data[8] != kind) continue;
        std::uint32_t code;
        std::memcpy(&code, row.data + 12, sizeof(code));
        if (code != catalogCode) continue;
        value.type = row.data[16];
        std::memcpy(&value.durationSeconds, row.data + 20, sizeof(value.durationSeconds));
        return true;
    }
    return false;
}

bool RF455ClientItems::makeStorePreview(std::uint8_t kind, std::uint32_t itemIndex,
                                        RF455StorePreview& out, std::uint32_t upgradeCode,
                                        std::uint32_t priceMultiplier) const
{
    const auto row = data.getItem(kind, itemIndex);
    if (!row.data || row.size < 90) return false;
    constexpr std::size_t nameWidth = 64;
    const auto* name = row.data + 8;
    const auto* end = static_cast<const unsigned char*>(std::memchr(name, 0, nameWidth));
    RF455StorePreview preview;
    preview.name.assign(reinterpret_cast<const char*>(name),
                        end ? static_cast<std::size_t>(end - name) : nameWidth);
    // Shop RVA 0x0B83D0 queries the timer by the item's stored kind and code.
    std::uint32_t code;
    std::memcpy(&code, row.data + 4, sizeof(code));
    const auto itemKind = row.data[88];
    preview.timed = findItemTimer(itemKind, code, preview.timer);
    // RVA 0x136C30 dispatches the purchase cost by currency. This is its unit
    // cost before the avatar's discount and tax adjustments.
    constexpr std::size_t priceOffsets[] = {92, 92, 96, 96, 104, 108, 100};
    const auto currency = row.data[89];
    if (currency < sizeof(priceOffsets) / sizeof(priceOffsets[0])) {
        const auto offset = priceOffsets[currency];
        std::uint32_t rawPrice;
        if (row.size >= offset + sizeof(rawPrice)) {
            std::memcpy(&rawPrice, row.data + offset, sizeof(rawPrice));
            preview.currency = currency;
            preview.basePrice = std::uint64_t(rawPrice) * (currency <= 1 ? priceMultiplier : 1u);
        }
    }
    const auto talics = RF455_DecodeTalics455(data, row, upgradeCode);
    preview.sockets = talics.sockets;
    preview.installedTalics = talics.count;
    preview.talicIds = talics.ids;
    out = std::move(preview);
    return true;
}

bool RF455ClientItems::loadItemPremiumFile()
{
    // Client 455 x86 RVA 0x204530 reads the common ItemPremium table.
    if (!itemPremiumLoaded) {
        itemPremiumLoaded = itemTableFile455(".\\DataTable\\ItemPremium.edf", itemPremium, 0, 328);
    }
    return itemPremiumLoaded;
}

RF455ItemDataSpan RF455ClientItems::itemPremiumRow(std::uint32_t ordinal) const
{
    // RVA 0x204660 indexes the table directly by row ordinal.
    return itemPremium.get(ordinal);
}

bool RF455ClientItems::makePremiumOffer(std::uint32_t ordinal, RF455PremiumOffer& out) const
{
    const auto row = itemPremiumRow(ordinal);
    if (!row.data || row.size != 328) return false;
    RF455PremiumOffer offer;
    // RVA 0x0924F0 uses one quantity per page for pages 0..4 and a
    // quantity per slot for page 5. Keep the slot positions even on misses.
    for (std::size_t page = 0; page < offer.pages.size(); ++page) {
        const bool last = page == 5;
        for (std::size_t index = 0; index < offer.pages[page].size(); ++index) {
            auto& slot = offer.pages[page][index];
            slot.kind = row.data[(last ? 265 : 8 + 10 * page) + index];
            slot.quantity = row.data[last ? 316 + index : 260 + page];
            const auto codeOffset = (last ? 276 : 60 + 40 * page) + 4 * index;
            std::memcpy(&slot.catalogCode, row.data + codeOffset, sizeof(slot.catalogCode));
            slot.resolved = data.findItemRowByCode(slot.kind, slot.catalogCode, slot.itemOrdinal);
        }
    }
    out = offer;
    return true;
}

bool RF455ClientItems::loadItemFiles(){
    const auto* nation=RF455_GetNormalNationPaths();if(!nation->configured)return false;
    std::string names=std::string(nation->dataRoot)+"\\NDItem.edf";
    if(data.hasItemLocalization())return itemNamesPath==names;
    // All11 pinned country vslot160 implementations return1, including Korea.
    if (!data.hasItemData() && !RF455_ReadEdfInput(".\\DataTable\\Item.edf",
        [&](const unsigned char* raw, std::size_t size) { return data.loadItemEdf(raw, size, true); }))
        return false;
    if (!RF455_ReadEdfInput(names.c_str(), [&](const unsigned char* raw, std::size_t size) {
        return data.localizeItemEdf(raw, size);
    })) return false;
    itemNamesPath.swap(names);
    return true;
}

bool RF455ClientItems::loadQuestFile(std::int32_t selector)
{
    questWideMode = false;
    return loadQuestFiles(selector, false);
}

void RF455ClientItems::selectQuestTextForRace(std::int32_t selector, unsigned race)
{
    // Brazil's country vtable entry calls the Quest selector at RVA 0x206450.
    const auto* nation = RF455_GetNormalNationPaths();
    if (!nation->configured || nation->nation != RF455_MapNation("Brazil") || race > 4) return;
    const bool wide = (race & 1u) != 0;
    if (questWideMode == wide) return;
    questWideMode = wide;
    loadQuestFiles(selector, wide);
}

bool RF455ClientItems::loadQuestFiles(std::int32_t selector, bool wide)
{
    // 455 x86 RVA 0x205D90 selects the global table before applying NDQuest.
    const auto* nation = RF455_GetNormalNationPaths();
    std::string base = "./DataTable/Quest";
    if (selector != -1) base += "_" + std::to_string(selector);
    base += ".edf";
    std::string local = nation->configured
        ? std::string(nation->dataRoot) + (wide ? "/NDQuestW.edf" : "/NDQuest.edf") : "";

    const bool sameBase = data.hasQuestData() && questDataPath == base;
    if (!sameBase || (!questNamesPath.empty() && questNamesPath != local)) {
        if (!RF455_ReadEdfInput(base.c_str(), [&](const unsigned char* raw, std::size_t size) {
            return data.loadQuestEdf(raw, size);
        })) {
            data.clearQuestData();
            questDataPath.clear();
            questNamesPath.clear();
            return false;
        }
        questDataPath.swap(base);
        questNamesPath.clear();
    }
    if (!local.empty() && questNamesPath != local &&
        RF455_ReadEdfInput(local.c_str(), [&](const unsigned char* raw, std::size_t size) {
            return data.localizeQuestEdf(raw, size);
        })) {
        questNamesPath.swap(local);
    }
    return true;
}
