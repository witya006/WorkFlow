# Частичная проверка 211 — вступительные ролики

Обычная оконная сборка Taiwan после Esc на логотипе и
после Esc на следующем ролике отрисовала экран входа.
Ручная приёмка старта включает отдельный пароль FireGuard
для подходящего аккаунта, меню «Войти», «Создатели», «Выход»
и сквозной туториал после создания нового персонажа. Эти
сценарии и полноэкранный режим роликов открыты. Принято 0/12.
[Доказательства](../research/client455-title-movies.md)

# Частичная проверка 210 — корректировка позиции

Дробные координаты дошли до аватара через штатный диспетчер.
Проверены движение, остановка, предыдущая позиция и шесть
неверных сообщений. Живая причина сброса координат и
переход по телепорту открыты. Принято 0/12 областей.
[Доказательства](../research/client455-move-correction.md)

# Частичная проверка 208 — HP локального аватара

Кадр удара обработал 70 000 урона. Серверное сообщение
обновило HP аватара и шкалу до 90 000 из 160 000.
Проверены два пакета неверной длины, нулевое HP и
сохранение HP персонажа при управлении машиной.
На NeutralB прошёл исходящий выстрел. Входящий урон
и обновление HP в живом бою открыты. Принято 0/12 областей.
[Доказательства](../research/client455-avatar-health.md)

# Частичная проверка 207 — обычные входящие атаки

Штатные обработчики приняли три формата входящей атаки и
отклонили шесть пакетов неправильной длины. Компонентно
подтверждены выбор клипа Wing, урон, специальный результат,
промах и сохранение состояния запроса игрока. Открыта
проверка входящих атак в живом бою. Принято 0/12 областей.
[Доказательства](../research/client455-creature-attacks.md)

# Частичная проверка 206 — изменение HP выжившей цели

Статус `PARTIAL_COMPONENT_ORDINARY_HEALTH`. В обычный диспетчер
переданы два результата по одному монстру.
Подтверждены промежуточный и последний кадры первого попадания,
второе попадание и итоговое HP 42%. В этом компонентном сценарии
оба серверных ответа поданы через штатный клиентский диспетчер.
В живом прогоне Wing погиб от первого выстрела на 31 урона.
Повторное попадание по выжившей цели открыто. Принято 0/12 областей.
[Доказательства](../research/client455-ordinary-health.md)

# Частичная проверка 205 — обычный бой и здоровье цели

Статус `PARTIAL_LIVE_MONSTER_DEATH`. При обычном входе на
NeutralB клиент получает HP и входит в боевой режим. За один вход
два выстрела нанесли по 22 урона. Оба попадания и гибель отображены,
а сервер подтвердил расход по одной стреле. Проверка охватывает
обычную атаку луком по целям, которые погибают от попадания.
Открыты атака по выжившей цели и остальные боевые сценарии. Принято 0/12.
[Доказательства](../research/client455-monster-target.md)

# Частичная проверка 204 — расход стрел и попадание

Статус `PARTIAL_LIVE_AMMUNITION_UPDATE`, `d8ad009f…` x86.
Один живой выстрел на NeutralB показал 22 урона и обновил
остаток с 313 до 312. Шкала HP цели осталась полной.
Повторный выстрел в одном сеансе и отдельный индикатор
боеприпаса с типом 16 открыты. Принято 0/12.
[Доказательства](../research/client455-ammunition-impact.md)

# Частичная проверка 203 — первый живой ответ обычной атаки

Статус `PARTIAL_LIVE_ORDINARY_ATTACK`, `083a7892…` x86.
На NeutralB штатные выбор, проверка стрел и подход привели
к отправке `5/1`. Один ответ `5/7` передал 22 урона в очередь
для разрешённой цели. Отрисовка попадания, обновление стрел
и повторные атаки открыты. Принято 0/12.
[Доказательства](../research/client455-primary-ammunition.md)

# Частичная проверка 202 — начальная загрузка предметов

Статус `PARTIAL_LIVE_INITIAL_ITEM_OWNERS`, `f27d2498…` x86.
В обычном входе на NeutralB размещены 8/8 предметов экипировки
и 21/21 запись инвентаря. Зафиксированы 315 экипированных
стрел. Проверка основного боеприпаса пока останавливает
обычную атаку. Действия с предметами и полный инвентарь
открыты. Принято 0/12.
[Доказательства](../research/client455-downloaded-items.md)

# Частичная проверка 201 — условия обычной атаки

Статус `PARTIAL_LIVE_AMMUNITION_UNAVAILABLE`, `f3a101bf…` x86.
В живом клиенте обычный выбор цели и клавиша атаки дошли до
проверки лука и боеприпасов без прежнего исключения. Отправка
атаки и живой урон открыты. Принято 0/12.
[Доказательства](../research/client455-armed-attack.md)

# Частичная проверка 200 — граница живой атаки

Статус `PARTIAL_LIVE_ATTACK_BLOCKED`, `c3c6df6b…` x86.
В собственном клиенте штатный клик выбирает Youngflem на NeutralB.
Окно цели и движение монстра видны. Сбой чтения экипировки
произошёл до отправки обычной атаки. Принято 0/12.
[Доказательства](../research/client455-live-combat.md)

# Актуальная частичная проверка 199 — 11.11.2026

Статус `PARTIAL_COMPONENT_MONSTER_CRITICAL`, `765fafe1…` x86.
Обычная очередь применила тряску и дополнительный свет. Проверены
два оригинальных клипа и подавление реакции контрольным флагом.
На NeutralB прошли вход и движение. Живой бой открыт. Принято 0/12.
[Доказательства](../research/client455-monster-critical.md)

# Историческая частичная проверка 198 — 11.11.2026

Статус `PARTIAL_COMPONENT_FORCE_DAMAGE_RENDER`, `8e3035b7…` x86.
Два числа урона показаны штатным рендером. Подтверждены затухание,
запуск трёх дорожек и звук Prism Beam. На NeutralB прошли вход и
движение. Живой бой открыт. Принято 0/12.
[Доказательства](../research/client455-force-damage-render.md)

# Историческая частичная проверка 197 — 11.11.2026

Статус `PARTIAL_COMPONENT_COMBAT_RESULT_RENDER`, `1e64dd9f…` x86.
Обычный графический код отрисовал `BLOCK` и `MISS`. Проверены
звук Miles, отсечение и затухание. На NeutralB прошли вход и движение.
Живой бой открыт. Принято 0/12.
[Доказательства](../research/client455-combat-result-effect.md)

# Историческая частичная проверка 196 — 11.11.2026

Статус `PARTIAL_COMPONENT_MONSTER_FORCE_IMPACT`, `643554e2…` x86.
Компонентно подтверждены два эффекта Силы с ключом штатной строки
и распределённым уроном. На NeutralB прошли вход и движение.
Живая отрисовка открыта. Принято 0/12.
[Доказательства](../research/client455-monster-force-impact.md)

# Историческая частичная проверка 195 — 11.11.2026

Статус `PARTIAL_COMPONENT_MONSTER_FORCE_REACTION`, `de40a4a1…` x86.
Обычная очередь эффектов монстра различает −2 и промах.
Компонентно сверены ключи и момент постановки в очередь.
На NeutralB прошли вход и движение. Живая отрисовка открыта. Принято 0/12.
[Доказательства](../research/client455-monster-force-reaction.md)

# Историческая частичная проверка 194 — 11.11.2026

Статус `PARTIAL_COMPONENT_MONSTER_HEALTH_FRACTION`, `b8bd9f67…` x86.
Два входа HP монстра, изменение по кадрам и лечение подтверждены
компонентно. В живом прогоне прошли вход и движение на NeutralB.
Живое обновление шкалы и события Силы открыты. Принято 0/12.
[Доказательства](../research/client455-monster-health.md)

# Историческая частичная проверка 193 — 11.11.2026

Статус `PARTIAL_COMPONENT_MONSTER_FORCE_DAMAGE`, `1d3df8ea…` x86.
Обработчик 5/9 поставил пять целей в очередь. Компонентно
подтверждено распределение 70 000 урона по двум кадрам.
Та же сборка прошла вход и движение на NeutralB. Живое применение,
доля HP и эффекты открыты. Принято 0/12.
[Доказательства](../research/client455-monster-force-damage.md)

# Историческая частичная проверка 192 — 11.11.2026

Статус `PARTIAL_COMPONENT_MONSTER_FORCE_RESULT`, `2672e567…` x86.
Команда 5/9 назначает Силу монстру и выбирает клип через обычный
диспетчер. Та же сборка прошла вход и движение на NeutralB.
Живое применение Силы, цели, урон и эффекты открыты. Принято 0/12.
[Доказательства](../research/client455-monster-force-result.md)

# Историческая частичная проверка 191 — 11.11.2026

Статус `PARTIAL_COMPONENT_MONSTER_FORCE_CLIPS`, `53eaff44…` x86.
Два штатных клипа Wing проверены на обычном методе монстра.
Та же сборка прошла живой вход на NeutralB. Живое применение Силы
и полная приёмка открыты. Принято 0/12.
[Доказательства](../research/client455-monster-force.md)

# Историческая частичная проверка 190 — 11.11.2026

Статус `PARTIAL_LIVE_MONSTER_STAND_FRAMES`, `a779670e…` x86.
Три кадра одного Youngflem подтверждают видимость и продвижение
клипа стояния в обычном клиенте. Сверка с 455 и ходьба открыты.
Принято 0/12. [Доказательства](../research/client455-monster-view.md)

# Историческая частичная проверка 189 — 11.11.2026

Статус `PARTIAL_LIVE_MONSTER_ANIMATION`, `f6816c3f…` x86.
Штатные клипы Wing возвращаются менеджером в живом клиенте.
Пробный прогон подтвердил продвижение клипа Youngflem. Полная
визуальная сверка открыта. Принято 0/12.
[Доказательства](../research/client455-monster-animation.md)

# Историческая частичная проверка 188 — 11.11.2026

Статус `PARTIAL_LIVE_TOWN_STATE`, `c8151a03…` x86.
На NeutralB аватар получил 4/34. Обычная городская атака
проверена компонентно. Модель монстра видна в финальном кадре.
Сопоставление анимации, живой городской отказ и полная приёмка открыты.
Принято 0/12. [Доказательства](../research/client455-town-state.md)

# Историческая частичная проверка 187 — 11.11.2026

Статус `PARTIAL_LIVE_WORLD_REFRESH`, `f16919a8…` x86.
На NeutralB применились 92 обновления отметок известных объектов.
Предметы на земле и припаркованные юниты проверены компонентно.
Полная приёмка мира и клиента открыта, принято 0/12.
[Доказательства](../research/client455-world-refresh.md)

# Историческая частичная проверка 186 — 11.11.2026

Статус `PARTIAL_LIVE_MONSTER_DATA`, `22421c33…` x86.
На NeutralB применены 17 созданий и 69 обновлений движения монстров.
Два кадра мира показывают аватар и местность. Подтверждение отрисовки
монстров и полная игровая приёмка открыты. Принято 0/12.
[Доказательства](../research/client455-monster-data.md)

# Историческая частичная проверка 184 — 11.11.2026

Статус `PASS_LIVE_RIGHT_DRAG_ELEVATION`, `dad137eb…` x86.
Камера достигает подтверждённого предела при тестовых отсчётах мыши,
на кадре видно небо. Положение камеры у аватара, физический ввод
и M9 открыты. Принято 0/12. [Доказательства](../research/client455-world-camera.md)

# Историческая частичная проверка 183 — 11.11.2026

Статус `PASS_LIVE_FORWARD_MOVEMENT_AND_SETTLING`, `253767b6…` x86.
Подтверждены движение и остановка на NeutralB при вводе в поток
клиента. Физический ввод, вращение камеры, ответ сервера и полное
поведение 455 остаются открытыми. Принято 0/12.
[Доказательства](../research/client455-world-walk.md)

# Историческая частичная проверка 182 — 11.11.2026

Статус `PASS_LIVE_TERRAIN_VISIBLE_WITH_PINNED_SKY_ASSETS`.
`c24a41d0…` x86. Аватар и местность видны после `3/2`.
Небо за пределами этих кадров. Управление, визуальная приёмка
мира и M9 открыты. Принято 0/12. [Сравнение](../research/client455-neutralb-sky.md)

# Историческая частичная проверка 181 — 11.11.2026

Статус `PASS_PASSIVE_OBSERVATION`, `c24a41d0…` x86. В двух кадрах
NeutralB после `3/2` виден аватар. Местность и небо остаются чёрными.
Управление, визуальная приёмка мира и M9 открыты. Принято 0/12.
[Доказательства](../research/client455-world-observation.md)

# Историческая частичная проверка 180 — 11.11.2026

Статус `PARTIAL_LIVE_WORLD_STARTED_MOVEMENT_OPEN`, `RF_Online.bin`
`b001f830…` x86. Аватар создан на NeutralB, первый проход отрисовки
завершён, ответ `3/2` принят. Прогон без фатального исключения. Камера,
движение, полные игровые системы и M9 открыты. Принято 0/12.
[Доказательства](../research/client455-avatar-world.md)

# Историческая частичная проверка 179 — 11.11.2026

Статус `PARTIAL_MAP_LOADED_AVATAR_EQUIPMENT_FAILURE`, `RF_Online.bin`
`16b78443…` x86. Получены позиции торговых NPC, загружена NeutralB.
При создании аватара возник `logic_error`, запрос `3/1` не отправлен.
Стартовая позиция, управляемый мир и M9 открыты. Принято 0/12.
[Доказательства](../research/client455-store-download.md)

# Историческая частичная проверка 178 — 11.11.2026

Статус `PARTIAL_WAITING_FOR_GUILD_AND_WORLD_INITIALIZATION`, `RF_Online.bin`
`35e531e1…` x86. Разобраны пустые макросы и объявления, получен `27/112`.
Исполнение макросов, окно объявлений, список гильдии, предметы, журнал,
игровой мир и M9 открыты. Принято 0/12.
[Доказательства](../research/client455-macro-download.md)

