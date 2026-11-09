# Память проекта

Обновлено 2026-11-10. **129 PARTIAL M6**.
Текущий gate: inventory/client455-weather-owner-checkpoint.json.
Команда: scripts/Invoke-Python.ps1 scripts/checkpoint_client455_weather_owner.py.
Доказательства: research/client455-weather-owner.md.
128 runtime gate исторический. Память до129: research/project-memory-before129.md.

## Цель и правила

CLIENT ONLY: поддерживаемые исходники и свой RF_Online.bin с полным функционалом
и поведением закреплённого455. M9 УЖЕ определён: финальная приёмка без
модернизации графики. Старый вопрос из Goal не повторять. M0–M4 diagnostic и
selectedM5 завершены; M6/M6F/M7/M9 OPEN, M8 не нужен. Build/Create1/partial lab
не означают полноту. docs/client-acceptance.md задаёт итоговые доказательства.
Server только read-only reference; не менять, не собирать, не восстанавливать.
Input EXE never execute; originals immutable; копии под work/. Git local only,
без remote/push/publish. Subagents только по прямому запросу пользователя.
Python: scripts/Invoke-Python.ps1 file.py, не -c/-m. VS2026 MSVC x86 primary.
Native/GPU jobs последовательно; дождаться terminal. Timeout не повод restart.
Перед runtime edit сохранить exact engine/PE/MAP/rsp/reports; ignored!=backup.
Не повторять159k/unchanged bulk suites без нового риска. Пользователю кратко RU,
updates <=60s. Для имён файлов сначала rg --files; не угадывать Windows glob paths.

## Подтверждённое129

Primary SHA b1b5febf0d0394712e2322350e19dafe60742e8642697b93cfb89135bac1fd8b;
secondary46528aac20499e3b3928d58658d7e0cefe26feba7cd193796d5cfbf7a2bbc558.
x86/base0x400000. 6fullasm/1546instructions/7byte ranges equalboth455.
Полные CFG + pcode. Constructor EH tail RVA65E0D0/99bytes включён отдельно,
не ограничиваться contiguous function size. MCP asm <=100/page, сверять
count/unique/done И каждый positive CFG block start, включая lower chunks.
Raw artifacts/client455-progress/weather-owner129-reference/session.json;
IDA d9c525ac saved/closed/list0. Configured smoke66tools/72442979 closed PASS.
Raw JSON20k chunks. Первую script asm page collector alias-ил с общим массивом:
duplicate suffix проверен против остальных7 страниц, first page восстановлен
до returned100count; untrimmed capture сохранён. Не повторять этот alias bug.

Actual map8EA220: читает1157D3C при8EA685, virtual slot15(+3C) при8EA68A,
call8EA690; затем ResetTexMemSize8EA692→8F1700, BSP8EA6A7→8FDEA0.
VtableB384D0→setter8E77B0: retainedDWORD this+244, lowBYTE/255→8B1210 exposure.
Нет прямыхcall xrefs кsetter, но это НЕ отсутствие вызова. INS8ED220/Planet915290
имеют другие owner paths и пока не перенесены. Прямой ctor weather default
не найден; свой getter читать только после load/setter.

Packed global1157D3C: BSS0, InitCore/R3X его не обнуляют. Три producers в90A4D0:
weather90AD04/haze90AD6A/special_weather90ADD3. atof double*255, trunc64, lowDWORD;
clear targetBYTE затем OR FULLDWORD<<0/8/16 без clamp/mask-byte. Возможен spill.
Новые weather_parameters.h/.inc и level_weather.inc. Source-owned CLevel overlay
level455.h: virtual SetWeatherColor455/GetWeatherColor455, DWORD в конец класса.
Старые members не сдвинуты; source sizeof/vtable изменены. Не заявлять target ABI.

ВАЖНОЕ исправление126/128: FOG/ENV НЕ case-sensitive. Реальный90A5ED _strupr
перед FOG/ENV,90ACEC _strlwr перед weather/scene flags. Uppercase вызов возвращён;
late weather callback после ENV. Filename скопирован до lower; consumed arguments
не получают новый uppercase. Старые исторические claims ошибочны и помечены.

