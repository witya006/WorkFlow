# Продолжение M6 — обмен предметов и переход в мир

Сборка `c9aeaf27…` прошла инициализацию окон изготовления и улучшения
после принятого выбора персонажа. Следующий сбой `CGUIExchangeWindow::SetSprite`
на собственном RVA `130fff`.
[Доказательства и адреса](../research/client455-item-work.md)

1. Сверить окно 13 у Board 16. В оригинале регистрация видна на RVA
   `147fb9`–`147fd9`. При сверке ресурса и действий спрайта проверить
   соседние регистрации до очередной живой проверки.
2. Продолжить до карты, аватара и ввода. Повторить переход через обычный
   выбор персонажа на локальном тестовом сервере.
3. Проверить соответствие таблицы 44 записям `Item.edf`, затем подключить
   обычные данные рецептов, условия и запросы изготовления и улучшения.
   Ограничения прежних контрольных точек остаются в приёмке M9.

# История 170 — изготовление предметов и переход в мир

Сборка `ad434f01…` прошла обмен между игроками и обработку руды после
принятого выбора. Следующий сбой `CGUIItemMakeWindow::Init/SetSprite`,
собственный RVA `13066F`.
[Доказательства и адреса](../research/client455-trade-ore.md)

1. Сверить Board 14 / окно 15. В оригинале конструктор окна RVA
   `2B9AE0` создаёт три панели. Init и SetSprite имеют RVA `2B9DC0`
   и `2BA0F0`. Перенести реальные данные и маршруты этих панелей.
2. Проверить обычный запуск и следующие регистрации, включая окно
   улучшения. Затем связать вход в карту, аватара и ввод.
3. В общей приёмке остаются полные сделки, переработка руды, игровые
   владельцы навыков и Силы, экипировка и остальная фабрика.

# История 169 — обмен между игроками и переход в мир

Сборка `7d348e69…` прошла инициализацию магазина NPC. Следующий сбой в
`CGUITradeWindow::Init/SetSprite`, собственный RVA `12FF6F`.
[Доказательства и адреса](../research/client455-shop-window.md)

1. В оригинале сверить окно обмена и его ресурсы. Board 10 создаётся на
   15 ячеек, RVA `147C2C`, затем инициализирует окно 23, RVA `147C51`.
   Проверить обычный запуск после выбора персонажа.
2. Следом проверить Board 11 для руды и другие регистрации. Вход в карту,
   аватар и ввод остаются ближайшим наблюдаемым результатом.
3. Сохранить в работе обычное наполнение навыков и Силы, миграцию
   экипировки и реальные действия NPC-магазина, включая торговые сообщения.

# История 168 — торговое окно и игровые владельцы навыков и Силы

Сборка `83b60d77…` прошла инициализаторы навыков и Силы после принятого выбора.
Следующий сбой в `CGUIShopWindow::SetSprite`, собственный RVA `12F8BF`.
[Доказательства и адреса](../research/client455-skill-force-window.md)

1. Сверить торговое окно, начиная с `CGUIShopWindow::Init` RVA `2987F0` и
   `SetSprite` `2990A0`. В `MainGame` у торгового Board 9 пакет 1 × 200 и
   окно 7. После инициализации оригинал перепозиционирует его по размеру
   экрана в `CShopTradeBoard::InitWindow` RVA `B8350`.
2. Подключить `RF455SkillForceData` через реальные Board-пакеты и владельцев
   строк. Точки `490460`, `48D2C0` и `48E3B0` в VA подтверждают фильтры и
   цепь объекта. В текущей проверке UI получил EDF-строки напрямую. Проверить
   обычное наполнение и действия через игровые сообщения.
3. Сверить следующие окна фабрики, экипировку 16 ячеек и ID 63, конфликт
   ID 32 и привязку горячих клавиш. Повторить живой переход и затем проверять
   карту, аватар и ввод. M9 включает оставшиеся проверки прежних этапов.

# История 168 — навыки и Сила после UnitTuning и UnitStorehouse

Сборка `23332d3f…` прошла обе панели после принятого выбора персонажа.
Следующий сбой в `CGUISkillWindow::Init/SetSprite`, собственный RVA `1305EF`.
[Доказательства и отправные точки](../research/client455-unit-windows.md)

