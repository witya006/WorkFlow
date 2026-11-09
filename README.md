# RF Online: исследовательская рабочая область

Цель: восстановить исходный код RF_Online.bin и довести собираемый КЛИЕНТ
до полного функционала и поведения закреплённой версии 455,
используя старые клиентские исходники и R3Engine как базу. Работа исключительно
над клиентом, его движком и необходимыми инструментами ресурсов. Серверные проекты
и серверные базы данных в задачи не входят. Серверные исходники разрешено читать
только как справочный материал, без изменений и сборки. Точная идентичность оригинальным
исходникам не предполагается. Модернизация графики — отдельный этап.

Основная папка: `E:\RFOnlineTrash\Source\WorkFlow`.
Репозиторий локальный; публикация и remote не настроены.

107 PARTIAL: в CMainApp восстановлен core прицеливания20: pending, отдельная
командная позиция, курсор через настоящий BSP, перемещение6 частей эффекта и
tagged Miles Radar.29 реальных проверок проходят; память785169→785169.
Pending0 разрешает hover при соответствующем статусе; pending1 пока отказывает
до мутации из-за отсутствующего C1A message provider. Игровых command producers
ещё нет; SetPending проверен в full-object lab, но удалён из обычной PE linker.
Новая PEd09eec8d…/entry15adc0/182-20-60/unresolved0/Create1. Status62/magic36/
resources66/audio157/runtime573/account/hotbar7/storage3 проходят;10 GPU frames
просмотрены,6 hover побайтно равны106. Gate107 current,106 historical.
Full nuclear/world/message/device/client acceptance ещё открыты. M6/M6F/M7/M9 OPEN.
[Доказательства](research/client455-nuclear-aiming.md).

Исторический106:

106 PARTIAL: настоящий прицел455 обновляется и рисуется через обычный
effectcore в контрольной D3D сцене: вращающийся радар/волна,6 tracks,90 ticks.
После обычной отмены children/master исчезают за62 ticks, кадр очищается.
Восстановлены512 активных эффектов, eviction/release и два render passes.
Просмотрены4 новых кадра эффекта и6 hover кадров; hover byte-equal105.
Предупреждения R3T подтверждены в коде455 и сохранены; память стенда освобождена.
Новая PE12ca86c5…/entry15ab00/182-20-59/unresolved0/Create1. Адресные регрессии
resources66/magic36/status58/audio157/account/hotbar7/storage3 проходят.
Gate106 historical,105 historical. Full nuclear owner/world pipeline/device
lifecycle ещё открыты. M6/M6F/M7/M9 OPEN.
[Доказательства](research/client455-effect-runtime.md).

Исторический105:

105 PARTIAL: восстановлен штатный владелец архивов Effect и автоматический
выбор группы при запуске эффекта/первой загрузке entity и particle. Обычный
прицел читает настоящий cue и загружает6 моделей/5 particle recipes/10 clones
с реальными D3D текстурами.66 проверок проходят;6 legacy R3T release warnings
и полный FrameMove/render остаются открытыми. Глобальные texture tables
освобождает отдельный owner: в стенде память возвращается к исходной.
PE015a25c2…/entry15a320,182 client/20 kernel/59 facade,unresolved0/Create1.
Magic36/status58/audio157/account/hotbar7/storage3 и6 просмотренных hover кадров
сохранены; кадры побайтно равны104. Gate105 current,104 historical.
M6/M6F/M7/M9 OPEN. Полное ядерное прицеливание ещё не принято.
[Доказательства](research/client455-effect-resources.md).

Исторический104:

104 PARTIAL: восстановлены формат эффекта на 64 дорожки, parser и временная
выборка CProcessMagic, EffectInfo56 и runtime456. Обычный кэш читает настоящий
скрипт ядерного прицела из RPK: все шесть дорожек проверены побайтно.
36 целевых проверок проходят; status58/audio157/account/hotbar7/storage3 сохранены.
Новая PE0419f2c0…/entry15a1f0: 182 client / 20 kernel / 59 facade, unresolved 0,
прежний Create→1. Шесть просмотренных hover кадров побайтно равны103.
Текущий gate: inventory/client455-magic-checkpoint.json; gate103 исторический.
Полная отрисовка эффекта и отмена прицеливания ещё открыты. M6/M6F/M7/M9 OPEN.
[Доказательства](research/client455-magic.md).

Исторический103:

103 PARTIAL: восстановлена звуковая зависимость ядерного прицеливания —
tagged3D audio с настоящим Miles,30 каналами и кэшем64 записей. CMainApp
открывает provider/listener в обычном Create; точная новая PE проходит Create→1.
157 проверок реального WAV/меток/остановки/LRU проходят. Статус58, account,
hotbar7/storage3 сохранены;6 просмотренных кадров hover побайтно равны102.
Новая PEcf7ac5e0…/entry159670,182client/20kernels/58facade,0unresolved.
Gate: inventory/client455-tagged-audio-checkpoint.json;102 теперь исторический.
Сам эффект и отмена ядерного прицеливания ещё не подключены. M6/M6F/M7/M9 OPEN.
[Доказательства](research/client455-tagged-audio.md).

Исторический102:

