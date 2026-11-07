# Анимация готовности и перезарядки — перенос099

2026-11-07. PARTIAL: выбранная цепочка ordinary CLinkBoard и typed CGUIItem
восстановлена в исходниках. Полный Linker, игровой bootstrap и клиент455 ещё
не приняты. Текущий checkpoint: `inventory/client455-ready-cooldown-checkpoint.json`.
Статический099 manifest остаётся историческим исследованием, а runtime098
checkpoint — историческим после смены исходников, PE и derived engine.

## Закреплённые входы

- Основной455 SHA-256:
  `b1b5febf0d0394712e2322350e19dafe60742e8642697b93cfb89135bac1fd8b`.
- Второй455:
  `46528aac20499e3b3928d58658d7e0cefe26feba7cd193796d5cfbf7a2bbc558`.
- Оба x86, image base `0x400000`. Все адреса ниже — RVA.
- Исторический099:79 canonical functions/5906 instructions/82 равных диапазона,
  включая20 class-specific virtual entries. Подробности в
  [статическом исследовании](client455-linker-cooldown.md).
- Дополнение:8 функций/248 инструкций и12 равных диапазонов обеих455:
  item-code getters `0x4e30/0x54e0`, data getter `0x5510`, SF group `0x154f0`,
  SF predicate `0x70f0`, Force pack `0x641f0`, Skill pack `0x90650`,
  group timer `0x90140`, vtable bytes `0x6a9284/0x6a9414/0x6a9438`, FPS34
  constant `0x6d9f94`. Range sizes/hashes сохранены в новом reference manifest.
- Raw assembly/decompilation/ranges:
  `artifacts/client455-progress/ready-cooldown099-additional.json` (ignored).
  IDA session `fa7d0341` сохранена и закрыта; после закрытия sessions count0.

Decompiler output использован совместно с assembly и привязкой диапазонов.
Оригинальные EXE не исполнялись. Серверные файлы и оригинальные установки
не менялись; внешних публикаций, новых установок или remote нет.

## Перенесённое поведение

`client455_gui_animation.h/.cpp` содержит собственное состояние выбранной
GUI-анимации. Это не имитация private200-byte ABI. Ready configuration по
RVA `0x21af30`: sprite1/action13/frame0, лист1024×640 с texture1024×1024,
8×5 клеток128px,34FPS,no-loop,initial stopped,blend3. Поэтому UVspan=.125
по обеим осям.40 клеток находятся внутри одного SPR frame.

Update сохраняет Show/stopped/paused gates, DWORD wrap и строгое
`elapsed > pauseInterval`. Переход кадра имеет один итоговый float spill после
x87 multiply/add. One-shot останавливается на39; next FrameMove убирает child.
SetFrame сохраняет raw stopped и нормализует выходящий WORD index. Reset не
сбрасывает Show/geometry. Нулевая grid dimension становится1; неизвестные
texture dimensions сохраняют прежний UV step. SetData обычной typed иконки
сбрасывает ready playback; SetPos центрирует его через signed division.
Изменение одного Size не выполняет повторного центрирования.

UV записываются непосредственно в собственное защищённое поле GUIObject.
Legacy SetSpriteU/V требует привязанный sprite и повторно масштабирует UV;
его подстановка была выявлена малым state fixture и исправлена до приёмки.
GUIItem.Update не обновляет ready повторно: анимация становится отдельным
ребёнком root window при истечении cache record, затем обновляется окном.

Для настоящей текстуры добавлен own inline nonvirtual GetFrameTexture455
в `2dsprite455.h`, не меняющий class layout/virtual dispatch. Единый overlay
принудительно включён в engine/client через существующий `anicamera455.h`,
после `port_std.hpp`. Это устраняет разные определения CSprite и конфликт
WinSock include order. Private target offsets/pointer casts не используются.

Ready Draw использует настоящий common.spr. Quad имеет stride28,FVF324,
half-pixel offsets,z.1/rhw.5. Blend3=SRCALPHA/ONE,texture modulation и clamp;
после рисования alpha disabled,address wrap,Z enabled. Это проверено чтением
реального D3D state. Generic другие blend и clippedDraw явно отказывают.

`client455_linker_cooldown.h/.cpp` подключён к обычным BeginDelayAnimation,
FrameMove,Remove и GetOrgBoardObject.50 записей по20 байт содержат bank,
object,start,offset,duration. Конструктор оставляет bank/padding unwritten.
Admission по RVA `0x101c30`: row находится в root window OR bank active.
Каждый свободный matching slot получает отдельное чтение clock. Сопоставляются
kind,rawdata DWORD+4 и wrapper index против source serial+4, а не atlas itemID.
Occupied cache не переписывается при новом запуске таймера; из-за этого cue
может начаться раньше заново запущенного радиального индикатора.