1. Сверить полный общий Init/SetSprite окон навыков и Силы с обеими копиями 455.
   Начать с `CGUISFWindow` RVA `2C80B0` и `2C84E0`, затем проверить видимые
   вкладки и связи с таблицами. Точки входа конкретных окон есть в статическом отчёте.
2. Перенести пакеты и ID окон по фактическому `MainGame`. Навыки используют
   7 × 20 и окно 5. Сила использует 6 × 20 и окно 6. Перед заменой проверить
   остальные владельцы этих ID и ветку профиля для Init Силы. Экипировка
   сейчас прошла собственный Init с наследием 15 ячеек и окна 90. Оригинал
   использует 16 и окно 63. Довести хранилище и связь с инвентарём вместе.
3. Проверить обычный вход после выбора на живом сервере и установить следующую
   границу. Остаток включает полную фабрику из 54 владельцев, коллизию ID 32
   между описанием миссии и Animus, позднюю привязку горячих клавиш и вход в мир.
4. Отдельно проверить строки хранилища и действия UnitTuning с реальными
   данными. Все ограничения предыдущих контрольных точек остаются в приёмке M9.

# История 167 — UnitTuning и полный граф панелей 455

166: PARTIAL_KNOWN_FAILURE. Own fe40637c…/x86/entry183720/2369024bytes,
182/67/20, build/link0. Новый обычный Linker startup5x10/window3 вернулся
после принятого выбора. Следующий старый CGUIUnitTuningWindow::SetSprite/Init
падает в GetSpriteXL ownRVA13028F. Мир и M9 открыты;0/12,25%(20–35%) прежние.

1. Читать research/client455-board-startup.md и текущий board-startup-checkpoint.
   Перед новой правкой использовать сохранённый точный before167:
   197файлов,7502253новых/4150820общих байт, own fe40637c…;
   before166 не перезаписывать. Не копировать полный клиент или набор ассетов.
2. Найти файлы через rg --files. Текущие классы: board/shopboard/cunittuningboard
   и userinterface/gamewindow/unit/guiunittuningwindow; не угадывать пути.
   По полным455 ASM/CFG обоих pins восстановить окно, skins/owners/layout и
   настоящий board startup. Target board12/window34,8packs/200slots;
   старые UI ID/спрайтовые индексы не считать455 контрактом.
3. Own candidates: SetSpriteB95F7, InitB7AD4, BaseInit12E62, CreateBoard26FC8.
   Это scan, не unwind. Verified window vtable1F53D0/slot6C→InitB72A0;
   BaseInit priorFF506C. Decoded prior E8call26F8B/ret26F90→Linker3CA00.
   Не лечить ошибку подстановкой спрайта или пропуском окна.
4. Фабрика455 всё ещё неполна:54target/17source classes/37missing. Семантика
   имеющихся17 не принята. До MainGame inventory настоящая фабрика создаёт
   окна20/50/21/5/52. Эти пути и поздний hotkey66CB20 с одним владельцем
   остаются обязательными; текущие старые Belt consumers ещё имеют guards.
   Прежний regex084 пропустил CBlackListBoard12bytes/slot30; старые53 — неполная
   выборка, не полный размер фабрики. В166 подтверждены все54 allocation sites.
5. Новый helperInitializeMainGame455 подключён и проверен:5x10,window3,50owners,
   настоящая цепь HWND→manager→bank4. Native7d430eab/8кадров совпал с просмотренным
   0c0ccbc4; полный item use/gameplay не принят. Старое исключение Potion11
   в fixture не считать проверкой его поведения.
6. Все165 inventory gaps и предыдущие actor/options/Animus/network/M6F gaps
   сохраняются. Pack/equipment Init в живом пути ещё не доказаны — они после
   UnitTuning. Затем LoadData/avatar/control/world и игровые сценарии.

IDAa06985c9/5c316b5a saved/closed/list0; jobs завершены/handoff удалён. Shared staging:
38assets/79608818linkedbytes/0newpoolbytes. Анализ2463(+2)/657(+6), индекс37871.

# История очереди166

# Продолжение M6 — настоящая фабрика панелей455 (166)

