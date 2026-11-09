# Lighting consumers130 — геометрия и освещение объектов

2026-11-10. **PARTIAL M6**. В обычные клиентские методы CEntity подключены
модуляция цвета карты, fixed-function light и Grass/LitGrass. Восстановлены
36-byte vertices с нормалями и capability-gated pre/after bump materials.
Текущий gate: `inventory/client455-lighting-consumers-checkpoint.json`.
Команда: `scripts/Invoke-Python.ps1 scripts/checkpoint_client455_lighting_consumers.py`.
129 исторический; M6/M6F/M7/M9 OPEN. Полное освещение не принято.

## Статические доказательства

Primary455 SHA-256 `b1b5febf0d0394712e2322350e19dafe60742e8642697b93cfb89135bac1fd8b`;
secondary455 `46528aac20499e3b3928d58658d7e0cefe26feba7cd193796d5cfbf7a2bbc558`.
Оба x86/base0x400000. Подтверждены17 full functions/3450 instructions/18 byte
ranges, полные pcode/CFG и все positive block starts. Диапазоны и константы
совпали между обоими455. Дополнительные четыре transform context byte ranges
проверены отдельно; full assembly этих четырёх функций не заявляется.

| RVA | Роль |
|---|---|
| 0x4e3630 | CEntity fixed material:flag40 имеет приоритет над flag20 |
| 0x4e3f10 | Выбор Grass/LitGrass и передача modulated map color |
| 0x4e3a00 / 0x4e4000 | Настоящие fixed/shader методы рисования entity |
| 0x4e0a20 | R3E113→expanded36 vertices, normals и накопление между группами |
| 0x4c0560 | Face plane normal, float spills и нормализация |
| 0x4b52f0 | Light/material builder; ambient divisor412 |
| 0x4c7b10 / 0x4c80a0 | Main material pre/after pair и bump capability |
| 0x4c7a60 | Bump matrix: четыре чтения process time, множитель2 |
| 0x4d8760 / 0x4d8920 | Grass/LitGrass constants и actual shaders |
| 0x4da0c0 | Загрузка shader files; включён lower chunk RVA0x4d9f50 |
| 0x4faf70 | BSP entity map-color writer и вызовы обоих CEntity paths |
| 0x50b1c0 | R3M reader:46 serialized bytes→54 runtime layer stride |

Head query shader loader возвратил71 instruction и пропустил нижние blocks.
Повторный bounded query с VA0x8D9F50 дал125 instructions с полным CFG coverage;
сохранены обе записи, в full count включены только125 уникальных инструкций.
Три owned IDA сессии saved/closed/list0. Input EXE не запускались.

Raw/session/context сохранены в ignored artifacts/client455-progress/
lighting-consumers130-*.json, их SHA-256 закреплены в tracked reference report.

## Перенос и границы

Shared r3d3d8455.h генерируется из неизменённого legacy header: TEX1 теперь
36bytes, normal offset12, color24, UV28, FVF338. Все182 клиентских/20 kernel
модули пересобраны. CEntity size212 не меняется. Actual shader declaration
40bytes по VA0xBF7878 подтверждает этот layout и normal semantics.

Загрузчик добавляет единичную face normal каждому исходному vertex ID, затем
нормализует накопленный вектор при каждом expanded output. Нулевой вектор
получает Y=1. Накопитель сохраняется между material groups, включая уже
нормализованные предыдущей группой значения. Epsilon smoothing не добавлен.
Учитывается именно порядок455, а не привычный вариант smoothing алгоритма.

Flag20 получает RF455_ApplySkyTint; при disabled day возвращается исходный
ARGB. Flag40 создаёт настоящий D3D light/material и имеет приоритет, если
установлены оба флага. LitGrass загружается из настоящего LitGrass1.vso;
нормали передаются через правильную declaration. Shader cleanup обнуляет
VS/PS. Продуценты flag40 в обычном gameplay ещё не восстановлены полностью.

В обоих путях flag40 выбирает MODULATE, остальные — MODULATE2X. Удалена
оставшаяся legacy запись MODULATE2X, которая перетирала выбор fixed helper.
После fixed draw LIGHTING остаётся включённым, COLORVERTEX выключается,
SPECULARENABLE включается; DIFFUSEMATERIALSOURCE сохраняет выбранный источник.
Эти состояния проверяются на фактическом устройстве после каждого fixed draw.
Изменение яркости нового LitGrass кадра относительно промежуточного запуска
ожидаемо из-за исправления COLOROP; промежуточные кадры не служат эталоном455.

