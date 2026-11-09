# Стартовый сценарий Title/Login — начальные данные138

2026-11-10. **AUDIT_OPEN**,runtime после137 не менялся. Это начало работы над
наблюдаемым рубежом A,не готовые экраны Title/Login.

20diagnostic pseudocode functions идва небольших instruction contexts сохранены
вartifacts/client455-progress/title138-initial.json;session9bfd18c8saved/closed/
list0 вtitle138-session.json. Полного ASM/CFG/secondary range audit138 ещё нет;
не считать эти20функций полностью доказанными или восстановленными.

Pinned primary x86/base400000/SHA
b1b5febf0d0394712e2322350e19dafe60742e8642697b93cfb89135bac1fd8b.
Ранее подтверждённые4stageRTTI/vtables — inventory/client455-progress-reference.json.

Конкретные различия с current source:

- Ordinary CMainApp.Create_GameProgress по-прежнему создаёт3legacy stages,
  GameMainLoop использует modulo MAX_GAME_PROGRESS;target имеет4иexplicit next.
- Legacy CGP_Title почти пуст:Input сразуexit. Target Create RVA157CE0
  создаёт32-byte movie owner,читаетlocale CcrLogo.dat/PlayAvi/Logo,загружает
  video,запускает и выставляетvolume. Destroy освобождаетowner иglobal flag.
- Target Title fields после24-byte base:movie24,escape28,flag32,ARGB36,field40.
- Movie owner создаёт376-byte CTextureRenderer ииспользуетDirectShow COM.
  Renderer держитtexture352,width360,height364;RenderTitleRVA1582A0рисуетеё.
- **В закреплённом primary FrameMoveRVA157F80 безусловно пишетexit1 иперепрыгивает
  кэпилогу**(instructions VA557FB1..557FBD). Не восстанавливать исполнение
  недостижимой ветки fades/playback по одному оставшемуся machine code.
  Это не доказательство пропуска Create/Render или общего поведения всех455.
- Вoriginals реальноестьko-kr/ru-ru CcrLogo.dat иSnd/BGM/ccrinc.AVI878592bytes.
  Korean config также перечисляет4prologue videos. Не подменятьmissing movie
  фиктивнымуспехом. Standard DirectShow dependency следует использоватьизSDK,
  прежде чем переписывать системные COM/filterbaseclasses по бинарнику.

Следующий шаг:проверитьactual Title→Login маршрут своего executable иfirst
Login LoadData/UI;нужные неисполненныеvideo/factory/Avatar contracts учестьявно.
Full Title/movie source,4stagefactory,Login/auth/selection/world остаются OPEN.