1157CB8 — hardware D3DCAPS9.TextureOpCaps offset144,bit21=BUMPENVMAP0x00200000.
НЕ общий sunlight enable, НЕ DOT3/луминанс. SDK d3d9caps.h pinned in reference.
Material8C80A0 flag8000 читает offset216 целевого материала; не подставлять
legacy m_dwFlag по имени. CPUfilter8B30B0 directcallers8E3630/8E3F10 обращаются
this+100 color/this+104 flags40/20; ownership ещё не доказан. Pcode сохранён
в129raw. Это следующий130, пока не реализовано.

## Точная сборка и проверки129

Shared FI header changed → full182client/20kernel rebuild PASS, errors0.
Engine67/18derived SHA9b366d8ffab4a9cf4192b87d2f7c5dcda5ba74b278a94ccc92db0bf05e4baced.
49 payload changes/10timestamp-only/8byteequal128; не описывать как3changes.
PEd678c71bcfd68cd6ee6752277d2afffdfc81957a1c14a551698836df2ffca4a7,
2251264bytes/x86/base400000/entry16BAB0/WinMainB98B0/afterCreateB9A24.
Unresolved0/no CharacterMR/no FORCE. ANI2/BBX,own-entry/imports,sound1,
window/device/existingCreate1/contracts PASS; known handled first-chance exceptions
сохранены. Полный Create/bootstrap/game loop не принят.

Weather work/m9/bd1e90f3/weather-owner-001:90 actual scripts/PC24-53-64,
casefold FOG/ENV/flags,virtual owner+ordinary neutralB map load,5fog aggregates.
1445 ORACLE grid points не поштучно захваченные native colors; SunColor взят
наблюдаемый, полная CRT equivalence не доказана. Software aggregates PC24.
5GPU weather frames с actual BSP draws/blue0,64,128,192,255 просмотрены.
Параметр0x00BF3F7F унаследован из нашего script fixture, не original neutralB data.
Warning1 — original missing trade_bel.r3e, не заменён. NeutralB camera109548bytes
SHA4d71c20bdab6507a03904bc77c3d9cac16d062e666c923f71d7370b3030f6044.
Камера смотрит вверх; тонкие полосы геометрии — открытый world/camera/material
visual gap. Не выдавать этот кадр за full world acceptance.
Первый weather lab09c97674 упал: второй CLevel destructor освобождал global map
resources. Исправлен ТОЛЬКО lab lifetime: второй owner живёт до конца основной
карты; production destructor не трогать ради теста. Итоговый bd1e90f3 PASS.

Lighting6f38030b:867 captured CPU colors/3aggregates/27Mie/4scripts/5valid1badR3X,
5ordinary+3fogframes/29BSP PASS. Старый lowercaseFOG expected исправлен.
World78346d12:76queue/16clock/6oldwarnings. Fade43b94c91:90+27/no warnings.
Materialba00650e:60profiles/3frames/36materials/1missingwarning. Все25GPUviewed;
20 previous lighting/world/fade/material frames byteequal128. Общие прежние
bulk suites не повторялись. Перед изменениями exact128 engine/PE/MAP/rsp,
21reports в artifacts/client455-progress/*before129*. Игнорирование не backup.
No live native/build/IDA jobs remain после terminal polling.

## Сохранить контракты128 и дальнейшую работу

FrameMove clock→lighting; previousorbit/currentfar→Sunposition; newSun/Mie/night;
packedTint использует OLDfog, затем новыйfog. Не устранять one-frame lag.
Sunposition far не Sun-draw distance1400. Fogflag2 weighted endpoints, иначе
17x17 grid289/center8/step1290/radius4/height5160, unsignedsum/exposure divisor,
clamp255; NOzero-divisor successfallback. NegativeZzero=-0, не менять на+0.
Mie exact19h boundary .7916666865348816→0 между ненулевыми соседями.
R3Xflag4 day/8night; absent endpoint set preserves previous. FOG_COLOR-only
current/main defaults5/5000 НЕ заполняют day distances. Fixture inherited night
не называть исходными данными карты. ModernCRT/полные FP/statusflags OPEN;
unused transform/extinction FP effects omitted and explicitly tracked.
Lab observer patch originalFULL D3D vtable slots57/82/83, restore around Get/forward,
НЕ clone119slots: есть private driver entries. Production vtable не патчить.

Следующий130: material8000 and actual CPU tint owners/consumers, не helper symbols.
Затемlensflare8CB460/localfog/indirect parameters/fullshader/CRT/FP/reset,
INS/Planet/world visibility/alpha/textures/stages/auth/protocol/Character/gameplay.
Полная client acceptance остаётся незавершённой; goal active, не pause/block/complete.