# Историческая частичная проверка 177 — 11.11.2026

Статус `PARTIAL_WAITING_FOR_MACRO_AND_LINKER_OWNERS`, `RF_Online.bin`
`168d1414…` x86. Применены настройки банков Linker, из двух занятых
слотов разрешено 0. Получены `3/50` и `13/105`. Их потребители, владельцы
слотов, вход в мир и M9 открыты. Принято 0/12.
[Доказательства](../research/client455-linker-download.md)

# Историческая частичная проверка 176 — 11.11.2026

Статус `PARTIAL_WAITING_FOR_LINKER_AND_ITEM_OWNERS`, `RF_Online.bin`
`cd3f1c0d…` x86. Применены основные показатели развития и найдены данные
семи заданий. В живом обмене получен `3/45` на 157 байт. Linker, журнал,
полное владение предметами и Силой, вход в мир и M9 открыты. Принято 0/12.
[Доказательства](../research/client455-mastery-quests.md)

# Историческая частичная проверка 175 — 11.11.2026

Статус `PARTIAL_WAITING_FOR_MASTERY_AND_ITEM_OWNERS`, `RF_Online.bin` `0280bf77…` x86.
Базовые поля применены, разобраны форматы 21 записи инвентаря и 82 записей
Силы. Получен ответ `3/8` на 322 байта. Размещение записей, обработка `3/8`,
реальный игровой мир и M9 открыты. Принято 0/12.
[Доказательства](../research/client455-initial-download.md)

# Историческая частичная проверка 174 — 11.11.2026

Статус `PARTIAL_WAITING_FOR_BASE_DECODER` для `RF_Online.bin` `c85bd40d…` x86.
Обычный клиент после выбора отправил `3/3` и получил `3/4` на 431 байт.
Компонентно проверены четыре кадра окон цели и счётчика подземелья.
Разбор ответа, инвентарь, реальный игровой мир и M9 открыты. Принято 0/12.
[Доказательства](../research/client455-target-windows.md)

# Историческая частичная проверка 173 — 11.11.2026

Статус `PARTIAL_KNOWN_FAILURE` для `RF_Online.bin` `59122c67…` x86.
После принятого выбора вернулся инициализатор окна группы 19.
Следующий сбой в окне выбранного монстра, собственный RVA `130a9f`.
Компонентно проверены два кадра и пять сообщений группы. Реальные
групповые операции, вход в мир и M9 открыты. Принято 0/12 полных областей.
[Доказательства](../research/client455-party-window.md)

# Историческая частичная проверка 172 — 11.11.2026

Статус `PARTIAL_KNOWN_FAILURE` для `RF_Online.bin` `917f69fb…` x86.
Обычный запуск после принятого выбора прошёл обмен валют, добычу,
смену класса и подключение Linker. Следующий сбой в строке окна группы,
RVA `13088f`. Компонентно проверены три кадра и восемь сообщений.
Реальные игровые операции и мир предстоят. Принято 0/12 полных областей.
[Доказательства](../research/client455-service-windows.md)

# Историческая частичная проверка 171 — 11.11.2026

Статус `PARTIAL_KNOWN_FAILURE` для `RF_Online.bin` `c9aeaf27…` x86.
Инициализаторы изготовления и улучшения вернулись после принятого выбора.
Следующий сбой в окне обмена валют, RVA `130fff`. На стенде проверены
вкладки и списки рецептов, ячейки улучшения, 14 сообщений и четыре кадра.
Реальные данные рецептов, игровые операции и вход в мир предстоят. Принято 0/12.
[Доказательства](../research/client455-item-work.md)

# Историческая частичная проверка 170 — 11.11.2026

Статус `PARTIAL_KNOWN_FAILURE` для `RF_Online.bin` `ad434f01…` x86.
Инициализаторы обмена и обработки руды вернулись после принятого выбора.
Следующий сбой в окне изготовления предметов, RVA `13066F`. На стенде
проверены сетки, три сообщения обмена, суммы и прокрутка результата руды.
Обычные сделки, переработка, полная фабрика и вход в мир предстоят. Принято 0/12.
[Доказательства](../research/client455-trade-ore.md)

# Историческая частичная проверка 169 — 11.11.2026

Статус `PARTIAL_KNOWN_FAILURE` для `RF_Online.bin` `7d348e69…` x86.
После принятого выбора вернулся инициализатор магазина NPC. Следующий сбой
в окне обмена между игроками на RVA `12FF6F`. Три кадра, 20 видимых ячеек,
навигация, контрольные списки и денежные поля проверены компонентно.
Реальные сделки, игровая фабрика и вход в мир открыты. Принято 0/12.
[Доказательства](../research/client455-shop-window.md)

# Историческая частичная проверка 168 — 11.11.2026

Статус `PARTIAL_KNOWN_FAILURE` для `RF_Online.bin` `83b60d77…` x86.
После принятого выбора пройдены инициализаторы навыков и Силы. Следующий
сбой в торговом окне на RVA `12F8BF`. Компонентно проверены вкладки и строки
из EDF. Автоматическое наполнение, игровые действия, полная фабрика и мир
открыты. Полных областей принято 0/12, M9 открыт.
[Проверка и её объём](../research/client455-skill-force-window.md)

# Историческая частичная проверка 167 — 11.11.2026

Статус `PARTIAL_KNOWN_FAILURE` для `RF_Online.bin` `23332d3f…` x86.
Обычная инициализация UnitTuning и UnitStorehouse пройдена после принятого
выбора персонажа. Следующий сбой в старом окне навыков на RVA `1305EF`.
Игровые действия обеих панелей, полный граф фабрики, мир и M9 остаются открыты.
Полных областей принято 0/12.
[Проверка и её объём](../research/client455-unit-windows.md)

# Историческая частичная проверка166 — 11.11.2026

Gate board-startup-checkpoint: PARTIAL_KNOWN_FAILURE, own fe40637c…/x86.
Обычный Linker startup5x10/window3 вернулся после принятого выбора;50 owners,
8 кадров и настоящий маршрут сообщения через менеджер проверены компонентно.
Следующий сбой — старый UnitTuning.Init/SetSprite, ownGetSpriteXL13028F.
Фабрика17 классов/37 отсутствующих, семантика17 также не принята. Прежний
счётчик53 исправлен на54 после подтверждения CBlackListBoard. Мир/M9 открыты,
0/12 полных областей; прежние требования не сокращены.
[Доказательства и все ограничения166](../research/client455-board-startup.md).

# Историческая частичная проверка165 — 11.11.2026

11.11.2026. Частичная165: подключены настоящие виды инвентаря, сумок20slots и
экипировки16slots. Native459bd43c:3расы/Taiwan/4просмотренных кадра,64bitmoney,
маски/состояния/reload и6маршрутов событий проходят. Final own96afbd62…/x86/
entry182C50/2364928bytes;182client/67engine/20kernels,build/link0.
Live выбор принят, обычный Inventory.Init вернулся. Следом срабатывает собственный
RF455_RejectRemovedLegacyBelt в старом Create_Board. Сумки/equipment Init в живом
пути пока не доказаны;мир не достигнут. Дальше настоящая455фабрика/порядок board
создания,не возврат удалённого старого storage. Potion/hotbar остаются в M9.
52fullfunctions/4375instructions обоих pins. Анализ2461(+42)/651(+45) из37871;
25новых выборочных partialbindings,24standalone,всего137в9реестрах. Это не
готовность. M6/M6F/M7/M9OPEN,0/12,ориентир25%(20–35%) прежний.
Staging32assets/16010369linkedbytes/0newpoolbytes. IDA18a8be40closed/list0,
nativejobsdone/privatehandoff removed,server/originals без изменений.
Gate inventory/client455-inventory-checkpoint.json:PARTIAL_KNOWN_FAILURE.
Доказательства/полный остаток:research/client455-inventory-views.md.

# Актуальная частичная проверка164 — 11.11.2026

11.11.2026. Частичная164: окно настроек455 подключено к обычному клиенту.
Три звуковых и шесть графических регуляторов, радио/переключатели, настоящие
skins/подписи/сообщения проверены; четыре GPU-кадра просмотрены. Исправлено
чтение неизвестного статуса при очистке hover без активного прицеливания;
начальное значение статуса не выдумывается. Точный chat script добавлен в стенд.
Own6b5e61e6…/x86/entry182C50/2364928bytes,182client/67engine/20kernels,
build/link0. Live002: выбор принят, весь обычный Create_UI включая чат вернулся;
следующий отказ — старый CGUIInventoryWindow при создании предметных панелей,
ownRVA12F78F/GetSpriteXL. Мир ещё не достигнут, полный UI455 не принят.
Gate inventory/client455-option-checkpoint.json: PARTIAL_KNOWN_FAILURE.
53полных функции/5879инструкций сверены по обоим pins. Усечённая CFG-выгрузка
заменена полной, verifier проверяет фактическое число блоков. Функции2419(+44)
адресных/606(+47) полных из37871;21новая выборочная partialbinding,112в8реестрах.
Это охват анализа, не готовность. M6/M6F/M7/M9OPEN,0/12,ориентир25%(20–35%).
Before165:165files/6858255private+4295738sharedbytes;клиент не клонировался.
IDA76ab68ba saved/closed/list0,nativejobsdone,privatehandoff removed.
Сервер и оригиналы не менялись. Доказательства: research/client455-options.md.

# Актуальная частичная проверка163 —11.11.2026

Gate client455-mob-control-checkpoint PARTIAL_KNOWN_FAILURE. Own ae592e21…:
настоящие MobControl455/16детей/3команды иshared movement. Native4GPUframes,
3actual HWND messages,signedHP/FP,EXP/resource/namepolicy иmovementreplay PASS.
Live выбор принят,MobControlInit вернулся;nextoldOption.SetSprite/Init fatal
own12ED3F/GetSpriteXL. Возврат промежуточных UIInit не закрывает их fullbehavior.
World/fullUI/fullAnimus/equipmentresourceproducer/tooltippolicy/lifecycle/edge
domains не приняты.0/12,25%(20–35%),M9OPEN. Функции2375/559 из37870 —охват
анализа,91bindingsвыборочны,не totalrestored. Полные требования ниже сохраняются.
[Доказательства163](../research/client455-mob-control.md).

# Историческая частичная проверка162 —11.11.2026

Gate client455-recall-checkpoint PARTIAL_KNOWN_FAILURE. Own e929b1ec… подключил
настоящее окно Recall455 и его строки;8контрольных records/5просмотренных GPU
кадров/HP-FP DWORD/EXP/cover/scroll/resize проходят. Live выбор принят, RecallInit
вернулся; следующий отказ oldMobControl.SetSprite/Init numeric sprite consumer,
own12E81F/GetSpriteOrgXL. Мир/полныйUI/полные Animus gameplay providers/settings/
cursor-link/lifecycle не приняты. Target uninitialized index/state и FPкрая
не объявлены эквивалентными own sentinel/bounded checks.0/12,25%(20–35%),M9OPEN.
2347/529 из37870 — охват анализа,69bindings выборочны,не totalrestored.
Пять новых IDAheads уточняют индекс;inputEXE bytes не менялись. Полные требования
ниже сохраняются. [Доказательства162](../research/client455-recall.md).

# Историческая частичная проверка161 —11.11.2026

Gate client455-char-info-checkpoint PARTIAL_KNOWN_FAILURE. Own 3ebd9a7d…
подключил настоящее CharInfo455:3pages/23value owners/real skins/race/layout.
Native3races/6GPUframes/input/resize/mastery/resist PASS. Live1/14→1/15/22/result0,
CharInfoInit пройден;следующий oldRecall.SetSprite/Init fatalown12E8FF/GetSpriteXL.
World/control/fullUI/M9 не приняты.0/12,25%(20–35%). Открыты dynamic action/
equipment providers,mastery max/resist bounds уlegacycallers,metrics/lifecycle/
malformeddomains. Полные требования ниже сохраняются;счёт2310/490 —охватанализа.

# Историческая частичная проверка158 —11.11.2026

Gate selection-checkpoint PARTIAL_KNOWN_FAILURE,owndf69c7ef…/entry17FCD0.
Реальный Enter/выбор1/14→1/15/22/result0 иtyped Avatar default/worn transfer
достигли существующегоMainGame::Create_UI. Послеэтого естьunhandledC0000005
GetSpriteXL/GaugeExp legacy skin. Мир/полныйselectionstage ещёнеприняты.
Nativewire/4wallet/defaultretained/PRNG и3priorPNG PASS. Полные требованияниже
сохраняются;M6/M6F/M7/M9OPEN,0/12. Счёт2231/403 —охватанализа,неготовность.

# Историческая частичная проверка157 —11.11.2026

Gate actor-lighting-checkpoint,own88dc3d11…/x86/entry17F850. Actual map actor
light/material restored:12real lobbycases/gear/GPU PASS,3priorPNG unchanged.
Live auth/character frame370/8000ms/unhandled0,Renderreturned. Сравнение просмотрено:
персонаж больше не почти чёрный. Это не полная эквивалентность455UI/selection.
Ввод выбора/переход в мир не проверены;known FP/undefined/clone/particle/lifecycle
и все полные требования ниже сохраняются. M6/M6F/M7/M9OPEN,0/12.

# Историческая частичная проверка156 —10.11.2026

Gate inventory/client455-combat-transition-checkpoint.json,own68e02c3d….
Живой вход/список/кадрвыбора проходят,364frames/8000ms,unhandled0.
Пользователь увиделанимацию;персонажпочтичёрный. Переходоружия/щита,
typedLogin accesses иeffects startup исправлены. FullUI/освещение/выбор/
enterworld/gameplayнеприняты.25%(20–35%),0/12,M6/M6F/M7/M9OPEN.
Нижеисторическиезаписи;все полные требованиясохраняются.