102 PARTIAL: восстановлены поле статуса персонажа, его вычисление из64-битных
флагов и условие отмены перетаскивания. Настоящий обычный Avatar теперь может
брать, отпускать и возвращать предмет. Прошли58 CPU проверок;6 просмотренных
GPU кадров побайтно совпали с101. Отмена ядерного прицеливания ещё не перенесена:
эта ветка явно отказывает до изменения предмета на курсоре.
Новая PE:5f1f0f77…, entry1587b0;182 клиентских/20 kernel/57 facade модулей,
0 неразрешённых символов; прежний Create вернул1. Account, hotbar7 и storage3
проходят. Текущий gate: inventory/client455-player-status-checkpoint.json.
Gate101 теперь исторический. M6/M6F/M7/M9 остаются открытыми.
[Доказательства](research/client455-player-status.md).

Исторический101:

101 PARTIAL: в обычном клиенте восстановлены Copy620, предмет на курсоре,
два backup object и screen icon handoff. Проверены замена/очистка/возврат
в actual Linker, timer Update и освобождение ссылок. Пять payload kinds,
bare wrapper,256 board IDs и6 новых просмотренных GPU кадров проходят;
32 прежних кадра побайтно сохранены. Quest sentence provider ещё отказывает.
Новая PEe77ec7e7…/entry1586b0/182client-20kernels-57facade/0unresolved/Create1.
Текущий gate — inventory/client455-board-hover-checkpoint.json;100 runtime
исторический. Live Avatar cancel,полная operation queue и игровые handlers
ещё не восстановлены. M6/M6F/M7/M9 открыты.
[Доказательства](research/client455-board-hover.md).

Исторический100: значок блокировки flag21,256raw/256normalized/18geometry/
6новыхGPU/35сохранённыхкадров. [Разбор](research/client455-item-lock.md).

Исторический099: source-owned ready-animation и cache50×20,132state/48grid/
6новыхGPU и20сохранённыхкадров были проверены. [Разбор](research/client455-ready-cooldown.md).

Исторический перенос098: typed GUIItem timer, копирование, круговой индикатор
и подписи.175state/112label/57radial и29GPU были проверены; статические
доказательства сохранены. [Разбор](research/client455-gui-timer.md).

Исторический перенос — linker-window097: обычное окно панели теперь рисует банки
5×10,переключение/закрепление/сворачивание и масштабирование. Проверены ввод,
bitmap-номера,8 GPU кадров и новая PE/Create1. Владельцы предметов/инвентарь
сохранили6 кадров. Игровые действия и таймеры ещё открыты;далее098 — эти связи.
Gate097 current,096 runtimehistorical;M6/M6F/M7/M9 открыты.
[Доказательства](research/client455-linker-window.md).

Предыдущий перенос — linker-owners096: обычный CLinkBoard создаёт собственные
копии иконок/предметов и регистрирует их.50 владельцев/5×10,удаление оригинала,
очистка/3 просмотренных GPU и новая PE/Create1 проходят. Шесть прежних кадров
инвентаря/реестра не изменились. Полное окно и его ввод,live callbacks/Macro ещё
открыты;далее097 — завершение этих связей. Gate096 текущий,095 runtimehistorical.
M6/M6F/M7/M9 открыты. [Доказательства](research/client455-linker-owners.md).

Предыдущий перенос — icon-links095: восстановлен общий реестр иконок и обновление
количества/доступности у зарегистрированных копий.160 key cases, три просмотренных
GPU кадра и прежний инвентарь прошли; его три кадра не изменились. Новая PE/Create1
и затронутые network/storage/account проверки проходят. Реальные Linker/Macro
Add/Remove ещё не подключены. Далее096 — эти владельцы и fullCItemBoard.Add.
Текущий gate — inventory/client455-icon-links-checkpoint.json;094 runtimegate
исторический. M6/M6F/M7/M9 открыты.
[Доказательства](research/client455-icon-links.md).

Предыдущий перенос — item-icon-metadata094: реальные поля предмета доходят до
CGUIInventoryBoard; обычный TakeInItem использует общий проверенный core455.
566 metadata/520 race-level сценариев,16 реальных владельцев иконок,3 просмотренных
GPU кадра, сеть/хранение и новая PE/Create1 проходят. Полный CItemBoard.Add и
игровые связи ещё открыты. Далее095 — shared icon state и Add/Linker/Macro/Vending,
затем bootstrap. Current gate — inventory/client455-item-icon-metadata-checkpoint.json;
093 runtimegate исторический. M6/M6F/M7/M9 открыты.
[Доказательства](research/client455-item-icon-metadata.md).

Предыдущий перенос — item-atlas093: typed CGUIItem сам выбирает изображение по
itemID/spriteID/type через восстановленные callbacks455.880 граничных сценариев,
4 просмотренных GPU кадра,9 неизменных кадров092, предметы/данные/сеть и новая
PE/Create1 проходят. Далее094 — реальные payload metadata и игровые владельцы
иконок, затем normal bootstrap. Полный клиент ещё не готов; M6/M6F/M7/M9 открыты.
Текущий gate — inventory/client455-item-atlas-checkpoint.json;092 runtimegate
исторический. [Доказательства](research/client455-item-atlas.md).

Предыдущий перенос — item-icon092: предмет передаёт индекс и цвет рамки реальной
иконке; основной проход рисует ресурсы455 в размерах32/64. Проверены256 цветов,
120 границ количества,9 GPU кадров и освобождение спрайтов. Предметы/данные,
сеть и точная новая PE/Create=1 проходят. Полный инвентарь и игровой цикл ещё
открыты. Текущий gate — inventory/client455-item-icon-checkpoint.json;
runtime091 теперь исторический. Далее093 — автоматический выбор atlas, typed
consumers и bootstrap. M6/M6F/M7/M9 открыты; общий процент не измерен.
[Доказательства](research/client455-item-icon.md).