165 завершён как PARTIAL_KNOWN_FAILURE. Inventory/20slot packs/16slot equipment
views подключены. Native459bd43c:3расы/Taiwan/4просмотренных PNG,состояния,
маски/reload,64bitmoney и6GUI/Win32 маршрутов проходят. Own96afbd62…/x86/
entry182C50/2364928bytes;182/67/20/link0. Live auth/выбор result0 принят,
Inventory.Init вернулся. Next RF455_RejectRemovedLegacyBelt в старом Create_Board.

1. Читать research/client455-inventory-views.md и research/client455-storage.md.
   Before166 уже сохранён:179files/7344900private+4005559sharedbytes.
   Не перезаписывать и не копировать полный клиент/ассеты.
2. Восстановить настоящий455MainGame/board factory и порядок создания по полным
   ASM/CFG обоих pins. Исследование085 содержит53constructor/vptr/RTTI identities;
   найти актуальные reference/raw/ownmanager files через rg --files и сверить
   текущие регистрации,а не считать исторический17-object список полной фабрикой.
3. Старый potion-belt storage отсутствует в455. Нельзя возвращать его в wire
   enum,подменять Force3/Trunk5,удалять guard ради прохождения или отказываться
   от potion/hotbar функционала M9. Нужны настоящие клиентские владельцы/связи455.
   Это клиентская работа;серверные исходники/настройки не трогать.
4. Текущий системный E06D7363/KernelBase RVA140B82 не является own fault RVA.
   Own guard candidate28A61;verified E8call26BFD/return26C02→guard28A40.
   Inventory ownvtable1F099C/slot6C→Init89A70. Source order и call corroborated;
   candidate scan не unwind. Create_UI иInventoryInit вернулись;equipment Init
   стоит после guard,live pack/equipment acceptance пока нет. World/M9OPEN.
5. Все165gaps сохраняются:16UI equipment slots против15legacy backend;
   basefield+332,extra pack arrays,full item/actions/tooltip/ready cues,
   settings677DD0/highlight3325/3326,mouse/hittest/lifecycle/error domains.
   Native сцена с пустыми владельцами не доказывает получение/применение items.
6. Sprite44=SocketState.spr. Inventory action2 имеет11кадров0..10,но455
   сохраняет inactive pressed descriptor11. Не подставлять другой кадр и не
   отвергать normal Init из-за неактивного state. Полная pressed ветвь открыта.
   На reload target сбрасывает masks/natural size:full provider restore открыт.
7. После правильной фабрики — LoadData/avatar/control/world и реальные игровые
   сценарии;остальные Options/Animus/actor/network/M6F gaps никуда не исчезли.
   M9 давно определён,повторное уточнение не требуется.

Анализ2461(+42)/651(+45),IDA37871,137выборочных partialbindings.25%(20–35%),0/12.
Все4финальных PNG совпали с просмотренными;preEnter также просмотрен.
IDA0/nativejobsdone/privatehandoff removed. Играть/запускать только свою PE.

# История очереди165

# Продолжение M6 — инвентарь455 и предметные панели (165)

164 завершён как PARTIAL_KNOWN_FAILURE. Options455 подключён; четыре кадра,
реальные GUI/Win32 сообщения, значения/радио/reload и startup hover regression
проверены. Own6b5e61e6…/x86/entry182C50/2364928bytes;182/67/20/link0.
После принятого сервером выбора весь обычный MainGame::Create_UI вернулся,
включая Chat.InitializeChat455. Следующий отказ — старый CGUIInventoryWindow
при CInventoryBoard::InitWindow: ownRVA12F78F/GetSpriteXL+5F.

1. Before165 уже сохранён:165files/6858255private+4295738sharedbytes.
   Не перезаписывать и не клонировать полный клиент/ассеты. Exact164 gate:
   inventory/client455-option-checkpoint.json; research/client455-options.md.
2. Найти актуальные InventoryWindow/InventoryBoard sources через rg --files.
   Работать в tracked generator/native source. Сначала подтвердить владельцев,
   real skins/геометрию/сообщения по полным455 ASM/CFG и обоим pins.