# Историческая частичная проверка155 —10.11.2026

Gate inventory/client455-live-login-checkpoint.json,own da42b501….
Реальные launcher-auth/game-entry приняты сервером0.4.0. Compact1/9(178)
иtyped upgrade исправлены;fragmented receiver/границы/onlyBYTE113 проходят.
OrdinaryTaiwan Login и3assembledPNG PASS. Живой equipped selection ещёпадает
вSetAction→legacyGetEquipItem;мир не достигнут. Ниоднаполнаяобласть не закрыта.
Оценка25%(20–35%),M6/M6F/M7/M9OPEN. Все требованияниже сохраняются.
Данные154 иниже исторические;не смешиватьсвежийобычныйLogin сживымпадением.

# Историческая частичная проверка154 —10.11.2026

Gate inventory/client455-player-owner-checkpoint.json,own31d24ab9….
Primary12-slot owner/frame/render,Avatar default garment/SFcallback иcloak
проверены в собственном входе среальными ресурсами иcontrolledcamera/light.
Taiwan Create/Login/account3Avatar PASS;полные appearance/selection/world/gameplay
ещё не приняты. FullCharacter clone lifecycleOPEN:cleanupадаптациитольковprobe.
User-started0.4.0:ownTCP27830прошёл;launcher-auth27831accepted/key16.
Это не game-auth своейPE инеполнаяэквивалентностьGoMMO/pinned455.
Оценка25%(20–35%),0/12полныхобластей,M6/M6F/M7/M9OPEN.
Все требования полноты ниже сохраняются. Следующие записи исторические.

# Текущее состояние приёмки —10.11.2026

Полностью принятых областей0/12. M6/M6F/M7/M9 OPEN.
Оценка25%(20–35%) является плановой,не измеренным соответствиемэталону.
Последний проверенный partialgate153:inventory/client455-equipment-frame-checkpoint.json,
own3296a413….32модели/33текстуры/6базовыхслотов не закрываютполный
внешнийвид,выбор,авторизациюилиигровоймир. ОбычныйLogin показываетожидание.
[Точные опоры, остаток, исходные данные](progress-report.md).

147:настоящий cache20×30/13dummy, затронутые Avatar/registered/Create/Login
проверены. Полные constructor/lifecycle/renderer/equipment/selection ещё открыты.
149: Render(default/matrix), fade/alpha, metadata152→overlay604 и очередь
сохранённых поз/владельцев проверены на реальной модели. Вторичная геометрия
теперь удержана обычной PE; подтверждены обычные queue entrypoints.
Обычный CPlayerProc ещё не использует полный12-slot controller. Ненулевые
частицы экипировки не проверены; общий particle registry остаётся старым.
Полный mesh-object renderer/appearance/selection открыт.
150: исправлен прежний вывод13слотов — полные ctor/dtor создают12.
Index12 — доступ за массив, его собственный отказ не принимается как
поведение эталона. Visibility guard и PRNG ctor/copy проверены отдельно.
Доказательства:research/client455-player-visual.md;общая оценка неизменна.

151: ordinary network PremiumDWORD и Avatar benefit/bonus producers из57/12
подключены и проверены. Полные Premium window/icon481,condition/UI refresh
иостальнойCashShop не приняты. Полный ordinaryplayer по-прежнему открыт.

152:ordinary stat writers14..18 перенесены с fullDWORD/float аргументами.
Три basic rows подключены к value owners;настоящий текущий Avatar caller
прошёл. Полный455metric/refresh/layout и весьперсонаж ещё не приняты.

153:объекты экипировки получили FrameMove/Animation/концы ANI/живую привязку
magic и правильные координаты звука. Default6owners Avatar теперьCEquip;
полныйCPlayerProc ещё не подключён. Реальные ANI/Spine/Miles,обычныеCreate/
Login/account3Avatar ишесть прежнихrender кадров прошли. Все открытые требования
к полному персонажу,выбору,миру,particle registry иM9 сохраняются.

Все требования полноты ниже сохраняются. Исторические gates подтверждают только
свой участок/свою сборку и не являются свежей проверкой всего текущего клиента.

# Полнота восстановления RF_Online.bin

Текущий частичный gate142: inventory/client455-item-bootstrap-checkpoint.json.
Штатный Login подключён к cash→set→Item47+ND.6real locale/selector cases,
76049raw rows/names/descriptions/work directory и12actual typed wrappers каждый PASS.
Это вызов настоящего ItemDataMgr вfull-object probe;обычный Login success-response
bootstrap ещё не пройден. Legacy ITEM_DATA/derived items/Avatar equipment OPEN.
GetData455 accessor удержан probe,не ordinary gameplay. research/client455-item-bootstrap.md.
Штатный Resource.edf загружает9 групп и регистрирует1267/10483/18872 bone/mesh/ANI.
Пять реальных player skeletons и одна ANI из RFS загружены. Единственный mesh skip
объясняется отсутствующим parent ID20483/NPC в исходном каталоге.
Полный bootstrap и selection всё ещё открыты;research/client455-resource-catalog.md.
Request58/reply12 world-entry перенесены;валидные/короткие/fragmented encrypted
ответы проверены через обычные buffers/dispatcher. Ordinary TCP отправка67bytes
наблюдалась;auth/bootstrap/selection не приняты. research/client455-world-entry.md.
Дополнительно перенесены запрос1/8 и ответ1/9 списка:506/164,3 настоящих Avatar,
имена/уровни/64-битные деньги и время/tutorial writer. Полные классы/внешний вид,
bootstrap и обычный экран выбора не приняты. research/client455-registered-characters.md.
Account140 проверялся на своей PE;его снимок before141 сохранён,на новой PE suite
не повторялся. Обычный WinMain→Title→Login собственной f0114c80… показывает реальную lobby;
лишние панели больше не открываются одновременно после переноса root Add455.
Ввод/авторизация/выбор персонажа/мир и полная455UI не приняты.
Исследование и оставшийся стык response→bootstrap→selection: research/client455-login.md.

На2026-11-10 введена отдельная **плановая** оценка:около25%,диапазон20–35%,
по12взвешенным функциональным системам. Это не доказанное покрытие455.
Полных принятых систем0/12;сквозной Login→selection→world→gameplay не принят.
Опорные данные:inventory/client455-progress-assessment.json и актуальная
очередь A–E вdocs/roadmap.md. Требования100%функционала/M9 не уменьшены.

M6 — частично: восстановлены пять ресурсов кадра и их освобождение.
Собственная сборка RF_Online.bin:42213f08…;свежий existingCreate1 проходит.
Проверены восемь конфигураций ресурсов,два захвата кадра и прежний эффект.
Общие игровые ресурсы повторных проверок теперь используются через shared pool.
Текущая проверка: inventory/client455-scene-capture-checkpoint.json.
Следующий функциональный рубеж — обычные Title/Login455.
Полная приёмка M6/M6F/M7/M9 остаётся открытой.
[Доказательства137](../research/client455-scene-capture.md).

Ниже сохранена история предыдущих этапов; текущий gate указан выше.

112 PARTIAL_COMPONENT: подтверждён настоящий вход начала прицела — client
Nuclear processor,group60/opcode0/result0,а не input callback.45body ranges/
22fullasm/903instructions совпали между двумя455;ctor/vtable/RTTI подтверждены.
Восстановлен C++decoder всех9 payload layouts:2429 коротких native assertions
PASS,включая packed14/count0..255/short/null/float bits. Это отдельный source
component,ordinary receiver ещё не подключён. Runtime111/PE031df367…/engine
неизменены,его suites не повторены. Guard использует action category5 и internal
Character DWORD640&3,а не status17708/serverflags;нужны реальные writers/UI.
Следующая113 — actual network receiver+guard/selection/dialog/record owners.
Component112 historical; runtime gate114 current (см. начало). M6/M6F/M7/M9 OPEN.
[Доказательства112](../research/client455-nuclear-protocol.md).

Исторический runtime результат111:

111 PARTIAL: обычный formatter подключён к actual Login и четырём панелям
чата/центру экрана. Обычный typed hover у настоящего Avatar с pending1 теперь
отменяет реальный прицел/звук,обнуляет координаты и выводит C1A до item mutation.
83 целевые проверки с реальным EDF предметом/BSP/6effects/Miles проходят.
Новая PE031df367…/entry161590/182client-20kernel-64facade/unresolved0/Create1.
Свежие center69/status62 и15 просмотренных GPU кадров;10 center/hover побайтно
равны109. InsertText455 теперь удержан обычной PE. CE7 core проверен вlab,
но его game-action registration ещё нет и helper удалён ordinary linker.
Gate111 historical после113,109 historical. Tutorial только routing kernel;полные stages/
Login/auth/chat UI и прочие client-acceptance gaps открыты. Далее113 — actual network receiver/guard для начала прицеливания. M6/M6F/M7/M9 OPEN.
[Доказательства111](../research/client455-message-runtime.md).

Историческое исследование110:

Исследование110: общий dispatch и настоящие C1A/CE7/Login цепочки подтверждены
на двух455:22 функции/22fullasm/1254instructions,22bodies+46-byte EH region,
23 decoded calls и RTTI CGP_LogIn. Login пишет256-byte сообщение и рисует его
внизу экрана; Tutorial2 имеет отдельный counter и фиксирует style2/category3.
При отмене C1A идёт после Clear эффекта/звука,до hover mutation. При начале CE7
идёт после request-state clear,до SetPending;повторное начало снова пишет CE7.
Важно:legacy MainGame2→target3 через существующий bridge,не Tutorial2.
Это AUDIT_OPEN:обычный source/runtime ещё не изменён. На момент110 gate109 оставался текущим.
Далее111 — перенести подтверждённую цепочку с actual Login/chat/center и live
hover/effect/Miles,а не повторять аудит. M6/M6F/M7/M9 OPEN.
[Доказательства110](../research/client455-message-dispatch.md).

109 PARTIAL: восстановлены профиль36 стилей и вставка в четыре настоящие панели
чата:14 категорий, настройки, фильтры и перенос строк.385 целевых проверок,
8 реальных файлов/288 записей и5 просмотренных кадров чата проходят.
Сохранены особенности455: fallback13, byte-lexer Taiwan и signed settings masks.
Профиль/init подключены к обычному MainGame; новый InsertText455 пока вызывается
только full-object lab, игровые legacy callers ещё не перенесены.
Свежие center69/6hover/Create1 проходят;10 кадров побайтно равны108.
PE ef33b250…/entry160400/182-20-63/unresolved0. Gate109 historical,108 historical.
Общий C1A/CE7 dispatch, live pending1 hover и полный chat UI открыты.
M6/M6F/M7/M9 OPEN; дальнейший участок111 — перенос общих сообщений и отмены прицела.
[Доказательства109](../research/client455-chat.md).

Исторический108:

108 PARTIAL: в настоящем CGP_MainGame восстановлен владелец экранных сообщений:
queue64/active84/max3,59-byte CRT split,pacing500ms,fade3600ms и medium GDI16.
69 проверок и4 просмотренных GPU кадра реальных C1A/CE7 проходят;после fade кадр
пуст. Это прямой Add в actual stage member,не полный C1A/chat dispatch.
Прицел перенесён из early effects update в late Render после UI;порядок
подтверждён вызовами в собственной PE. BSP/Miles29/status62/6hover/Create1
проходят;hover побайтно равен107. PE5ad0b484…/entry15b6d0/182-20-61/unresolved0.
Gate108 historical,107 historical. Full chat/C1A/live pending1 hover,полный teardown
этапа и другие client-acceptance gaps открыты. M6/M6F/M7/M9 OPEN.
[Доказательства](../research/client455-system-messages.md).

Исторический107:

107 PARTIAL: в CMainApp восстановлен core прицеливания20: pending, отдельная
командная позиция, курсор через настоящий BSP, перемещение6 частей эффекта и
tagged Miles Radar.29 реальных проверок проходят; память785169→785169.
Pending0 разрешает hover при соответствующем статусе; pending1 пока отказывает
до мутации из-за отсутствующего C1A message provider. Игровых command producers
ещё нет; SetPending проверен в full-object lab, но удалён из обычной PE linker.
Новая PEd09eec8d…/entry15adc0/182-20-60/unresolved0/Create1. Status62/magic36/
resources66/audio157/runtime573/account/hotbar7/storage3 проходят;10 GPU frames
просмотрены,6 hover побайтно равны106. Gate107 historical,106 historical.
Full nuclear/world/message/device/client acceptance ещё открыты. M6/M6F/M7/M9 OPEN.
[Доказательства](../research/client455-nuclear-aiming.md).

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
[Доказательства](../research/client455-effect-runtime.md).

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
[Доказательства](../research/client455-effect-resources.md).

Исторический104:

104 PARTIAL: восстановлены формат эффекта на 64 дорожки, parser и временная
выборка CProcessMagic, EffectInfo56 и runtime456. Обычный кэш читает настоящий
скрипт ядерного прицела из RPK: все шесть дорожек проверены побайтно.
36 целевых проверок проходят; status58/audio157/account/hotbar7/storage3 сохранены.
Новая PE0419f2c0…/entry15a1f0: 182 client / 20 kernel / 59 facade, unresolved 0,
прежний Create→1. Шесть просмотренных hover кадров побайтно равны103.
Текущий gate: inventory/client455-magic-checkpoint.json; gate103 исторический.
Полная отрисовка эффекта и отмена прицеливания ещё открыты. M6/M6F/M7/M9 OPEN.
[Доказательства](../research/client455-magic.md).

Приняты выбранные layout/parser/cache контракты. Full effect rendering и nuclear
owner ещё не приняты; общий список gaps сохранён. Исторический103:

