# Память проекта

Обновлено 2026-11-10. **139 PARTIAL; M6 открыт.**
Gate: inventory/client455-world-entry-checkpoint.json.
Команда: scripts/Invoke-Python.ps1 scripts/checkpoint_client455_world_entry.py.
Доказательства: research/client455-world-entry.md.
Предыдущая подробная память: research/project-memory-before139.md.
Последний commit до139: c121c4f (ordinary Login/root registration138).

## Цель и ограничения

CLIENT ONLY: поддерживаемые исходники и собственный RF_Online.bin с полным
функционалом/поведением закреплённого455. M9 уже определён: финальная приёмка
без модернизации графики. Устаревшее goal-описание про M4/неизвестныйM9 не применять.
M0–M4/selectedM5 достигнуты; M6/M6F/M7/M9 OPEN;M8 не требуется.
Server только читать reference, не изменять/строить/восстанавливать даже копии.
Оригиналы immutable; input EXEs никогда не выполнять. Работа под work/.
LocalGit, no push/remote/publication. Не делегировать без прямой просьбы.

## Текущий139

Own PE eb84c16bd41447d4afb150d856108ea16915932cebbf4a496b49cb838c6370c8,
x86/base400000/entry16FC30/2270208bytes.182client/20kernels build/link0/unresolved0.
Engine137 SHA708c892e60c3bf7457389b40ac24b9a466958c9d232d9efaf497d1ac3232b870
не менялся. Header-зависимые client/facade объекты пересобраны.
Primary SHA b1b5febf0d0394712e2322350e19dafe60742e8642697b93cfb89135bac1fd8b;
secondary46528aac20499e3b3928d58658d7e0cefe26feba7cd193796d5cfbf7a2bbc558.

Восстановлен обычный world-entry group1/op1 request58 и group1/op2 reply12.
Request: account@0,keys@4,fullscreen@20,version126455@21,signature33bytes@25.
Keymask=(k0+k2-k1-k3)*12AB34CC modulo32;каждый key XORmask.
До отправки close-request flag435992=1. Reply:result0/grade1/kind2;
cashShop flag3/indexWORD4,NPC6/7,quest9/10;nonzero flag→uint16index,zero→-1.
Результат/grade/seen/selectors пишутся даже при ошибке;ReceiveResponseMsg идёт
до записи kind. CNetworkMgr.m_worldEntry455 хранит данные для следующего bootstrap.
Own packed protocol headers58/12; bounded actual AnalysisServerPacket1/2.
Новые client455_world_entry.h/.inc; pure reader не мутирует state для short/null.
Полные8functions/1372instructions/225positive CFGblocks равны2pins.
RVA16A840 request,16A960 reply,16AAD0 kind,4ADAC0 keys,13EF80/13ED80 result,
162AC0 pending response,162F50 full core dispatcher.
Raw artifacts/client455-progress/world-entry139-reference/session.json.

Свежий account full-object native PASS:fixed62-byte plain oracle,fullscreen,
short0..11/null,24 result/selector combinations,fragmented/wrapped encrypted
receiver,ошибка242 иуспех0,real pending dialog close. Это искусственные входные
байты,не реальная auth/session. Native report inventory/client455-account-native.json,
отдельный world_entry_output. Standalone probe пропускает WinMain,поэтому явно
задаёт g_bIsWindowed;не путать этот client global с состоянием engine wrapper.

Свежий own WinMain/Miles/providers/ordinary Login PASS:
work/m9/eb84c16b/login-frame001,created1/loaded1,frame70/3204ms/640x500,
Renderreturn/ownexit observed,no fatal. PNGfe5073d2… просмотрен:lobby/waiting,
unopened panels отсутствуют. TCP fixture получил67bytes (138получал35),ответов0.
Component7assets/ordinary43assets shared,newpool0. Reference EXEs не выполнялись.
IDAe71a49ca saved/closed,list0. Native jobs нет. Exact138 snapshot47files before139.

## Следующий140: bootstrap и реальные данные выбора персонажа