3. Текущий собственный Inventory vtableRVA1F099C/slot6C→Init89A00;
   CBaseBoard.InitWindow call12D5F=FF506C/return12D62, затем actual failure.
   SetSprite8B150/Init89C8D — кандидаты стека, не unwind. Прежний Create_UI
   call2694C/return26951 раньше board call/return26B9D: обычный UI создан,
   но это не full455UI acceptance и не мир. Нужна настоящая панель инвентаря,
   без sprite alias, пустых заглушек и придуманного начального player status.
4. После board/UI creation — LoadData, Avatar/control, затем игровые сценарии.
   М6F/M7/M9 и все12полных областей остаются открыты. M9 уже определён.
5. Options partial: backend применения/сохранения, EAX/special/newgraphics/
   targeting, rating dialog/startup-board dismissal/logout condition producer.
   Guild/detail-texture — unrepresented legacy adapters; внутренние сообщения
   WM_APP8203/8210 не выдавать за455contracts и не возвращать их к collisions.
6. Все прежние Gauge/CharInfo/Recall/MobControl/Animus/equipment/tooltip/status/
   actor/network/lifecycle gaps сохраняются. CPU pending1 refusal теперь
   означает отсутствие message providers в стенде, не отсутствие C1A handler.
7. MCP может усекать массивы при сохранённых count/done. Проверять фактическую
   длину; пользоваться возвращённым локальным output URL для полного ответа.
   Запускать только свою PE. Сервер — только предоставленная среда проверки.

Функции2419(+44)/606(+47),IDA37871(+1getter boundary),112выборочных bindings.
Ориентир25%(20–35%),0/12 без изменений. Не повторять неизменённые крупные suite.
Все4OptionsPNG и final live preEnter просмотрены. IDA0/nativejobsdone,
private handoff удалён, server/originals без изменений.

# История очереди163 — MobControl455 и остальной MainGame UI

162 завершён как PARTIAL_KNOWN_FAILURE, не как полный клиент. Настоящий Recall455
подключён; восемь контрольных строк/HP/FP/EXP/состояния/scroll/resize/пять GPU-кадров
проверены. Live auth/список/Enter1/14→1/15/22/result0: RecallInit вернулся,
следом старый CGUIMobControl::SetSprite/Init падает в числовом sprite consumer.
Own e929b1ec…/x86/entry181DA0/2360320bytes,182client/67engine/20kernels/link0.
Gate inventory/client455-recall-checkpoint.json. Мир ещё не достигнут.

1. Перед163 сохранить exact162: preserve utility --previous before162
   --destination before163 --checkpoint inventory/client455-recall-checkpoint.json.
   Before162 уже124files; не перезаписывать и не клонировать клиент/ассеты.
2. Прочитать research/client455-recall.md. Следующий источник — обычный
   CGUIMobControl; найти точный путь через rg --files. Править tracked generator/
   native source, а не derived копии. Не чинить отсутствующую skin alias-ом.
3. Pointer-only inventory/client455-mob-control-discovery.json: primary
   vtableRVA6DFB24, кандидаты VA6AD3C0/6ADA40/6AE720 (RVA2AD3C0/2ADA40/2AE720).
   Сначала полные инструкции/CFG и оба pins, затем реальные owners/skins/контракты.
4. Текущий fatal ownRVA12E81F/GetSpriteOrgXL+5F. Связь с MobControl corroborated:
   его SetSprite94D59/Init94659, caller26CFE=FF506C/return26D01 и own vtable
   1F066C/slot6C→Init94330. Stack candidates не выдавать за unwind; RecallA0193
   среди них может быть остаточным адресом. Наблюдение: world/UI ещё не завершены.
5. Recall остаётся partial: полные Animus item/board/table/network producers,
   реальный summon gameplay, settings save/restore, cursor/link/lifecycle и
   непринятые FP/overflow/OOM ветки. CharInfo и Gauge gaps также сохраняются.
6. После полного MainGame UI — настоящая карта/avatar/control, затем связанные
   gameplay сценарии и полнота всех12областей. Сервер только среда пользователя.

Адресный охват2347(+37), fullASM529(+39),69выборочных bindings. IDA37870(+5
уточнённых function heads, не пять новых возможностей). Ориентир25%(20–35%),
0/12,M9OPEN. Перед продолжением не повторять успешные неизменённые крупные suite.
Последний live002 и пять final Recallframes просмотрены; private handoff удалён.
Диагностическое чтение стека исправлено на DWORD chunks, а не игровой обход.
IDA sessions0/nativejobsdone. Originals/servercode/config без изменений.

