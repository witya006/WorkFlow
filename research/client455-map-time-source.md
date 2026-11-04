# Пакет8/5, CLand и время карты

Перенесён selected client-only path: CNetMsgProcessor_Map8/5 → CLand cache →
successful-load clock hook. Реальные client processor/CLand и GPU map проверены
через own entry полного проекта. Normal WinMain/живые соединения/input EXE не
запускались. M6 в целом и M9 открыты.

## Эталон и особенности

Оба PE x86/base0x400000:currentSHA
b1b5febf0d0394712e2322350e19dafe60742e8642697b93cfb89135bac1fd8b,
backup46528aac20499e3b3928d58658d7e0cefe26feba7cd193796d5cfbf7a2bbc558.
inventory/client455-time-callers.json закрепляет10bodies/6calls/2strings (включая
text-command caller4335A0/335A0,call4335BD; raw command-caller-0x4335a0.json сохранён).

| Участок | VA / RVA | Контракт |
|---|---|---|
| Map dispatch/receive |5801B0/1801B0,580AE0/180AE0| header8/5; payload DWORD+1/+5,byte0 игнорируется |
| Cache setters |580B20/180B20,580B40/180B40| CLand+32=opaque value,+36=timestamp,+40=receipt GetTickCount |
| Init |7C79F0/3C79F0| обнуляет+32/+36; +40/+24 не инициализируются в этом body |
| Calendar |7C8ED0/3C8ED0| localtime32 от cached signed32 timestamp; tm не является wire fields |
| Successful map load |7C8B60/3C8B60| применяет elapsed time и устанавливает оба clocks |
| Numeric fragment |7C8DC4/3C8DC4,130bytes| x87 spills,rate,truncation,lowDWORD/unsigned modulo |

Wire содержит как минимум9bytes. Reference handler не проверяет length/status;
полный transport validation domain открыт. Значение byte0/первого DWORD неизвестно;
opaque value и timestamp сохраняются в own state без применения binary CLand offsets.
После localtime32 добавляются elapsed_seconds%60 к tm_sec и (elapsed_seconds/60)%60
к tm_min. Полные elapsed hours игнорируются, calendar/day carry не выполняется.
Game fraction=lowDWORD(truncate(rate*totalSeconds))%86400/86400; real fraction=
totalSeconds%86400/86400. Clock setters запрашивают ticks независимо. Для map12
сохраняется tm_mday в field+24, для остальных0. Другие consumers field+24 неизвестны.
Quirks не исправлялись. Init receipt/mapDay domain до первого valid packet не закрыт.

## Исходники и доказательства

Own module scripts/native/client455_map_time.cpp/.h.130byte numeric body совпал
с обоими pinned PE после проверки REL32 GetDayRate и absolute86400 constant.
Собственные balanced prologue/float-return проверяются отдельно. Actual normal/lab
linked code проверен; lab E9 linker forwarding к GetDayRate разрешён и проверен
по bytes/target. Component и full-client own entry прошли314checks/12FP modes,
UTC0/JST-9:unaligned packet/ignored byte0,partial Init,receipt tick/wrap,даты,
rate/independent clocks,hour/day quirks и FPU control/TOP. Это не все timezone/DST
и не полная old-CRT localtime32/UCRT equivalence; negative/invalid timestamp не проверен.

RF_CLIENT_455_MAP_TIME defaultOFF, driver явно ON после module/source proof.
apply_client_map_time455.py сохраняет original bytes/branches трёх copied files:
cland.cpp/.h и network/netmsgprocessor/map/cnetmsgprocessor_map.cpp. Собственный
16byte state не меняет serialized layouts. В byte-index LoadLevel clock hook
вызывается после CreateEffect, если IsLoadedBsp. Полная455CLand failure/UI/camera/
effects sequence ещё не восстановлена. Source ledger21behavior files; actual
CLand/packet object references и288modern x86 /MT objects проверены.

## Actual CLand/packet/GPU scenario

Own graphics entry использует CLand constructor/Create и LoadLevel(char*) для
Platform01; настоящий CNetMsgProcessor_Map::AnalysisServerPacket принимает synthetic
8/5:byte0=0x7F,value0=0x11223344,timestamp43200,receipt tick0x23456789. Настоящий
CLand::ApplyMapTime455 в post-load boundary устанавливает при UTC0 fractions0.5/0.5,
mapDay1 для synthetic mapIndex12. Реальный индекс Platform01 этим не устанавливается.
Тем же методом пользуется compiled byte-index load hook, но полный byte-index
UI/camera/effects path в lab не исполняется. Root CNetworkMgr/socket dispatch не проверен.

Далее FrameMove/render/release сохранил23helpers/8interiors,15/500weather particles
и states[0,0]/[1,1]/[0,0].2GPU cases/66checks,0errors/warnings,Dmalloc/COM balance0;
FPU007F,frame просмотрен. CLand destructor/Destroy/UnloadLevel выполнены. Game DLL
GetModuleHandle checks до/после прошли.1275clock/703weather/30resource regressions прошли.

Normal2448896bytes,entryRVA0x1BBDF0,SHA
a1b9dd5d7e45313ef414d90dff198717e66bc5d58e5ed95bcb72fba601cf456a;
snapshot artifacts/client-first-build/map-time455,не исполнялся.
Lab4105216bytes,entryRVA0x7E78,SHA
ad3a17d3d54372c4a05962ae0088b3f44d3d96b438f0873e94c06317cae5f441;
work/client-map-time-lab/ad3a17d3d54372c4/RF_Online.bin.
Reports inventory/client455-map-time{,-link,-runtime,-graphics-runtime}.json.
Raw analysis artifacts/clock455-analysis; owned IDA92d1827c закрыта/save.

Повтор: build_client455_map_time.py → apply_client_map_time455.py → prepare_client_build.py
→ normal/lab driver → verify_client_map_time455.py [--lab] → probe_client_clock455.py
--map-time. GPU: probe_client_graphics455.py --level Platform01 --output
inventory/client455-map-time-graphics-runtime.json (HAL вне sandbox).

Открыто: byte0/value0 semantics/other consumers,calendar timezone/DST/old-CRT and
invalid/uninitialized domains,complete CLand/root network/other messages,console
%time/%real_time,full lighting/sky/particles/Character/UI/audio/gameplay и D3D9.
M6F/M7/M9 не закрыты; M8 модернизация не требуется.