103 PARTIAL: восстановлена звуковая зависимость ядерного прицеливания —
tagged3D audio с настоящим Miles,30 каналами и кэшем64 записей. CMainApp
открывает provider/listener в обычном Create; точная новая PE проходит Create→1.
157 проверок реального WAV/меток/остановки/LRU проходят. Статус58, account,
hotbar7/storage3 сохранены;6 просмотренных кадров hover побайтно равны102.
Новая PEcf7ac5e0…/entry159670,182client/20kernels/58facade,0unresolved.
Gate: inventory/client455-tagged-audio-checkpoint.json;102 теперь исторический.
Сам эффект и отмена ядерного прицеливания ещё не подключены. M6/M6F/M7/M9 OPEN.
[Доказательства](../research/client455-tagged-audio.md).

Принята выбранная аудиозависимость, не полное прицеливание/звук/клиент.
Общий список gaps сохранён. Исторический102:

102 PARTIAL: восстановлены поле статуса персонажа, его вычисление из64-битных
флагов и условие отмены перетаскивания. Настоящий обычный Avatar теперь может
брать, отпускать и возвращать предмет. Прошли58 CPU проверок;6 просмотренных
GPU кадров побайтно совпали с101. Отмена ядерного прицеливания ещё не перенесена:
эта ветка явно отказывает до изменения предмета на курсоре.
Новая PE:5f1f0f77…, entry1587b0;182 клиентских/20 kernel/57 facade модулей,
0 неразрешённых символов; прежний Create вернул1. Account, hotbar7 и storage3
проходят. Текущий gate: inventory/client455-player-status-checkpoint.json.
Gate101 теперь исторический. M6/M6F/M7/M9 остаются открытыми.
[Доказательства](../research/client455-player-status.md).

Приняты проверенные статусы и перетаскивание обычным Avatar. Ядерный владелец,
остальные эффекты статуса и сетевые получатели остаются открытыми. Прежние gaps
сохраняются.

Исторический101 (егоnull-avatar ограничениерасширено102):

101 PARTIAL: в обычном клиенте восстановлены Copy620, предмет на курсоре,
два backup object и screen icon handoff. Проверены замена/очистка/возврат
в actual Linker, timer Update и освобождение ссылок. Пять payload kinds,
bare wrapper,256 board IDs и6 новых просмотренных GPU кадров проходят;
32 прежних кадра побайтно сохранены. Quest sentence provider ещё отказывает.
Новая PEe77ec7e7…/entry1586b0/182client-20kernels-57facade/0unresolved/Create1.
Текущий gate — inventory/client455-board-hover-checkpoint.json;100 runtime
исторический. Live Avatar cancel,полная operation queue и игровые handlers
ещё не восстановлены. M6/M6F/M7/M9 открыты.
[Доказательства](../research/client455-board-hover.md).

Принят только указанный offline/null-avatar домен. Nonphysical CPU icons
synthetic;Quest names,liveAvatarcancel,fulloperationqueue/three-layer tooltips,
прочиеboardAdd/mixednetworkcallers иfullgame остаютсяOPEN. Это sourceGPU,
не captureоригинальногоEXE. Исторический результат100:

100 PARTIAL: восстановлен значок блокировки предмета по flag21 в обычных
CGUIItem/CBoardObject/CLinkBoard. Реальный sprite52 содержит glyph8×12 на
texture8×16. Проверены копирование, позиция, Empty/Remove и отдельный Draw
при обрезке изображения.256 значений BYTE setter,256 wrapper flags,18 geometry
cases и6 новых просмотренных GPU кадров проходят;35 прежних кадров byte-equal.
Новая PE49882fc3…/entry157aa0/182client-20kernels-56facade/0unresolved/Create1.
Исторический gate — inventory/client455-item-lock-checkpoint.json;099 runtime
исторический. Full drag/use/remove/swap/hover/MsgProc,live callbacks,potion cache,
Macro/Vending/fullAdd/bootstrap ещё обязательны. M6/M6F/M7/M9 открыты.
[Доказательства](../research/client455-item-lock.md).

Lock child принят только в описанном домене. Invalid sprite descriptors,
полный privateABI/fullGUI/lifecycle/reset/unsafe/OOM/concurrency/shutdown
не приняты. Native source GPU не является reference executable capture.
M6/M6F/M7/M9 OPEN. Исторический результат099:

099 PARTIAL: обычный CLinkBoard получил50 записей перезарядки, поиск исходного
владельца, запуск таймеров и вспышку готовности. Ready child использует настоящий
лист455,40 клеток128px,34FPS и blend3.132 сценария анимации/48 сетки и6 новых
GPU кадров проходят;20 прежних просмотренных кадров побайтно сохранены.
Новая PE6b30676b…/entry157830/182client-20kernels-56facade/0unresolved/Create1.
Исторический gate: inventory/client455-ready-cooldown-checkpoint.json;098 runtime
исторический. Игровые use/remove/swap/hover,live callbacks,lock,potion cache,
Macro/Vending/fullAdd/bootstrap ещё обязательны. M6/M6F/M7/M9 открыты.
[Доказательства](../research/client455-ready-cooldown.md).

Это source-owned CPU/GPU evidence,не capture оригинального455. Глобальные
исходные packs вlab размещены явно;это не normal bootstrap/fullCItemBoard.Add.
SFgroup uses synthetic CPUicons,actualsourcepayloads. Fullgenericanimation
clippedDraw/otherblend/privateABI/FPunsafe/OOM/reset/shutdown ещёOPEN.

Исторический результат098:

098 PARTIAL: actualtyped CGUIItem timer455 state/update/copy/conditionalempty,
registry start-stop fanout,радиальныйDraw/wholeclip/контекстная подпись и typed
Linkerquery подключены.175state/112label/57rays/171triangles,29viewedGPU,
window/owners/metadata/icon/hotbar/storage/account/newPE/Create1 pass.
Grade draw order исправлен:11из23 прежних кадров изменились,12 byte-equal.
Это sourceGPU,не reference capture. Target CPU-selected SSEtan/FPexceptions/
unsafe numeric/privateABI,прочие GUIItemchildren/shake/fullcopy-empty/lifecycle,
cooldowncache/actualhandlers/livecallbacks/lock/Macro/Vending/fullAdd/bootstrap
и все прежние клиентские gaps обязательны. Stopfanout normalPE пока unused.
Gate098 runtimehistorical после099;M6/M6F/M7/M9 OPEN.
[Доказательства](../research/client455-gui-timer.md).

Исторический результат097:

097 PARTIAL:ordinary CLinkBoard использует новый actualbanked window hierarchy,
Init/Draw/layout/scale/bankcontrols/MouseEvent/PostMessage и bitmap numbers.
21layout/1050icons/320cycle/48events/1792glyphcases/GUI observerqueue/8viewedGPU
проходят.50actualclones/16realoriginals,096owners/094metadata(6byte-equalframes),
hotbar/storage/account/newPE/Create1 pass. Пять кадров окна и три glyph frames
не являются reference capture или whole-game acceptance. Use callback native
recording;actual use/remove/swap/hover handlers/typedtimer/cooldown/livecallbacks/
lock/Macro/Vending/fullAdd/bootstrap/Tutorial/Login/auth/game и прежние gaps
обязательны. Negative50C signed-byte behavior сохранён поasm;unsafe domain не
принят. Gate097 current,096 runtimehistorical;M6/M6F/M7/M9 OPEN.
[Доказательства](../research/client455-linker-window.md).

Исторический результат096:

096 PARTIAL: actual CLinkBoard Add/Remove/Clear создаёт/удаляет typed clones,
banked icons и registry links;50 реальных владельцев/3 просмотренных GPU,
original-owner release/last-owner cleanup/Dmalloc и точная PE/Create1 проходят.
Register/unregister теперь retained в ordinaryPE.095registry/094metadata
повторены,6 raw кадров byte-equal;hotbar/storage/account проходят. Новые icons
живут в actualwindow member;fullCGUILinkWindow layout/scale/input ещё не включён
вместо legacy8slot draw. SF/Animus CPU icons synthetic,live callbacks/lock/potion
cooldown явноrefused;fullcopy/empty/shutdown/privateABI/typedmixedcallers/Macro/
Vending/fullCItemBoard.Add/bootstrap/Tutorial/Login/auth/game и прежние gaps
обязательны. Gate096 current,095 runtimehistorical;M6/M6F/M7/M9 OPEN.
[Доказательства](../research/client455-linker-owners.md).

Исторический результат095:

095 PARTIAL: source-owned registry в actualMainApp группирует зарегистрированные
иконки по type/itemID/index;typed SetNum/SetUsable/find включены в ordinaryPE.
160 key cases, duplicates/first-remove/current-key/emptybucket,WORD/rawBYTE,
3 просмотренных GPU и точная новая PE/Create1 проходят.094 metadata повторён,
3 кадра byte-equal,hotbar/storage/account проходят. Probe регистрирует реальные
copies явно; ordinaryLinker/Macro Add-Remove всё ещё не подключены, registration
в обычной PE unused. Unsafe erase(end()) target заменён явным отказом и учтён
как разрыв. FullCItemBoard.Add/Vending27/normalbootstrap/полные owners/UI/Tutorial/
Login/auth/game и все прежние gaps обязательны. Gate095 текущий,094 runtime
исторический;M6/M6F/M7/M9 OPEN.
[Доказательства](../research/client455-icon-links.md).

Исторический результат094:

094 PARTIAL: physical metadata читает реальные owner tables,inventory20 core
включён в ordinary TakeInItem. Actual CGUIInventoryBoard принимает source-owned
payload wrapper,выставляет индекс/grade/quantity/usable и рисует16 реальных
предметов.566 metadata/520 race-level/9 Quest+SF refusal/3 просмотренных GPU,
clone/clear/last-owner/Dmalloc и новая PE/Create1 проходят. Basic reader/handoff
пока не вызывается полным CItemBoard.Add и удаляется normal linker как unused;
own-entry тест использует production facade. Полный event flow/notifications/
cooldowns/sharedfollowers/Linker6/Macro35/Vending27/SF/Quest/остальные boards/
bootstrap/Tutorial/Login/auth/game и прежние gaps обязательны. Gate094 текущий,
093 runtimehistorical;M6/M6F/M7/M9 OPEN.
[Доказательства](../research/client455-item-icon-metadata.md).

Исторический результат093:

093 PARTIAL: обычный typedCGUIItem.SetSprite выбирает target8/19 и страницу/
ячейку через реальные Item/UnitParts/Default callbacks.880 oracle cases incl
signedwidth/WORDrowwrap/partialwrites/fallback,4 просмотренных GPU кадра и9
byte-equal кадров092 проходят. Owners2013/data575/SF1447/hotbar/storage/account
и новая PE/Create1 проходят. GPU sample ID заданы явно: actual payload→icon
metadata/игровые окна ещё не подключены. Полные GUIItem children, targetUnit57
lifecycle, mixed consumers, normalbootstrap, inventory/hover/Linker/Tutorial/
Login/auth/gameplay и все прежние gaps обязательны. Gate093 текущий,092 runtime
historical; M6/M6F/M7/M9 OPEN. Это движение внутриM6, не полнота всего клиента.
[Доказательства](../research/client455-item-atlas.md).

Исторический результат092:

092 PARTIAL: typed CBoardObject передаёт индекс и цвет рамки CGUIItem; выбранный
core Draw рисует настоящие inventory/item.spr455. Уточнено: GUIItem1240 — рамка,
не caption.256 grade/120 quantity boundaries/8 widths/9 просмотренных GPU кадров
и Dmalloc reload проходят. Владельцы2013/data575/SF1447/hotbar/storage/account
и точная новая PE/Create1 проходят. Автоматический itemID→atlas ещё открыт:
GPU тест передаёт явную SPRITE_INFO. Полные GUIItem timers/overlays/shake/copy,
base virtual SetSize, mixed payload consumers, normal bootstrap, Linker5x10/
hover/input/use/cooldowns/download и все игровые разрывы остаются обязательными.
Gate092 текущий;091 runtimegate исторический. M6/M6F/M7/M9 OPEN. Общая доля
восстановления не измерена; локальные проверки не задают процент всего клиента.
[Доказательства](../research/client455-item-icon.md).

Исторический результат091:

091 PARTIAL: обычные CItemObject592/CBoardObject620 теперь используют реальные
общие payload/data owners и менеджер CMainApp.2013 bind/clone/pack-removal
сценариев, два whole620byte oracle, signed BYTE/retired-primary-empty guard и
новые hotbar keys прошли. Прежние data575/SF1447 проверены на production
providers, без второго архива. Hotbar/storage/account и новая PE/Create1 прошли.
Это проверка ядра владения без иконок: typed icon/caption и mixed-derived binding
явно отказывают;9 Quest name случаев требуют sentence provider. loadFiles
реально читает EDF, но ещё не вызван обычным bootstrap. Full inventory/hover/
Linker UI/input/download/gameplay не приняты. Legacy Clear теперь вызывает
новую базу и снимает icon; старые mixed Create/consumers надо мигрировать.
Gate091 текущий;090 runtimegate исторический. M6/M6F/M7/M9 OPEN.
[Доказательства](../research/client455-item-object.md).

090 PARTIAL: actualordinary CObject80/CResObject584 ctor/copy/name64/virtual
Clear/flags/effectID lifecycle восстановлены. Два whole-record oracle/28offsets/
160flags (20retain/140clear/48receiptreset),hotbar/storage/account/actorFX/
3worlds и exactnewPE/Create1 прошли.15GPUframes просмотрены;089payload575/SF1447
обновлены на новом link/dependencyset. Live magiccache не загружен commonprobe;
весьFX/privateABI/resourceRenderName metrics/reset/unwind не принят.
Обычные CItemObject/CBoardObject620/board-hover/Linkerowners ещёнеперенесены.
Предварительное обещание090 закрыть этих владельцев перенесено в091 после
подтверждения обязательного общего layout/lifecycle разрыва48/472→80/584.
Gate090 текущий;086/088/089 runtimegates исторические после сменыlink/reports,
staticreferences действуют. M6/M6F/M7/M9OPEN;все прежние gaps обязательны.
[Доказательства](../research/client455-resource-object.md).

