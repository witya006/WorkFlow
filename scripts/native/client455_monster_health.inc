void CMonster::ReceiveHealth455(WORD tenThousandths)
{
    const float fraction = static_cast<float>(double(tenThousandths) / 10000.0);
    if (fraction >= m_displayedHealth455 || !m_pCombatState->GetTotalEnemyNum(ET_ATTACKER))
        m_displayedHealth455 = fraction;
    m_targetHealth455 = fraction;
}

void CMonster::ApplyFinalHealthImpact455()
{
    if (m_targetHealth455 >= 0.0f) m_displayedHealth455 = m_targetHealth455;
}

void CMonster::ApplyHealthImpact455(DWORD currentDamage, DWORD originalDamage, BYTE frames)
{
    if (m_targetHealth455 < 0.0f) return;
    if (frames <= 1) {
        ApplyFinalHealthImpact455();
        return;
    }
    const float portion = static_cast<float>(double(currentDamage) / originalDamage);
    const float change = (m_displayedHealth455 - m_targetHealth455) * portion;
    m_displayedHealth455 = m_displayedHealth455 > change ? m_displayedHealth455 - change : 0.0f;
}
