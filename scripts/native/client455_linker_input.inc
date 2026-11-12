void CInputProcessMgr::ProcessLinkerKeys455(DWORD now, BOOL focused)
{
    auto* board = _GetLinkBoard();
    if (!board) return;
    auto& window = board->LinkerWindow455();

    const bool slotModifiers = m_bShiftKeyDown || m_bControlKeyDown || m_bAltKeyDown;
    for (BYTE slot = 0; slot < 10; ++slot) {
        const auto& key = m_listKey[KM_LINKER_SLOT_FIRST + slot];
        if (key[1] >= 256 || !(gScan[key[1]] & 1)) continue;
        if (key[0] != ID_INVALID && key[0] != VK_CONTROL) continue;
        // The normal 455 slot loop treats Ctrl bindings as unmodified
        // outside chat and skips slot actions with any modifier held.
        if (focused || slotModifiers) {
            if (key[1] >= VK_F1 && key[1] <= VK_F12) gScan[key[1]] = 0;
            continue;
        }
        gScan[key[1]] = 0;
        if (now - m_linkerKeyTimes455[slot] <= 500) continue;
        m_linkerKeyTimes455[slot] = now;
        window.UseItem455(window.HotbarState455().active, slot);
        break;
    }

    if (!(gScan[VK_OEM_3] & 1)) return;
    gScan[VK_OEM_3] = 0;
    if (!focused && !m_bShiftKeyDown && !m_bAltKeyDown) window.CycleBank455(TRUE);
}