Material env-bump использует **layer1 flag**, не top-level m_dwFlag. Его
capability — D3DCAPS9.TextureOpCaps bit21. Pre отключает alpha test, выбирает
bump stages и textures; after восстанавливает stages и binds current sky tint.
Top-level flag40 и безусловный финальный COLORARG2=DIFFUSE восстановлены.
Bump matrix использует time×2 вместо старого time×3.

**Материалы не имеют одинакового ABI:** source records332/layers46/max4;
target runtime526/layers54. Подтверждённый R3M reader читает46 bytes из файла
в каждый54-byte runtime slot. Поэтому совпадение logical fields не требует
reinterpret cast source record к526bytes. Extra8 runtime fields и большая
ёмкость слоёв остаются открытыми. Первоначальный неверный static_assert на
526 был удалён и заменён проверкой собственного332-byte layout и mapping.

**Transform gap:** target8BFBC0 — affine inverse с0.001 guards;
8C0980 трансформирует вектор; normalize51D5D0 идёт через41DB70→41DB90.
Source пока использует D3DX inverse/legacy transform/x87 sqrt для выбранного
affine fixture. Точные guards, determinant arithmetic, underlying normalizer,
rotation/nonuniform scale/all FP modes требуют следующего переноса.

LitGrass читает19.xyz и21/22. Target передаёт по3 registers из stack buffers,
в том числе соседние неиспользуемые lanes. Source задаёт неиспользуемые lanes
детерминированно; полная проверка последующих consumers остаётся открытой.
Полные shader caps/failure/reset/OOM, CRT/FP/NaN/status flags ещё не приняты.

## Реальные проверки

Итоговый native run: `work/m9/84c65e3f/lighting-consumers-001`.

- Настоящая bd_grass01.r3e,113/5328 expanded vertices/одна группа. Captured
  resolved resource byte-equal закреплённому input. Все5328 normals побитно
  равны independent float32 oracle при наблюдаемом PC24/nearest; error0.
  Oracle берёт positions из GPU capture и topology из stock R3E: полного
  доказательства старого position decompressor/CRT этим не получено.
- Двусторонние faces почти взаимоуничтожаются; порядок float32 округлений
  меняет направление малого residual. Начальный double geometry oracle
  ошибочно давал другую нормаль. Контрольный расчёт исправлен по assembly;
  production не менялся ради согласования с приближённым oracle. Epsilon нет.
- Пять настоящих indexed CEntity paths: disabled/map tint/fixed-lit/Grass/LitGrass,
  в каждом видна модель; actual stream stride36. Захваченные в draw callbacks
  Grass1 и LitGrass1 побайтно равны исходным220/300-byte shader files.
- Восемь pre/after cases: capability0/1 × top-level flag0/40 × bump0/1.
  Это проверки actual D3D state, не доказательство bump GPU parity на двух
  разных физических картах. Три time cases подтверждают bump time×2.
- Пять новых кадров просмотрены. Свежие25 world/material/fade/lighting/weather
  кадров побайтно равны129 и используют доказанно тот же просмотренный контент:
  повторный visual review заменён проверкой raw+PNG SHA и recorded provenance.
  scripts/reuse_client455_visual_review.py отказывает при любом различии.
- Свежие lighting867 captured colors/3fog aggregates/27Mie/29BSP, weather90script
  cases/5fog aggregates,world76queue/16clock,fade90+27,material60/36 проходят.
  Старые bulk suites без нового риска не запускались.
- Own-entry/imports/ANI-BBX/sound1/window/device/existingCreate1/contracts
  проходят на точной новой PE. Известные handled first-chance exceptions
  сохранены. Полный bootstrap/game loop/455 acceptance не заявляются.

Engine67/21derived SHA-256
`6751765f42dc448ae54f8ee51cdb30a7ca07ba863cf87697cc6dd1149cd1653d`:
40 payload differences/19 timestamp-only/8 equal129.
RF_Online.bin x86/2255872bytes/base400000/entryRVA16C930:
`52c253106d9c6f8372f57c7976f026a7f807c5233f1945e23bcc771903ba61a2`.
Unresolved0; CharacterMR/FORCE не применяются. Exact129 engine/PE/MAP/rsp,
shared header и reports сохранены до изменений; ignored не является backup.

Следующий131: точные lit inverse/normalizer и flag40 producers, runtime material
fields/capacity и shader lifecycle; далее lensflare/localfog/INS/Planet/world,
stages/auth/protocol/Character/gameplay и полная client acceptance. Серверы и
оригиналы не изменены; Git local only. Текущий goal turn — progress.
