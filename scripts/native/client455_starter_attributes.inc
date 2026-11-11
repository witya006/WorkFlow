void LoadAttribute(CGUISelectAttribute* window)
{
    for (BYTE race = 0; race < 3; ++race) {
        for (BYTE choice = 0; choice < 4; ++choice) {
            const auto row = _GetCharDataMgr()->GetClassData455(g_pClassType[4 * race + choice]);
            if (!row.data || row.size < 272) continue;

            // The creation screen shows the base class before earned proficiency
            // or advanced class bonuses. All pinned starter rows have zero PT.
            DWORD base[3];
            std::memcpy(base, row.data + 224, sizeof(base));
            constexpr float initialRank = 1.0f;
            const auto hp = 80 + static_cast<unsigned>(std::sqrt(10.0 * (base[0] + initialRank)));
            const auto sp = 160 + static_cast<unsigned>(2.5 * (base[2] + initialRank));
            window->SetBasicPoint(race, choice, 0, hp / 200.0f);
            // Base FP is shown until force mastery bonuses are wired to this preview.
            window->SetBasicPoint(race, choice, 1, (40.0f + 5.0f * base[1]) / 200.0f);
            window->SetBasicPoint(race, choice, 2, sp / 200.0f);
            for (BYTE part = 0; part < 6; ++part)
                window->SetBattleSkill(race, choice, part, initialRank / 20.0f);
            for (BYTE part = 0; part < 3; ++part)
                window->SetMakeSkill(race, choice, part, initialRank / 20.0f);
        }
    }
}
