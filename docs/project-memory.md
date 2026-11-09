# Память проекта

Обновлено 2026-11-10. **140 PARTIAL; M6 открыт.**
Gate: inventory/client455-registered-characters-checkpoint.json.
Команда: scripts/Invoke-Python.ps1 scripts/checkpoint_client455_registered_characters.py.
Доказательства: research/client455-registered-characters.md.
Предыдущая подробная память: research/project-memory-before139.md.
Последний commit до140: 1299b89 (world-entry139).

## Цель и ограничения

CLIENT ONLY: поддерживаемые исходники и собственный RF_Online.bin с полным
функционалом/поведением закреплённого455. M9 уже определён: финальная приёмка
без модернизации графики. Устаревшее goal-описание про M4/неизвестныйM9 не применять.
M0–M4/selectedM5 достигнуты; M6/M6F/M7/M9 OPEN;M8 не требуется.
Server только читать reference, не изменять/строить/восстанавливать даже копии.
Оригиналы immutable; input EXEs никогда не выполнять. Работа под work/.
LocalGit, no push/remote/publication. Не делегировать без прямой просьбы.

## Текущий140

Own PE a3002fc48427f09cb1cb7c2f57c95696162d1099ce7714e890f1053d1c321607,
x86/base400000/entry1703F0/2271744bytes.182client/20kernels build/link0/unresolved0.
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

Registered-character request1/8 и reply1/9 теперь подключены к обычному receiver.
Payload506:header14+3×164. Name17,serialDWORD@17,race21,slot22,class5@23,
level28,dalant64@29,gold64@37,baseShape45,equipment8×signed16@49,upgrade65,
reserved83@73,lastConnection64@156. Нельзя считать имя21bytes.
Decoder bounds/null/count>3 до мутации;slot>2 skip;duplicates ordered.
Level0→1/skipTutorial0,else skip1;latest signed64 localmax0/strictgreater;
count0 оставляет actors и прежнийlatest slot. Parts1,2,3,4,5,7,6,8.
9fullfunctions/623instructions/72positive CFG равны2pins.
RVA16ADD0 request,16AE40 response,16B4D0 recordctor,6B2E10 parts.
Raw artifacts/client455-progress/registered140-reference/session.json.

Свежий account full-object native PASS,work/m9/3cd21e07/account-001:
real3Avatar/CP949names/64money-time/tutorial writer,fragment/wrap encrypted
receiver,short/null/count4/invalidslot/count0;world-entry и avatar-stage также PASS.
Это искусственные входные байты,не реальная auth/session. Native report
inventory/client455-account-native.json,отдельный registered_character_output.
Первый probe падал без Character shaders:добавлен staging реальных shaderfiles,
production initialization не отключалась.27assets shared,newpool0.
Полные таблицы/class-tier/appearance/обычный экран выбора НЕ приняты.
Standalone probe пропускает WinMain:явно задавать g_bIsWindowed,не путать сwrapper.

Свежий own WinMain/Miles/providers/ordinary Login PASS:
work/m9/a3002fc4/login-frame001,created1/loaded1,frame70/3203ms/640x500,
Renderreturn/ownexit observed,no fatal. PNG8ed17237… просмотрен:lobby/waiting,
unopened panels отсутствуют.139TCP fixture получил67bytes (138получал35),ответов0.
Reference EXEs не выполнялись. IDA2a850a2f saved/closed,list0. Native jobs нет.
Exact139 snapshot49files before140;exact138 snapshot47files before139 сохранены.

## Следующий141: bootstrap и реальные данные выбора персонажа

Target result getter53EF80 читаетbyte435973;consumer53D0F0 при result0/state6
вызывает5E7BE0. Этот data bootstrap и его3selector consumers пока не перенесены.
Complete diagnostic pcode сохранён также в registered140-reference/session.json;
нужно полное выбранное ASM/CFG/equality и ordinary source integration.
Порядок:ItemCash/ItemSetEffect/Item/Resource/character tables+boards/Quest/
EventShip/NDMsgMonster/ItemTimer/country slot296/NDMsgEvent/EventSound/
SpecialStore/ItemCollection/Map/5default effects/Avatar finalization/request1/8.
ItemTimer и SpecialStore не подменять Exp/Combine. Роль slot296 неизвестна.
Legacy CDataMgr count/stride иResource260/328/244/9groups лишь частично совпадают:
нельзя загружать455Item через старую запись/embedded descriptions без переносаND.
Class setter412140 отличается от legacy SetClassDTIndexByStrDTCode;
весь class-tier/appearance/resource/item consumer ещё не принят.
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
Отчёты разделяют:собирается/проверено отдельно/работает обычно/полностью принято.
Список142исторических/пересекающихся работ не знаменатель готовности.
Для текущей сборки зависимости обеспечены;полных source455/SDK0комплектов,
referencePE2. Полная feature/packet/state/resource/scenario опись не завершена.
Не повторять159k неизменённых проверок. Проверять затронутое и выполнять
обязательные зависимости сборки;не обещать календарный срок по микро-тестам.

## Операционные правила

VS2026/MSVCx86. Python: scripts/Invoke-Python.ps1 file.py,не-c/-m.
Native/GPU jobs последовательно;timeout не termination,проверять тот жеhandle.
IDA:owned work copies,session на каждомcall,ASM≤100/page ивсе positiveCFG/tails,
save/close;MCP raw писать≤20kchunks. rg--files перед неизвестными путями;
использовать rg --glob при фильтрации каталогов,не path wildcard в PowerShell.
Общие исходные assets через client455_asset_staging.py,только owned copies;
configs/exes private. Snapshot13before-root,47before138/before139 и49before140 сохранены.
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
