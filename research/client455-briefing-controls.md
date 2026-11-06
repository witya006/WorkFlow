# Контролы брифинга455 — участок071

2026-11-07. Добавлены source CGUIBriefingBoard, CGUITutorialKeyBoard и отдельный
RF455GuiAnimatedImage bridge по455. Это необходимые компоненты отсутствующего
окна. Сам CGUIBriefingWindow/portrait/outline/capture provider ещё не подключён;
старые0.7 CGUIObjectAni consumers этим переносом не объявлены соответствующими455.

Эталон x86/base400000 SHA-256
`b1b5febf0d0394712e2322350e19dafe60742e8642697b93cfb89135bac1fd8b`;
backup `46528aac20499e3b3928d58658d7e0cefe26feba7cd193796d5cfbf7a2bbc558`.
29 function ranges/3vtable regions равны между pins,8 полных asm сохранены.
IDA e0103d83 и38abac4e закрыты с сохранением. Входные EXE не запускались.

| RVA | Реализованный/уточнённый контракт |
|---|---|
| 331E60/331EE0/331F60 | Main-board geometry,RGB-preserving alpha,body/border/caps draw order |
| 3320B0/3323F0/332900 | Keyboard rows,ND1058,selectors/gaps/retained geometry |
| 228820/228900/228AE0/228BD0 | Animation reset,BYTE grid,frame/UV,x87 time/loop/pause |
| 227910/227960/227A20 | Ex SPI/UV restore using original-image/texture ratios |
| 2262E0 | Base Draw includes own fill/image;corrects070 typing assumption |
| A63A0/233360 | Rich caller uses CGUIScreen capture pointer,not a close-caption flag |

Frame uses two cap images: common4:3/4 are462×32,common9:6/7 are611×32. Body
and two vertical border rectangles are drawn first. Then base fill/image and
children are drawn. Alpha updates cap colors and body/border alpha while
preservingRGB. Pre-Init colors are unspecified in target ctor;owned source
zero defaults are not accepted as parity for drawing before configuration.

Keyboard uses target sprite21 `tutorial.spr`, falling back to Common for both
localizations. It contains plus12²,5mouse sheets and12keyboard images. Supported
keys:0..4,17,18,32,65,70,73,77,79,83,87,90,112. Selector255 leaves animation and
size unchanged;other unsupported selectors reset animation but retain geometry.
Row height uses stored sizes even for omitted images. The plus placement uses
two5px gaps while computed width includes only one;this quirk is preserved.
Counts0/1/2 and all256 BYTE selectors were exercised;higher row counts are not
claimed as tested. LabelND1058 is real localized text.

Animation uses float FPS/frame and x87 multiply/add with a finalfloat store.
Grid args are BYTE,zero becomes1. Cell size uses original dimensions/grid;
UV size uses cell or forced extent divided by texture dimensions. SetImage
restores original/texture ratios;SetSheet computes cell/UV size but does not
advance displayed UV until SetFrame/Update. Before first Update a mouse sheet
can therefore appear compressed as several images;captured fixtures preserve
this intermediate state rather than force an extra frame update.

Loop overflow discards excess,setsframe0/paused and reads time once. Pause
resumes only on unsigned elapsed strictly greater than interval;the resume
Update does not advance the frame. Non-loop clamps to last and setsfinished.
New bridge covers verified mode0/unrotated/key sheets;full legacy Ani migration,
other draw modes/rotation/unsafe FP/resources/failure domains remainOPEN.

## Исправление прежних предположений

Первый UV перенос ошибочно умножал original/texture ratio повторно через legacy
SetSpriteU/V. Native test detected the wrong static key crop. Reset now assigns
raw0..1 UV directly;SetImage stores the single confirmed ratio. Frames rerun.

070 incorrectly read60CAC0 as children-only. Full2262E0 confirms base object
fill/image before children. CGUITextTypingBoard.Draw corrected to actual
CGUIContainer.Draw;its old no-fill assertion was replaced with an independent
80000red-pixel rectangle check. Main-board base fill also correctly covers its
manual body/border before cap children. This correction supersedes the contrary
070 report;default white/unset backgrounds made prior ordinary frames unchanged.
Typing reference now19ranges/1vtable/9fullasm;fresh Ko/Ru native/GPU passed.

The rich caller asm also confirmed screen global ECX at633360:flag1 captures
the briefing pointer and clears board close-block;flag0 releases capture and
setsclose-block. The screen setter rejects pointers not registered in its
container. Complete capture input/removal/lifetime consumers still need recovery.

## Проверки и экономия повторов

Real Ko/Ru source objects/GDI/D3D/resources passed naturally exit0. Tested cap
sizes,independent body/border coordinates,alphaRGB,allBYTE key membership,plus
and2row positions,stale sizes/state,UV padding,sheet frames/forced crop/zero grid,
loop/pause/nonloop/hidden gates.20frames saved,12unique views inspected;the other
8 are byte-identical across profiles. Typing self-fill inspected separately;
Python checkpoint independently counts80000 red pixels.

Final controls probe SHA-256
`85a2312e56faffd07cc26a2aa2bdf56546fe28b5cee4de57185e1e3225d571c3`, entryE48D0.
Typing corrected probe
`676c939a6ddb6b296f179cacb7a32448ad0ff3524aaaa631ee90907a3a31bab3`.
After final audit boundary wording,the repeated controls run produced identical
20GPU hashes to the reviewed c06fc728 run;full native manifests retain both paths.

Production PE SHA-256
`fea692b941be17117b80a697c2af1a09317905bb8ce6fe9ceee7917b594c6cc9`,
x86/base400000/entry150290,2041856bytes,182client/20kernel/30facade TU,0unresolved.
New controls and corrected typing are compiled in facade but unused by an
ordinary briefing instance yet;they may be stripped. No force retention.
Preparation idempotentE22CE37B097B88ECEAE37AC1C2E4CABC898700C78FDAABC2ADDEBB1FD0B496B5.

Full comparison against070 own PE found only COFF and IMAGE_DEBUG_DIRECTORY
link timestamps differ (file offsets296/1873360). After masking exactly those
DWORD fields,**every byte** matches;not only `.text` or a selected symbol.
Schema checked against installed SDK winnt.h22703. This proves the scope for
reusing prior unchanged GUI component evidence,not whole-client455 equivalence.
The7 prior GUI native manifests remain unmodified and retain their original
normal-link digests;typing gate explicitly records reuse after runtime equality,
unchanged recorded sources,and exact match to6173adf reports.44 prior GPU hashes
still equal069 baseline. Unchanged large suites were not rerun.

The exact final PE was run afresh through WinMain/TCPfixture/engine/D3D/Character/
existingCreate1 and stopped before game loop. Firstchance40080201 remainsunknown.
Current typing and controls gates PARTIAL;other historical gates were not falsely
retagged as fresh runs. Neither component tests nor Create constitute fullUI/auth.

Next072: actual CGUIBriefingWindow/outline/portrait/page/button/events and screen
capture/provider,then CTutorialBoard real view. After that actualAvatar/world/
Tutorial/fourstage. Full client-acceptance gaps remain required forM6F/M9.

Evidence: inventory/client455-briefing-controls-{reference,native,production,
checkpoint}.json and corrected text-typing manifests. Raw files:
artifacts/client455-tutorial/*071.json;own frames work/m9/c06fc728 and85a2312e.
