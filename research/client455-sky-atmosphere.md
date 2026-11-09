# Атмосферный проход и солнце455 — участок126

Состояние: **PARTIAL**, M6/M6F/M7/M9 открыты. В обычную собственную сборку
подключён настоящий проход атмосферы, его ресурсы и выбранные обновления Sun.
Это не полная приёмка освещения или визуальное сравнение с работающим455.

Воспроизводимый текущий gate:
`scripts/Invoke-Python.ps1 scripts/checkpoint_client455_sky_atmosphere.py`.
Результат: [sky-atmosphere-checkpoint](../inventory/client455-sky-atmosphere-checkpoint.json).

## Привязка к оригиналу

Обе входные PE — x86, base400000, SHA256:

- primary: `b1b5febf0d0394712e2322350e19dafe60742e8642697b93cfb89135bac1fd8b`;
- secondary: `46528aac20499e3b3928d58658d7e0cefe26feba7cd193796d5cfbf7a2bbc558`.

16 полных функций,2029 инструкций,19 диапазонов кода совпали между двумя455.
Основные RVA:4B1840 prepass;501450 mesh;5017F0 dome draw;500DA0 Sun draw;
500B00 SunColor;4B19F0 constants;4B1640 Sun angle/color;
4B1F20 полный lighting frame;4B1260/4B1280 create/release.
Выбранные параметры/конструкторы:501900,501BC0,5013D0,501410,5018B0;
binding/constants wrapper4D88D0.

Проверены страницы pcode/asm, уникальность инструкций и **каждый положительный
CFG block start**. Одних total/cursor недостаточно: у VA9018B0 есть нижний chunk
901760..9017EF, который запрос disasm от9018B0 пропускал. Запрос от901760
дал70 инструкций; верхняя часть содержит7. У8B1260/8B1280 также есть отдельные
хвосты900C90/900CB0. Audit учитывает объединение тела и CFG, не захватывает
нулевые внешние блоки как код функции. Вывод по8B1F20 сохранён из125 и проверен
по новому CFG. Частичные exploratory parents не названы полными asm.

Raw: `artifacts/client455-progress/sky-atmosphere126-reference.json` и
`sky-atmosphere126-session.json`. IDA d09e1f5b saved/closed/list0.
Ни один входной EXE не исполнялся. Серверные файлы не изменялись.

## Восстановленное поведение

Обычные level FrameMove и CSkyBox теперь обновляют Sun и вызывают8B1840 при
включённом sky2. Prepass сохраняет global/device VIEW/PROJECTION, обнуляет
перенос VIEW, временно задаёт near10/far60000 и восстанавливает матрицы и
ViewProj. Depth/zwrite/alphatest выключаются, как в выбранном оригинале.

Флаги — **scene flags**, не movie flags. R3X offset524 поступает в состояние;
текстовые токены case-sensitive: `*no_sun` OR1,`*no_sky_color` OR4,
`*use_fog_fog2` OR2. LoadLevel сбрасывает их после успешного открытия/закрытия
карты. Подтверждены bounded context bytes и вызовы restore/invalidate/loadshader,
полные родители этих context-фрагментов не объявлены полностью разобранными.

При shader available привязка и константы выполняются даже если flag4
подавляет купол. Flag1 подавляет солнце. Если оба подавлены (5/7), shader
сохраняется; очистка VS/PS происходит только внутри внешней ветки.
Scatter shader остаётся активным при следующей отрисовке Sun — особенность
оригинала сохранена. В конце helper переключает declaration, не очищая shader.
Общая старая SetVPIPTex1 с24byte/FVF остаётся отдельным renderer gap.

Новые ресурсы создаются обычным D3D_R3RestoreDevice после InitFullScreenEffect,
освобождаются в начале D3D_R3InvalidateDevice. Купол:65×65=4225 вершин,
20byte stride,8192 треугольника;VB84500bytes/IB49152bytes/INDEX16,
usage8/poolMANAGED. Формула: шаг1290, capped radius32, высота5160,UV i/64,j/64,
индексы a,b+1,b,a,a+1,b+1. Счётчики присваиваются после успешного создания
обоих буферов; release сохраняет счётчики. Cache binding не обещает полного
unbind: dome напрямую меняет buffers, а финальный helper использует старый cache.

Sun:4 вершины XYZ/normal/color/UV,stride36; declaration byte-equal VA BF7878,
купол — BF78A0. WORLD строится из scale/translateZ1400/rotateX/rotateZ-30.
Текстура загружается существующим R3LoadDDSAndTextureMem с исходным выбором
формата/фильтров, а не упрощённым D3DX loader.

Ресурсы закреплены [манифестом](../inventory/client455-sky-atmosphere-inputs.json):