089 PARTIAL_SOURCE_RUNTIME: реальные Item47/Quest12/Character7 readers и пять
freshpayloadfactories работают с concreteprimarymanager/087clone-release.
Полные bytes76049 itemrows/3NDItemprofiles,575selectedfactories/ownedwrappers,
99AnimusXP boundaries прошли standalone/full-object. SF1447regression проходит
с той же новой библиотекой. Это не ordinarygame binding/полные gameplayметоды.
Questname требует sentenceprovider и явноthrows;NDQuest/полный Character,
reload/duplicateowner/OOM/unsafe/privateABI и все прежние gaps остаются.
Production086/gate current;088runtimegate исторический по sourcehashes,
static088reference сохранён. GPU/startup/159k suites не повторялись.
M6/M6F/M7/M9OPEN;реестр неполный,общий процент не вычислен.
[Доказательства](../research/client455-item-payloads.md).

088 PARTIAL_SOURCE_RUNTIME: concreteSF factory selector1/5data tables/primary
manager связаны с087wrapperclone/release.1447realpayloads/wrappers/целые
локализованныеbytes прошли standalone/full-object;host уженеrecording дляSF.
OriginalprofileTaiwan8/zh-tw,новаяearlyPE950/6997/localTCP/sound1 проверка
прошла доD3D. Rootcounts88/84/504/60/711:ko/ru несовместимы наtable4/1,
провереныправильныйотказ иprefixwrites,безподгонкиданных/конфига. Это ограничение
входного комплекта,не требование придумывать новые строки для codeparity.
Полныеordinaryowners/SFgameplay/другие5payloadfactories/5x10GUI/Tutorial/game
ещёOPEN. Production086/егоgate current;старыеGPU/Korea-startup/159k suites
не повторялись. M6/M6F/M7/M9OPEN.
[Доказательства](../research/client455-skill-force-items.md).

087 PARTIAL_SOURCE_FOUNDATION: выбраны/перенесены recordcopy/clone/refrelease
правила CItem92/CBoardObject620,включая signedBYTE и primarycache-empty guard.
3 whole-record oracle/12 lifetime сценариев/7 границ прошли standalone и с
полным набором клиентских объектов через ту же отдельную библиотеку.
Managerhost recording:actualderivedfactory/virtualpredicates/destructors и
ordinaryLinker binding остаютсяOPEN. Opaque resource fields копируются,полный
CResObject lifecycle не принят. Production086 и его текущий gate сохранены;
GPU/startup/159k suites не повторялись. Все086/прежние gaps обязательныM9.
[Доказательства](../research/client455-item-ownership.md).

086 PARTIAL: ordinaryCLinkBoard delta-save50ячеек/5секунд и group13/op17
перенесены. Семь actual send-ring/AES пакетов,drag suppression,cache-before-send,
rawflags и FrameMove проверены. Три storage запуска/account/exactnewPE/Create1
прошли. Legacy view остаётся8-slot,source objects borrowed; это не приёмка
целевых ownedclones/5x10GUI/input/cooldowns/download или игрового Linker.
Gesture/Macro — только pureencoder,actual providers отсутствуют. Oldbelt paths,
36factoryclasses/fullitems/Tutorial/игра и все прежние gaps обязательны.
Engine unchanged082;старые GPU/159k suites не переобъявлены свежими086.
Текущий gate hotbar086;085 исторический по старой normal-link. M6/M6F/M7/M9OPEN.
[Доказательства](../research/client455-hotbar.md).

085 PARTIAL: canonical Force3/Animus4/limit56 и ReturnItem eligibility0/1/5
перенесены. Три actual-source запуска проверяют17 реальных классов/пакеты/
256BYTE IDs/legacybelt refusal; account и exactnewPE/Create1 прошли. Старый
CBeltBoard не регистрируется; marker255 не является validwireID. Оставшиеся
старые MainGame.Create_Board/BeltList пути явно отказывают и требуют455 замены.
Это не приёмка fullfactory (36 target classes missing), Trunk/hotbar/trade/
itempacket/DB/полного ReturnItem/GUI/Tutorial/gameplay. Engine contracts reused,
старые GPU/159k suites не переобъявлены свежими085. M6/M6F/M7/M9 открыты.
[Доказательства](../research/client455-storage.md).

084 AUDIT_OPEN: common Tutorial init требует53 объектов фабрики455; текущая
source фабрика содержит18. У17 совпадают имена, эквивалентность поведения не
принята;36 других имён отсутствуют в этой фабрике, что не является полным
инвентарём отсутствующих исходников/функций. Force source4/target3 иAnimus5/4
нельзя передавать в QBI host без восстановления контрактов. QuestBriefing20 и
Tutorial — разные владельцы с window38.92 pinned ranges/1514 actual asm/RTTI
и восемь source-only запусков дают карту разрывов. Production PE083 неизменна;
actual Tutorial/common UI/Avatar/factory не приняты. M6/M6F/M7/M9 открыты.
[Доказательства](../research/client455-tutorial-integration.md).

083: цепочка signed64 Avatar → инвентарь, группировка и геометрия сумм
восстановлены. Проверены 184 случая двух локалей/четырёх режимов округления,
шесть кадров валюты и девять actor кадров; свежие account/actor/FX и exact
PE/Create=1 прошли. Gate083 PARTIAL. Полные Init инвентаря, сеть/торговля/
магазины с оставшимися DWORD/float, unmasked FP/CRT failures не приняты.
Actual Tutorial/factory/QBI host и полноценная игра ещё открыты. Движок и его
контракты082 переиспользованы; три карты/Miles082 не объявляются свежими083.
Число тестов и завершённые M0–M5 не дают общего процента готовности.
M6/M6F/M7/M9 открыты.
[Доказательства](../research/client455-money.md).

082: actualMiles immediateaudio/RVP ambient/event/timer_rate работаютвпроверенном
домене. RealMP3decoder/status/loop/volume,129boundary,2ambientstarts/2stops/4events,
3maps/actorFX/15viewedframes/exactPE/Create1passed. StockRVP2WAV/210events имеют
nohandle вcompiled455branch:поведениеперенесено,неэкстраполироватьнаPlayWave/весь
звук. FullMilesinit/3D/PlayWave/music/streaming/audiooutputPCM/failures/x87/scanner
ещёOPEN. 8D6900label081corrected:cacheDESTRUCTOR. ПолныйTutorial/Avatar/QBI/fourstage/
Login/auth/gameplay/FX ивсе прежниеразрывы обязательны. Gate082PARTIAL;M6/M6F/M7/M9OPEN.
[Доказательства](../research/client455-rvp-audio.md).

081: базовый отдельный RVP particle/entity pass иsharedFX deferred lifetime
подключены;269stockticks/148particle/6isolatedentitydraws,15reviewedframes,
3maps/exactPE/Create1passed. CParticle/CEntity1296/212 иactual weather allocations
согласованы;Coraheap corruption исправлена ипроверена. Это bounded legacy/basic
FX:advancedcurve/light/distort/trace/azirang/special,полныйentity455math/render,
process-ownedChef/context/failureunwind/material-lightreset ещёнеприняты.
Малые captures/счётчикdraws недоказывают isolatedparticle/finepixel parity.
Audio/magic/collision/shadow/screen/timer/fullTutorial/auth/game ивсе прежниеgaps
остаютсяобязательными. Gate081 PARTIAL;M6/M6F/M7/M9 OPEN. Достоверный процент
всего клиента по неполному реестру невычисляется.
[Доказательства](../research/client455-rvp-effects.md).

080: ordinary RVP resource/animation/dummy/culling/palette/model draw/EFF binding
восстановлены в проверенном домене.12stock actors/4sharedmodels, отдельные
9distinctpose ticks/459parts,11reviewedframes,3camera regressions иexactnewPE/
Create1 прошли. Малые captures не доказывают детальную визуальную эквивалентность.
Separateparticle/entitypass/sharedFXlifetime/audio/magic/collision/shadow/trace/
screen/timer-rate, fullTutorial/game и все прежние gaps обязательны дляM9.
Gate080 PARTIAL; M6/M6F/M7/M9 OPEN.
[Доказательства](../research/client455-rvp-actor.md).

079: ordinary RVP camera/timeline больше неstub. Три мира/27camera events/
82commands, pause/flag16/reload/renderer ownership иintro26прошли.46GPUviews
просмотрены;точнаяноваяPE/Create1passed. Actor/effect/audio/screen/timer providers
отклоняютсяявно,полныйRVP/Tutorial/игра ещёOPEN. SharedFX/cache/deferredlifecycle,
Render8CE5D0reset,pausedautoCAMscratch,scanner078/numeric/failures неприкрыты.
No-cameraRVP изменилintroFOV/FSE/GPU;полныйstageorder455ещёнесертифицирован.
Render/Releaseподписи078исправлены. M6/M6F/M7/M9OPEN.
[Доказательства](../research/client455-rvp-runtime.md).

078: RVP load-model и интерполяция проверены на44originals/615actor-records/
1569commands плюс all12 fixture. Это запись до resource/camera binding,
не подтверждение работающего проигрывателя. Ordinary player остаётся stub,
новая библиотека пока используется только ownprobe. 34missing из77exact-path
refs не объявлены игровым blocker без проверки поведения455. ProductionPE и
Create evidence077 не менялись; M6/M6F/M7/M9 OPEN.
[Доказательства](../research/client455-rvp.md).

077: приняты ограниченные RTMovie positive flags/display/defaultFOV contracts.
Реальный intro backend, flags8/GPU6/intro26/fullscreen18/40 просмотренных кадров
и точная PE/Create1 прошли. Это не полный RVP: собственный RTMovieFrameMove
подтверждён как пустая compiled stub. Stage/QBI/follow пока recordings в probe.
Полные RVP/Tutorial/Avatar/fourstage/вход/игра и прежние gaps остаются открытыми;
добавлены wrapper screen500/viewport480 и %fov. M6/M6F/M7/M9 OPEN.
Процент полноты не вычислен: реестр возможностей пока неполный.
[Доказательства](../research/client455-movie-state.md).

076: ordinaryFullScreenEffect motion branch/density/Beginresult перенесены.
GPU18/target-depth-viewport-UI/lowVRAM512 иrealintro26/34viewedframes passed.
Intro mode/densityactualbackend,ноstage/QBI/follow/cameraControlsещёrecordings.
ExactPE/Create1passed. Полныеpostprocess/water/bloom/extra455targets/shadow/reset,
CGP_Tutorial/Avataractor/fourstage/game/M6F/M7/M9OPEN.
[Доказательства](../research/client455-fullscreen-effect.md).

075: introsequence/camera/fade веткаперенесена,26камер3миров/29GPU/skip/reload/
Dmallocpassed. ActualAvatarтолькоrace/stage,UIреальные;QBI/follow/newenginecontrols
вprobeexplicitrecordings,неполныеproviders. Normalfacadecompiled,ordinaryTutorial
owner/factoryпоканет;unusedcodeудалёнlinker. PECreate1passed/runtimeequal074except
timestamps. Полныеstage/game/M6F/M7/M9OPEN.
[Доказательства](../research/client455-tutorial-intro.md).

074: три реальныекарты455 загружены/отрисованы черезCLand. SourceBSPowner и
деструкторLevelперенесены,load/reload/release/collision/Dmallocbalance и6GPU
кадров проверены. ExactnewPE/Create1passed. Это boundedBSP path:fullILevel/
Empty/INS,alpha/effects/lighting/audio/полныеphysics иTutorial/worldGameplay
ещёнеприняты. M6/M6F/M7/M9 OPEN.
[Доказательства](../research/client455-world.md).

073: ordinary CAvatar stage/skip иMainApp Createfailure gate перенесены,
login342 учитывает stage2,SendNetMessage использует реальныеstage/skip.
Knownignored и1/17transport приняты вограниченномдомене;остальныеlocalhandlers
явноотклоняются инеприняты. Полнаяfactoryостаётсяlegacy3/modulo. Window/board,
22GPU hashes иfinalPE/Create1passed. Correction:45FBD0 — Screen singleton,
а неуказательэтапа. ПолныеTutorial/world/handlers/Avatar иM6F/M7/M9OPEN.
[Доказательства](../research/client455-avatar-stage.md).

Участок072: source CGUIBriefingWindow/provider,outline/portrait/pages/keys и
реальныйscreen capture перенесены. CTutorialBoardprobe больше неиспользует
rich Viewfixture. Ko/Ru3pages,realmousequeue,22viewedGPUframes,affectedGUI и
exactnewPE/Create1 passed. ActualAvatar/world/Tutorialstage ещёнет;не force-retain.
Полнаяpixel/window/currentstageguard/resource-reset/lifecycle/IME/layer приёмка
остаётсяOPEN вместе свсеми игровымиразрывами.M6/M6F/M7/M9 OPEN.
[Доказательства](../research/client455-briefing-window.md).

Участок071: frame/key/animation sourcecontrols сrealresources иKo/Ru/GPUverified.
070typingno-self-fillclaim отозван:source/fixture исправлены по2262E0,проверены
80000redpixels. Самиordinarybriefing/window/capture/portrait/TutorialещёOPEN.
Productionruntime equal070 excepttimestamps;oldGUI evidence reusedexplicitly,
не объявленоfresh. ExactnewPECreate1не означаетfullUI/auth/мир.
[Доказательства](../research/client455-briefing-controls.md). M6/M6F/M7/M9 OPEN.

Участок070: CGUITextTypingBoard source interval/cursor/DBCS/space/timing и
partialDraw восстановлены;actual full-object Ko/Ru/GPU passed. Source compiled
in normalfacade,ordinary briefing instance ещё OPEN. Sharedrenderer extract
сохранил44GUI GPU hashes069;Create1passed. Отрицательные/потерянные markers/
unsafe domains не приняты. Полные briefing/key/portrait/Tutorial остаютсяOPEN.
[Доказательства](../research/client455-text-typing.md). M6/M6F/M7/M9 OPEN.

