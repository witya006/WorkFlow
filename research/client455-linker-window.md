# Окно панели быстрого доступа — 097

2026-11-07. M6 PARTIAL; M6/M6F/M7/M9 OPEN.
Current gate: `inventory/client455-linker-window-checkpoint.json`.
Только клиент; inputs/originals/server не менялись, input EXE не исполнялись.

Обычный CLinkBoard теперь содержит CGUILinkWindow455 вместо старого окна8 ячеек.
Его реальные50 icon owners096 подключены к CGUIContainer hierarchy, Draw и
mouse observers. InitWindow вызывает новый Init и устанавливает окно справа
внизу экрана. Порт включает сворачивание/раскрытие, выбор и закрепление банков,
циклический переход по разрешённым банкам, масштабирование и сообщения окна.
Это восстановленный view/input-dispatch component, не завершённый Linker:
настоящие item-use/remove/swap/cooldown/gameplay handlers ещё обязательны.

## Бинарная опора

Оба pins x86, image base0x400000:

| Вход | SHA-256 |
|---|---|
| current | b1b5febf0d0394712e2322350e19dafe60742e8642697b93cfb89135bac1fd8b |
| reference-backup | 46528aac20499e3b3928d58658d7e0cefe26feba7cd193796d5cfbf7a2bbc558 |

51 equal ranges:36 functions/3509 asm instructions,14 double constants и
отдельный21-byte active-bank branch. Full MsgProc assembly сохранён отдельно.
Raw evidence: ignored `artifacts/client455-progress/linker-window097-reference.json`
и `linker-window097-message-assembly.json`. IDA a69bf228 и дополнительная сессия
сообщения savedclosed/list0. Манифест содержит хеши обеих сессий/inputs/fixtures.

| RVA | Выбранный контракт |
|---|---|
| 0x267140 / 0x2674c0 | окно / bank construction |
| 0x267770 / 0x267980 | Init и attachment controls/icons |
| 0x267c70 / 0x269570 | масштабирование / expanded hierarchy и position |
| 0x268560 / 0x268750 / 0x268840 / 0x268980 | sprites и visual bank state |
| 0x269100 / 0x269150 / 0x269190 | expand/collapse/select |
| 0x2692e0 / 0x269410 / 0x2694b0 | sparse cycle/pin/all flags |
| 0x2697c0 / 0x269b90 | MouseEvent / поиск icon по адресу |
| 0x242560 / 0x242670 / 0x2427b0 | image-text construction/config/string |
| 0x2428e0 / 0x2429e0 / 0x242b50 | glyph mapping / normal draw / clipped draw |
| 0x3b5be0 / 0x3b5fb0 / 0x3b2b80 | arrow refs / number refs / alignment |
| 0x1002b0 / 0x101be1 | bottom-right window placement / signed50C branch |

Размер481×46, шаг44, offset24 взяты из проверенных integer operands;масштаб
min(screenWidth/1024,1),row461×46,icon38 и остальные размеры прочитаны из double
constants бинарника. Положение вычисляется с truncation после сложения с origin:
для отрицательных координат это отличается от отдельного округления offset.

Expanded view оставляет active bank в main row;остальные ненулевые bankFlags
добавляются вверх в порядке0..4. Flags сохраняют raw int,не нормализуются в bool.
Цикл пропускает flag0,ищет до4 соседних банков и остаётся на active,если иных нет.
Банк отображает десять иконок и номер из настоящего bitmap atlas.

Mouse dispatch использует455 сообщения:drag502,Alt512,Ctrl510,ordinary-left504,
hover501,Shift-right3327;right без Shift/drag вызывает use provider. Select
посылает50C,expand50D. Native проверяет actual PostMessage и registered observer
через GUI event queue. Полные consumer handlers этих сообщений пока не приняты.

У board50C сравнение signed JGE:отрицательное LPARAM проходит верхнюю границу,
затем сохраняется low BYTE. Источник сохраняет это поведение;проверены-1→255 и
-255→1. Первоначальный unsigned guard исправлен после проверки asm. Это не
доказательство безопасности последующего использования malformed bank values.

## Реализация и проверка

Новые `client455_linker_window.{h,cpp}` и `client455_image_text.{h,cpp}` входят в
canonical facade. `client455_linker_window_port.py` воспроизводимо меняет member,
constructor binding,InitWindow,bank-message handling и тип старых icon callers.
RF455LinkerIconSlots теперь получает scale от actual window.