| Файл | Размер | SHA256 |
| --- | ---: | --- |
| Scatter.vso | 612 | eee9e9786da4201d5c4d2dd58d9bc9af7ef81f3cc5dbae326d6de291fc8a60af |
| Scatter.vsh | 2647 | 7a4e233746b1792668360784ececccd6a349d79518c6f884a36c2d5b301b4df6 |
| sun.dds | 349652 | f70290eae5954cbde36936698ba9048fbd05d9caa66376c19807ba515ecdf589 |

Реальная Sun текстура:256×256,9mips,ARGB,pool1/format21. Раннее предположение
fixture512 было исправлено по реальному DDS; production не подгонялся под него.

Скалярные Sun значения сохраняют x87 порядок/spill: orbit,theta,phi,scale,alpha,
intensity. Учтены float denominator spill на рассвете/закате. Параметры
scattering имеют подтверждённые начальные значения/коэффициенты и выбранные
переходы Mie. File-backed night Mie BF7354=.03,day Mie BSS=0.
Все косвенные writers этих значений пока не восстановлены.

## Сборка и проверки

Engine67/17derived SHA256
`744733c27378f78731ce68653ca4755e8d2dcb22a53bc6b44741292a21133e55`.
Изменены payload только level,skybox,r3d3d8,r3vertexbuffer,client455_weather;
62 объекта byte-equal,0 timestamp-only. Shared headers/layouts неизменны,
182 client/20kernel не пересобирались без основания. Fresh ANI2/BBX smoke
и обычный relink прошли. Exact125 engine/PE/MAP/linkRSP/reports сохранены
`artifacts/client455-progress/*before126*` до изменения.

Own PE SHA256
`4dd76810b62a7137004f75e4cbd2490361a0d0180a1682e42cfa766de0626a5c`,
2245632bytes/x86/base400000/entryRVA16A440,WinMainB98B0/afterCreateB9A24.
Unresolved0,legacy CharacterMR/FORCE не подключены. Fresh own-entry/import audit,
sound1/window/device/contracts/existingCreate1 PASS. Device fixture теперь
также получает3 настоящих sky inputs. Обработанные first-chance исключения
40080201/E06D7363/406D1388 сохранены; фатального исключения нет.

Native `work/m9/4847c2b2/sky-atmosphere-001`:

-16 prepass cases:flags0..7 × shader present/absent;4 dome/8 Sun submissions.
- Полный dump4225 vertices: max absolute geometry difference0; все24576
  индексов byte-equal; shader GetFunction byte-equal actual612bytes.
- Матрицы,near/far,shader carry/preserve,declarations,quad positions/UV,
  c0/c4 transforms и direction/reflectance проверены на реальном устройстве.
  **Полные irradiance/constants/SunColor компоненты ещё не приняты.**
-72 Sun scalar boundary/PC24/53/64 nearest-even cases и5 actual FrameMove
  profiles сравниваются независимым рациональным oracle по битам.
- Create через ordinary callback; explicit release/recreate/missingshader;
  final release через ordinary callback. Это не полная Reset/lost/OOM приёмка.
-5 кадров просмотрены; changedbytes относительно disabled: midnight485560,
  morning483470,noon458675,evening483082. Disabled byte-equal125 sky2-noon.

Material regression `work/m9/40ad6a14/sky-material-001`:60 profiles,
3actualframe,36material/26indexed/10zeroalpha,directunloaded PASS;5GPU viewed.
Unit material cases задаютsceneFlags5 для отдельной проверки материала;
обычные sky2 GPU кадры включают новую атмосферу. World
`work/m9/a841e924/world-frame-001` и fade
`work/m9/6ffedb56/sky-fade-001`:10GPU viewed и byte-equal125;76queue/16clock,
90fadeframes+27helpers PASS. Итого20 просмотренных кадров,не20 карт/функций.
Warning neutralB1: исходный e_neutrala/trade_bel/trade_bel.r3e отсутствует;
не подменён. World6 прежних warning,fadewarnings0.

Лабораторный observer меняет отдельные slots82/83 **полной оригинальной vtable**
только собственного процесса и восстанавливает их перед forward/Get; protections
восстанавливаются. Не клонировать119slots: существуют private D3D entries.

Builder ведёт hash ledger собственной генерации, чтобы после неуспешной сборки
можно было обновить уже записанный им generated source. Сторонний drift по-прежнему
отклоняется; baseline033 и оригиналы неизменны. Это исправляет повторяемость
после ранней ошибки отсутствующего r3math.h,а не обходит разрешения пользователя.

## Открыто и следующий участок127

Остальные части8B1F20:lightcolors/exposure globals BF734C/BF7350,day/nightfog,
световая позиция/lensflare. Нужны реальные writers и интеграция с текущим profile,
а не новые произвольные значения. SunColor пока использует modern CRT math:
все x87/CRT transcendental/FP/rounding inputs не приняты. Косвенные parameter
writers,полный lost/reset/OOM/reentry/caps,INS/Planet/general renderer,полный
world/stages/auth/protocol/Character/gameplay и все client-acceptance gaps OPEN.
Новые159k/прочие широкие повторения не проводились. Модернизации графики нет.