Участок069: ordinary modal.SetMsg plain/rich/colorFFE3E0D9/naturalpixel extent
перенесены,wrapperformatted/close параметры доступны.300/250 fallbackonly;
requestedsize заменяется послеextent. Ko/Ru12групп сGDIoracle и10viewedGPUframes,
affectedGUI/Create1passed;productionrich/extentprovidersretained naturally.
Empty-fragment extent target243D30 имеетuninitialized newline local:source
explicitrefusal,не parity. GlobalbaseGUI.SetSize nonvirtual/allwrapperguards,
полныеBriefing/Tutorial/Avatar/world/GUI/игра остаютсяOPEN.
[Доказательства](../research/client455-message-sizing.md). M6/M6F/M7/M9 OPEN.

Участок068: boundedbase GUI input/focus/key/queue/main-list contracts перенесены
и проверены Ko/Ru:double7/right8,300ms/wrap,modalguard,focusorder,keyscan/dedup,
focus70/value80/middlebutton. Исправлена ошибочная065arrow binding:ordinary
defaultunbound,EXexplicitbound. GenericAddinheritsShow;Remove retainslive mouse
refs. Sourceordinaryproviders retained,PECreate1 иaffectedGUIpassed;40GPUhashes
равныпредыдущимпросмотренным. FullGUI/IME/popup/other2lists/layers/destructor
registry/all7–8gameplay handlers ещё не приняты. Nativefirstchance40080201
causeunknown,безвыводаопаритетеfailuredomains.
[Доказательства](../research/client455-gui-input.md). M6/M6F/M7/M9 OPEN.

Участок067: обычный владелец миникарты получил EX opacity control,skin0/1,
alignment,Init80/80,подтверждённые alpha mappings и Draw455. Реальный mouse→
owner→EX→queue путь/81amount/пополненные lists/RGB/Ko-Ru GPU прошли. Production
owner/EX/facade присутствуют в map;новая PE existingCreate1. На кадрах сетка
из main5:32;нет terrain/dynamicmap56,partialalpha показывает старый nullsprite
rectangle fallback. Полная карта/прочие controls и alpha groups/zoom555940/
target parent pipeline не приняты. Положительный camera branch отказан явно.
[Доказательства](../research/client455-minimap-opacity.md). M6/M6F/M7/M9 OPEN.

Участок066: приняты bounded EX/Var source contracts и full-object Ko/Ru queued
input/GPU пробы. EX plain/base track inconsistency,no repeat,alpha и Var sizing/
origin/mode/release/row2 проверены. Это не интеграция minimap455:реальный owner
и helper7B2C60 ещё открыты. Var ctor direct xrefs нет;action15 недоступен через
loader455 actions<16;неизвестный horizontal local не подменяется значением.
Новая production PE/existingCreate1 и затронутые GUI проверки прошли.
[Доказательства](../research/client455-scrollbar-variants.md). M6/M6F/M7/M9 OPEN.

Участок065: ordinary scrollbar geometry/amount/mouse/clock и composite thumb
подключены; Ko/Ru queued GUI/GPU проверки прошли. Наличие23pinned ranges и
этих тестов не закрывает EX/Var, parent input pipeline или полноту GUI455.
В common action2 отсутствуют default cap frames44–49;сохранён target clamp43,
алгоритм отдельно проверен на собственном synthetic sprite. Production PE
собирается/existingCreate1; M6/M6F/M7/M9 OPEN.
[Доказательства](../research/client455-scrollbar.md).

Участок064: ordinary TextBoard fragment/line caches, pixel layout/retention/Draw
подключены. FONT_INFO16/TextInfo28 и markup/extent/BYTE-copy quirks проверены
в full-object probe, Korea/Russia GPU кадры просмотрены. Production rich callers
и legacy message sizing ещё не перенесены; весь scrollbar/input/briefing/
Tutorial остаётся открытым. Полная PE собирается и проходит existingCreate1.
[Доказательства](../research/client455-text-board.md). M6/M6F/M7/M9 OPEN.

Участок063: текущие GDI byte width/DBCS fit/кэш высоты и геометрия обычного
CGUIText проверены независимым Win32 oracle и Korea/Russia GUI/D3D probes.
Own lifecycle adapter устраняет pre-main доступ к не созданному font provider
базы0.7. Полная новая PE собирается, existingCreate1 сохранён. Полные TextBoard/
scrollbar, FreeType/16byte font scale, briefing и Tutorial ещё не приняты.
[Доказательства](../research/client455-text-metrics.md). M6/M6F/M7/M9 OPEN.

Участок062: обычные modal button bindings/67×21/ND106–107, outline/colors/
margins, Enter/Esc/Y/N и mouse1/2/3 проверены на реальных Korea/Russia GUI/D3D.
Новая полная PE собирается, existingCreate=1. Ошибка спрайтов061 исправлена.
Общий text-board/scrollbar, FreeType/ANSI, полный frame/lifecycle/provider и
Tutorial/fourstage остаются открытыми. Это не приёмка полного GUI или игрового
входа455. [Доказательства](../research/client455-modal.md). M6/M6F/M7/M9 OPEN.

Участок061: приняты bounded правила управления CTutorialBoard и реальный вызов
модальных GUI-диалогов2/3. Own full-object harness/D3D exit0. На кадре выявлены
старые назначения спрайтов кнопок: внешнее соответствие455 не принято.
Rich-view/stage/Avatar в harness — тестовые получатели. Полный briefing,
production host/регистрация/маршрутизация событий и ordinary Tutorial открыты.
Report group1/op17 содержит неизвестный byte payload; значение не придумывать.
[Доказательства](../research/client455-tutorial-board.md). M6/M6F/M7/M9 открыты.

Участок060: приняты bounded QBI19–46 rules с recording host. Factory47types и
99programs/39864records подготовлены, но это не реальное проигрывание обучения.
Concrete UI/Avatar/world/frame/feedback и ordinary Tutorial/fourstage обязательны.
Failed UI point coordinates и equip23 invalid table domain остаются известными
расхождениями; itemtail/прочие ранее открытые области не закрыты.
[Доказательства](../research/client455-tutorial-actions.md). M6/M6F/M7/M9 открыты.

Участок059: приняты bounded Move/Creation/Position rules с recording host,
known monster17/item25 wire и category47 map. Real world/Avatar/backend и
decrement shared remaining ещё не приняты. Item receiver читает unknown DWORD
по+25; не подставлять значение без доказательства. Full Tutorial и28 других
селекторов обязательны. [Доказательства](../research/client455-tutorial-spatial.md).
M6/M6F/M7/M9 открыты.

Участок058: принят bounded QBI scheduler и message/wait rules с recording host.
Это не реальные UI/Avatar side effects.41селектор, остальные context fields,
настоящий host/Tutorial/fourstage остаются открытыми. Отказ при отсутствии
процессора проверен; пропуск неизвестных команд не допускается.
[Доказательства](../research/client455-tutorial-runtime.md). M6/M6F/M7/M9 открыты.

Участок057: принят bounded wire reader47селекторов SCP, lossless99realfiles
и семантическая сверка именованных полей. Эта самостоятельная библиотека пока
не подключена к обычному Tutorial. Исполнение команд, CTutorialBoard, Avatar,
scene иfourstage остаются обязательными открытыми критериями. Неподходящий
ko-kr/Tutorial.scp учтён отдельно. [Доказательства](../research/client455-tutorial-scripts.md).
M6/M6F/M7/M9 открыты.

Участок056: ordinary CAniCamera1.2/1.3/read/play/FOVscale/release принят в
описанном bounded домене.4real1.2CAM и synthetic1.3 проверены с настоящим
D3D9 projection. Fullcamera matrix/FOV-updater consumer8D5FF0, fullTutorial/
Avatar/fourstage/мир ещё не приняты. [Доказательства](../research/client455-camera.md).
M6/M6F/M7/M9 открыты.

Участок055: принят локальный базовый контракт CGameProgress loop/next/exit,
Title constructor next1 и общий particlecount reset в текущем владельце.
Доказательство — actual full-object native methods, не весь stage runtime.
Factory всё ещё3/modulo, next не подключён к обычным переходам; target
dynamicparticles/Title/Login/Tutorial/world/Avatar ещё открыты.
[Доказательства](../research/client455-progress-base.md). M6/M6F/M7/M9 открыты.

Аудит054: обязательна приёмка всех четырёх этапов455: Title0/Login1/Tutorial2/
MainGame3, их явных переходов и Avatar stage. Tutorial подтверждён RTTI и
фабрикой; его локальные клиентские сообщения тоже входят в scope. Текущая
старая база имеет3stage/modulo и не реализует Tutorial. Пока это не закрыто,
M6F/M9 не могут быть приняты. [Доказательства](../research/client455-progress.md).

Текущий участок M6,account053: gate seed и account payloads/ответы подключены
к обычным send/receive/dispatch. Реальные методы проверены собственными
пакетами, включая настоящий pending dialog и повреждённые границы. Это
компонентное доказательство; реальная аутентификация не выполнялась. Ticket/
ini/mode providers,35handlers,notify11/fullUI/world/gameplay/IME/shutdown
остаются открытыми. [Доказательства](../research/client455-account.md).
M6/M6F/M7/M9 открыты.

Текущий участок M6,connection052: обычный WinMain проверяет настоящее соединение
до engine; события/задержка callback/timeout восстановлены. Реальные методы
подтвердили TCP-peer, raw-error и timeout с текстами NDLanguage. Собственные
ошибочные диалоги закрывает только проверочная программа, результат Connect
не подменяется. Это не аутентификация. Текущий Russian argv оставляет endpoint1
пустым; target setter/selector подтверждены, но полный country/handler эффект
ещё неизвестен. [Доказательства](../research/client455-connection.md).
M6/M6F/M7/M9 открыты.

Текущий участок M6,network-codec051: AES192-CBC/формат пакетов и буферы455
подключены к настоящим CNetProcess::LoadSendMsg/_PopRecvMsg. Байты направлений
сверены с независимым Windows CNG; фрагментация/переход через конец кольца и
виртуальный dispatch проверены. Normal сеть создаёт два процесса из шести.
Это не приёмка полного транспорта,35обработчиков, аутентификации или входа.
[Доказательства](../research/client455-network-codec.md). M6/M6F/M7/M9 открыты.

Текущий участок M6,bootstrap050: подтверждены FG rawint/instance policy,
настоящий ранний NetworkCreate и per-process Connect/error state. Own probes
проверили имя/два процесса/mutex,6process states,реальный TCP и callback.
455читаетошибкупослеclosesocket:наэтойWindows10061 теряетсядо0;connectedfalse.
Это совпадениеAPIконтракта,неуспешное соединение. ExistingCreate вернул1;
полный455transport/двеnetworkconfigs/35handlers/framing/cipher/crypto/вход
ещёнеприняты. M6/M6F/M7/M9 открыты.
[Доказательства](../research/client455-bootstrap.md).

Текущий участок M6,launcher049: file93bytes/argc5profiles,checknation ипередача
данных обычнымnetwork memberfields восстановлены. NativeKorea/Russia/Europe
проверенынасинтетическихofflineданных,безNetworkCreate/connect/auth. Exact
WinMain launcherидётпередlanguage;существующийCreate вернул1,дальшеstop.
Это не проверка аутентификации,полного455Create илиигровоговхода. Wire ID/PW
пока13bytes,аstate50/32;world/personal/premium/modeпотребители иостальная
bootstrap/networkцепочкаоткрыты. [Доказательства](../research/client455-launcher.md).
M6/M6F/M7/M9 открыты.

Текущий участок M6,sprites048: source455route55names иtexture upload включают
DXT5,которого не поддерживал legacyкод. Только подтверждённые startup IDs0/1
подключены к normalUI. ActualCMainApp.LoadData/CGUIMouse в ownlab загрузили и
нарисовали реальные455resources;562texture frames наязык сверенысполнымиbytes,
обаprocess naturalexit0. Это не полный455UI. ExactownPE отдельно дошла до
legacylauncherAPI послесуществующегоCreateprefix,затемостановленаотладчиком.
Ни launcherконтракт455,ниполныйCreate/логин/остальныеUIslots этимнеприняты.
[Доказательства](../research/client455-sprites.md);M6/M6F/M7/M9 открыты.

Текущий участок M6, lifecycle047: восстановлена только null-level ветка
UnloadLevel, подтверждённая инструкциями обоих pinned455PE. Три собственных
full-object labs с реальным глобальным CMainApp/CLand и две GUI-пробы без Land
завершились естественно с exit0. Full WinMain в lifecycle lab не исполнялся;
старый CLevel после Create не равен8байтному target ILevel wrapper. Полные
world ownership/effects cleanup/WinMain/shutdown остаются открытыми.
[Доказательства](../research/client455-lifecycle.md); M6/M6F/M7/M9 открыты.

Текущий участок M6,font046: selected GDI/Unicode font path иnormal engine bridge
восстановлены. Actual CGUIText Korean/Russian frames совпали сwide API;
GDI metrics/atlas oracle/cache eviction проверены,процессы завершилисьexit0.
Это lab entry среальным UI consumer,неполный production Create/интерфейс455.
Fontstartup exact own PE подтверждён. FT/ANSI/IME/layout/early-abort/shutdown
остаются открытыми. research/client455-font.md; M6/M6F/M7/M9 открыты.

Текущий участок M6, language045: EDF decoder/NDLanguage indexed lookup/DBCS
и countryCRT/codepage agreement восстановлены. Exact own WinMain действительно
загрузил Korean949/Russian1251 пакеты;9realEDF прошли byte roundtrip. Это не
отрисованный текст/UI или fullfont/ETCAction/startup455 acceptance. После
Korean init normal Character device подтверждён;stop до старых data readers.
research/client455-language.md; checkpoint PARTIAL; M6/M6F/M7/M9 открыты.