# История очереди162 — настоящий Recall455 и остальной MainGame UI

161:CharInfo455 outer/3pages/23owners подключён к обычному клиенту. Native3races/
6GPUframes/input/resize/mastery/signedresist PASS.60fullfunctions/6095instructions
bothpins. Own 3ebd9a7d…/x86/entry181DA0/2360320bytes/build-link0. Живой выбор принят,
CharInfoInit пройден;следующий oldRecall.SetSprite/Init fatal own12E8FF/GetSpriteXL.
Gate inventory/client455-char-info-checkpoint.json PARTIAL_KNOWN_FAILURE.

1. Перед162 сохранить exact161:preserve utility --previous before161
   --destination before162 --checkpoint inventory/client455-char-info-checkpoint.json.
   Before161 уже113files,неперезаписывать. Полный клиент/ассеты не копировать.
2. Прочитать research/client455-char-info.md. Recall source:
   work/client455-port/normal/source/userinterface/gamewindow/recall/guirecallwindow.cpp.
   Не править derived source напрямую:новый port hook/native generation.
3. Только pointer navigation:client455-recall-discovery.json,primary vtable6DFD14,
   InitVA6AF7F0/SetSprite6AFC20/SetBound6AFC90. Собрать полные ASM/CFG/обаpins.
   Legacy title inventory0/5 иresize7/2 не заменять skin alias/скрытием окна.
4. Восстановить настоящие owners/layout/контракты Recall455,проверить реальные
   summon/unit providers. Затем ordinarylive и следующий настоящий UIотказ.
5. CharInfo остаётся partial:action/equipment content callbacks/tooltip/help,
   mastery max/resist bounds producers,stat semantics17/18,lifecycle/FPedge domains.
   Не считать typed component setters доказательством полноты ordinary producers.
6. После полного MainGame UI — карта/avatar/control и связанные игровые сценарии.

Адресный охват2310(+48),fullASM490(+51),44выборочныхbindings.14прежнихdependency
bindings получилиordinaryownerpath,неявляютсяновыми14targetfunctions.0/12,M9OPEN.
Последний live требует own-child background update message;первыйa51без1/14непринят.
Драйвер не меняет OSfocus/глобальный ввод. Никаких server/original changes.

# Историческое продолжение M6 — подключение настоящего CharInfo455 (161)

160:CGUITabBoard455 source/component восстановлен,17functions/1318instructions
bothpins,5section example/scroll/reflow/mouse/4GPUframes/RAII PASS.
Но он ещё не используется старым CharInfo;в ordinary map нетего symbols.
Normal7354a931…/x86/entry17FA40/2349056bytes/build-link0,182client/67engine/20kernels.
Runtime sections прежней159сохраненыкроме verifiedlinkerdebugtimestamp210254.
Последнийживойотказ159:CharInfo.SetSprite/Init → GetSpriteOrgXL12C53F.

1. До161 сохранить точный160:preserve utility --previous before160
   --destination before161 --checkpoint inventory/client455-tab-board-checkpoint.json.
   Before160 уже104files,неперезаписывать. Нетнеобходимостиповторятьoldbulk/live159.
2. research/client455-tab-board.md содержит подробную первичнуюнавигацию.
   Raw44decomp:artifacts/client455-progress/charinfo160-reference/discovery-unverified.json.
   OuterInit665F70/SetSprite666580/Bound666690/Mouse6667E0/Select6669A0,
   MainBoardInit661800(356lines,естьtail)/Skin6630C0/Race6629F0.
3. Сделать нормальные semantic owners трёхpage (5/2/4section);использовать
   CGUITabBoard455 иреальные target47/common skins/animated headers/highlight.
   Подключить23m_uiInfoValues455,mastery6+3,resist4/extra7 иactualproviders.
   Не подменятьinnerboardстарымlayout и не скрыватьокно.
4. Primarycountryvirtual61/83 иracename data записаныкаккандидаты:проверить
   instructions/обаpins/factory доихпереноса. Непроверенныйdecompнедостаточен.