Предыдущий перенос в обычный клиент — item-object091: CItemObject592 и
CBoardObject620 используют общий предмет из менеджера CMainApp. Проверены
2 013 реальных владельцев и клонов через настоящий контейнер доски; прежние
данные/SF, сеть/Avatar и новая PE/Create=1 проходят. Иконки, смешанные старые
обработчики и автоматическая загрузка новых таблиц ещё не перенесены.
Далее092 — эти связи, затем полный Linker/UI/Tutorial. Текущий gate —
item-object091; M6/M6F/M7/M9 открыты.
[Доказательства](research/client455-item-object.md).

Предыдущий перенос в обычный клиент — resource-object090: восстановлены общие
CObject80/CResObject584, копирование, имя64 и правила сохранения/удаления эффектов.
160 сценариев флагов, предметы/Avatar, модели/FX, три карты и новая PE/Create=1
прошли; просмотрены15 GPU кадров. Это необходимая основа новых владельцев предметов.
Далее091 — CItemObject/CBoardObject и игровые владельцы, затем Linker/UI/Tutorial.
Текущий gate — resource-object090; M6/M6F/M7/M9 открыты.
[Доказательства](research/client455-resource-object.md).

Предыдущий source-runtime M6 — item-payloads089: чтение47 таблиц предметов455,
Quest12/Character7 и создание пяти остальных типов предметов проверены на
реальных данных.575 сценариев владения/клонирования и99 границ Animus XP прошли
отдельно и с объектами полного клиента; прежние1447 SF прошли с новой библиотекой.
Обычные игровые владельцы ещё не подключены; production086 неизменна.
Далее090 — CItemObject/CResObject, игровые владельцы, затем Linker/UI/Tutorial.
M6/M6F/M7/M9 открыты. Общий процент пока не измерен.
[Доказательства](research/client455-item-payloads.md).

Предыдущий source-runtime M6 — skill-force088: настоящие SF payloads и менеджер
создают1447 предметов из корневых455 EDF и освобождают владельцев через087.
Полный byte-oracle/standalone/full-object прошли. Установлен профиль Taiwan;
его zh-tw таблицы согласованы,ko/ru дают проверенные ошибки количества.
Новая ранняя проверка обычной PE/Taiwan/950/TCP/sound прошла; ordinarySF/Linker
binding ещё впереди. Далее089 — остальные payload/data factories и реальные
игровые владельцы. [Доказательства](research/client455-skill-force-items.md).

Предыдущая основа M6 — item-ownership087: восстановлены выбранные kernels
копирования/клонирования и освобождения shareditem92/wrapper620. Библиотека
проверена отдельно и с объектами полного клиента; managerhost пока recording,
в обычный Linker ещё не подключена. Очередь после087 — настоящие фабрики/менеджеры,
типизированные владельцы и их lifecycle. [Доказательства](research/client455-item-ownership.md).

Последний перенос в обычный клиент — hotbar086: обычный CLinkBoard формирует
изменения50 ячеек и отправляет group13/op17 через настоящий сетевой буфер/AES.
Проверены перетаскивание, кэш при отказе отправки, FrameMove и новая PE/Create1.
Полные владение/клонирование, окно5x10, ввод/cooldown и старые belt callers
ещё открыты. После общих владельцев — окно и настоящий Tutorial.
M6/M6F/M7/M9 открыты. [Доказательства](research/client455-hotbar.md).

Предыдущий реализованный участок M6 — storage085: реальные Force/Animus
регистрируются под455 ID3/4, таблица расширена до56, исправлена eligibility
возврата предметов0/1/5. Старый отдельный пояс выведен из фабрики; его неперенесённые
обработчики явно отклоняются. Новая PE, целевые проверки и Create=1 прошли.
Полные фабрика/протокол предметов/обучение ещё открыты; далее Linker/hotbar
и общие владельцы настоящего Tutorial. M6/M6F/M7/M9 открыты.
[Доказательства](research/client455-storage.md).

Предыдущий аудит M6 — tutorial-integration084: закреплены общие зависимости
настоящего обучения и карта53 классов досок455. Текущая исходная фабрика создаёт18;
у Force и Animus другие ID. Это исследование для переноса, runtime083 не менялся.
Далее — контракты хранения/досок, общая подготовка UI/Avatar и реальный Tutorial.
[Доказательства](research/client455-tutorial-integration.md).

Предыдущий реализованный участок M6 — money083: восстановлена 64-битная передача валюты
Avatar → инвентарь, форматирование и положение текста по 455. Korea/Russia,
проверки затронутых Avatar/account/actor/FX и новая PE/Create=1 прошли.
Это зависимость обучения; полный Tutorial и игровая интеграция ещё открыты.
Сейчас M6; M0–M5 закрыты в своих критериях. Процент всего клиента не измерен:
реестр поведения ещё неполный. M6/M6F/M7/M9 открыты.
[Доказательства](research/client455-money.md).

Предыдущий участок M6 — rvp-audio082: подключены реальные Miles immediate-audio
и timer_rate, проверены MP3/ownership/ambient ordering и текущая PE/Create=1.
В 455 RVP WAV-ветка регистрирует звуки без handle; это сохранено по бинарнику.
Три карты и actor/FX прошли регрессию. Далее083 — настоящий Tutorial и переходы
клиента;полный звук/эффекты/вход/игра остаются открыты. M6/M9 открыты.
[Доказательства](research/client455-rvp-audio.md).

