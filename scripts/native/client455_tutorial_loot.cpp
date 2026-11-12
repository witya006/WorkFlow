#include "gameobject/manager/ccharactermgr.h"
#include "gameobject/board/common/cboardmanager.h"
#include "cland.h"
#include "ccamera.h"
#include "datafile.h"
#include "datatable/cresourcedatamgr.h"
#include "input/imeedit.h"
#include "gameprogress/cgameprogress.h"
#include "userinterface/spritemgr.h"
#include "mainapp.h"
#include "client455_client_items.h"
#include "client455_protocol_observation.h"
#include "client455_tutorial_inventory.h"
#include "client455_tutorial_loot.h"
#include <algorithm>
#include <cstring>
#include <limits>

namespace {
constexpr float pickupRange = 100.0f;

float distanceSquared(const float* lhs, const float* rhs)
{
    const float x = lhs[0] - rhs[0], y = lhs[1] - rhs[1], z = lhs[2] - rhs[2];
    return x * x + y * y + z * z;
}
}

struct RF455TutorialLoot::Drop {
    CGroundItem object;
    std::uint8_t table = 0;
    std::uint32_t index = 0;
};

RF455TutorialLoot::RF455TutorialLoot() = default;
RF455TutorialLoot::~RF455TutorialLoot() = default;

bool RF455TutorialLoot::spawn(std::uint8_t table, std::uint32_t code, const RF455TutorialVector& position)
{
    auto& items = RF455_GameItems().data;
    std::uint32_t index;
    if (!items.findItemByCode(table, code, index)) return false;
    const auto row = items.getItem(table, index);
    if (row.size < 76) return false;
    DWORD mesh;
    std::memcpy(&mesh, row.data + 72, sizeof(mesh));

    auto drop = std::make_unique<Drop>();
    drop->table = table;
    drop->index = index;
    auto& object = drop->object;
    object.SetName(const_cast<char*>(reinterpret_cast<const char*>(row.data + 8)));
    object.SetBone(mesh);
    object.SetMesh(mesh);
    if (!object.GetMesh() || !object.GetMesh()->m_Load) return false;
    Vector3f placed{};
    for (unsigned i = 0; i < position.size(); ++i)
        placed[i] = static_cast<std::int16_t>(RF455_TutorialCoordinateWord(position[i]));
    object.SetPosition(placed, TRUE, FALSE);
    object.CheckYPos();
    object.SetCreateTime(timeGetTime());
    object.SetQuantity(1);
    object.SetReceiveFixPositionMsg(TRUE);
    object.SetLightColor(D3DCOLOR_XRGB(128, 128, 128));
    object.SetLightColorFromMap();
    object.Disable(ROSF_OUT_OF_VISUAL_FIELD_SERVER | ROSF_OUT_OF_VISUAL_FIELD_CLIENT);
    object.Animation();
    const auto serial = RF455_GetTutorialCreationIds().item++;
    object.SetIndex(serial);
    drops.push_back(std::move(drop));
    RF455_ObserveProtocol("tutorial-loot-spawn", code, index, serial);
    return true;
}

void RF455TutorialLoot::pointAt(long x, long y, const RF455TutorialVector& camera)
{
    clearHover();
    float nearest = (std::numeric_limits<float>::max)();
    for (const auto& drop : drops) {
        Vector3f hit{};
        if (!drop->object.CollisionCheckWithBoundBox(x, y, hit)) continue;
        const float distance = distanceSquared(hit, camera.data());
        if (distance < nearest) {
            hovered = drop.get();
            nearest = distance;
        }
    }
}

bool RF455TutorialLoot::pickHovered(RF455TutorialInventory& inventory)
{
    return collect(hovered, inventory);
}

bool RF455TutorialLoot::pickNearest(RF455TutorialInventory& inventory)
{
    Drop* selected = nullptr;
    float nearest = pickupRange * pickupRange;
    for (const auto& drop : drops) {
        const float distance = distanceSquared(_GetAvatar()->GetPosition(), drop->object.GetPosition());
        if (distance < nearest) {
            selected = drop.get();
            nearest = distance;
        }
    }
    return collect(selected, inventory);
}

bool RF455TutorialLoot::collect(Drop* drop, RF455TutorialInventory& inventory)
{
    if (!drop || distanceSquared(_GetAvatar()->GetPosition(), drop->object.GetPosition()) >= pickupRange * pickupRange)
        return false;
    const auto serial = static_cast<WORD>(drop->object.GetIndex());
    if (!inventory.collect(drop->table, drop->index, serial, drop->object.GetQuantity())) {
        RF455_ObserveProtocol("tutorial-loot-bag-rejected", serial, drop->index, 0);
        return false;
    }
    if (hovered == drop) clearHover();
    const auto found = std::find_if(drops.begin(), drops.end(), [drop](const auto& candidate) {
        return candidate.get() == drop;
    });
    drops.erase(found);
    return true;
}

void RF455TutorialLoot::render()
{
    for (const auto& drop : drops) {
        auto& object = drop->object;
        if (object.ProcessClipping()) continue;
        object.Render();
        if (drop.get() == hovered) {
            object.Enable(ROSF_RENDER_NAME);
            object.RenderName();
        }
    }
}

void RF455TutorialLoot::clear()
{
    clearHover();
    drops.clear();
}
