void CAttackerInfo::SetForceDamage455(LONG damage)
{
    m_forceOriginalDamage455 = damage > 0 ? static_cast<DWORD>(damage) : 0;
    SetTotalDamagePoint(m_forceOriginalDamage455);
}

void CAttackerInfo::AdvanceForceDamage455()
{
    const DWORD remaining = GetTotalDamagePoint();
    const BYTE frames = GetEffectFrameNum();
    DWORD current = remaining;
    if (frames > 1) {
        const DWORD average = remaining / frames;
        const DWORD radius = static_cast<DWORD>(double(m_forceOriginalDamage455) * 0.1f) + 1;
        const bool add = (std::rand() % 2) != 0;
        const DWORD adjustment = std::rand() % radius;
        current = add ? average + adjustment : average - adjustment;
    }
    SetCurDamagePoint(current);
    SetTotalDamagePoint(remaining - current);
    DecreaseEffectFrameNum();
}
