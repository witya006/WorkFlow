# 148: карта отрисовки экипировки455

Актуализация149: общие Render wrappers, источник overlay604 и очередь поз
перенесены и проверены; полный player и particle registry ещё открыты.
Текущее состояние: [client455-equipment-draw.md](client455-equipment-draw.md).
Ниже сохранена исходная карта148; её очередь не является текущим планом.

10.11.2026. AUDIT_OPEN. Реализация не перенесена,обычный внешний вид не принят.
Исследование:inventory/client455-equipment-render-reference.json.
Raw:artifacts/client455-progress/equipment-render148-reference/session.json.
27полных функций/1827инструкций/213положительных CFG и176bytes vtable
совпадают на двух закреплённых x86455;SHA/RVA сохранены в отчёте.
IDA eaa5fe38 сохранена/закрыта,idb_list0. Входные EXE не исполнялись.

## Подтверждённый вызов

Vtable AA8F64 (RVA6A8F64):
offset24→46E120 Render(),28→46E520 Animation(),32→46DBC0 FrameMove(),
148→46E160 Render(matrix),152→46E1E0 draw(matrix),
156→46E1A0 draw(default),172→46D8B0 grade.

46E120/46E160 сначала вызывают46E3A0 fade;mode3 возвращает1 без draw.
Обычная ветка:46E120→46C260→7CD2A0→46C370→46C3D0→SetMaterial931790
→virtual156→46E1A0→46C470→46C420.
Матричная ветка:46E160→46C2E0→тот же guard/material→virtual152
→46E1E0→46C940→46C420.
Guard требует mesh,IsEnable(2),IsDisable(4096).
Flag4 устанавливает mesh alpha перед draw и возвращает1 после.

ВАЖНО:46D190 — общая Animation-функция,НЕ CEquipObject::Render.
Старая заметка могла называть её render wrapper. Точная vtable выше авторитетна.
46C200 — metadata getter,также не Render.

46C470/46C940 используют разные общие пары scroll/time:
C0C078/C0C080 иC0C084/C0C08C. Float increment=(DWORD(now-before))*0.0005f;
scroll>1 сбрасывается0,не modulo. InitEffect и alpha read/write precede selection.
Metadata72→meshID,metadata0→table index. Kind27 идёт в kit EffectList,
unit kinds37..43 используют runtime byte152 иunit EffectList.
Остальные используют SetMeshEffect(meshID,virtualgrade,group5 дляmodelrace1/3).
Virtualgrade46D8B0 вызывает payload virtual68;прежде чем называть его смысл,
сверять реальный accessor/writers,не переносить названия старых классов.
46C920 читает equipment byte604:опциональный overlay.
Первая ветка делает дополнительный DrawCharacter2,матричная только setup/reset,
как в целевом теле;не объединять их на основании внешнего сходства.

## Следующие действия

1. Проверить полные overlay descriptors4×526bytes@113FC70 иtextures@11404A8,
   их producers/loaders и существующие engine APIs. Не подставлять no-op.
   7E89E0/7E8B60 pcode уже сохранён;они задают материал/текстуры/состояния,
   иrestore не является произвольным возвратом всех прежних D3D state.
2. Связать typed equipment с реальными SetMeshEffect/kit/unit/overlay/очередью эффектов.
   Существующие Character455/normal_effects содержат часть настоящих providers;
   их точную полноту проверить перед повторным переносом.
3. Подключить реальные Render/Animation/FrameMove к CPlayerProc/Avatar и
   существующему13slot controller/conditions/effects. Не выдавать recorders за backend.
4. Проверить одетого персонажа в обычном клиентском маршруте и затем selection.

Это продолжение147,не новый процент готовности. Полные source/renderer/appearance/
selection/world/gameplay иM9 остаются открыты.
