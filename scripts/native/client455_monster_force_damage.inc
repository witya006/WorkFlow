void CAttackerInfo::SetDamage455(LONG damage)
{
    m_specialHit455 = damage == -2;
    m_originalDamage455 = damage > 0 ? static_cast<DWORD>(damage) : 0;
    SetTotalDamagePoint(m_originalDamage455);
}

void CAttackerInfo::AdvanceDamage455()
{
    const DWORD remaining = GetTotalDamagePoint();
    const BYTE frames = GetEffectFrameNum();
    DWORD current = remaining;
    if (frames > 1) {
        const DWORD average = remaining / frames;
        const DWORD radius = static_cast<DWORD>(double(m_originalDamage455) * 0.1f) + 1;
        const bool add = (std::rand() % 2) != 0;
        const DWORD adjustment = std::rand() % radius;
        current = add ? average + adjustment : average - adjustment;
    }
    SetCurDamagePoint(current);
    SetTotalDamagePoint(remaining - current);
    if (frames <= 1) m_originalDamage455 = 0;
    DecreaseEffectFrameNum();
}

void CCombatState::AdvanceImpact455(CAttackerInfo& attack)
{
    const BYTE frames = attack.GetEffectFrameNum();
    const DWORD original = attack.GetOriginalDamage455();
    attack.AdvanceDamage455();
    if (m_pOwner->IsEqualCharType(CTI_MONSTER))
        static_cast<CMonster*>(m_pOwner)->ApplyHealthImpact455(attack.GetCurDamagePoint(), original, frames);
}