Предыдущий участок M6 — rvp-effects081: добавлены базовые particle/entity проходы,
общий FX-кэш и отложенное освобождение. Полный ролик, три карты, исправление
ABI погоды и новая PE/Create=1 проверены;15 кадров просмотрены. Полные эффекты,
звук, вход и игра ещё открыты. Далее082; M6/M9 открыты. Процент всего клиента
не измерен: реестр поведения ещё неполный.
[Доказательства](research/client455-rvp-effects.md).

Предыдущий участок M6 — rvp-actor080: RVP загружает модели, выбирает анимацию,
сохраняет отдельные позы общих моделей и рисует их. Сцена12 объектов и отдельная
анимационная сцена прошли GPU/ownership проверки; новая RF_Online.bin проходит
Create=1. Частицы, звук и полная игра ещё открыты. Далее081; M6/M9 открыты.
[Доказательства](research/client455-rvp-actor.md).

Предыдущий участок M6 — rvp-runtime079: обычный CLevel вызывает настоящий
RVP camera/timeline вместо пустого body. Три мира/27 camera events и26 intro
cameras прошли;46 кадров просмотрены, новая PE прошла Create=1. Actor/effect/
audio/timer providers и полный Tutorial ещё открыты. Далее080.
[Доказательства](research/client455-rvp-runtime.md). M6/M9 открыты.

Предыдущий участок M6 — rvp078: перенесена модель объектов/команд RVP и
интерполяция. Все44 файла (615 записей объектов/1569 команд) совпали с независимым
разбором; native fixture покрывает12 команд. Производственный проигрыватель
пока остаётся заглушкой; далее079 — реальные ресурсы/исполнение/Tutorial.
[Доказательства](research/client455-rvp.md). M6/M9 открыты.

Предыдущий участок M6 — movie-state077: восстановлены флаги RTMovie, полосы,
логотип и отдельный default FOV 0.6; intro вызывает настоящий движок.
Проверены 8 сочетаний флагов, 26 камер трёх миров и fullscreen; просмотрены
40 кадров, новая PE прошла Create=1. RVP-проигрыватель подтверждён как заглушка;
его восстановление, полный Tutorial и игровая интеграция остаются открытыми.
[Доказательства](research/client455-movie-state.md). Далее 078; M6/M9 открыты.

Предыдущий участок M6 — fullscreen-effect076: перенесён настоящий fullscreen
motion-проход455;intro mode/density теперь вызывают движок. GPU18 и3мира/26камер/
34просмотренных кадра прошли;новая PE/Create1 проходит. FullTutorial/QBI/camera
controls/factory остаются OPEN. Далее077 — продолжение настоящего Tutorial owner.
[Доказательства](research/client455-fullscreen-effect.md).

Предыдущий участок M6 — tutorial-intro075: восстановлен порядок26 камер трёх
настоящих учебных миров, fade/skip/reload;29GPU кадров просмотрены. ExactPE/Create1
прошёл;runtime равен074 кроме linktimestamps. Actual stage/QBI/new-engine controls
иfourstage остаются OPEN. Далее076 — настоящий CGP_Tutorial owner.
[Доказательства](research/client455-tutorial-intro.md).

Предыдущий участок M6 — world074:Bellato/Cora/Accretia455 загружаются иотрисовываются
через настоящий CLand. Исправлены владелец BSP идеструктор уровня;повторная
загрузка/GPU/collision/Dmalloc balance проверены. Новая PE/Create1 проходит.
Полные ILevel/INS/Tutorial/игра ещёоткрыты;далее075 — настоящий Tutorial stage.
[Доказательства](research/client455-world.md).

Предыдущий участок M6 — avatar-stage073: состояние этапа связано с настоящим
Avatar,исправлена проверка Create ивключены подтверждённые ветки login/local
Tutorial routing. Недостающие обработчики дают явный отказ. Окно/панель и новая
PE/Create1 проверены;полные Tutorial/world/fourstage ещё открыты. Далее074.
[Доказательства](research/client455-avatar-stage.md).

Предыдущий участок M6 — briefing-window072: восстановлено исходное окно брифинга
со страницами,кнопками,портретами,клавишами и настоящим screen capture.
CTutorialBoard probe использует его вместо View fixture. Ko/Ru/22GPU кадра,
затронутый GUI и точная новая PE/Create1 прошли проверки. Настоящие Avatar/world/
Tutorial stage ещё не связаны. Далее073;M6/M9 открыты.
[Доказательства](research/client455-briefing-window.md).

Предыдущий участок M6 — briefing-controls071: восстановлены frame/key/animation
controls455,исправлен typing basefill. Ko/Ru native/GPU прошли;точная новая PE
сохранила Create1. Её runtime bytes совпали с070 за исключением timestamps,
поэтому неизменённые GUI suites не повторялись. Fullbriefing/provider ещё OPEN.
[Доказательства](research/client455-briefing-controls.md). Далее072,M6/M9 открыты.

Предыдущий участок M6 — text-typing070: восстановлен CGUITextTypingBoard,зависимость
настоящего брифинга. NativeKo/Ru traces/GPU прошли;44кадра существующего GUI
совпали с069,новая сборка сохранила Create1. Сам briefing/key/portrait/window
provider ещё не подключён;далее071 — его восстановление.
[Доказательства](research/client455-text-typing.md). M6/M9 открыты.