Текущий участок M6, nationpaths044: case-sensitive выбор страны/корня данных
подключён к ordinary WinMain и проверен на11странах. Exact own PE прошла ранний
Create до Character/bone/mesh/animation/bounds managers; Character использует
реальный app device. Стоп перед старым _CreateCharDataMgr. CRT/font/NDLanguage,
полный locale/launcher/network/Create/UI/gameplay/shutdown не приняты.
research/client455-nation-paths.md; checkpoint PARTIAL; M6/M6F/M7/M9 открыты.

Текущий участок M6, devicestartup043: по эталону исправлены color32 и strict
Create result policy. Новая полная PE прошла actual normal window/D3D init,
ready1/windowed1, с ненулевыми HWND/device, и остановлена до CMainApp::Create.
Это не приёмка target startup: nation/launcher/network order455, locale/root,
BGM, camera console18 и полное Create/UI/lifecycle ещё открыты.
research/client455-device-startup.md; checkpoint PARTIAL; M6/M6F/M7/M9 открыты.

Предыдущий участок M6, startup042: точная собственная full PE041 действительно
дошла через CRT/WinMain/engine до успешного Miles startup (return1), providers
сверены по SHA. Процесс остановлен debugger до D3D/window/Create; этот запуск
не доказывает graphics initialization, всю WaveList/playback/launcher/network
или normal shutdown. Это own execution evidence, не сравнение startup всего455.
research/client455-startup.md; scoped checkpoint PARTIAL; M6/M6F/M7/M9 открыты.

Предыдущий участок M6, accounting041: семь подтверждённых cumulative counters
питаются от настоящих producers и читаются diagnostic consumer через own source
snapshot. Actual ANI/two renderers/mesh lifetime и model/GPU descriptors прошли.
Вся новая normal source ветка компилируется и линкуется в RF_Online.bin, 0 missing
symbols. Это отдельный подтверждённый результат. Normal WinMain, initialization,
device lifecycle и полный UI/network/gameplay ещё не приняты; M6/M6F/M7/M9 открыты.
research/client455-normal-accounting.md; scoped checkpoint PARTIAL.

Предыдущий участок M6, characterclock040: таймер Character и реальный normal bridge
подключены, численные и provider сценарии прошли. Это отдельные миллисекунды,
не повторный update engine clock. Full normal link имеет один g_ChMemoryInfo.
Сам таймер не доказывает новые frame methods924700/9248A0 или полный actor
lifecycle; normal WinMain/UI/network/gameplay приёмка остаётся открытой.
research/client455-character-clock.md; checkpoint PARTIAL; M6/M6F/M7/M9 открыты.

Предыдущий участок M6, effects039: EFF reader/registry/file lists/application,
InitEffect и particle/entity views подключены к обычной сборке. Реальные файлы,
контракты выборки/сброса и применение настоящей DDS к модели на GPU проверены.
Это не приёмка полного particle emitter или игрового lifecycle. Pattern tail
grades9..35 по-прежнему неизвестен. Полный линк: 2 символа; normal WinMain,
клиентская сеть, UI и игровые сценарии ещё не приняты. M6/M6F/M7/M9 открыты.
Подробности: research/client455-effects.md; checkpoint PARTIAL.

Предыдущий участок M6, effecttables038: два загрузчика таблиц иquery подключены
кобычному sourcefacade, реальные2246patterns/4600items проверены. Это определённая
область выбора эффекта. Reader455 оставляет grades9..35 какнеизвестные stackbytes;
нашиqueries явно выявляют эту границу, не принимают её какнулевой эффект.
EFFloading/application/particles иполнаяигровая приёмка ещё открыты. Полныйлинк15
символов. research/client455-effect-tables.md; checkpoint PARTIAL/M9OPEN.

Текущий участок M6, normalshadow037: восстановлены BeginShadow/EndShadow,
текстуры и общий quad. Реальная модель дала силуэт512x512, переключение/
восстановление/reuse прошли, COM0. Это собственный явно завершённый проход:
настоящие callers455 используют BOOL при возвращаемом HRESULT0 и не дают
доказательства нормального shadow lifecycle. Полный линк20символов, M9OPEN.
research/client455-normal-shadow.md; inventory/client455-normal-shadow-checkpoint.json.

Текущий участок M6, normalcontracts036: пять методов модели/сброса/перепривязки
восстановлены. Реальная модель после reset/reattach/rematch рисует прежние два
кадра, BBX/границы проверены. Полный линк ещё22метода/данных. Это собственный
тестовый entry с производственными компонентами; normal WinMain, timedblending
и вся игровая/UI/network приёмка остаются открытыми. Подробности:
research/client455-normal-contracts.md; checkpoint PARTIAL. M9OPEN.

Текущий участок M6, normal renderer035: CUnity → модели/ANI → поза → CRender
подключены и отрисовали выбранную модель на D3D9. Проверены два кадра, обёртки,
видимость и ресурсное завершение. Это не нормальный WinMain и не вся игровая
приёмка. Полный линк ещё требует 27 методов/данных. Подробности и открытые
границы: research/client455-normal-renderer.md, checkpoint со статусом PARTIAL.

Текущий участок M6, normal port034: компилируются 180 исходных клиентских единиц
с типами455/D3D9, после выделения CUnity/CAnimation — 182 объекта x86/MT.
Реальные потребители загружают ANI; это два модуля, а не весь клиент.
Нормальная RF_Online.bin ещё не линкуется:39 методов/данных.
inventory/client455-normal-checkpoint.json имеет статус PARTIAL. Высокоуровневые
обёртки, эффекты, normal runtime и M6/M6F/M7/M9 остаются открытыми.

## Требование пользователя

Получить исходный код, из которого воспроизводимо собирается RF_Online.bin,
доведённый до 100% функционала и поведения выбранного эталона 455.
Это конечная цель проекта. Старый собираемый клиент, первый парсер или успешный запуск
являются промежуточными результатами. Идентичность текста оригинальных исходников
и побайтовое совпадение EXE не следуют из функционального соответствия.

Цель 100% фиксируется как требование. Достигнутую степень соответствия устанавливаем
по доказательствам; сейчас она неизвестна. Процент по числу восстановленных функций
не вычислять: функции различаются по объёму и могут быть не найдены.

Число assertions не является мерой готовности клиента. Для изменения проверять
затронутый контракт и зависимые сценарии; неизменённые большие наборы не повторять
без конкретного риска. Общую регрессию выполнять после сквозных изменений и при
приёмке этапа. В отчётах указывать сценарии и их результат, а не только счётчик.

Последний выбранный участок M6: начальный real R3EngineD3D9port в отдельнойкопии,
67x86/MTunits собраны. Device/Grassshader/Characterowner same-device иPlatform01
GPU/helpers/interiors/weather прошли.180normalclientconsumers ещёнеперенесены;
это не полный RF_Online455 и не original game frame parity. Gate
inventory/client455-engine9-checkpoint.json;research/client455-engine9-port.md.

Предыдущий выбранный участок M6: source renderer owner constructor/device binding/
destruction иtypedcontexts проверены нареальной модели/ANI/3textures отдельно и
вполном client lab. Два кадра равны,allocations/COM освобождены. Normalowner API
ещёunused/stripped;fullnormal Character/D3D9 port не принят. Gate
inventory/client455-renderer-owner-checkpoint.json.

Предыдущий выбранный участок M6: scene frustum/AABB source подключены к
SetCharacterClipping/ProcessClipping;72matrix/204AABB cases/9actor scenarios
и короткая Platform01 регрессия прошли. Это не полная game camera/actor visibility
или typed Character455/D3D9 integration. Gate inventory/client455-frustum-checkpoint.json.

Предыдущий результат: расчёт кадра и CAnimation ctor подключены к обычной
сборке, 612 численных случаев/16 actual CResObject сценариев прошли. Это доказательство
выбранного контракта; полный Character455/actor lifecycle/normal draw остаются открыты.
Основание: inventory/client455-animation-timing-checkpoint.json.

Следующий выбранный участок M6: elapsed clock теперь source и подключён к обычному
R3EngineMT. Actual clock→frame caller проверен в полном client lab; остальные
области и полнота клиента открыты. inventory/client455-loop-clock-checkpoint.json.

Следующий участок: source коллекция AnimationManager4028/record ownership проверена
в полном client lab на одном real ANI. Normal CUnity/CAniData ещё legacy; библиотека
сама по себе не закрывает область «Персонажи». inventory/client455-animation-manager-checkpoint.json.

Shader bootstrap455 теперь source:12VS/3PS/2declarations проверены realHAL/fullclient.
Контрольный draw использует synthetic triangle, не full Character draw. Normal
model/animation/renderer migration ещё открыта. inventory/client455-shaders-checkpoint.json.

Следом source draw primitives проверены на реальном BELPHEGORHOLIDAY с ANI и3textures:
46geometry parts/44skinned,кадры160/2160 совпадают в standalone и полном client lab.
Harness выбирает basic shader/камеру/CullNONE: это ещё не full92E5F0/effects/transparent
или normal renderer acceptance. inventory/client455-draw-checkpoint.json.

## Эталон

Main Character draw030 теперь source: эффекты, прозрачность, deferred batch, CPU и
shadow ветки представлены и проверены16targeted сценариями в полном client lab.
Реальная модель рисуется через основной маршрут, два кадра совпали с компонентом.
Это не normal integration/visibility/game frame acceptance; original CRT и
undefined scratch domains явнооткрыты. inventory/client455-character-draw-checkpoint.json.

Бинарный эталон закреплён в config/client-target.json: текущий пользовательский
RF_Online.bin, SHA-256 b1b5febf0d0394712e2322350e19dafe60742e8642697b93cfb89135bac1fd8b,
x86, image base 0x400000. Backup — вторичный материал; различия локализованы.
Полный манифест ресурсов/конфигурации ещё требуется дополнить для сравниваемых сценариев.
Условия сравнения включают ресурсы, настройки, ввод, сетевые входы и состояние клиента.
Поведение существующего сервера само по себе не доказывает клиентский алгоритм.
Серверные исходники — справочник для чтения без изменений/сборки; выводы сверять с 455.

## Начальные области покрытия

Это отправная карта для инвентаризации, а не доказанный полный перечень возможностей.
Каждую строку развернуть в конкретные функции и сценарии по данным анализа эталона.

| Область | Что сопоставлять | Текущий статус |
|---|---|---|
| Запуск и конфигурация | Инициализация, параметры, локализация, ошибки | Частично: own PE CRT/WinMain/engine/Miles/window/D3D ready; target startup order/Create/launcher/locale/error/shutdown ещё открыты |
| Файлы и данные | Форматы, таблицы, ресурсы, загрузка и обработка ошибок | Частично: helper SPT, selected RPK/R3X consumers, EDF/NDLanguage; область в целом открыта |
| Рендер и мир | Сцена, камера, освещение, эффекты, видимость, коллизии клиента | Частично: selected maps/helpers/weather/clock; D3D9 и полное поведение открыты |
| Персонажи | Модели, экипировка, анимации, клиентские состояния | Частично: selected mesh/texture/buffer/model/manager; normal dispatch/BN/animation/full Character открыты |
| Ввод и интерфейс | Управление, окна, текст/IME, фокус, сочетания клавиш | Частично: selected CGUIText GDI/Unicode draw иstoredCP boundaries;полные UI/layout/IME/input открыты |
| Звук | События, позиционирование, музыка, настройки | Частично: Miles startup и selected tagged/RVP playback; все события/music/3D/settings и полный lifecycle открыты |
| Клиентская сеть | Пакеты, сериализация, обработчики, порядок состояний/ошибок | Частично: pre-engine Connect/wait/events, AES/формат пакетов, send/receive rings и два процесса; полный транспорт/35обработчиков/auth/country bootstrap открыты |
| Вход и выбор персонажа | Клиентские экраны, переходы и обмен сообщениями | Сквозной455поток не принят;описаны stage contracts,но full factory/Title/Login/auth/selection/world открыты |
| Игровые действия | Перемещение, выбор цели, атака, умения и отображение результатов | Selected Character flags/Nuclear восстановлены;полный обычный movement/combat/skills цикл455 не принят |
| Предметы и взаимодействия | Инвентарь, торговля, NPC, квесты и прочие обнаруженные клиентские сценарии | Selected EDF/payload/owners/icons/inventory handoff восстановлены;полные inventory/equipment/use/trade/NPC/quests открыты |
| Социальные функции | Чат, группы, гильдии и прочие обнаруженные функции | Selected4pane/system message output восстановлен;полные input/send/receive/party/guild открыты |
| Жизненный цикл | Загрузка/смена локаций, разрыв соединения, выход, освобождение ресурсов | Selected map/model/GPU reload/release проверены;все4stages/DC/reconnect/смена локаций/reset/shutdown открыты |

Первый предметный реестр: inventory/client-features.json. M5 закрыт для helper SPT455
и его interior/weather consumer:140files/97 543records; две math функции инструкционно
совпадают с455. Actual LoadLevel/FrameMove/render/release прошли на lobby/Platform01
через own entry полного проекта.23helpers/8interiors управляют двумя real weather layers.
13GPU cases/321checks,703weather/30resource/23 337targeted helper checks прошли.
research/client-m5-checkpoint.md; client455-graphics-runtime.md. Это ограниченный
результат; строки «Файлы и данные»/«Рендер и мир» целиком остаются открыты.
Full particles/clock/lighting/D3D9 parity и normal WinMain не проверены.

Численный clock перенесён следующим участком M6:8scalar functions+256byte frame
prefix,773instruction bytes совпали с обоими PE;1275native checks/12FP modes в
module и полном клиенте, linked code/default provider проверены. Actual Platform01
FrameMove/GPU повторно прошёл. Это закрывает численный участок при равном FPU
окружении; cached client map time/packet/console integration и lighting остаются
открытыми. research/client455-clock-source.md. Критерии полноты не изменены.

