#include "client455_sprites.h"
#include "client455_nation_paths.h"
#include <io.h>
#include <cstdio>
#include <cstring>
namespace {
// 455 x86 VA BDB6A0 / RVA7DB6A0:55 fixed128byte filename entries.
const char*const names[]={
    "mouse.spr","common.spr","loading.spr","login.spr","main.spr",
    "system.spr","inventory.spr","maploading.spr","item.spr","shop.spr",
    "oreproc.spr","mining.spr","exchange.spr","summon.spr","itemmake.spr",
    "itemupgrade.spr","trade.spr","dungeon.spr","unit.spr","unitparts.spr",
    "class.spr","tutorial.spr","pvp.spr","guild.spr","emblem.spr","trunk.spr",
    "cribattle.spr","itemcombine.spr","patriarch.spr","unmannedminer.spr",
    "CashShop.spr","npc/bel.spr","npc/cor.spr","npc/acc.spr","Library.spr",
    "journal.spr","magicenchant.spr","TalikEnchant.spr","TabIndexIcon.spr",
    "supplybox.spr","Revive.spr","renewal.spr","macro.spr","post.spr",
    "SocketState.spr","skillwindow.spr","forcewindow.spr","charinfo.spr",
    "WarTimer.spr","EtcUI.spr","Rader.spr","Common2.spr","ItemLock.spr",
    "server_rate.spr","ItemCollection.spr"
};
static_assert(sizeof(names)/sizeof(*names)==55,"455sprite table");
}
const char*RF455_SpriteFilename(unsigned id){return id<55?names[id]:nullptr;}
bool RF455_SelectSpritePath(unsigned id,char*output,std::size_t capacity){
    if(id>=55||!output||capacity<260)return false;
    // 7B0110:localized existence check precedes loading;Common is returned
    // even when neither input exists. Loading success is a separate contract.
    std::sprintf(output,"./SpriteImage/%s/%s",RF455_GetNormalNationPaths()->folder,names[id]);
    if(_access(output,0)==-1)std::sprintf(output,"./SpriteImage/Common/%s",names[id]);
    return true;
}