Target result getter53EF80 читаетbyte435973;consumer53D0F0 при result0/state6
вызывает5E7BE0. Этот data bootstrap и его3selector consumers пока не перенесены.
Есть diagnostic pcode в artifacts/client455-progress/login138-reference/flow-diagnostic.json;
нужно полное выбранное ASM/CFG/equality и ordinary source integration.
Registered-character target request1/8 (56ADD0),reply1/9 (56AE40),а legacy1/7 и1/8.
Восстановить payload/dispatcher/consumers вместе,не просто перенумеровать.
Далее actual character selection→world/control/combat/inventory/chat.
Не bypass waiting/не force success;не писать server logic.
Other core/35processor payloads и bootstrap/error consumers ещё legacy/partial.

Target init5401D0:state6 normal,7logout. Country slot284false во всех11profiles;
не включать legacy reconnect безусловно. Create53BB20 имеет brokenIDB boundary,
JUMPOUT/ложную CRT-аннотацию;для переноса использовать реальные инструкции.
Full Title/movie/factory4/explicitnext ещё OPEN;legacyfactory3/modulo.
Target Title.FrameMove557F80 безусловно exit/jump:не включать deadfade.
CcrLogo.dat/реальныйAVI существуют;не переписывать CRT/COM вместо functionalroute.
Full455UI:10Login windows/layout/focus/input/system sprite5 ещё OPEN.
138root Add уже исправлен:AlwaysTop front/append,SetParent,Show(FALSE).
Legacy label0.738 не менять косметически как доказательство455.

## Оценка и приоритет

Около25%,диапазон20–35%,остаток75%:инженерная оценка12систем,не функция tests/bytes.
Полных принятых областей0/12. inventory/client455-progress-assessment.json.
A ordinaryTitle/Login;B auth/selection;C world/avatar/input/movement;
D combat/items/chat/NPC/quests/social;E fullM6F/M7/M9. Все старые gaps сохранены.
CRT/FP/failure fidelity остаётся backlog и не заменяет связанный игровой сценарий.
Не повторять159k неизменённых проверок. Проверять затронутое и выполнять
обязательные зависимости сборки;не обещать календарный срок по микро-тестам.

## Операционные правила

VS2026/MSVCx86. Python: scripts/Invoke-Python.ps1 file.py,не-c/-m.
Native/GPU jobs последовательно;timeout не termination,проверять тот жеhandle.
IDA:owned work copies,session на каждомcall,ASM≤100/page ивсе positiveCFG/tails,
save/close;MCP raw писать≤20kchunks. rg--files перед неизвестными путями;
использовать rg --glob при фильтрации каталогов,не path wildcard в PowerShell.
Общие исходные assets через client455_asset_staging.py,только owned copies;
configs/exes private. Snapshot13before-root и47before138/before139 сохранены.
Storage snapshot150.95GiBlogical/42.29GiBunique;hardlinks повторяются в сумме.
Старые большие каталоги не удалялись;до очистки нужна reachability evidence/inputs.
Не hardlink originals;Windows fileidentity через os.stat(path),не DirEntry.stat.

## Движок и сохранённые ограничения

Перенесены selected render/model/animation/material/audio/effects/maps,не целый мир.
FullFraction/particle/BBoShasi,INS/Empty/visibility/collision/device lifecycle ещё OPEN.
Пять scene targets137/capture helper существуют;ordinarycapture caller ещё не доказан.
Capture8CE020 сохраняет surface ref/игнорирует HRESULT;только lab компенсирует.
Synthetic PerbMap не считать455asset. Wrapper initially640x500/viewport640x480 open.
CLevel::SetViewMatrix не inverse/viewproj;publishcamera отдельно.
TemporaryCLevel должен переживать activemap;destructor освобождает global resources.
Material526/serialized46/MAX2048;не исправлять specular_flikering typo/OR bits.
ShaderPS6 fourthlane и прочие unowned stack lanes не выдумывать.
Остальные факты/доказательства — research/project-memory-before139.md,
research/project-memory-before137.md,docs/client-acceptance.md.
