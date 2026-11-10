# Следующая работа — отрисовка экипировки и связанный выбор персонажа

10.11.2026. M6/M6F/M7/M9 открыты. Оценка25%(20–35%),0/12полных областей принято.
Полная оценка: [progress-report.md](progress-report.md).

## Проверенная база147

Own x86 RF_Online.bin993978ff…;182client/67engine/20modules/unresolved0.
Gate:inventory/client455-character-palette-checkpoint.json.
Новый настоящий CCharacter имеет20parts×30palettes и13dummy. Source/native,
Avatar3локализации,registered receiver3Avatar,Create иобычный Login прошли.
Кадр66/3031ms просмотрен:lobby/ожидание,полный455UI ещё не принят.
Девять first-chance исключений имеют прежний профиль145;необработанных нет.
Начальная ошибка C2079 вprobe исправлена include cresourcedatamgr.h.
Map-файлы Avatar/account теперь сохранены вуникальных папках запусков.
Общий пул при этих проверках не пополнялся;большие suites не повторялись.

Предыдущая145 сохранена вbefore146. Проверенная147 сохранена вbefore148/manifest.json:49точныхфайлов.
Не перезаписыватьbefore148 иbefore146.

## Ближайшая работа148

1. Перенести полный typed equipment mesh renderer среальными providers.
   Карта27полных функций/1827инструкций/213CFG иvtable176bytes совпала2pins.
   inventory/client455-equipment-render-reference.json иresearch/client455-equipment-render.md.
   Не тратить следующий turn на повтор этих27функций:полные pcode/ASM/CFG сохранены.
2. Проверить overlay descriptors4×526bytes@113FC70/textures@11404A8 иих writers;
   существующие providers Character455/normal_effects/kit/unit/эффектной очереди.
   Не заменять неизвестные handlers пустыми. 46C470/46C940 — разные renderветки.
3. Подключить к настоящим CPlayerProc/CPlayer/Avatar существующие13slotcontroller,
   ANI/fade,условия,эффекты ипозиции;frame/animation/render иUI callbacks.
   Цель — правильный одетый персонаж вобычном клиентском маршруте.
4. Закончить bootstrap:Quest/EventShip/NDMsgMonster/ItemTimer/NDMsgEvent/EventSound/
   SpecialStore/ItemCollection/Map иAvatar finalization.
5. Принять Title/Login ивыбор:ввод/список/внешнийвид/выбор/ошибки/переходы.
   Затем C:карта/управление,D:связанные игровые действия,E:полная приёмка.
   Переоценить объём послеB/C. Не принуждать авторизацию к успеху;сервер не писать.

## Подтверждённые ограничения

- VtableAA8F64:Render24→46E120,Animation28→46E520,FrameMove32→46DBC0;
  matrixRender148→46E160,matrixDraw152→46E1E0,normalDraw156→46E1A0,grade172→46D8B0.
  46D190 — общая Animation,не Render;46C200 — metadata getter.
- Render вызывает fade advancement до guard;fade3 возвращает1 безdraw.
  Две drawветки имеют разные общие scroll/time иразный overlaydraw.
- 4513C0 SetEquipItemToDefaultMesh действительно пустой/return1 в455.
  Не придумывать default-substitution;искать настоящий producer внешнего вида.
- 146компоненты проверены отдельно;ordinary CPlayerProc/skill/UI/liveupgrade/
  set/SF/potion producers/consumers ещё не подключены полностью.
  Baseitemsource44C670,неcurrent44C630;kindmetadata88;heightmeshIDmetadata72.
- Characterdummy13 иequipmentdummy10 — отдельные кэши.
- Полные renderer/physics/lifecycle/CRT-FP/ошибки остаются требованиямиM9.
- Оригиналы/сервер только читать,входныеEXE не выполнять. Работать подwork/.
- Sharedpool собственных копий;не создавать полную копию клиента накаждый запуск.
  Опись14:12:21:155,29GiB попутям/42,87GiB уникальныхфайлов;удалений0.
- IDAeaa5fe38 saved/closed/list0;активных jobs нет. Новыхустановок не нужно.