5. ПослеfullCharInfoInit пройтиследующийнастоящийUIотказ,затем карта/avatar/control.
   M9веськлиент,0/12,25%(20–35%). Sourcebindings26выборочно,необщийготовыйперенос.

Функции2262(+16)/439(+17) из37865. Gate160 PARTIAL_COMPONENT_ONLY,
runtimebaseline159 PARTIAL_KNOWN_FAILURE. Нижеистория160.

# Историческое продолжение M6 — окно характеристик455 и создание мира (160)

Частичная159 проверена: own afb30309…/x86/entry17FA40/2349056bytes,
182client/67engine/20kernels/link0. Gate client455-hud-checkpoint:
PARTIAL_KNOWN_FAILURE. Верхняя Gauge455 восстановлена,17детей/3GPUкадра/
семь пороговых случаев/перезагрузка PASS. Live Enter снова принят; затем
ошибка own12C53F/GetSpriteOrgXL ← CGUITileObject::SetSpriteInfo ←
CGUICharInfoWindow::SetSprite74366/Init73301 ← MainGame::Create_UI26729.

1. До правок160 сохранить точную159 вbefore160 через preserve utility:
   --previous before159 --destination before160
   --checkpoint inventory/client455-hud-checkpoint.json. Before159 не менять.
2. В старом CharInfo::SetSprite источник SP_ID_INVENTORY/action6/7 не
   соответствует настоящему окну455. Перенести target47 charinfo.spr,
   Init/layout/value owners/табуляцию/scroll и потребителей по исходному BIN.
   Не скрывать окно,не подставлять чужуюskin и не считать staging полноценным переносом.
3. После этого следовать следующему реальному отказу Create_UI/Create,
   затем настоящая карта/avatar/control. Full MainGame UI_LoadSprite ещё старый;
   target54BDF0 list записан в private decomp, полныйASMне принят.
4. Gauge: lowerEXP/unit routes/caption/notice producers/hover flags и четвертый
   gameplay provider всё ещё открыты. Четвёртая полоса НЕ объявлена EXP/DP.
5. Счётчики2246(+15)/422(+19) из37865;5новых частичных bindings,выборочно12.
   Полных областей0/12,25%(20–35%),M9OPEN. Server/originals не менять.

Research:research/client455-hud.md. Новых native/IDA jobs не осталось.
Ниже история159.

# Историческое продолжение M6 — игровой интерфейс и создание мира (159)

11.11.2026. Частичная158/df69c7ef…/x86/entry17FCD0/2349568bytes,
182client/67engine/20kernels,build/link0. Gate selection-checkpoint:
PARTIAL_KNOWN_FAILURE, не успешный полный прогон.
Реальный адресный Enter принят:tx1/14/1→rx1/15/22/result0;новый22-byte
receiver иtyped6default/11worn Avatar transfer/skipTutorial работают до
следующего участка. Native4wallet routes/fragmented encryption/default
retain+PRNG и3прежнихPNG проходят. Мир пока не достигнут.

Следующее:

1. Точная158 уже сохранена вbefore159/manifest.json (92files), не перезаписывать.
   Snapshotbefore158 хранит157(69files),не перезаписывать.
2. Фактический следующий отказ ownRVA12C8AF/GetSpriteXL@CSprite+5F:
   CGUIObjectAni::SetSpriteInfo ← CGUIGaugeExpWindow::SetSprite/Init ←
   CGP_MainGame::Create_UI/Create ← CMainApp::GameMainLoop. Events:
   work/m9/df69c7ef/selection-live-taiwan001/debug-events.jsonl.
3. Причина в старом MainGame UI provider: SP_ID_GAUGE_EXP2 всё ещё ведёт
   к ./SpriteImage/gaugeexp.spr. Его нет ни в original455, ни вlab, ни вzh-tw.
   Текущий SpriteMgr bridge покрывает только пять system namespaces.
   Найти в455 настоящий HUD/gauge/main sprite/init/create routes и перенести
   потребителей/atlas/layout/lifetime. Не скрывать виджет и не переименовывать
   другую страницу под старуюskin. Server/SDK не является этим блокером.
   Разведка159: inventory/client455-hud-discovery.json (только RTTI/pointers),
   private hud159-discovery/decomp-unverified.json (15 непроверенных decomp).
   Gauge ориентировочно использует target main4/EtcUI49 и четыре полосы.
   Проверить полный ASM/CFG и назначение четвёртой; это не готовый перенос.
