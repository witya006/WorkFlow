# Память проекта

Оценка10.11.2026: docs/progress-report.md — компактный текущий отчёт.
Подтверждённая база142: PE f0114c80…;точный normal-build берётся изbefore143,
если нынешний build-report уже143. Не смешивать доказательства разных сборок.
143 WIP не учтён вготовности:PlayerCharacter/SF5/Store/Character7+ND иtyped
class lookup написаны,15functions/1737instructions/193CFG regions равны2pins;
Python oracle5cases проходит. Native/runtime новой реализации НЕ проверены.
Последняя правка Character ignoredshortread была ПОСЛЕ успешной компиляции143:
сначала prepare/build/normal-consumers/link,затем новый full-object probe/gate.
Raw143 сохранён;IDA5fe0894d saved/closed. КлассыAvatar/UI/equipment не менялись.
Данные143:SFko/ru localization false;Storezh/ru default false,zhStore_1 true;
Characterko203/ru682 ignoredreads —targetRead не меняет cursor/destination
приошибке,5FC260 игнорируетрезультат. Не заменять mincounts/repair/resync.
В143 проверитьextra seek5EEAA0 при необходимости;полнаяunsafe equivalence open.
Оценкаостаётся25%(20–35%),0/12 fullacceptance. Нет обоснованного срокаM9.
Приоритет A→B→C→D→E;неизменённыеbulk suites не повторять ради счётчика.

Обновлено 2026-11-10. **142 PARTIAL; M6 открыт.**
Gate: inventory/client455-item-bootstrap-checkpoint.json.
Проверка: scripts/Invoke-Python.ps1 scripts/checkpoint_client455_item_bootstrap.py.
Доказательства: research/client455-item-bootstrap.md.
Последний commit до142: 72f7041 (Resource141).
Подробные старые факты: research/project-memory-before139.md и research/ по участкам.

## Цель и ограничения

CLIENT ONLY: поддерживаемые исходники и собственный RF_Online.bin с полным
функционалом/поведением закреплённого455. M9 уже определён: финальная приёмка
без модернизации графики. Старое goal-описание про M4/неизвестныйM9 не применять.
M0–M4/selectedM5 достигнуты; M6/M6F/M7/M9 OPEN; M8 не требуется.
Server только читать reference; не изменять/строить/восстанавливать даже копии.
Originals immutable; input EXEs никогда не выполнять. Работа под work/.
LocalGit, no push/remote/publication. Не делегировать без прямой просьбы.

## Текущий142

Own PE f0114c80b2a08bdb313113368c729b4a7cb4b4c0c05cdc193ee368edf627f2d1,
x86/base400000/entry172C30/2283520bytes.182client/20kernels/build/link0/unresolved0.
Engine137 SHA708c892e60c3bf7457389b40ac24b9a466958c9d232d9efaf497d1ac3232b870
unchanged. Обязательный normal-consumer proof обновлён.
Primary SHA b1b5febf0d0394712e2322350e19dafe60742e8642697b93cfb89135bac1fd8b;
secondary46528aac20499e3b3928d58658d7e0cefe26feba7cd193796d5cfbf7a2bbc558.

Обычный Login вызывает CItemDataMgr.LoadBootstrap455:cash→set→Item47+ND.
Порядок подтверждён декодированными CALL/JMP в production PE.
Cash selector -1/default иначе полный DWORD decimal suffix; ND overlay DWORD16.
При cashND count mismatch/отсутствующем ND base сохраняется; outer продолжает.
Все11 country vslot160=true,включаяKorea;не выводить это только изTaiwan.
4newfullfunctions/257instructions/27positiveCFG regions равны2pins;
RVA1F8EC0 cash,2089E0 set,4329B0/42C490 profile true methods.
Existing588instruction Item1FEE30 evidence089 переиспользован.
Raw artifacts/client455-progress/item-bootstrap142-reference/session.json.

Six real full-object runs:ko-default/zh-default/ru-default/zh1/zh10/ko1.
Cash1000rows,set1373,Item47/76049rows;independent alltable/name/description/
work arrays CRC/consumed bounds PASS. Twelve real CBoardObject/payloads каждый:
borrowed row/name,clone retains,last owner erases. Receiver world-entry supplies
selector through actual12-byte decoder,не реальная auth.
Russia cashND count mismatch иabsentkoND_1 дают false,base retained,Item PASS.
Новый GetData455 accessor сейчас удержан только probe;LoadData inlined вbridge.
Legacy ITEM_DATA/derived CBoardItem/CEquipItem/Avatar default/equipment consumers
НЕ перенесены. Нельзя cast455raw встарые layouts или заявлять appearance/selection.

Fresh WinMain/Miles/providers/ordinary Login PASS:work/m9/f0114c80/login-frame001,
created1/loaded1,frame70/3234ms/640x500,Renderreturn/exit observed,no fatal.
PNG276eb78c… просмотрен:lobby/ожидание,unopened panels hidden.
Обычный success-response bootstrap в этом запуске не выполнялся.
Wide unchanged account/resource/graphics suites не повторялись.
Exact141 snapshot49files before142;140before141 и139before140 сохранены.
IDAb958e3d1 saved/closed/list0;nativejobs нет.

## Следующий143: character tables/classes и выбор персонажа

Target53D0F0 result0/state6 calls1E7BE0. Initial item142 иResource141 интегрированы;
остальные таблицы/связи ещё legacy/partial. Далее PlayerCharacter,SkillForce,
Store(selector),Character7 иND/NDW overlays/class-tier lookup/names.
Переиспользовать RF455ItemDataStore.character иRF455SkillForceData;не cast raw
вlegacy CPlayerClass. Class setter412140 отличается отстарого helper.
Затем typed item/Avatar equipment consumers иordinary appearance/selection.
Не bypass waiting/не force success/не писать serverlogic.