CGUIImageText455 читает цифры/символы из atlas1/action7/frame3 с cell7×9. Glyph
индексы проверены по MOV operands. Неизвестный/непомещающийся glyph сохраняет
пустую позицию. Реальный zh-tw frame не содержит всех19 кодируемых glyphs.
Clipped draw сохраняет наблюдаемую неидеальную UV формулу target и меняет V,
который затем использует normal draw. Это подтверждённое поведение, не исправление
графики. Полный allocator/error/numeric/private C++ ABI домен не принят.

Native с actualnormal objects/facade проверяет:

- 21 layout scenarios:7 widths320..1920,zero/positive/negative origins;1050
  actual icon placements/sizes и реальные container metrics.
- 320 sparse bank-cycle scenarios,raw flag2,pin/selector/expand controls.
- 48 modifier/drag mouse cases с exact raw PostMessage code/data/windowID.
  Use callback здесь recording subclass:это явно не игровое использование предмета.
  Отдельно обычный MouseEvent и настоящий SendMouseEvent→GUI queue→observer.
- 1792 glyph cases:all256 input bytes×7 widths,включая signed overflow geometry.
  Выбранные clipped/normal/after-clip UV состояния проверены на GPU.
- Actual CLinkBoard.InitWindow/Draw/50 owned clones,16 EDF-backed inventory
  originals;50 copies получают допустимые данные. Potion11 исключён из window
  fixture,поскольку реальный cooldown provider ещё explicitly refuses096.
- 8 GPU кадров просмотрены:5 состояний окна и3 image-text frames. Это own-source
  GPU capture, не reference executable capture. Disk inputs unchanged,all payload
  owners cleared,Dmalloc balanced;контейнеры удалены из actual screen до destruction.

Реальные localized zh-tw main/common.spr выбраны через тот же lookup, что source;
их framing/texture dimensions roundtrip проверен. Нельзя подменить их Common
версией и заявить ту же визуальную проверку.

С новой source facade повторены096 ownership и094 metadata,6 raw frames
byte-equal ранее просмотренным. Hotbar7 packets/storage3/account проходят.
Exact current PE ранний WinMain и Create return1 проходят;first-chance события
сохранены,terminal exception не наблюдался. Authentication/game этим не проверены.
Не повторялись unchangedworld/audio/159k/093atlas/092icon/2013owner/SF1447/095manual.

PE x86,2121216 bytes,
SHA-256 `9d8b57ad0ebb735aea477d99c9eebff05381d359f3086e7e137f6fbbfb702622`,
entry RVA0x155690,WinMain0xb73e0,afterCreate0xb754a;182client/20kernels/53facade,
0unresolved. Ordinary MAP retains Init0xc6d50/Layout0xc6f90/MouseEvent0xc7570 из
window provider и image-text draw0xcfe60/clip0xcfcc0. Engine082 unchanged:
`9caa283a6bf8a2fa1c9a05251b6cad451296bb03bda8a1860c22a872e88fe769`.

## Обязательное продолжение098

Restore actual CGUITimer/typed GUIItem timer state,copy/reset/draw/fanout и
Linker cooldown cache;подключить настоящие item-use/remove/swap/hover handlers
новых455 сообщений. Typed timer legacy callers сейчас explicitly throw,
а не возвращают ложный успех. Source right-use делегирует реальному board;
полная игровая реализация этого метода остаётся открытой.

Live SF/Animus source-board callbacks,flag21 lock/remainingchildren/followers,
Macro35 special-text kind7,Vending27/fullCItemBoard.Add notifications,normal
tablebootstrap всё ещё обязательны. Затем remainingboards/Trunk/protocol/
Tutorial/QBI/fourstage/Login/auth/game и прежние M6F/M7/M9 gaps. Не смешивать
legacy enum IDs с typed payload kinds и не делать static_cast к старым derived.
Resize/device-reset/fullwindow lifecycle,privateABI/unsafe inputs/OOM/concurrency
ещё не приняты целиком. До M9 не дошли.

Timer exploration (не asm/pincomplete acceptance): ignored
`artifacts/client455-progress/linker-timer097-exploration.json`.
61BC20 fanout вызывает61BCB0 для self и semantic registry members;
41EED0 читает CGUITimer.started уchild+216. Не подменять обычным legacy timer
без проверки дополнительных target fields и update/draw contracts.

Проверка сохранённого результата:

```powershell
.\scripts\Invoke-Python.ps1 scripts/checkpoint_client455_linker_window.py
```