4. После настоящего MainGame UI Create следовать следующему реальному
   пакету/загрузчику до карты/avatar/control. Live также принял8/5/9 —
   полный контракт этого сообщения ещё не проверен. ВходныеEXE не выполнять.
5. Full7BB470 equipment-board1 virtual176/tutorial branch и полный target
   Login NetworkInput/state/camera,clone/FP/lifecycle остаются требованиями.

Счётчики2231(+6) адресных функций/403(+7) complete ASM/CFG из37865.
Четыре новые sourcebindings не являются четырьмя полной equivalence.
При отчёте разделять новые RVA, смену состояния уже учтённых функций,
интеграцию в обычный клиент и практический результат. Точный общий итог
перенесённых функций остаётся не установлен; 7 последних bindings — выборка.
Research:research/client455-selection.md. M6/M6F/M7/M9OPEN,0/12,25%(20–35%).
Ниже исторический план158.

# Исторический план158 — выбор персонажа и переход в мир

11.11.2026. Частичная157 завершена, own88dc3d11…/x86/entry17F850/2348544bytes,
182client/67engine/20kernels/build-link0. Gate actor-lighting-checkpoint PARTIAL.
Actual BSP color→actor material→equipment→GPU восстановлен для определённого
цвета. 12 случаев на настоящей lobby.BSP PASS; три прежних PNG равны156.
Свежий live selection frame370/8000ms без unhandled: персонаж больше не почти
чёрный. Переход в мир не проверялся. Нет заявления о полной455UI/кадре.

Далее:

1. Перед обычными source edits158 сохранить точную157 вbefore158;before157
   хранит156 и не перезаписывается. История Git сохраняет scripts/docs.
2. Сверить target Login message/input→выбор существующего персонажа→запрос
   перехода/ответ/следующий stage. Не force state, не обходить waiting/проверки.
3. Проверить фактический Enter в собственной PE с настоящим93-byte билетом
   и данным пользователем аккаунтом. Входные EXE не запускать. Не направлять
   клавиатуру в чужое окно; для своего клиента предпочтителен адресный ввод.
4. Следовать первому реальному отказу до управляемого персонажа на карте;
   сохранять точные пакеты/состояния в обезличенном виде, ресурсы брать из
   существующего общего пула, без полной копии клиента. Сервер не менять.
5. Новый счётчик:2 225(+3) адресных функций/396(+3) complete ASM/CFG.
   Три precise source bindings в actor-lighting-bindings.json. Setter7CEA00
   пока только на стенде; его player state/legacy ground callers открыты.

Свет безBSP/override уоригинала undefined; own явно отказывает. ПолныеFP,
все специальные цветовые производители,clone/UI/particle/lifecycle и прочие
client-acceptance требования открыты. Оценка25%(20–35%),0/12,M6/M9OPEN.
Ниже исторический план157; не повторять уже выполненный перенос освещения.

# Исторический план157 — освещение живого персонажа

11.11: добавлен исходный срез учёта функций: 2 222 с адресными доказательствами,
393 с полным листингом/CFG из 37 865 функций IDA. Это пересчёт прежних отчётов,
не новый перенос. docs/function-coverage.md; inventory/client455-function-coverage.json.
При следующем участке фиксировать RVA → исходный символ → охват/расхождения →
проверка на стенде/в обычном клиенте. Старые групповые отчёты не переводить
автоматически в число полностью восстановленных функций. Прирост хранится в
inventory/client455-function-history.json; сама очередь освещения не меняется.

Сейчас156,own68e02c3d…,gate inventory/client455-combat-transition-checkpoint.json.
Живой кадр выбора получен:364frames/8000ms,unhandled0. Пользователь подтвердил
анимацию и сообщил почти чёрного персонажа;это видно на сохранённом кадре.
Следующая задача157:проверить CResObject::SetLightColorFromMap,реальный цвет
изlobbyBSP,GetMatLightFromColor,материал иCharIF constants. Не обходить маршрут
постоянным белым материалом. Точная156 уже вbefore157,50файлов.
SetAction weapon/shield,typed Login reads/fade иCreateEffect/DestroyEffect
исправлены;ниже план155 исторический,не повторять уже исправленные участки.
GameBarStoreзапрос устранён и подтверждён пользователем:HKCUcapture/DVR0;
backup artifacts/environment/game-capture-20261110-232356-911.json.

