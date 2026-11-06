# Разбор следующего окна: CGUIBriefingWindow, начало070

Это карта статического разбора для071, **не готовая реализация/приёмка**.
Эталон455 x86/base400000 SHA-256
`b1b5febf0d0394712e2322350e19dafe60742e8642697b93cfb89135bac1fd8b`.
Source0.7 не содержит этого класса. Raw decompile записан в игнорируемые
artifacts/client455-tutorial/briefing-core070.json и briefing-dependencies070.json.
Типы this/arguments у части IDA helper aliases неточны: перед переносом читать
полные asm. Функции/смещения ниже обозначают анализ, не автоматическое доказательство
private ABI или смысла всех полей. Эталон не исполнялся.

| RVA | Наблюдение |
|---|---|
| 332B80 | Window ctor; vtableAE6454,base CGUIWindow |
| 332ED0 | Init462×207,portrait frame134²/background128²,key frame140×207,button45×20 |
| 333350 | RestoreSprite: frame style,close common helper,key portrait sprite info |
| 333450 | Title passes to CGUIText |
| 333480 | Portrait add/remove, race/role indices and helper333DE0 |
| 333620 | Key frame add/remove then layout |
| 333680 | Auto-size flag at+1180 |
| 3336B0 | Clear typing + page count/current bytes0 |
| 333790 | Insert CGUITextInfo28 sequence,optional6visible-line resize,page count BYTE |
| 333920 | Page selection,view start/end,typing interval80,delay250 first/0 others |
| 333A50 | No pages→event1201/value1;finished→next orclose;unfinished→forcefinish |
| 333AF0 | currentPage+1==pageCount |
| 333B30 | Field+1944 state,virtual208 called with inverse boolean |
| 333B80 | Virtual208 label uses ND1059 when nonzero,ND106 when zero |
| 333BE0 | Mouse thunk: base window then click4 from close or next control |
| 333C50 | Base Update,shown gate,typing completion state,portrait animation helper |
| 333CB0/333DE0 | Portrait timer/random/state,requires full asm/resource proof |
| 333F20 | Portrait/key membership changes main width/text offsets/control positions |
| 334140 | Main-board cap sprite choices common action4 vs9 |
| 334210/334360 | Lazy allocate key widget,replace rows,show/hide inside key frame |
| 331CB0 | CGUIBriefingBoard ctor,2image children,2cap flags |
| 331EE0 | Main board alpha updates children and both color fields |
| 3320B0 | CGUITutorialKeyBoard ctor:2rows,plus image12² sprite21:0:0,labelND1058 |
| 3323F0 | Key rows max2,plus/or widths/heights/positions;helper332900 still unread |

Observed window offsets: title336,portraitFrame460,portraitAni608,
portraitBackground804,portraitTimer900,cache904..1031,keyFrame1032,
autoSize1180,keyPointer1184,mainBoard1188,typingBoard1528,pageCount1772/current1773,
close1776,state1944,nextButton1948,portrait/race-role bytes2268/2269.
Это промежуточные имена по использованию, не готовый source overlay.

Main-board Init: typing margin25,15/gap5; title colorFFC7C6B6;
frame/background colors требуют проверки unsigned conversions и helper owners.
Source CGUITextTypingBoard восстановлен отдельно070,см.client455-text-typing.md.
Полный window/main-board/key/portrait draw и static sprite21 loader ещё не перенесены.

CTutorialBoard rich message target RVA0A63A0 (raw board-decompile061 уже есть):
title ND445,Clear,build TextInfo28 fromserialized font fields,insert text array,
portrait disabled,keys enabled;align bottom40 andhorizontalcenter;Open if hidden;
branch allowed-close uses633360,его точный смысл/arguments надо подтвердить asm.
Key messages use ushort low/high bytes;17 produces2rows. Don't replace this with
generic messagebox/instant text,or claim the existing fixture is this window.

Следующий анализ: full asm/layout/draw CGUIBriefingBoard731E60..7320A0,
key helper732900 и glyph/control resource21 paths,portrait helpers733DE0/CGUIObjectAni,
then build actual window/provider and connect CTutorialBoard probe. Full stage/Avatar/
world host remains separate required integration after real window,not a fake host.