Полный порядокbootstrap:ItemCash/ItemSetEffect/Item/Resource/character tables+
boards/Quest/EventShip/NDMsgMonster/ItemTimer/country slot296/NDMsgEvent/
EventSound/SpecialStore/ItemCollection/Map/5default effects/Avatar finalization/
registered request. Рольslot296 неизвестна;ItemTimer/SpecialStore не Exp/Combine.
Pcode root:artifacts/client455-progress/registered140-reference/session.json;
Resource141 raw содержит полный ASM root. All remaining loaders need own evidence.
Затем ordinary world/avatar/control/movement/collision→combat/items/chat/NPC/social.

## Сохранённые реальные участки139–141

World-entry request58/reply12 уже интегрированы. State m_worldEntry455 содержит
cashShop/npcShop/quest selectors (-1 илиuint16). Request keys XOR mask
(k0+k2-k1-k3)*12AB34CC modulo32,version126455,signature33bytes.
Reply result/grade/seen/selectors пишутся даже приerror;ReceiveResponseMsg доkind.
Registered request1/8/reply1/9,payload506=header14+3×164.
Name17/serialDWORD17/race21/slot22/class5@23/level28/dalant64@29/gold64@37/
baseShape45/equipment8×signed16@49/upgrade65/reserved83@73/lastConnection64@156.
Level0→1/skipTutorial0,else skip1;latest signed64 localmax0/strictgreater.
Count0 retainsactors/latest;parts1,2,3,4,5,7,6,8;class/appearance consumers open.
Standalone account skipsWinMain:explicit g_bIsWindowed,не путать сenginewrapper.

Resource.edf9groups/30623rows:1267bones/10484meshes/18872ANI. Registered1267/
10483/18872:oneNPC20483 missingparent skip. Five real playerBN shapes30/25/29/38/30
andfirstmeshname5;real playerANI fromRFS loaded. OtherANI metadata only.
Legacy260/328/244/84 rows match;bounded preflight/missing-player/shape checks added.
Own GetResourceList missingreturn fixed;otherlegacy getters/errorUI/quit open.
1120checked unresolvedrefs503BN/592BBX/25ANI afterloose/RFS lookup;not full asset
inventory or proof each path required. Seven archived members resolved.
Character manager keeps exact case/separate records;ANI normalizes/deduplicates.

## Оценка, память и работа

Около25%,диапазон20–35%,остаток75%:engineering estimate12systems,не tests/bytes.
0/12 full acceptance;144historical/overlapping records не знаменатель.
A Title/Login;B auth/selection;C world/control;D gameplay/NPC/social;E fullM9.
Отчёты разделяют:собирается/проверено отдельно/работает обычно/полностью принято.
Сборочные зависимости обеспечены;fullsource455/SDK0sets,referencePE2.
Feature/packet/state/resource/scenario inventory ещё неполон.
Не повторять159k unchanged suites. Проверять затронутое/обязательные зависимости.
CRT/FP/failures backlog сохраняется,но не заменяет связанный игровой сценарий.

VS2026/MSVCx86. Python scripts/Invoke-Python.ps1 file.py,не-c/-m.
Native/GPU sequential;timeout не termination,poll тотжеhandle.
IDA ownedworkcopies/sessioneverycall/ASM≤100+allpositiveCFG/tails/save-close.
MCP rawchunks≤20k;rg --files --no-ignore для ignored work,перед неизвестнымpath.
Не использовать PowerShell path wildcards вrg;filter через --glob.
Shared staging толькоownedcopies;никакихhardlinks originals;configs/exes private.
BN/BBX/ANI/MSH/RFS добавлены immutable. Resource firstpool+53.1MB,повторы0.
Item142 newpool509445bytes/adopt46.2MBexistingowned,29refs/165MBlogical.
Storage oldsnapshot150.95GiBlogical/42.29GiBunique,старое не удалялось.
Before cleanup verifyevidence/inputreachability. Windowsidentity os.stat(path),
неDirEntry.stat снулевыми inode/linkfields.

## Движок/UI: не потерять ограничения

FullFraction/particle/BBoShasi/INS/Empty/visibility/collision/device lifecycle OPEN.
Scene targets137/capturehelper есть;ordinarycapture caller не доказан.
Capture8CE020 retainsurface ref/ignoresHRESULT;толькоlab компенсирует.
SyntheticPerbMap не455asset;wrapper640x500/viewport640x480 open.
CLevel.SetViewMatrix неinverse/viewproj,publishcamera отдельно;temporaryCLevel
должен переживатьactivemap,destructor freesglobals.
Material526/serialized46/MAX2048;specular_flikering typo/ORbits сохранять.
ShaderPS6 fourthlane/unownedstack lanes не выдумывать.
FullTitle/movie/factory4/explicitnext OPEN;legacyfactory3/modulo остаётся.
Title557F80 exit/jump unconditional,не включатьdeadfade. RealAVI/CcrLogo.dat есть.
Login init5401D0 state6normal/7logout;country slot284false всех11,не force reconnect.
Create53BB20 brokenIDB/JUMPOUT/falseCRT annotation:читать реальныеinstructions.
Full455UI10windows/systemsprite5/layout/focus/input OPEN.
RootAdd138 Show(FALSE)/AlwaysTop ужеперенесён. Legacylabel0.738 косметически не менять.
