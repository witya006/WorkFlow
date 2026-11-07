#pragma once
#include <cstdint>
#include <map>
#include <vector>
class CGUIItem;
std::uint64_t RF455_IconLinkKey(CGUIItem&);

// Source-owned semantic-key registry,not the private targetUIManager ABI.
// Owners register copies and must unregister before changing identity/destroying.
class RF455IconLinks {
    std::map<std::uint64_t,std::vector<CGUIItem*>> buckets;
public:
    void registerIcon(CGUIItem&);
    bool unregisterIcon(CGUIItem&);
    const std::vector<CGUIItem*>* find(CGUIItem&)const;
    std::size_t bucketCount()const{return buckets.size();}
    std::size_t linkCount()const;
    void clear(){buckets.clear();}
};
RF455IconLinks& RF455_GameIconLinks();