Предыдущий участок M6 — message-sizing069: обычный SetMsg использует pixel extent,
цвет455 и отдельный plain/rich параметр. Естественный размер вычисляется до
scroll fallback;300/250 не являются общими пределами. Ko/Ru12групп и10кадров,
затронутые GUI/Create1 проверки прошли. Пустой fragment extent явно unsupported,
полные Briefing/Tutorial/GUI остаются OPEN.
[Доказательства](research/client455-message-sizing.md). M6/M9 открыты.

Предыдущий участок M6 — gui-input068: перенесены базовые mouse/key/focus/queue
правила455,main-list Add/Remove и средняя кнопка. Double7/right8,порог300,
key dedup и focus order проверены Ko/Ru. Убран недоказанный arrow adapter
обычного scrollbar;EX binding сохранён. Новая PE собирается/existingCreate1,
затронутый GUI прошёл проверки. Полные GUI/IME/other layers/игра ещё открыты.
[Доказательства](research/client455-gui-input.md). M6/M9 открыты.

Предыдущий участок M6 — minimap-opacity067: EX подключён к обычному владельцу
мини-карты; оформление, выравнивание, 81значение alpha и настоящий mouse→queue
путь проверены для Korea/Russia. Восстановлен Draw455;провайдеры присутствуют
в production PE,existingCreate=1 сохранён. Игровая карта,другие controls,
camera consumer и полный parent input остаются открытыми.
[Доказательства](research/client455-minimap-opacity.md). M6/M9 открыты.

Предыдущий участок M6 — scrollbar-variants066: восстановлены отдельные классы
EX/Var; Korea/Russia проверки реальных GUI-объектов, очереди событий и GPU
прошли. EX найден в миникарте455; подключение этого владельца ещё впереди.
Var не имеет прямых вызовов конструктора в IDB, а его action15 недоступен через
обычный loader455. Полная PE собирается и проходит existingCreate=1.
[Доказательства](research/client455-scrollbar-variants.md). M6/M9 открыты.

Предыдущий участок M6 — scrollbar065: перенесены обычная полоса прокрутки,
составной бегунок, геометрия, snapping и mouse/clock rules455. GUI/GPU проверки
Korea/Russia и начальная инициализация новой PE прошли. Обнаружено ограничение
кадров composite skin в имеющихся ресурсах; EX/Var и parent input ещё открыты.
[Доказательства](research/client455-scrollbar.md).

Предыдущий участок M6 — text-board064: обычная панель использует fragment/line
caches455, пиксельный перенос, retention и Draw. Форматирование/extent проверены
в full-object probe; production rich callers ещё открыты. Korea/Russia GUI/GPU
и начальная инициализация новой RF_Online.bin прошли. Далее полный scrollbar,
message sizing и briefing. [Доказательства](research/client455-text-board.md).

Предыдущий участок M6 — text-metrics063: обычный CGUIText получил GDI-размеры455,
побайтовое измерение/DBCS fit и кэш высоты. Исправлена ранняя инициализация
геометрии в базе0.7; Korea/Russia проверки и просмотр кадров прошли.
Новая RF_Online.bin собирается и проходит существующий Create.
Полные TextBoard/scrollbar, FreeType/scale, briefing и Tutorial ещё открыты.
[Доказательства](research/client455-text-metrics.md).

Предыдущий участок M6 — modal062: обычные модальные окна получили кнопки,
подписи, рамку и обработку ввода455. Korea/Russia GUI/D3D проверки прошли;
новая полная RF_Online.bin собирается и проходит существующий Create.
Полные text-board/scrollbar, briefing и обучение ещё открыты.
[Доказательства](research/client455-modal.md).

Предыдущий участок M6 — tutorial-board061: восстановлено управление панелью,
выходом и выбором сценария; сообщения2/3 открывают настоящие GUI-диалоги и
проверены на D3D. На кадре обнаружены старые назначения кнопочных спрайтов.
Полный briefing и подключение к игровому Tutorial ещё открыты.
[Доказательства](research/client455-tutorial-board.md).

Предыдущий участок M6 — tutorial-actions060: правила UI/Equip/Cursor/Combat/Item
перенесены; фабрика охватывает47типов и подготавливает99реальных сценариев.
Проверка — recording host. Настоящий UI/Avatar/world и ordinary Tutorial
ещё открыты. [Доказательства](research/client455-tutorial-actions.md).

Предыдущий участок M6 — tutorial-spatial059: перенесены правила Move/Creation/
Position. Factory охватывает0–18; recording-host проверки прошли. Настоящий
мир/Avatar, остальные28 селекторов и неизвестный хвост item packet ещё открыты.
[Доказательства](research/client455-tutorial-spatial.md).

Предыдущий участок M6 — tutorial-runtime058: восстановлены порядок/состояния QBI,
сообщения и ожидания. Собственная библиотека проверена с recording host;
реальный UI/Avatar host и остальные41 селектор ещё открыты.
[Доказательства](research/client455-tutorial-runtime.md).

Предыдущий участок M6 — tutorial-scripts057: восстановлен формат47команд SCP.
Новая C++ библиотека прочитала99реальных сценариев и сохранила все байты;
поля/границы проверены. Исполнение команд и подключение Tutorial ещё впереди.
[Доказательства](research/client455-tutorial-scripts.md).

Предыдущий перенос M6 — camera056: обычный CAniCamera загружает1.2/1.3,
восстановлены FOV scale и playback boundaries455. Реальные камеры обучения/
входа, GPU projection и release проверены; новая PE сохранила existingCreate=1.
Полный Tutorial/fourstage/мир ещё открыты. [Доказательства](research/client455-camera.md).

