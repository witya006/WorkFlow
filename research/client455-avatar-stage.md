# Avatar и связь с этапом клиента — участок073

В обычную сборку перенесены состояние этапа Avatar,проверка Create в MainApp,
выбор ветки упаковки логина и вход в клиентскую маршрутизацию Tutorial.
Полная фабрика четырёх этапов и сам Tutorial пока не восстановлены. M9 открыт.

## Эталон и доказательства

455 x86/base0x400000. Основной SHA-256:
`b1b5febf0d0394712e2322350e19dafe60742e8642697b93cfb89135bac1fd8b`;
backup `46528aac20499e3b3928d58658d7e0cefe26feba7cd193796d5cfbf7a2bbc558`.
34полных диапазона и две vtable64bytes совпали между pins;15полных asm
сохранены в ignored artifacts/client455-progress/*073.json. Сессия b3b8653d
сохранена и закрыта. Оригинальные EXE не запускались,серверные файлы не менялись.

| RVA | Подтверждено |
|---|---|
| 002110/003330 | Avatar constructor:BYTE20165=0,DWORD20168=0;copy переносит оба |
| 01E130/0A6160 | Сравнение stage BYTE и запись произвольного BYTE |
| 020BB0/020BE0 | Запись/чтение полного skip DWORD без нормализации в BOOL |
| 3D1370 | Create==0 прекращает текущий MainLoop;после успеха stage пишется в Avatar |
| 3D1C30 | Запрос Tutorial2 превращается в MainGame3 при skipDWORD!=0 |
| 162E80 | Stage2 отключает преобразование login bytes независимо от skipDWORD |
| 162BE0/164520 | Stage2+skip0 идёт в localTutorial;1/17 — прямой transport |
| 164640/1647D0/164EC0/165030/1651A0 | Отдельные клиентские обработчики групп4/5/7/13/17 |

RF455AvatarStage — исходная семантическая структура,а не overlay private ABI.
Она хранится в настоящем CAvatar. Getter глобального Avatar скомпилирован в
cavatar.obj;обычный account caller использует его при построении342байтов.
После успешного Create CMainApp пишет Avatar stage. Старая фабрика ещё использует
MainGame2,поэтому временный явный bridge переводит его в Avatar455 MainGame3.
Этим нельзя обозначать готовую fourstagefactory. При совместном переносе фабрики
bridge надо удалить:настоящий Tutorial2 должен остаться2.

## Клиентская маршрутизация сообщений

Обычный CNetworkMgr::SendNetMessage проверяет реальный Avatar stage2+skip0 до
переключения codec. Подтверждённые ignored messages возвращаютTRUE без записи в
send ring;это поведение target,а не отсутствие реализации. Group1/op17 вызывает
transport непосредственно и сохраняет прежний codec.enabled. Для ещё не
восстановленных localhandlers источник возвращаетFALSE и пишет числовую пару
group/opcode в локальный лог. Это явный известный разрыв,не успешная симуляция.

Границы маршрутов:

- Group4:handlers1/19/31;прочие ignored.
- Group5:весь helper остаётся незавершённым. Даже неизвестный opcode может вызвать
  локальный feedback об ошибке атаки;обобщать его как ignored нельзя.
- Group7:handlers2/5/9/11/13;Group13:2/21/26;Group17:4;прочие ignored.
- Остальные группы,включая21,ignored. При stage2+skip0 Account login helper
  возвращает успех отправки,но342байта в transport не попадают. При stage2+
  skip!=0 они отправляются без преобразования. Эти два пути проверены отдельно.

Это исключительно клиентская логика455. Отсутствие разработки сервера не является
блокером восстановления этих обработчиков.

## Исправление трактовки PostUIMessage

Название «current-stage guard45FBD0» из предыдущих заметок было неверным.
C0BD64 — singleton CGUIScreen:его constructor636C80 вызывается из Screen62FB40,
а getter4F5E40 читает HWND по+340. Это не указатель этапа/Avatar/MainApp.
Обычный PostUIMessage(UINT,LPARAM) теперь проверяет Screen singleton и возвращает
FALSE при его отсутствии. Проверка временно снимала только singleton pointer,
затем восстановила его;разыменования null и уничтожения живого Screen не было.

## Проверено

- Настоящий CAvatar constructor,stage values0/1/2/3/127/255 и skip0/1/FFFFFFFF;
  сравнение,выбор requested2 и разные условия login/localTutorial.
- Настоящий CMainApp::GameMainLoop с виртуальным stage fixture:Create failure
  не вызывает MainLoop и не меняет Avatar;успех пишет stage только при создании;
  legacyMainGame2 получает Avatar455 MainGame3. Полный stage fixture не выдаётся
  за CGP_Tutorial,его frame/render здесь не проверяются.
- Обычный account send/rings:stage1/2/3 при трёх skipDWORD,342байта,ignored
  Tutorial account request,1/17 transport с сохранённым codec и явный отказ
  непренесённого4/31. Использованы известные fixture bytes;реальный heartbeat
  с неинициализированным byte по-прежнему не изобретён.
- Ko/Ru source briefing и CTutorialBoard снова прошли.22кадра побайтово совпали
  с вручную просмотренными в commit687b88c;визуальная проверка переиспользована
  явно. Другие старые GUI/kernel suites не перезапускались и не помечались fresh.
- Финальная PE SHA-256:
  `3d1f8c323584e2a21a3e9c8b284d355f898ffcb5528f942385b333b682148970`,
  x86/base400000/entry150550/2042880bytes,182client/20kernel/32facade TU,
 0unresolved. Точная PE прошла WinMain/TCP fixture/engine/sound/D3D/Character и
 existingCreate=1;остановка до игрового цикла.40080201 через KernelBase остаётся
 неизвестным first-chance событием,не принято как полная failures equivalence.
- Configured IDA MCP:66tools,список10functions,декомпиляция и close/save прошли.
  Запуск отдельного probe внутри sandbox не смог создать worker(code2);вне sandbox
  проверка прошла,встроенный MCP работал. Переустановок не было.

Gate:inventory/client455-avatar-stage-checkpoint.json,статусPARTIAL.
Генератор повторно дал тот же preparation digestC250DB70…;оригинальные inputs и
engine056 не менялись. Новые маршруты встроены в обычные методы,force-retention нет.

## Следующий участок074

Прочитаны реальные методы CGP_Tutorial:Create5586D0,Destroy558AE0,Frame558B80,
camera5590B0,Load5594D0,world559670,Unload559750,Restore559810,Input5598C0.
Они заметно отличаются от MainGame;одной сменыID недостаточно. Actual source
Tutorial class пока не создан. Детальные decompile/asm сохранены для продолжения.

Приоритет — настоящий world owner/ILevel/BSP39:Tutorial выбирает bellato/cora/
accretia BSP иCAM по race/2. Все шесть реальных файлов доступны,их SHA иразмеры
в reference manifest. Три BSP имеют versionDWORD39,три CAM — float1.2. Camera
loader уже восстановлен056,но intro/переходы stage ещёнет. Затем подключать
actualAvatar/world/localfeedback host,board/47QBI иfourstagefactory/nextDWORD
совместно. Не направлять основной мир в Tutorial dispatcher.

Открыты все неперенесённые localhandlers,сетевой writer skipDWORD,полный
Avatar/Character/world/UI/input/camera/renderer lifecycle,auth/gameplay/IME,
unsafe/OOM/failure domains. Старый modulo переход пока сохранён явно как gap.