# Исторический план после155

10.11.2026. Частичная контрольная точка155:
inventory/client455-live-login-checkpoint.json, own da42b501…,
x86/entry17F660/2347520bytes,182client/67engine/20kernels,build/link0.
Оценка25%(20–35%),полных областей0/12;M6/M6F/M7/M9 OPEN.

## Подтверждённый практический маршрут

- Пользователь запускает E:/RFOnlineTrash/rf455-v0.4.0.
  Game127.0.0.1:27830,launcher27831,website8080.
- Оригинал E:/RFOnlineTrash/RFOnline/RF_Online.bin совпадает с primary b1b5…;
  rflauncher.exe38e32658… совпал с комплектом. Пользователь вошёл до мира.
- Собственный клиент использует93-byte launcher handoff:auth6C/03→6C/04
  accepted,key16;затем game1/1 payload58→1/2 payload12,result0.
- Реальный ответ1/9 имеет178bytes для одного персонажа. Исправлен прежний
  ошибочный отказ по минимальной длине506. Активные записи проверяются
  по14+164*count,только отсутствующий неиспользуемый хвост дополняется нулями.
  Target16AE40 копирует506 избуфера ииспользует count;не утверждать,
  что unsafe overread или полная исходная длина wire уже воспроизведены.
- Registered handler использует GetNormalItem455/typed normal payload.
  Setter462170 пишет толькоBYTE113 без clamp/callback. Native границы,
  fragmented encrypted178 и3прежних assembled renderPNG PASS.
- Обычный Taiwan Login/кадр новой PE PASS. Живой вход НЕ завершён:
  после registered reply падает equipped action. Мир не достигнут.

## Следующее действие

1. До дальнейших обычных source edits сохранить точную155 вbefore156.
   Before155 уже содержит принятую154,52файла;не перезаписывать.
2. Воспроизведённый следующий вызов:
   CAvatar::SetCombatMode→CCharacter::SetCombatMode→CAvatar::SetAction
   →CPlayer::SetAction (ownRVA555FE)→CPlayerProc::GetEquipItem (ownRVA10B23).
   Это явный отказ оставшегося legacy consumer при непустом оружии.
3. Сверить соответствующий target combat-mode transition,перенести на
   typed equipment/SetItemAnimation455/реальный fade. Не вызывать унового
   объекта унаследованный legacy SetAnimation вместо recovered wrapper.
4. Для живого прогона запускать только собственный BIN. Тестовые данные
   есть в пользовательском сообщении;не записывать пароль,ключ,identifier
   или rawpackets. Временный handoff удаляется. Не выполнять входные EXE.
5. inventory/client455-live-resource-inputs.json хранит только нужные
   архивы/текстуры;новые зависимости добавлять через
   prepare_client455_live_resources.py --events <owned debug-events.jsonl>.
   Он сохраняет предыдущие зависимости;не копировать весь клиент.
   485missing изэтих логов отсутствуют ивисходной установке;пока не трактовать
   их все как блокирующие:пользовательский оригинальный проход работает.
6. После перехода вооружённого персонажа довести обычные анимации/материал,
   оставшиеся bootstrap/UI/selection. Затем управляемый персонаж вкарте,
   бой/умения/предметы/чат иостальные12областей. 1/21 payload1 наблюдён,
   его полное назначение/поведение ещё не принято.

## Границы доказательств

Full Character clone lifecycle,Siege/activeUnit,particle registry,UI metrics,
полные specialskill/linker callbacks ивсе docs/client-acceptance.md остаются.
Зелёная сборка,обычный Login,живой world-entry иisolated render не закрывают M9.
Последняя полная storageопись20:56:14:158.84logical/43.19uniqueGiB,не физический
новый замер. Удалений нет. Большие неизменённые проверки не повторять.
Подробности:research/client455-live-launcher.md,client455-player-owner.md.