Предыдущий перенос M6 — progress-base055: восстановлены обычный базовый цикл,
поле next-stage и Title next1. Реальные методы/счётчики проверены; полная
сборка и existingCreate=1 сохранены. Фабрика4stage/Tutorial ещё открыта.
[Доказательства](research/client455-progress-base.md).

Предыдущий аудит M6 — progress054: подтверждены четыре этапа455, включая
CGP_Tutorial; источник mode2 — Avatar stage. Текущая база ещё имеет три этапа
и старые переходы. Следующий перенос охватывает stage/Avatar/Tutorial вместе.
[Доказательства](research/client455-progress.md). Runtime в054 не менялся.

Последний реализованный участок M6 — account053: начальный seed, пакеты входа342байта,
ответы и world records72байта подключены к обычным send/receive/dispatch.
Реальные методы и диалог ожидания проверены на собственных пакетах; полная
сборка и запуск до существующего Create=1 сохранены. Настоящая аутентификация,
полный UI/протокол/мир ещё открыты. [Доказательства](research/client455-account.md).

Предыдущий участок M6 — connection052: настоящий Connect/wait выполняется до
движка. Восстановлены обработка сетевых событий, задержка callback и тайм-ауты.
Korean CCR WinMain через реальное TCP-соединение прошёл engine/D3D/existingCreate;
ошибки проверены отдельно. Это не игровой вход. У argv-профилей остаётся вопрос
endpoint0/1 и недостающих country/handler side effects.
[Доказательства](research/client455-connection.md). M6/M9 открыты.

Предыдущий участок M6 — network-codec051: AES-CBC с отдельными ключами направлений
и формат пакета подключены к обычным отправке/приёму. Восстановлены кольцевые
буферы 20КБ/1МБ и два настроенных сетевых процесса при вместимости шесть.
Байты сверены с Windows AES, реальные методы клиента проверены на фрагментации
и переходе через конец буфера. Полный протокол, вход и UI ещё открыты.
[Доказательства](research/client455-network-codec.md). M6/M9 открыты.

Предыдущий участок M6 — bootstrap050: FG/USEFG, country-specific instance check
и сетевое состояние Connect восстановлены. Настоящий NetworkMgr создаётся
один раз перед движком. Полная собственная PE собирается; прежний Create
возвращает1. На закрытом порту подтверждена особенность455: чтение ошибки
после closesocket теряет10061 и даёт0, connected остаётсяfalse. Полный транспорт,
шифрование, вход и UI ещё открыты. [Доказательства](research/client455-bootstrap.md).
M6/M9 открыты; следующий участок051 — клиентский transport/framing/crypto.

Предыдущий участок M6 — launcher049: восстановлены 93-байтовый launcher-файл
и аргументы Россия/Европа. Обычный WinMain читает их перед языком и движком;
старое позднее чтение удалено. Существующий CMainApp.Create вернул успех.
Проверки проведены на собственных offline-данных; подключение и вход455 ещё
не приняты. [Доказательства](research/client455-launcher.md); M6/M9 открыты.

Предыдущий участок M6 — sprites048: обычный CMainApp.LoadData загружает настоящие
языковые/Common спрайты455; восстановлена загрузка DXT5. Курсор и кнопка
отрисованы, содержимое текстур сверено с файлами. Точная собственная PE прошла
инициализацию UI до чтения launcher-данных. Полные интерфейс/вход/игра ещё
открыты. [Доказательства](research/client455-sprites.md); M6/M9 открыты.

Предыдущий участок M6 — lifecycle047: восстановлен подтверждённый по 455 выход
из UnloadLevel до создания уровня. Три пробы реального глобального CMainApp/
CLand и две GUI-пробы без создания Land завершились естественно с кодом 0.
Полная новая RF_Online.bin собирается; полные Create, ILevel и игровой цикл
ещё открыты. [Доказательства](research/client455-lifecycle.md). M6/M9 открыты.

Предыдущий участок M6 — font046: обычный engine text path использует455GDI/
Unicode backend. Реальный CGUIText нарисовал Hangul/кириллицу из NDLanguage;
метрики/atlas проверены независимым GDI,оба UI probes завершились чисто.
Exact own PE font/D3D/Character startup и прежние кадры сохранились. FullUI/
FT/IME/early-abort/shutdown открыты. research/client455-font.md; M6/M9 открыты.

Предыдущий участок M6 — language045: EDF/NDLanguage reader, indexed lookup и
DBCS boundaries восстановлены. Exact own WinMain загрузил корейский и русский
пакеты с правильными codepages; после корейского сохранился startup Character.
Все9доступных пакетов прошли byte roundtrip;11CRT locale согласованы. Шрифт/
текст/UI и весь Create ещё открыты. research/client455-language.md; M6/M9 открыты.

Предыдущий участок M6 — nationpaths044: выбор страны/корня данных подключён к
обычному WinMain. Новая полная сборка прошла ранний CMainApp::Create до Character
и менеджеров; Character привязан к настоящему устройству приложения. Остановка
до старых игровых таблиц. Полный язык/CRT/font/NDLanguage и Create/UI открыты.
research/client455-nation-paths.md; checkpoint PARTIAL; M6/M9 открыты.

Предыдущий участок M6 — devicestartup043: по 455 восстановлены установка32бит
без принудительного fullscreen и строгий результат Create. Производная
библиотека движка сохраняет033; полная PE прошла actual window/D3D init:
ready1/windowed1, устройство ненулевое. Остановка перед CMainApp::Create.
research/client455-device-startup.md; checkpoint PARTIAL; M6/M9 открыты.