Expiry по `0x101750` использует unsigned DWORD(now-start)+offset>=duration
и обнуляет все20 байт. Скрытая строка тоже истекает, без ready child.
Remove по `0x1007e0` обнуляет только ptr/start. Pending erase возвращает next,
а внешний цикл делает ещё один increment: соседние stopped cues могут
оставаться до следующего FrameMove. Sentinel wrap смоделирован явно,
без undefined `++std::list::end()`; все unsafe lifetime домены не приняты.

Original lookup `0x102190` и equal lookup `0x102330` различаются. Физический
тип проверяет boards1/0/5 против1/0. Для остальных original ищет фактический
payload pointer, equal — serial. SF идёт в3/7,Animus4,kind6→22,kind7→35.
SF group delay использует rawBYTE15; Force category BYTE12 задаёт pack
0/1→0,2→1,…5→4,прочее255; Skill pack задаётся BYTE12 напрямую.
Subtype2 запускает один equal source. Rawgate114A070 по умолчанию0;
nonzero+SF подавляет весь start. Значение gate за пределами этой ветви и
реальный writer ещё не установлены. Potion11 всё ещё явно отказывает без
настоящего Avatar potioncache.

## Проверка и её границы

`audit_client455_ready_cooldown.py` создаёт маленькие независимые AS99/AG99
fixtures. `probe_client455_ready_cooldown.py` линкует actual ordinary objects
и текущие production libraries, исполняет собственный native probe:

- 132 state cases/48 grid cases; copy-reset/centering/rawBOOL/clock wrap.
- Реальный global BoardManager, исходный inventory pack, EDF-backed original,
  два настоящих owned Linker clones и общий icon registry.
- Actual BeginDelay/FrameMove/Remove, повторный occupied start, attached/current/
  hidden expiry, ready attachment/playback/removal и pending erase quirk.
- Actual global Force pack, два SF payload и synthetic CPU icons: source group
  fanout и raw gate. Различие original pointer/equal serial проверено отдельно.
- Шесть GPU кадров idle/0/8/39/detached/removed просмотрены на contact sheet;
  реальная blue ready flash видна. Все owners/registry/sprite allocations очищены.

Lab явно размещает source objects в actual packs и инициализирует offline
network owner. Это не normal fullCItemBoard.Add или normal bootstrap; сетевого
входа/authentication нет. SF CPU icons синтетические, полный SF UI не принят.
GPU evidence получено от восстановленного source, не от capture оригинального455.

Свежие затронутые timer/window/owners/metadata probes проходят; все20 raw кадров
побайтно равны прежним просмотренным. Их visual-review manifests сохранены как
старые baseline; новый checkpoint связывает baseline hashes с текущими кадрами.
Повторно просматривать одинаковые пиксели не требуется. Hotbar7 actual packets,
storage3/account и engine startup contracts проходят. Unchanged world/audio/
159k/atlas093/icon092/2013owner/SF1447/manual095 suites не повторялись.

Обычная PE:182 client/20 kernels/56 facade TU,0 unresolved;
SHA `6b30676b54424e15bdb60e296794b3e9ac9861ba24745e2df0798e5e947a4212`,
2139648bytes,x86,base400000,entry `0x157830`, WinMain `0xb7580`, afterCreate
`0xb76ea`. Точная собственная PE достигает существующего Create return1
с offline launcher fixture; остановлена до обычного игрового цикла.
Это ограниченная startup проверка, не приёмка полноценного455 Create.

Derived engine67objects:
`546a7529b51139e856b1a108fcad7849c14b2d00563b7abbfdcc8db10026fa5a`.
Старый baseline engine033 и его source сохранены. Derived082 library9caa…
заменена этим build; отдельного snapshot старойlib нет. Исторические linked
PE/кадры/labs сохранены; игнорируемые каталоги сами по себе не backup.

Воспроизведение: `scripts/Invoke-Python.ps1 scripts/checkpoint_client455_ready_cooldown.py`.
Raw files и staged inputs лежат в ignored work/artifacts; маленькие manifests,
source/scripts/docs находятся в локальном Git. Checkpoint проверяет их hashes.

## Следующий участок100

Actual use/remove/swap/hover и MsgProc, затем liveinventory/equip/SF/Animus
callbacks и Avatar potioncache,flag21lock,Macro35,Vending27,fullCItemBoard.Add,
normal table bootstrap. CObjectBoard.UI_UseRequest в0.7 nonvirtual; target
bank-slot entry `0x100f80` нельзя подключать по совпадению имени/позиции.
Статические handler bodies уже сохранены в099 raw evidence.

Generic clipped animation/other blends,полные GUIItemchildren/shake/copy-empty,
resource/window/deviceReset/shutdown,privateABI/FPnumeric/unsafe/OOM/concurrency/
pending stale pointers остаются открытыми, как и все прежние SF/Quest/36boards/
Trunk/protocol/Tutorial/QBI/fourstage/Login/auth/game gaps.
M6/M6F/M7/M9 OPEN. Общая доля восстановления клиента не измерена.
