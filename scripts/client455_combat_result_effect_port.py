"""Connect monster block and miss to the ordinary 455 text and sound consumers."""

from client455_trade_ore_port import replace


def port_combat_result_effect(raw, relative):
    if relative == 'addcodebyjang/foreffect.h':
        anchor = b'void FrameMoveEffect();'
        return replace(raw, anchor, b'void DispatchQueuedEffects();\n' + anchor), True
    if relative == 'addcodebyjang/foreffect.cpp':
        anchor = b'#include "../Global.h"'
        raw = replace(raw, anchor, anchor + b'\n#include "ForEffect.h"\n#include "client455_equipment_effects.h"')
        raw = replace(raw, b'\tvoid MonsterMiss();',
                      b'\tvoid MonsterMiss();\n\tvoid MonsterBlock();\n\tbool CanShowMonsterResult();')
        anchor = b'void CAllEffectInfo::MonsterMiss()'
        raw = replace(raw, anchor, b'''bool CAllEffectInfo::CanShowMonsterResult()
{
    if (!mSrc->IsEnable(ROSF_CLIPPED | ROSF_OUT_OF_VISUAL_FIELD_CLIENT)) return true;
    auto* avatar = _GetAvatar();
    if (mSrc == avatar) return true;
    return avatar && mTar == avatar && avatar->IsLastAttackTarget455(mSrc);
}

void CAllEffectInfo::MonsterBlock()
{
    RF455_PlayActorEffectSound(277093 + rand() % 2, mSrcPos, 0);
    Vector3f position = {mSrcPos[0], mSrcPos[1] + 5.0f, mSrcPos[2]};
    EFUtil_StartStringMoveOut(position, "BLOCK", 1, 0xffffffff);
}

''' + anchor)
        anchor = b'\tFrameMoveAllEffectsList();'
        end = raw.index(b'\n', raw.index(anchor))
        raw = raw[:end] + b'\n\tDispatchQueuedEffects();\n}\n\nvoid DispatchQueuedEffects()\n{' + raw[end:]
        anchor = b'\t\t\tif( code1 == MET_DAMAGE_MISS )\n\t\t\t\tMonsterMiss();'
        raw = replace(raw, anchor, b'''            if (code1 == MET_DAMAGE_MISS) {
                if (CanShowMonsterResult()) MonsterMiss();
            } else if (code1 == MET_DAMAGE_BLOCK455) {
                if (CanShowMonsterResult()) MonsterBlock();
            }''')
        return raw, True
    if relative == 'character/character/ccharacter_relationinfo2.h':
        anchor = b'constexpr DWORD CAI_DAMAGED_SPECIAL_HIT455 = 0x60000006;'
        return replace(raw, anchor, anchor + b'\nconstexpr DWORD MET_DAMAGE_BLOCK455 = 13;'), True
    if relative == 'character/npc/cmonster.cpp':
        return replace(raw, b'case CAI_DAMAGED_SPECIAL_HIT455: return 13;',
                       b'case CAI_DAMAGED_SPECIAL_HIT455: return MET_DAMAGE_BLOCK455;'), True
    if relative == 'character/avatar/cavatar.h':
        anchor = b'\tBYTE m_townState455 = 0xff;'
        raw = replace(raw, anchor, anchor + b'\n\tCCharacter* m_lastAttackTarget455 = nullptr;')
        anchor = b'    BYTE GetTownState455() const { return m_townState455; }'
        return replace(raw, anchor, anchor + b'\n    bool IsLastAttackTarget455(const CCharacter* target) const\n'
                       b'    { return m_lastAttackTarget455 == target; }'), True
    if relative == 'character/avatar/cavatar_combat.cpp':
        start = raw.index(b'CAvatar::Attack( BYTE')
        end = raw.index(b'\n}', start)
        body = replace(raw[start:end], b'\treturn hResult;',
                       b'\tif (hResult != ARC_FAIL_MOVE_TO_TARGET) m_lastAttackTarget455 = pi_pTarget;\n'
                       b'\treturn hResult;')
        return raw[:start] + body + raw[end:], True
    if relative == 'addcodebyjang/effectutilfont.cpp':
        raw = b'#include <cmath>\n' + raw
        start = raw.index(b'\t\tif( !strcmp("FAILURE",ch) )')
        end = raw.index(b'\t\tif(stVbufCnt >', start)
        raw = raw[:start] + b'''        if (!strcmp("FAILURE", ch) || !strcmp("BLOCK", ch))
        {
            const bool block = !strcmp("BLOCK", ch);
            const float width = block ? 90.0f : 98.0f;
            const float leftU = block ? 100.0f / 512.0f : 0.0f;
            const float rightU = leftU + width / 512.0f;
            const float right = pos[0] + width * scale;
            const float bottom = pos[1] + _FONT_YLENG * scale;
            const float topV = f_ydiff * 3;
            const float bottomV = topV + f_ydiff;
            SetVBuf(stVbufCnt, pos[0], pos[1], pos[2], pos[3], leftU, topV, color);
            ++stVbufCnt;
            SetVBuf(stVbufCnt, right, pos[1], pos[2], pos[3], rightU, topV, color);
            ++stVbufCnt;
            SetVBuf(stVbufCnt, pos[0], bottom, pos[2], pos[3], leftU, bottomV, color);
            ++stVbufCnt;
            SetVBuf(stVbufCnt, pos[0], bottom, pos[2], pos[3], leftU, bottomV, color);
            ++stVbufCnt;
            SetVBuf(stVbufCnt, right, pos[1], pos[2], pos[3], rightU, topV, color);
            ++stVbufCnt;
            SetVBuf(stVbufCnt, right, bottom, pos[2], pos[3], rightU, bottomV, color);
            ++stVbufCnt;
        }
''' + raw[end:]
        anchor = b'\t\tVector3fCopy(stStringOut[i].mPos,temp);'
        raw = replace(raw, anchor, b'''        const char* text = stStringOut[i].mStr;
        const bool resultWord = !strcmp("BLOCK", text) || !strcmp("MISS", text) || !strcmp("FAILURE", text);
        constexpr double resultLifetime = 0.9;
        constexpr double resultFadeStart = 0.45;
''' + anchor)
        raw = replace(raw, b'if( stStringOut[i].mTime > 0.7)',
                      b'if (stStringOut[i].mTime > (resultWord ? resultLifetime : 0.7))')
        start = raw.index(b'\t\talpha = (DWORD)(min( 1 - stStringOut[i].mTime')
        end = raw.index(b'\n\n\t}', start)
        raw = raw[:start] + b'''        const double elapsed = stStringOut[i].mTime;
        const float scale = resultWord && elapsed < resultFadeStart
            ? static_cast<float>(1.0 + std::sin(elapsed / resultFadeStart * 3.141592025756836) * 0.8f)
            : 1.0f;
        if (resultWord) {
            alpha = static_cast<DWORD>(min(1.0, (resultLifetime - elapsed) / resultFadeStart) * 255.0);
            pos[0] = static_cast<float>(static_cast<LONG>(pos[0] + 0.5f)) - strlen(text) * 10.0f * scale;
            pos[1] = static_cast<float>(static_cast<LONG>(pos[1])) - _FONT_YLENG * 0.5f * scale;
        } else {
            alpha = (DWORD)(min(1 - stStringOut[i].mTime, 1) * 255);
            pos[0] = (float)((LONG)(pos[0] + .5f)) - ((strlen(text) / 2) * _FONT_XLENG);
            pos[1] = (float)((LONG)(pos[1])) - _FONT_YLENG / 2;
        }
        color = (alpha << 24) | (stStringOut[i].mColor & 0x00ffffff);
        PushEffectFont(pos, stStringOut[i].mStr, scale, stStringOut[i].mStyle, v_buf, color);''' + raw[end:]
        return raw, True
    return raw, False