Предыдущий участок M6 — startup042: точная собственная RF_Online.bin прошла CRT,
вошла в обычный WinMain, выполнила engine bootstrap и успешный Miles Audio init.
Запуск из отдельного lab остановлен отладчиком перед D3D; окно/Create/сеть и
полный shutdown ещё не приняты. Импорты и реально загруженные providers проверены.
research/client455-startup.md; checkpoint PARTIAL; M6/M9 открыты.

Предыдущий участок M6 — accounting041: общее накопительное хранение счётчиков
Character и чтение их диагностическим экраном подключены. Реальные ANI/модели/
GPU-ресурсы и release проверены. Новая D3D9/Character source ветка полностью
скомпилировалась и слинковалась в RF_Online.bin: 0 missing symbols. Это ещё не
приёмка normal WinMain или поведения всего455. research/client455-normal-accounting.md;
checkpoint PARTIAL; M6/M9 открыты. Далее — normal startup/initialization.

Предыдущий участок M6 — characterclock040: отдельный таймер Character восстановлен
и подключён к обычному _R3CalculateTime. QPC, fallback и независимость от таймера
движка проверены. Полный линк: один g_ChMemoryInfo; следующие задачи — учёт памяти
и полная линковка. research/client455-character-clock.md; M6/M9 открыты.

Предыдущий участок M6 — effects039: загрузка EFF, выбор и применение эффектов,
сброс и ссылки на particle/entity slots подключены к обычной сборке. Эффект
с настоящей DDS проверен на модели через D3D9; прежние кадры сохранились.
Полный линк сократился с 15 до 2 символов: Character accounting и clock.
research/client455-effects.md; checkpoint PARTIAL; M6/M9 открыты.

Предыдущий участок M6 — effecttables038: два readerтаблиц иquery подключены,
реальные таблицы проверены. Неизвестные grades9..35 выявляются явно; весь EFF
ещё не перенесён. Полный линк15символов. research/client455-effect-tables.md;
checkpoint PARTIAL; M6/M9OPEN.

Предыдущий участок M6 — normalshadow037: восстановлены BeginShadow/EndShadow
и теневые render targets. Реальная модель дала силуэт, прежние цветные кадры
совпали. Полный линк ещё20символов; обычный игровой shadow lifecycle открыт.
research/client455-normal-shadow.md; checkpoint PARTIAL; M6/M9OPEN.

Предыдущий участок M6 — normalcontracts036: восстановлены пять методов
reset/parent/eye/texturepath/bounds. Реальная модель после сброса и повторного
назначения анимации/перепривязки рисует прежние два кадра. Полный линк ещё22символа.
research/client455-normal-contracts.md; checkpoint PARTIAL; M6/M9OPEN.

Предыдущий участок M6: обычные CUnity → модели/ANI → поза → CRender → D3D9
отрисовали реальную модель. Два кадра через координаты и явную матрицу совпали;
проверены фильтры видимости, alpha/material и очистка ресурсов. Полный линк ещё
открыт: 27 методов/данных. research/client455-normal-renderer.md;
inventory/client455-normal-renderer-checkpoint.json (PARTIAL). M9 открыт.

Предыдущий участок M6: 180 клиентских исходных единиц перенесены на типы 455
в work/client455-port/normal. После выделения CUnity/CAnimation собираются 182
объекта x86/MT. Реальная загрузка ANI через обычные потребители проверена.
Полная линковка открыта: 39 методов/данных; CharacterMR не используется.
inventory/client455-normal-checkpoint.json; research/client455-normal-port.md.
M6/M9 остаются открытыми.

Предыдущий участок M6: реальный R3Engine перенесён на D3D9 в work/client455-port,
67units x86/MT собираются. Device/Platform01 прошли с Grass shader и source
Character owner на одном D3D9 device,8interiors/2weather layers проверены.
Normal180clientTUs/typed Character facade ещё не подключены; базовая сборка
work/client-build сохранена. Gate inventory/client455-engine9-checkpoint.json;
research/client455-engine9-port.md. M6/M9 остаются открытыми.

Предыдущий участок M6: source владелец Character455 — constructor/device binding/
destruction и typed model/draw contexts. Реальная модель с ANI/3textures прошла
через принадлежащие ему managers/pools/shaders отдельно и в полном client lab;
два кадра совпали, allocations/COM освобождены. Normal runtime прежний кроме
timestamps; совместный normal typed Character/D3D9 port ещё открыт. Gate
inventory/client455-renderer-owner-checkpoint.json; research/client455-renderer-owner.md.

Предыдущий участок M6: восстановленный расчёт плоскостей камеры иAABB подключён
к обычным SetCharacterClipping/CResObject::ProcessClipping. Численные/actor cases
и короткая Platform01 регрессия прошли. Normal Character API audit завершён:
ещё39функций старогоSDK. Следом совместный typed model/animation/Character owner/
D3D9 device port. Gate inventory/client455-frustum-checkpoint.json;
research/client455-normal-character-interface.md. M6/M9 остаются открытыми.

Предыдущий участок M6: основной Character draw/эффекты/прозрачность/batch/CPU/shadow
перенесены в source.16targeted сценариев и реальная модель с ANI/3textures прошли
отдельно и внутри client lab; два кадра совпали. Normal typed model/animation/
D3D9engine migration,visibility/CRT/undefined domains ещё открыты. M6/M9 не закрыты.
Gate inventory/client455-character-draw-checkpoint.json;research/client455-character-draw.md.