Следом selected client map message8/5 →CLand cache→successful-load hook перенесён
и проверен:314native checks/12FP modes/UTC+JST,130instruction bytes equal455,
actual client processor/CLand/Platform01 GPU2cases/66checks. Full byte-index CLand
UI/effects/error path,root network/transport,opaque fields и old-CRT localtime32
timezone/DST/invalid domains остаются открытыми. Это не закрывает строку «Клиентская
сеть» или полный жизненный цикл. research/client455-map-time-source.md.

Selected local time/real_time input восстановлен с grade>=1,history/prefix boundary
и независимыми clocks:432ASCII cases/2628checks,20actual CHAT_INFO checks,commands→
weather/GPU2cases/69checks. Other local directives/full chat/GUI key events и old-CRT
locale остаются открытыми; это method-boundary проверка. Clock теперь10scalar
functions+256byte prefix/1037instruction bytes,1443checks/12FP modes. Подробности
research/client455-time-commands-source.md; область «Ввод и интерфейс» целиком открыта.

Ресурсный аудит M5 закрепил78MapEntity RPK,70BSP39/93EBP20 и20weather assets.
Header/table round trips,8tool parser tests и DDS mip sizes прошли, native/GPU
load в том цикле не выполнялись. Последующий source RPK/fopen/exists и particle end
подключён и проверен:18 907native module checks и30actual full-project checks;
следом selected consumers прошли actual map/GPU cases. research/client455-resource-io-source.md;
один weather path missing для3Tower R3X. Неверные metadata sizes/offsets не
исправлялись: research/client455-map-resources.md. Полного resource manifest ещё нет.

## Запись каждой возможности

Уникальный ID; источник обнаружения; SHA-256/VA/RVA для бинарного доказательства;
описание входов/состояний/выходов; особенности и ошибки эталона; соответствующий
исходник; способ сравнения; результаты; известные расхождения; уверенность.
Статусы: обнаружено → описано → реализовано → проверено; отдельно блокировано/неизвестно.
Намеренные исправления особенностей эталона согласовывать отдельно от восстановления.

## Известные открытые вопросы после первой сборки

RF_Online.bin получен и чисто пересобран в diagnostic configuration: /Od, reconstructed
Character interface/адаптированная библиотека и отдельные подтверждённые 455 branches.
Обычный WinMain не запускался; own full-project lab выполнял CPU и GPU scenarios.
Pure legacy OFF configurations и canonical optimized Release
не объявлены готовыми. Это сборочный результат M4, не финальная приёмка 455.
research/client-first-build.md; inventory/client-first-build.json.

- Восстановленный Character.h обеспечивает компиляцию; конструкторы, inline/default
  arguments и runtime ABI старой STL/CRT не проверены. research/character-library.md.
- Старый прямой FILE EOF доступ CharacterMR несовместим с UCRT. Изолирующий адаптер
  прошёл 1828 собственных проверок и настоящие text/binary loaders с CPU mesh effects
  (59 checks). Legacy SetEffect bridge bounded; original inline/bad-input behavior
  и 455 map/36 grades не доказаны. 455 draw source calls проверены статически, GPU нет.
  Менеджеры/empty renderer прошли 3630 проверок на unloaded records, setters — 18 ABI
  checks, exception helpers — 770
  сравнений с classic exports. Полный SDK ABI/exception unwind/render не доказан;
  research/character-effects-and-exceptions.md. Одного успешного link недостаточно для M4.
- Старый CLevel::GetFrustumNormalPlane вызывает себя (C4717); есть глобальная функция
  с тем же именем. Не исправлено; поведение/эквивалент в 455 ещё не установлены.
- _NEW_UI_ нужен текущим исходным классам предметов и включён для современной сборки;
  этим не подтверждено соответствие старого UI эталону 455.
- Логирование 455 проверено на 14 own cases/66 checks; lifecycle clear routine неизвестен.
  Success->lobby edge не содержит древнего CheckFiles, но остальные integrity/resource
  checks и полная login sequence ещё требуют аудита. Не считать их покрытыми.

Character prerequisite:8legacy functions/full InitVertex имеют source;245binding+
6732InitVertex checks/144cases/12FP modes standalone/full-client,4COFFtests и2actual
LoadRealData→source call destinations. Mesh/triangles/weights/matrices/errors/release
проверены через test-only COM capture. Это не Character455/GPU acceptance:
legacy1072/36byte vertex/heap blends отличается от4555803/64/inline;455normals negated,
Полный MESH08 runtime loader ещё отсутствует. Его format reader/writer готов:
858real files/12090meshes прошли lossless roundtrip;6304native checks standalone/
full-client,12samples/393parts/1309guarded truncations и7Python tests. Normal loader
ещё не использует модуль. research/client455-mesh08-format.md.
Отдельные packed455parent/bone kernels имеют source:2237checks/12real paired fixtures/
393meshes/455skeleton records и20overlap cases standalone/full-client. Normal
loader иполные skeleton/transform/animation/material/GPU consumers ещё открыты.
research/client455-mesh-bindings-source.md. Сами paired fixtures не доказывают
игровой выбор скелета иполную загрузку BN.
Constructor final state/header/matrix/material-request kernels source готовы:
14562checks/12real files/393parts/12FP modes standalone/full-client. Matrix provider
закреплённаяD3DX9_36;texture callbacks вtests scripted. Arbitrary matrix bitproof,
actual TextureManager/sharedGPU/destructor/full loader остаются открытыми.
research/client455-mesh-runtime-source.md. Проверка матричной DLL не закрывает D3D9renderer.
Последующее: реальный source Character RFS/DDS/TextureManager backend прошёл
8440checks standalone/full-client,80profiles/68texturepairs/all mip contents/
137renders,97real material parts/59bindings,COM/Dmalloc0;9Python tests.
Это выбранный texture domain. Normal model-loader,shared buffers,skinning/draw,
full device reset/unwind/private ABI/malformed/OOM/locale области ещё открыты.
research/client455-character-textures.md;client455-texture*.json. Не считать
приёмкой всего Character или renderer.
SharedGPUsourceunit:159173checks standalone/fullclient,12real files/393parts,
276nonzero-indexGPUuploads и117zero-indexskips. Capture bytes/failure/counter tests,
4physical synthetic indexed draws/rollover,COM/Dmalloc0.18ref bodies equalbothpins.
Это не полный shader/skin/animation/draw coverage:lab POSITIONT/COLOR declaration
не подменяет455declaration. Normal full model-loader/ownership ещё открыты.
research/client455-shared-buffers.md;inventory/client455-shared-buffers*.json.
Connected MESH08 route/lifetime:9953CPU/10021HALchecks standalone/full-client,
12files/393parts/276realuploads/59texturebindings. Dtor5803byte endstate/order,
reverse cookiearray,ownedrelease,reload overwrite иbounded nullallocationcleanup
проверены. Ownheap/COM/Dmalloc0. Это не full manager/filedispatch/BN/animation/
shaders acceptance;пары скелетов —tooling fixtures,known800byteprefix не полныйABI,
OOM/unchecked/full exception unwind открыты. research/client455-model-pipeline.md.
Selected455record/manager/rawMSH/refresh:850CPU/1138HALchecks standalone/fullclient;
whole1188byte ctor vs92instruction oracle/12FPmodes,manager4148/cache/ID/delete/clear/
dtor,18rawreads/12models/393parts/276uploads/59pointers. RealMSHизсобственногоRFS и
11loose models rawбайты равныpins.13APIs source/called,ownheap/COM/Dmalloc0.
Stickydispatcher9238A0 исследован,ещё не реализован;полныйBN/animation/typedconsumers/
shader/draw иunsafefailure equivalence открыты. Cache retains danglingpointers —
поведение сохранено,stale dereferences не сертифицированы. research/client455-character-manager.md;
inventory/client455-character-manager-checkpoint.json. Это не приёмка Character целиком.
Intermediate legacyMSH/BN reader/part720/model28 lifetime отдельно source:
4606standalone checks/12realBN455records+5synthetic4records/1183guarded prefixes/
7allocfailpoints/12FPmodes/6Python tests. File importer/converter/realruntime skeleton
иnormal dispatch этим не подтверждены. research/client455-legacy-model-reader.md.
Следом fullselectedvalid-input legacyMSH/BN converter/fileIO/MTG/weights/indexing/
binding source подключён:66627capture/14896HALchecks standalone/fullclient,
34runs972parts/832HALindexeduploads/2CPUretained.12actualBN→MESH08pairs393parts/
276uploads,heap/COM/Dmalloc0;10sourceAPIs verified. BNinitialmatrices/parent/blend
tables проверены,полныеANI/animation/skinningdraw/shaders/normaldispatcher/typed
consumers всё ещё открыты. Failure/locale/privateABI/unwind gaps явно перечислены
вresearch/client455-legacy-model-runtime.md;gateclient455-legacy-runtime-checkpoint.json.
Приёмка всегоCharacter/M6/M9 не заявлена.

## Приёмка

Secondary91E270 source state84/globals28/5effects подключёнкFrameMove;
36whole-statecases/2actualCoraBN/6updates standalone/fullclient,6source APIs,
heap/Dmalloc0. Relatedpose11pairs passed;неизменённыеbulk suites не повторялись.
Lab используетmodernMTsin callback:reference static__CIsin/SSE bitparity не
подтверждена,actor ctor/frameproducer/normal consumers/draw ещёopen.
CPUonly. Gateinventory/client455-secondary-checkpoint.json;
research/client455-secondary-motion.md. Это не fullFrameMove/M6/M9 acceptance.

Selected pose/FrameMove phases source:11realpairs/22ANI/132updates/2298skinmatrices
standalone/fullclientownentry,132selectedkeycases и8analytic scenes/12maskedFPmodes.
5source APIs,heap/Dmalloc0. CPUpose не является animateddraw. Secondary91E270,
producer кадров/manager/worker/normaltypedconsumers/shaders остаются открытыми.
Часть parent-ramp analytic expectations имеет1e-4допуск из-заpinnedD3DXinverse;
wholematrix skin/parent consistency exact. Не заявлять независимое полное сравнение
с выполнением referenceFrameMove. Gateinventory/client455-pose-checkpoint.json;
research/client455-pose-source.md. Старые runtime suites не повторялись.

Последующий selected ANI/rawIO/record284/lifetime/attachment/Character dispatcher
source:27files1062tracks/6Python tests;14513CPU/15181HALchecks standalone/fullclient,
22real ANI switches на11BN→MESH08pairs794parts/660HALuploads;13sourceC APIs.
Sticky flags/previous-current/borrowed key lifetime/cumulativecounter/raw leak
проверены;тест очищает leak отдельно после наблюдения,не маскируя его.
Normalconsumers/pose math/AnimationManager/asyncworker/shaders/full failure domains
остаются открытыми. Не считать HAL uploads приёмкой анимированного персонажа.
Gate inventory/client455-animation-checkpoint.json;
research/client455-animation-dispatch.md. M6/M6F/M7/M9 открыты.

По уточнению пользователя M9 — финальная приёмка этого клиента 455 без модернизации
графики. M6F и M7 входят в критерии; M8 не требуется. Восстановление рендера/шейдеров,
необходимых для поведения эталона, входит в восстановление клиента. Обновление
визуального стиля или перевод на новый графический API требует отдельной задачи.

- Полные исходники клиентской реализации и необходимых для неё компонентов,
  закреплённые зависимости, команды и повторяемая сборка RF_Online.bin.
- Реестр возможностей эталона с проверками реальных сценариев, граничных состояний
  и ошибок. Для форматов — эталонные образцы и round trip, где применимо.
- Сравнение эталона и восстановленного клиента при одинаковых входах; известные
  расхождения устранены, непроверенные области и недоступные сценарии явно перечислены.
- Все промежуточные замены/заглушки учтены. Заглушка с иным поведением не считается
  завершённой реализацией соответствующей возможности.

Пока остаётся неизвестное или непроверенное поведение, безусловное утверждение
«100% соответствие доказано» недопустимо. Итоговый отчёт должен указывать точные
границы проверки, даже когда весь выявленный реестр закрыт.
Текущий частичный этап143:ordinary CharacterDataMgr читает14таблиц иND,
165classlookups иреальныеSFboards провереныв4stockcases+DBCSfixture.
Fresh ownb41d50ff… Login/lobbyframe просмотрен. Полные Avatarclass/equipment/
skillboardpopulation/bootstrap/selection не приняты;M6/M6F/M7/M9 OPEN.
Gate inventory/client455-character-tables-checkpoint.json;
research/client455-character-tables.md. Общаяоценка25%(20–35%) не меняется.
Текущий144 PARTIAL:actual Avatarclassindex/name writers165/3locales иactual
encrypted1/9receiver3real classindices PASS;ordinaryLogin viewed.
Отдельные23textwidgets не доказывают455UIlayout/render. Classskillcallback,
equipment/appearance/selection остаютсяopen.
Gate inventory/client455-avatar-classes-checkpoint.json;research/client455-avatar-classes.md.
# Частичная проверка159, 11.11.2026

Верхняя Gauge455 перенесена в обычные источники,19reference functions/1406
instructions совпалиbothpins. Native actual17children/3GPUframes/цвета/числа/
level/reload PASS. Live выбор принят,GaugeInit пройден;следом fatal старого
CharInfo.SetSprite/Init. Это PARTIAL_KNOWN_FAILURE,не успешный полный запуск.
World/control/fullUI/M6F/M7/M9OPEN. Gate:inventory/client455-hud-checkpoint.json.

Частичная160: необходимый TabBoard455 восстановлен и проверен компонентно
(17fullfunctions/1318instructions/реальныеskins/4GPUframes),но ещё не подключён
кordinary CharInfo и не удержан вигровомPE. Это PARTIAL_COMPONENT_ONLY,
не новый успешный игровой переход;последнийживойрубеж остаётся159.
Gate:inventory/client455-tab-board-checkpoint.json. Полнаяприёмка/M9OPEN.