Предыдущий участок M6: восстановленные draw-state/program/material/palette/shared
submission рисуют реальный BELPHEGORHOLIDAY с ANI и3textures на D3D9 HAL.
46geometry parts/44skinned,2кадра совпали отдельно и в полном client lab.
Полный92E5F0/effects/transparent routing/normal D3D9 ещё открыты; M6/M9 не закрыты.
Gate inventory/client455-draw-checkpoint.json; research/client455-draw.md.

Предыдущий участок M6: source загрузка12штатных SHO, компиляция12VS/3PS и создание
двух Character declarations проверены на настоящем D3D9 HAL отдельно и в полном
client lab. Контрольный треугольник использует original shader; полный Character
draw и normal renderer ещё открыты. Подтверждённые различия old/455 layout требуют
совместного переноса consumers. Большие неизменённые наборы не повторялись.
M6/M6F/M7/M9 не закрыты. Подробности research/client455-shaders.md,
inventory/client455-shaders-checkpoint.json и docs/next-steps.md.

История предшествующих этапов (актуальная очередь выше):

Получена первая полная диагностическая сборка RF_Online.bin и успешная чистая
пересборка. Это старая база с выбранными подтверждёнными участками 455, а не готовый
клиент 455. Результат/границы: research/client-first-build.md.
M5 закрыт для первого выбранного участка: helper SPT455 и его interior/weather consumer.
140 файлов/97 543 записи проверены; две math функции совпадают с инструкциями455.
В own entry полного проекта настоящие LoadLevel/FrameMove/render/release прошли
на lobby и Platform01. На Platform01 загружены23helpers/8interiors; два погодных слоя
правильно меняют состояния внутри/снаружи и ночью/днём.13GPU cases/321checks прошли.
Основание и границы: research/client-m5-checkpoint.md, client455-graphics-runtime.md.
М6 в работе: clocks,packet8/5,CLand time и локальные time/real_time команды восстановлены.
1443clock+314map-time native checks/12FP modes;432command cases/2628checks и20actual
CHAT_INFO input/access/lifecycle checks прошли. Команды также управляют реальными
weather states на GPU. research/client455-time-commands-source.md. Затем восстановлены
8legacy Character functions,включая полный InitVertex:245binding+6732InitVertex checks/
144cases/12FP modes,4COFFtests,2actual LoadRealData→source calls в полном клиенте.
Это CPU comparison с test-only COM capture,не Character GPU acceptance.
research/character-init-source.md. Следом455MESH08/data/layouts перед D3D9 port:
найден отдельный loader для новых моделей. MESH08format module восстановлен:
858real files/12090meshes прошлиlossless roundtrip,6304native checks standalone/
full-client. Normal runtime model-loader ещё не переключён;следом materials/bones/
GPU state. research/client455-mesh08-format.md. Затем восстановлены четыре455CPU
parent/bone bindings:2237checks/12real mesh-skeleton pairs/393meshes standalone/
full-client. Normal loader не подключён; metadata/materials/sharedGPU ещё открыты.
research/client455-mesh-bindings-source.md. Остальные subsystems/chat/calendar/lighting открыты.
Далее sourceconstructor/header matrices/material request flow455 прошли14562checks/
12real files/393parts/12FP modes standalone/full-client. Матрицы используют именно
pinned D3DX9_36;actual TextureManager/sharedGPU/normal loader ещё открыты.
research/client455-mesh-runtime-source.md.
Нормальный WinMain ещё не запускался; D3D8 база ещё не восстановлена до D3D9 эталона.
M9 — полная приёмка455 без модернизации графики — остаётся открытым.

## Структура

- `docs/` — аудит, порядок работы, план следующих этапов.
- `config/` — пути и подготовленные примеры интеграций без секретов.
- `scripts/` — воспроизводимые проверки окружения и материалов.
- `inventory/` — манифест исходников, ключевых бинарников и сводка каталогов.
- `research/` — проверяемые выводы о функциях и форматах.
- `work/` — локальные копии бинарников, исходников и базы IDA; исключены из Git.
- `artifacts/` — большие выгрузки и результаты сборки; исключены из Git.
- `local/` — временные файлы и машинные настройки; исключены из Git.

Начать с `docs/environment-audit.md` и `docs/next-steps.md`.
Актуальная память: `docs/project-memory.md`; дорожная карта: `docs/roadmap.md`.
Критерии полноты клиента: `docs/client-acceptance.md`.
Аудит 14 проектов и первая сборка: `docs/build-audit.md`.
Повтор проверки входов сборки: `scripts/Invoke-Python.ps1 scripts/audit_build.py`.
Повторная инвентаризация: `scripts/Invoke-Python.ps1 scripts/inventory.py`.
Проверка GoMMO MCP: `scripts/Invoke-Python.ps1 scripts/probe_gommo.py`.
Проверка IDA MCP: `scripts/Invoke-Python.ps1 scripts/probe_ida_mcp.py --configured`.
Проверка VS/MSVC x86: `scripts/Invoke-Python.ps1 scripts/probe_msvc.py`.
Основная сборочная среда — VS 2026 Professional; VC6 не является обязательным этапом.
Настройка и использование IDA: `docs/ida-mcp.md`.
Universal Modder: 13 навыков и CLI um, см. `docs/universal-modder.md`.

Оригинальные каталоги перечислены в `config/paths.json`; скрипты аудита читают их,
но ничего в них не изменяют. Рабочие копии клиентского кода и движка подготовлены
в work/client-build с проверкой SHA-256; исходные байты и кодировки сохранены.
Начало переноса: research/client-port-first-build.md.
