# Частичная проверка 205 — запрос HP и гибель монстра

11.11.2026. Для 455 подтверждены `13/26`, `13/28`, `13/21`
и потребитель `3/24`. На NeutralB за один вход прошли два
выстрела по разным монстрам, по 22 урона. Для обоих подтверждены
HP 100% → 0% и гибель. Стрелы 310 → 309 → 308.
Адресный охват 2 890 (+10), полные листинги 1 110 (+11).
M6, принято 0/12.
[Доказательства](../research/client455-monster-target.md)

# Частичная проверка 204 — расход стрел и попадание

11.11.2026. `d8ad009f…` x86. В двух отдельных прогонах
показано по 22 урона. Ответы `5/21` обновили один и тот же
серийный номер экипировки с 314 до 313 и с 313 до 312.
На последнем кадре доля HP цели равна 100%. В журнале этого
прогона нет `13/27` или `13/29`. Повторный ввод в рамках
одного входа не дошёл до отправки. Адресный охват 2 880 (+8),
полные листинги 1 099 (+10). M6, принято 0/12.
[Доказательства](../research/client455-ammunition-impact.md)

# Частичная проверка 203 — первый живой ответ обычной атаки

11.11.2026. `083a7892…` x86. Обычный выбор и подход на
NeutralB привели к отправке восьмибайтового `5/1`. Клиент
поместил в очередь 22 урона из 25-байтового `5/7`. Получен
четырёхбайтовый `5/21`. Открыты обновление остатка стрел,
кадр попадания и повторные атаки. Адресный охват 2 872 (+9),
полные листинги 1 089 (+10). M6, принято 0/12.
[Доказательства](../research/client455-primary-ammunition.md)

# Частичная проверка 202 — предметы после входа

11.11.2026. `f27d2498…` x86. Вход на NeutralB применил 8/8
предметов экипировки и 21/21 запись инвентаря через типизированную
фабрику, включая 315 экипированных стрел. После исправления
привязки значка наблюдение прошло без необработанных исключений.
Обычная атака остановилась на проверке основного боеприпаса.
Адресный охват 2 863 (+5), полные листинги 1 079 (+7). M6,
принято 0/12.
[Доказательства](../research/client455-downloaded-items.md)

# Частичная проверка 201 — атака через восстановленную экипировку

11.11.2026. `f3a101bf…` x86. Штатная атака после выбора мышью
и `Ctrl+Space` распознаёт лук без прежнего исключения. Условия
остановились на боеприпасах. Базовый ответ создал 0 предметов,
из 21 записи инвентаря размещено 0. Оба обработчика используют
прежний фабричный путь. Запрос `5/1` с 8 байтами собран,
его отправка ещё открыта. Охват 2 858 (+13), полные листинги
1 072 (+13). M6, принято 0/12.
[Доказательства](../research/client455-armed-attack.md)

# Частичная проверка 200 — граница живой атаки

11.11.2026. `c3c6df6b…` выбрала Youngflem обычным кликом на
NeutralB. Зафиксированы окно цели и клип ходьбы. На третьем
клике исключение из `CPlayerProc::GetNormalItem` остановило
атаку. Эталон подтверждает запрос `5/1` с 8 байтами и ответ
`5/7` с записями по 14 байт. Адресный охват 2 845 (+16),
полные листинги 1 059 (+16). M6, принято 0/12.
[Доказательства](../research/client455-live-combat.md)

# Частичная проверка 199 — критическая реакция монстра

11.11.2026. `765fafe1…` x86. Компонентно проверены два
оригинальных критических клипа Wing, очередь до эффекта Силы,
контрольный флаг, тряска и дополнительный свет. На NeutralB
прошли вход и ходьба. Адресный охват 2 829 (+10), полные
листинги 1 043 (+13). M6, принято 0/12.
[Доказательства](../research/client455-monster-critical.md)

# Частичная проверка 198 — отрисовка урона Силы

11.11.2026. `8e3035b7…` x86. Штатный рендер вывел числа 31 877
и 38 123 из атласа 455. Компонентно проверены затухание,
три дорожки эффекта Prism Beam и штатный WAV.
Адресный охват 2 819 (+3), полные листинги 1 030 (+3). M6, принято 0/12.
[Доказательства](../research/client455-force-damage-render.md)

# Частичная проверка 197 — боевые надписи и звук

11.11.2026. `1e64dd9f…` x86. Штатная очередь отрисовала
`BLOCK` и `MISS` из атласа 455. Проверены затухание, отсечение
сторонней цели и реальный звук Miles в тихом режиме.
Адресный охват 2 816 (+9), полные листинги 1 027 (+9). M6, принято 0/12.
[Доказательства](../research/client455-combat-result-effect.md)

# Частичная проверка 196 — эффект попадания Силы с уроном

11.11.2026. `643554e2…` x86. Положительный урон передаёт в очередь
Force-ключ из штатной строки, режим и число по кадрам. Оба кадра
подтверждены компонентно. На NeutralB прошли вход и ходьба.
По RVA `0x3ec840` эталон выводит `BLOCK` и выбирает звук.
Адресный охват 2 807 (+15), полные листинги 1 018 (+17). M6, принято 0/12.
[Доказательства](../research/client455-monster-force-impact.md)

# Частичная проверка 195 — реакция на попадание без урона

11.11.2026. `de40a4a1…` x86. При попадании по монстру −2 ставит в
очередь эффект типа 13, обычный промах ставит тип 4. Оба ключа
подтверждены компонентно. Живая отрисовка остаётся открытой.
Адресный охват 2 792 (+11), полные листинги 1 001 (+12). M6, принято 0/12.
[Доказательства](../research/client455-monster-force-reaction.md)

# Частичная проверка 194 — здоровье монстра

11.11.2026. `b8bd9f67…` x86. Команды 13/27 и 13/29 обновляют
долю HP монстра. Снижение при активной очереди применяется на кадрах
Силы, лечение применяется сразу. Это подтверждено компонентно.
На NeutralB прошли вход и ходьба. Живые HP и Сила открыты.
Адресный охват 2 781 (+13), полные листинги 989 (+13). M6, принято 0/12.
[Доказательства](../research/client455-monster-health.md)

# Частичная проверка 193 — цели и урон Силы монстра

11.11.2026. `1d3df8ea…` x86. Команда 5/9 ставит известные цели
в боевую очередь, хранит 32-битный урон и распределяет остаток по
кадрам попадания. Компонентно подтверждены 70 000 и два кадра.
HP и визуальные эффекты открыты. Адресный охват 2 768 (+12),
полные листинги 976 (+12). M6, принято 0/12.
[Доказательства](../research/client455-monster-force-damage.md)

# Частичная проверка 192 — событие Силы монстра

11.11.2026. `2672e567…` x86. Команда 5/9 назначает активную Силу
монстру и запускает действие. Оба клипа Wing загрузились через
обычный диспетчер в компонентной проверке. На NeutralB прошла
ходьба, живое событие Силы открыто. Адресный охват 2 756 (+9),
полные листинги 964 (+9). M6, принято 0/12.
[Доказательства](../research/client455-monster-force-result.md)

# Частичная проверка 191 — клипы Силы монстра

11.11.2026. `53eaff44…` x86. Метод монстра выбирает тип 12 или 13
по семи группам эффектов 455 и типу первого эффекта на уровне Силы.
Оба клипа Wing импортированы компонентно. Подключение боевого события
к активной Силе монстра открыто. Адресный охват 2 747 (+2),
полные листинги 955 (+4). M6, принято 0/12.
[Доказательства](../research/client455-monster-force.md)

# Частичная проверка 190 — кадры Youngflem

11.11.2026. `a779670e…` x86. Короткое тестовое перетаскивание
установило угол 22,5°. В трёх кадрах полностью виден Youngflem,
позиции клипа стояния 1 556, 2 480 и 3 484. Ходьба и поворот
ещё открыты. Адресный охват 2 745, полные листинги 951. M6, принято 0/12.
[Доказательства](../research/client455-monster-view.md)

# Частичная проверка 189 — анимации монстров

11.11.2026. `f6816c3f…` x86. Ключи моделей используют сдвиг на 12.
Штатные клипы Wing вернулись в живом прогоне. Пробный прогон
подтвердил продвижение клипа Youngflem, частично закрытого интерфейсом.
Адресный охват 2 745 (+11), полные листинги 951 (+11). M6, принято 0/12.
[Доказательства](../research/client455-monster-animation.md)

# Частичная проверка 188 — обычная атака и видимый монстр

11.11.2026. `c8151a03…` x86. Входящее 4/34 записывает состояние
аватара. Компонентно проверено ограничение атаки по игроку, исключение
для монстра и сброс совпавшей цели. В NeutralB получено 0xff, на
финальном кадре виден монстр. Умения, Сила и сравнение анимации открыты.
Адресный охват 2 734 (+9), полные листинги 940 (+9).
[Доказательства](../research/client455-town-state.md)

# Частичная проверка 187 — отметки видимости и городские ограничения

11.11.2026. `f16919a8…` x86. На NeutralB применены все 92 сообщения
4/10, 70 для монстров и 22 для игроков. В эталоне 4/34 пишет
поле, используемое в проверках городских ограничений боя.
Адресный охват 2 725 (+10), полные листинги 931 (+12).
[Доказательства](../research/client455-world-refresh.md)

# Частичная проверка 186 — записи и движение монстров

11.11.2026. `22421c33…` x86. Обычный владелец Character.edf
обслуживает 1 999 строк монстров. На NeutralB созданы 17 из 17,
применены 69 из 69 обновлений движения. Два кадра мира не показывают
монстров. Боевые атрибуты, траектории, 4/10 и 4/34 открыты.
Адресный охват 2 715 (+16), полные листинги 919 (+18) за проверки 185–186.
[Доказательства](../research/client455-monster-data.md)

# Частичная проверка 184 — вертикальный поворот на NeutralB

11.11.2026. `dad137eb…` x86. Восстановлен предел −89° правого
перетаскивания. Три замера 40° → −46,5° → −89°, видно небо.
Аватар частично перекрывает обзор в крайнем ракурсе. Адресный
охват 2 699 (+3), полные листинги 901 (+5). M6, принято 0/12.
[Доказательства](../research/client455-world-camera.md)

# Частичная проверка 183 — движение и остановка на NeutralB

11.11.2026. `253767b6…` x86. Исправлен путь основной раскладки,
загружено 24 назначения Taiwan. Тестовый ввод в поток клиента
сдвинул аватар на 73,94 единицы. В очереди два `4/1` и один
`4/12`. Два поздних замера совпали. Физический ввод, вращение
камеры, NKM и точный ответ сервера открыты. M6, принято 0/12.
[Доказательства](../research/client455-world-walk.md)

# Частичная проверка 182 — местность NeutralB видна

11.11.2026. Тот же `c24a41d0…` x86. Три штатных файла `sky2`
добавлены в тестовый набор. В обоих кадрах после `3/2` видна
текстурированная местность. Небо, движение и камера открыты.
M6, принято 0/12 областей. [Доказательства](../research/client455-neutralb-sky.md)

# Частичная проверка 181 — кадры NeutralB после стартовой позиции

11.11.2026. `c24a41d0…` x86. На двух кадрах после `3/2` виден
аватар, небо и местность чёрные. Три замера без ввода зафиксировали
стабильную позицию и разрешённый ввод. Проверить рендер BSP и неба,
затем движение и камеру с реальным вводом. M6, принято 0/12 областей.
[Доказательства](../research/client455-world-observation.md)

# Частичная проверка 180 — началась обычная сцена NeutralB

11.11.2026. `b001f830…` x86. Используется типизированное оружие, исправлен
старый спрайт компактного чата, в стенд включён `LitGrass1.vso`.
Аватар создан, первый кадр завершён, `3/2` режим 0 обработан. Дальше
276 входящих сообщений, фатального исключения нет. Управление открыто.
Адресный охват 2 696 (+6), полный статический 896 (+7), 313 частичных
привязок в 23 реестрах. M6, 0/12 полных областей.
[Доказательства](../research/client455-avatar-world.md)

# Частичная проверка 179 — загружена NeutralB

11.11.2026. `16b78443…` x86. Из Linker отправлен `12/8`, получен
`12/9` на 961 байт. Разобраны 60 записей, создано 0 NPC. Флаг загрузки
выставлен из списка NPC, BSP NeutralB загружен. При создании аватара
`SetCombatMode` вызывает старый `GetNormalItem`. `3/1` не отправлен.
Адресный охват 2 690 (+7), полный статический 889 (+7), 309 частичных
привязок в 22 реестрах. M6, принято 0/12 полных областей.
[Доказательства](../research/client455-store-download.md)

# Частичная проверка 178 — получен список гильдии

11.11.2026. `35e531e1…` x86. Макросы `3/50` и объявления `13/105`
декодируются и сохраняются, живые записи были пустыми. После `27/111`
получен `27/112` на 2 байта. Эталонный `MainGame::Create` ждёт поле
`this+0x1c` перед `3/1`. Источник флага открыт. Адресный охват 2 683 (+8),
полный статический 882 (+8), частичных привязок 307 (+2) в 21 реестре.
M6, принято 0/12 полных областей. [Доказательства](../research/client455-macro-download.md)

# Частичная проверка 177 — настройки банков Linker применены

11.11.2026. `168d1414…` x86. `3/45` разобран, применены настройки банков,
разрешено 0/2 ссылок. Получены макросы `3/50` и объявления `13/105`.
Следующий запрос эталона после макросов `27/111` с байтом `0xff`.
Адресный охват 2 675 (+8), полный статический 874 (+9), частичных
привязок 305 (+1) в 20 реестрах. M6, принято 0/12 полных областей.
[Доказательства и следующий участок](../research/client455-linker-download.md)

# Частичная проверка 176 — получен ответ Linker

11.11.2026. `cd3f1c0d…` x86, статус `PARTIAL_WAITING_FOR_LINKER_AND_ITEM_OWNERS`.
Обычный путь применил основные поля `3/8`, сопоставил 7/7 записей `3/12`
с `Quest.edf`, обработал пустые `3/14` и `3/55`. После запроса `3/46`
получен `3/45` на 157 байт. Сумки 0/21, Сила 0/82, журнал и мир открыты.
Адресный охват 2 667 (+9), полный статический 865 (+10), частичных
привязок 304 (+5) в 19 реестрах. M6, принято 0/12 полных областей.
[Доказательства и следующий участок](../research/client455-mastery-quests.md)

# Частичная проверка 175 — достигнуты показатели развития

11.11.2026. Сборка `0280bf77…` x86. Базовые поля `3/4` применены для карты
0, инвентарь `3/6` разобран на 3 сумки и 21 запись, Сила `3/10` на 82 записи.
Старые владельцы не создали ни одного предмета и ни одной записи Силы.
Следующий ответ `3/8`, 322 байта, ждёт обработчика. M6, принято 0/12.
Адресный охват 2 658 (+8), полный статический 855 (+8), частичных привязок
299 (+6) в 18 реестрах. Мир не достигнут, финальный прогон без падения.
[Доказательства и следующий участок](../research/client455-initial-download.md)

# Частичная проверка 174 — получен ответ базовых данных

11.11.2026. Сборка `c85bd40d…` x86, статус `PARTIAL_WAITING_FOR_BASE_DECODER`.
После принятого выбора пройдены надголовная шкала, панель цели, меню и
счётчик подземелья. Клиент отправил `3/3` без payload, получил `3/4` на
431 байт. Фатального исключения в финальном прогоне нет. Запрос инвентаря
не отправлен, мир не достигнут. На стенде прошли четыре кадра.
M6, принято 0/12. Адресный охват 2 650 (+20), полный статический 847 (+20),
293 частичных привязки (+17) в 17 реестрах. Декодер 455 `3/4` на RVA
`16bea0`, старый `3/6` по-прежнему указывает в несовместимую ветку.
[Доказательства и следующий участок](../research/client455-target-windows.md)

# Частичная проверка 173 — пройдено окно группы

11.11.2026. Сборка `59122c67…` x86, статус `PARTIAL_KNOWN_FAILURE`.
После принятого выбора вернулся инициализатор группы 19. Следующий
сбой в `CGUISelectedMobInfoWin::SetSprite`, собственный RVA `130a9f`.
Проверены два режима, 11 удалённых участников, восемь эффектов на сторону
и пять сообщений на контрольных данных. Реальные групповые операции
и мир предстоят. M6, принято 0/12. Адресный охват 2 630 (+25), полный
статический 827 (+25), частичных привязок 276 (+21) в 16 реестрах.
Запрос базовых данных исправлен на `3/3`, отправка ещё не достигнута.
Ответ 455 `3/4` предстоит восстановить. Старый обработчик `3/6`
нельзя считать его заменой, в 455 этот номер относится к инвентарю.
[Доказательства и следующий участок](../research/client455-party-window.md)

# Частичная проверка 172 — пройдены обмен валют, добыча и смена класса

11.11.2026. Сборка `917f69fb…` x86, статус `PARTIAL_KNOWN_FAILURE`.
После принятого выбора вернулись инициализаторы окон 13, 11, 36 и
подключение единственного Linker. Следующий сбой в окне группы 19 на
собственном RVA `13088f`. Компонентно подтверждены три кадра, восемь
сообщений, предел золота, комиссия и размеры валютных пакетов.
Мир и реальные операции открыты. M6, принято 0/12. Адресный охват 2 605,
полный статический 802 из 37 871, частичных привязок 255.
[Доказательства](../research/client455-service-windows.md)

# Частичная проверка 171 — пройдены окна изготовления и улучшения

11.11.2026. Сборка `c9aeaf27…` x86, статус `PARTIAL_KNOWN_FAILURE`.
После принятого выбора персонажа вернулись инициализаторы окон 15 и 16.
Следующий сбой в `CGUIExchangeWindow::SetSprite`, собственный RVA `130fff`.
Проверены три группы рецептов, шесть ячеек улучшения, 14 сообщений и
четыре кадра, а также общая навигация по страницам в магазине NPC.
Обычное наполнение рецептов, транзакции и мир открыты. M6, принято 0/12.
Адресный охват 2 562, полный статический 758 из 37 871, частичных привязок 217.
[Доказательства](../research/client455-item-work.md)

# Частичная проверка 170 — пройдены обмен и обработка руды

11.11.2026. Сборка `ad434f01…` x86, статус `PARTIAL_KNOWN_FAILURE`.
После принятого выбора вернулись инициализаторы окна обмена 23 и обработки
руды 12. Следующий сбой в `CGUIItemMakeWindow::SetSprite` на собственном
RVA `13066F`. Его исходная версия 455 инициализирует три панели.
Компонентно проверены 15 ячеек на сторону, 21 контрольная строка руды,
три сообщения, денежные поля и три кадра. Игровые сделки, переработка и
вход в мир предстоят. M6 продолжается, принято 0/12 полных областей.
Адресный охват 2 538, полный статический 734 из 37 871, частичных привязок 197.
[Доказательства](../research/client455-trade-ore.md)

# Частичная проверка 169 — торговое окно NPC пройдено

11.11.2026. Сборка `7d348e69…` x86 дошла до
`CPlayerTradeBoard::InitWindow → CGUITradeWindow::SetSprite` после принятого
выбора и завершённого инициализатора NPC-магазина. Сбой `CSprite::GetSpriteXL`
на собственном RVA `12FF6F`. Статус `PARTIAL_KNOWN_FAILURE`.
Сетка, четыре суммы, страницы и три кадра магазина проверены на ресурсах 455.
Поставщики настоящих предметов и торговые действия открыты. М6 продолжается,
вход в мир предстоит. Ориентир около 25% (20–35%), принято 0/12 полных областей.
Адресный охват 2 517, полный статический 713 из 37 871, частичных привязок 178.
[Доказательства](../research/client455-shop-window.md)

# Частичная проверка 168 — навыки и Сила пройдены, дальше торговля

11.11.2026. `inventory/client455-skill-force-window-checkpoint.json` фиксирует
`PARTIAL_KNOWN_FAILURE` на сборке `83b60d77…` x86. После принятого выбора
персонажа вернулись инициализаторы навыков и Силы. Следом старый
`CGUIShopWindow::Init/SetSprite` падает в `CSprite::GetSpriteXL`, RVA `12F8BF`.
Полная фабрика и мир открыты. Текущий этап M6, ориентир около 25% (20–35%).

Компонентно проверены штатные окна с пятью вкладками, три расы для Силы,
сообщение помощи и четыре реальные строки EDF. Полное автоматическое
наполнение требует переноса управляемых объектов в пакеты и связи со строками.
Адресный охват 2 501 (+22), полные листинги 697 (+24) из 37 871. Всего 166
частичных привязок в 11 выборочных реестрах. [Проверка 168](../research/client455-skill-force-window.md)

# Частичная проверка 167 — обе панели пройдены, дальше навыки

11.11.2026. Актуальная проверка `inventory/client455-unit-windows-checkpoint.json`
имеет статус `PARTIAL_KNOWN_FAILURE`. Собственная сборка `23332d3f…` x86
прошла сборку и линковку. После принятого сервером выбора персонажа вернулись
инициализаторы UnitTuning, UnitStorehouse и старой экипировки. Следующее окно
`CGUISkillWindow` падает в `CSprite::GetSpriteXL` на RVA `1305EF`.

UnitTuning получил восемь пакетов по 200 ячеек и окно 34. UnitStorehouse получил
пакет из четырёх ячеек и окно 35. Проверены начальные состояния, три сообщения
и три кадра. Полный игровой цикл обеих панелей открыт. Прирост охвата анализа
16 адресов и 16 полных листингов. Всего 2 479 и 673 из 37 871. Частичных
привязок 148 в десяти выборочных реестрах. Оценка M6 около 25% (20–35%),
полных областей 0/12. M9 открыт.

[Подробности и открытые участки](../research/client455-unit-windows.md)

# Частичная166 — Linker startup пройден, дальше UnitTuning

11.11.2026. Текущая точка: inventory/client455-board-startup-checkpoint.json,
PARTIAL_KNOWN_FAILURE. Own fe40637c…/x86/entry183720/2369024bytes, build/link0.
Обычный MainGame использует5 банков по10 ячеек/window3;50 owners,8 кадров и
настоящее HWND сообщение через CBoardManager проверены. Live выбор принят,
Linker startup вернулся. Следующий старый UnitTuning.Init/SetSprite падает в
GetSpriteXL own13028F; мир не достигнут. 17 классов фабрики/37 отсутствующих,
без утверждения эквивалентности имеющихся17. Пять начальных окон фабрики и
поздняя одновладельческая привязка hotkey тоже открыты; остальные Belt guards
сохраняются. Всего54: прежний regex пропустил CBlackListBoard12bytes/slot30;
старые53 считать неполной выборкой. Полный potion/hotbar gameplay обязателен.
Анализ2463/657(+2/+6),
137 partialbindings прежние;0/12,M6/M6F/M7/M9OPEN,25%(20–35%) прежние.
Before167 сохранён:197файлов,7502253новых/4150820общих байт, own fe40637c….
Полный клиент не копировался.
Подробности: research/client455-board-startup.md; очередь ниже в next-steps.md.

# История165 — инвентарь пройден, дальше фабрика455

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

# Частичная164 — Options455, Create_UI завершён, следующий инвентарь

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

# Частичная163 — MobControl455 подключён, следующий отказ OptionWindow

11.11.2026. Own ae592e2181809f8fd06a17a5bcbf5b7b82c6185c4160b043f4e043f8416cb89a,
x86/entry1821E0/2362368bytes,182client/67engine/20kernels/build-link0.
client455_mob_control_port.py + native/client455_mob_control.h/.inc подключают
реальные16детей/3commands/HP-FP/stepEXP/extraresource/clip. HP/FP signedclamp0,
130x11/%6d / %d; EXP0..1/9pixelsteps/90pixelremainder/99.989998textcap.
Korea name trims7bytes ifstrlen>7,other10preserve;countryvirtual53bothpins verified.
Extra resource setter reproduces IMUL32wrap/signedIDIV;actual4711F0 producer
equipped12/13 identified,ordinaryprovider ещё не перенесён. Tooltip IDs3CE/3CF/39D
через legacyadapter,fullpolicyopen. SetMobState имеет только старую декларацию,
observedcaller/body не найден,не придумывать реализацию.

Shared native/client455_gui_move.inc заменяет обычный MoveObjectMgr,сохраняет
avatar/filter код uiglobal. Reset/reuse record,timestamp0inactive,duration0immediate,
halfPiDB0FC93F,sin(double) roundedfloat,exactendpoints,waves/accel. Production
использует real timeGetTime; explicit clock API для воспроизводимого replay.
Native10c89a6e/mob-control-001 PASS:16children/3actual HWND messages/4viewedGPUframes,
signed/EXP/resource/namebranches иmovementreplay170/129/wrap/endpoints/accel.
Controlledinitialresource стоит0/0 доsetter;не принимать заживойproducerstate.

34fullfunctions/3119instructions bothpins;функции2375(+28)/559(+30),IDA37870.
22новых partialbindings/18standalone,всего91выборочный,не totalrestored.
Final live ae592e21/selection-live-taiwan001 auth/list/Enter/result0,
MobControlInit вернулся;nextoldOptionSetSprite/Init own12ED3F/GetSpriteXL.
Own caller270C6=FF506C/return270C9,vtable1F0B60slot6C→OptionInit998A0 проверены.
Candidate stack scanнеunwind. Междунимивернулись4Init;это неfullbehaviorприёмка.
PreEnterPNG просмотрен:освещённыйперсонаж/старыйBeta0.738UI. World/M9OPEN,
0/12,25%(20–35%) прежние. Gate mob-control-checkpoint/currentassessment.

Before163135files=7193032private+3623572sharedbytes;до164 snapshotexact163.
Native30assets/17904385linkedbytes/0newpoolbytes. IDAe410717f saved/closed/list0,
nativejobsdone,originals/servercode/config untouched,privatehandoffremoved.
СледомOption455:primaryvtableRVA6E4C1C,VA7113C0/713060/714210 pointer-only.
Уточнение прежнего MobControl6AE720:Update,неBound. Доказательства/продолжение:
research/client455-mob-control.md,docs/next-steps.md. Навыки из обсуждения не установлены.

# История162 — Recall455 подключён, следующий отказ MobControl

11.11.2026. Own e929b1ec2f57f5a86415a1ce32d7992bcf6a47efeddd7813ea1bea5b8db8f19f,
x86/entry181DA0/2360320bytes;182client/67engine/20kernels/build-link0.
client455_recall_port.py + native/client455_recall_window.h/.inc подключают
настоящие окно/строки Recall455 к обычному клиенту. _recall_info40bytes/name+0/
index+4, fullDWORD HP/FP, real summon/common/item24 skins, cover/scroll/resize.
Удаление намеренно сохраняет высоту content как455. EXP geometry не clamp100;
числовой display cap99.989998. Initial target state/index undefined, own sentinel
явно ограниченный выбор. TakeOutLink/settings/fullAnimusproviders ещё partial.

Finalnative a5e7bd7a/recall-001 PASS: восемь контрольных записей, пять GPU-кадров
просмотрены. Первый19efa851 ошибочно ожидал140px; реальные ширины132/132/89,
исправлен oracle. 39fullfunctions/3039instructions bothpins; пять setter heads
определены только в рабочей IDB по ASM, индекс37865→37870. HexRays positive-SP
warnings не используются как доказательство; отсутствие xrefs не равно deadcode.

Final live e929b1ec/selection-live-taiwan002: auth/list/Enter/result0,
RecallInit вернулся; следующий fatal C0000005 own12E81F/GetSpriteOrgXL+5F внутри
MobControl.SetSprite/Init. Это подтверждено own FF506C caller26CFE/return26D01 и
own MobControlvtable1F066C/slot6C→Init94330, порядком source Create_UI. Кандидаты
стека не unwind, старый RecallA0193 среди них не является доказанным caller.
Первыйlive001 не дал stack candidates из-за чтения через границу доступной памяти;
helper читает до256DWORD individually, сохраняет только ownPE RVAs;002 повторён.
PreEnter002 PNG просмотрен, персонаж освещён, Beta0.738 label остаётся.

Gate recall-checkpoint PARTIAL_KNOWN_FAILURE/current assessment. World/fullUI/
M6F/M7/M9OPEN,0/12,25%(20–35%). Функции2347(+37)/529(+39),25новых частичных
bindings/17standalone,всего69выборочных; не общий итог восстановления BIN.
Before162124files=7189195private+3487736sharedbytes сохранён;до163 snapshot162.
Native34assets/81615873linkedbytes/0newpoolbytes. IDAbac5c81d saved/closed/list0.
Серверные файлы/настройки и оригиналы без изменений. Следом MobControl455:
pointer-only vtableRVA6DFB24,VA6AD3C0/6ADA40/6AE720; сверять до переноса.
Подробнее research/client455-recall.md. Обсуждавшиеся новые навыки не установлены.

# История161 — CharInfo455 подключён, следующий отказ Recall

11.11.2026. Own 3ebd9a7dcd40b4843352f75e505a585ec65149899891f3885380040703109b08,
x86/entry181DA0/2360320bytes;182client/67engine/20kernels/build-link0.
RF455CharInfoView подключён к настоящему CGUICharInfoWindow:3pages5/2/4sections,
23value owners,mastery/resist/extras,real skins/race layout/mouse/wheel/resize.
Nativedb389785:3races/6GPUframes PASS;все final images просмотрены/visualmanifest.
Исправлена naturalheightheader:sheet1x4 относитсятолькокhighlight. Ранние33923840/
161a997cкадрыгеометриюнеподтверждают;native проверяетheader/title/tab coordinates.
60fullfunctions/6095instructions bothpins;18partialbindings,12standalone retained.
14прежних TabBoardbindings подключены кordinary owner path,11standalone retained.

Final live 3ebd9a7d/selection-live-taiwan001:auth/list/1/14→1/15/22/result0,
CharInfoInit пройден;следом C0000005 вoldRecall.SetSprite/Init,own12E8FF/GetSpriteXL.
Стек982E1→A094E→9FFD7→26753→26021;virtual FF506C/ownvtable1F1034slot6C сверены.
World/fullUI/M6F/M7/M9OPEN,0/12,25%(20–35%). Gate char-info-checkpoint.
Первый a51live не послал1/14 из-за inactive GetMessage;он не принят как проход.
Owned-child driver теперь просит local WM_ACTIVATEAPP background updates перед
отложенным Enter;OSfocus/globalkeys не меняются. FinalpreEnterPNG просмотрен.

Открыты dynamic action/equipment providers/tooltip/help,mastery max/resist bounds
уlegacycallers,fullmetrics17/18/lifecycle/malformeddomains. Не подставлять лимиты.
Следом настоящий Recall455:primaryRTTIvtable6DFD14,Init6AF7F0/skin6AFC20/bound6AFC90.
Pointerdiscovery не behavior proof. Source:gamewindow/recall/guirecallwindow.cpp.
Функции2310(+48)/490(+51),44выборочныхbindings,необщийперенос. Coarse не повышен.
Before161113files сохранён(6427189private+4047560sharedbytes). До162 snapshot161.
Native sharedpool30assets/15.41MBlinked/0newbytes. Originals/servercode без изменений.
IDAa2513525saved/closed/list0. Подробнее:research/client455-char-info.md.

# История160 — настоящий TabBoard455, CharInfo ещё не подключён

11.11.2026. Новая зависимость client455_gui_tab_board.h/.cpp:5-section пример,
реальные skins/NDLanguage/GPU,раскрытие/membership,reflow,scroll observer,
resizeclamp,сохранённые borrowedchildren/RAII/Dmalloc. Nativefinal
work/m9/a7aba19d/tab-board-001 exit0,4GPUframes/3frame relations PASS.
Первый неверный fullreload equality oracle отклонён:style0 resetthumb6x18,
zeroAmount сохраняетстарыйразмер. Новыйoracle проверяетэтотreset иheaders.

FullASM/CFG17functions/1318instructions pinnedboth455.14partialsourcebindings.
Generator подключаетобъекткfacade library,но normal map НЕ содержиткласс:
старый CharInfo пока не используетего. Gate tab-board-checkpoint PARTIAL_COMPONENT_ONLY.
Normal7354a9313c6eb43db1f267a8f575c456818021ad6284699984470285cc3c571e,
x86/entry17FA40/2349056bytes,182client/67engine/20kernels/build-link0.
Runtime sections равныexact159кроме проверенного linkerdebug timestamp
RVA210254 (2byteschanged,field4bytes equalsCOFFtime вкаждомPE). Новыйliveнеповторялся;
последний159стек CharInfo.SetSprite/Init остаётсяblocker. Assessment сохраняет159
какhistorical acceptedpartialruntime.25%(20–35%),0/12,M6/M6F/M7/M9OPEN.

Before160 сохранён104files:7027314copied/3366723shared;не перезаписывать.
До161 snapshot160 через --checkpoint inventory/client455-tab-board-checkpoint.json.
ПерваяcompileошибкаWindows minmacro исправлена;consumer/link/native PASS.
Функции2262(+16)/439(+17) из37865;выборочно26sourcebindings,необщийперенос.

Следом fullCharInfo outer/3pages/23valueowners/mastery/race/providers. Discovery
RTTI3файла и44decompсохраненыprivate charinfo160-reference/discovery-unverified.json,
это ещё не принятые полныеinstructions. Подробныеадреса/шаги/границы:
research/client455-tab-board.md. Owned IDA5f9b1aa3 saved/closed;nativejobsdone.
Оригиналы/сервер не менялись;общийpoolnative28assets/15.34MBlinked/0newbytes.

# История159 — верхняя панель455, следующий сбой CharInfo

11.11.2026. Own afb30309dbb1c14058ef0d9a2b9b8e055ff466ef3c3f4335846a1eb5518c41ee,
x86/base400000/entry17FA40/2349056bytes;182client/67engine/20kernels,build/link0.
Engine unchanged. Gate inventory/client455-hud-checkpoint.json PARTIAL_KNOWN_FAILURE.
Before159=точная158/92files сохранён,не перезаписывать;до160 сохранить159.

client455_hud_port.py+hud.inc/members.inc подключают настоящие Gauge Init/
SetSprite/SetGauge/SetLevel к normal sources:main4/common1/EtcUI49,4полосы,
17children,zero-max→1,unsignedclamp,signednumbers,уровеньBYTE/centering.
Четвёртая vertical bottom anchored,цветпороги.2/.7. CharInfo value owners3/9..12.
Использован существующий CGUIImageText455,не старый CGUINumber. Нет gaugeexp alias.
FullASM/CFG11+8functions/1406instructions совпалиbothpins. Native
work/m9/7ca856c6/hud-001:3GPUкадра просмотрены,threshold7/callbacks/reload,
changed==reloaded!=initial,Dmallocbalanced. Не запускались прежние большие suites.

Actual live work/m9/afb30309/selection-live-taiwan001:tx1/14→rx1/15/22/result0,
GaugeInit пройден по порядку Create_UI. Следующий unhandledC0000005:
own12C53F GetSpriteOrgXL ← Tile.SetSpriteInfo97288 ← CharInfo.SetSprite74366 /
Init73301 ← Create_UI26729. Старый CharInfo использует inventory/action6/7.
Мир/управление НЕ достигнуты,полныйUICreate не завершён. Handoff удалён.

Function2246(+15) адресных/422(+19) fullASM-CFG из37865;5новыхчастичных
sourcebindings,всеговыборочно12,полнаяequivalence/общийперенос не подсчитаны.
Audit/research:client455-hud-reference/native/checkpoint иresearch/client455-hud.md.
IDA8c2a0833/7f0c7676 saved/closed;nativejobs terminal. M6/M6F/M7/M9OPEN,
0/12областей,25%(20–35%). Дальше настоящий CharInfo455/остальнойMainGameUI.

По вопросу о навыках прочитаны первоисточники Habr→GitHub. find-skills —
поиск/установка,не reverseengineer. improve-codebase-architecture — выборочный
audit адаптеров/сборки/ownership,не массовыйрефакторинг до доказанного455behavior.
grill-me — опрос о решениях;M9 уже определён. Последние два имеютзависимости
grilling/codebase-design/domain-modeling. Установка пользователем ещё не запрошена.

# История уточнения учёта функций и разведки159

11.11.2026. По запросу пользователя уточнён docs/function-coverage.md:
индексация37865 / адресные материалы2231 / полный ASM-CFG403 различаются
с переносом и соответствием поведения. 7 точных sourcebindings последних
157–158 проверены по текущим SHA файлов; все complete_equivalence=false,
один setter пока не подключён. Это выборочный учёт, не весь перенос и не
ноль восстановленных функций. Повторный разбор не увеличивает уникальные
функции; изменения состояния уже учтённых RVA показывать отдельно.
Проверка отбрасывания неполных доказательств/реального156 PASS.

Before159 уже сохранён: manifest92files,7,622,846bytes copied и2,680,893
shared с immutableprior snapshot. Не перезаписывать. Ownsource/PE158 не менялись.
В159 найдены RTTI/vtables MainGame/Gauge/GUIWindow/EquipBoard: скрипт
discover_client455_hud.py и inventory/client455-hud-discovery.json.
15 непроверенных decomp сохранены в
artifacts/client455-progress/hud159-discovery/decomp-unverified.json.
Это только разведка; не приняты fullASM/CFG/семантика, счётчики не повышать.
Ориентир: Gauge SetSprite использует target main4/EtcUI49, Init создаёт
четыре полосы; назначение четвёртой и полный MainGame route ещё проверить.
Owned IDA ae5a3b1a saved/closed. Native тесты не запускались повторно.
Следом настоящий HUD455, затем следующий реальный отказ. M9OPEN.

# Частичная158 — сервер принял выбор, достигнут MainGame::Create_UI

11.11.2026. Own df69c7efc4e996ce888bc95f45004073464caa5116dd7610d0ca8e35e1c21adf,
x86/base400000/entry17FCD0/2349568bytes.182client/67engine/20kernels,build-link0.
Engine unchanged. Gate selection-checkpoint PARTIAL_KNOWN_FAILURE,не fullPASS.
Before158 сохранёнexact157/69files:7,560,626bytes copied и2,020,573shared only
withimmutable prior snapshot. Originals/build outputs неhardlinked.

FullASM/CFG6+3functions/689instructions pinnedboth455. RVA16B920 request1/14/1;
16B9D0 response1/15/22:WORDresult0 lowBYTE stored,serialDWORD2,dalant64@6,
gold64@14. Storesoccur evenonerror,beforeReceiveResponse. Main skipTutorial==1
choosesmain,allotherDWORDvalues choosem_Course dummy. Boundedshort rejectsopen.
Sourceprotocol declarations corrected13/14→14/15/22;dispatcherboundedguard.
Source files:client455_selection.h/.inc/port.py. GetterSelectedSlot usesactual
COURSE enumglobal withoutcrossTU typeguess. Native work/m9/836ac6ec/selection-001
actual encrypted fragmented dispatch/4wallet routes/WORD256→BYTE0/signed64 PASS.

Livec0b63c86 actualEnter→success hitoldGetEquipItem inAvatarhandoff. Fixedtyped
6defaults/11worn transfer andcopiedskipTutorial. Target419F50→46C130 clears/copies
base640/retains;sourceCopyRetainedState455 semanticbasecopy,derivedowner/fadeleft,
noPRNG. GetDefault41A000 recorded. Nativeownerwork/m9/7f0d9d32/player-owner-001
newdefaultref/PRNG/resources/otherAvatarwear PASS;3priorPNG equal157.
Rawvptr/padding/selfcopy/aliases/allCloneLifecycle NOTaccepted. FullEventJoin7BB470
stillhasunported equipment-board1virtual176/tutorialbranch;ordinarynonzero skip
path exercised. Mouse7AA360/keyboard7AA5A0 recorded,notfullUIportclaim.

Runneraddedselectionmode:afterrealLoginframe+followingRenderreturn posts
WM_KEYDOWN/UP VK_RETURN onlytoownedchild HWND afterPIDcheck;nofocus/systeminput.
Livefinalwork/m9/df69c7ef/selection-live-taiwan001:
tx1/14/1→rx8/5/9→rx1/15/22→select-result0. Handoffremoved,noaccountkeys/rawpackets.
PreEnterimageinspected,lightroutepreserved. OneUNHANDLED C0000005 afterselection:
own12C8AF GetSpriteXL+5F ← SetSpriteInfo@CGUIObjectAni ← SetSprite/Init GaugeExp
← Create_UI/Create MainGame ← GameMainLoop MainApp. Client reachesexisting
MainGame creation,NOT renderedworld. OwnmapSHA2193f2158d2ba0ab1a6eff8fcd7aa4efdcff5d67bc05dcdf1d4c886d0d1d5eb9.
LegacySP_ID_GAUGE_EXP2 requests./SpriteImage/gaugeexp.spr;absentinoriginal/lab/
zh-tw. SpriteMgr bridge only5systemIDs. Needreal455HUD/atlas/provider/create,
not renamedoldskin/hidingwidget. MainGame UI isthenext159.8/5/9contractstillopen.

Functionevidence2231(+6)/complete403(+7),of37865;4newsourcebindings,totalsfull
implementation/equivalence null. Activepoint158 explicitlyretainsknownfailure.
Before159 preserveexact158 viautility;before158=157 staysimmutable. No server/
originalmods,nobigunchangedsuites. IDAb44716bd saved/closed/list0,nativejobsdone.
M6/M6F/M7/M9OPEN,25%(20–35%),0/12. Research:client455-selection.md.
Ниже исторические записи.

# Частичная157 — освещение живого персонажа восстановлено

11.11.2026. Own88dc3d11da68117f327510e40162a27ab6e46089a1446b62af1416c56b3f9917,
x86/base400000/entry17F850/2348544bytes;182client/67engine/20kernels,build/link0.
Engine unchanged. Gate inventory/client455-actor-lighting-checkpoint.json PARTIAL.
Full ASM/CFG3functions/208instructions на обоих pins:3CE7A0 actual map light,
04D230 Player wrapper,3CEA00 fullBOOL/DWORD setter. Код в tracked
client455_actor_lighting.inc/port.py, generated source через prepare script.
Direction negated,ambient light RGB1,diffuse+.15/.1/.1,ambientRGB+.2,
specular(updated diffuse*.3)/alpha1/power10;afterimage priority overblink.
Header476 теперьDWORD m_dwBlinkColor455,resource/item584/592 сохранены.
GetMatLightFromColor не менялся:ambientRGB/412,ноalpha BOTH /255;не повторять
ошибку первого теста. NoBSP/nooverride color уоригиналаundefined,ownthrowexplicit.

Native work/m9/5f0a7c7b/player-owner-001 exit0:actual lobby12cases,перенос материала
вреальнуюэкипировку иGPUdirection PASS;3прежнихPNG равны156. OrdinaryTaiwanLogin
work/m9/88dc3d11/login-frame-taiwan001 PASS. Live samehash login-frame-live-taiwan001:
real auth/game0/character178,370frames/8000ms/unhandled0,Renderreturn PASS.
Сравнение кадров156/157 просмотрено:персонажбольше непочтичёрный,лицо,
одежда/оружие различимы. Не полнаяpixel/reference stageэквивалентность.
Handoffудалён,секретынесохранены,сервер/оригиналынетрогались.

Functionmetrics2 225(+3)/396(+3) из37 865;3точныепривязкикsource иruntime
в actor-lighting-bindings.json. Дваlightingметода retained ordinary PE;
SetBlink455 толькоnativeprobe,OPT:REFremoved ordinary;егоигровыеplayer/ground
производители ещёнеперенесены. Fullsourcefunction/equivalence totals null.
Functionhistory исправлен вschemaobject/measurements (list ломал generic
manifest traversal);prepare/build послеfix прошли. Последнийnative staging
newpool280bytes,не новаякопияклиента. Общаяstorageописьнеповторялась.

Следующий158:сохранитьточную157 вbefore158 доordinaryedits,проверить target
Logininput/Enter/request/reply/nextstage и перейти креальномуworld/control.
Before157=156(50files) сохранён. M6/M6F/M7/M9OPEN,25%(20–35%),0/12.
Research:research/client455-actor-lighting.md. Ниже исторические записи.
IDA c28cc224 saved/closed/list0. Три установленные функции получили имена
RF455_Actor_MapLight/Player_MapLight/Actor_BlinkColor в рабочей IDB; функции
не добавлялись в бинарник, это имена доказанного разбора. IDA named674.

# Учёт функций — 11.11.2026

По запросу пользователя добавлены docs/function-coverage.md и машинные
inventory/client455-function-coverage.json, client455-function-history.json.
Свежий survey первичного BIN: 37 865 функций, 1 296 IDA library. Из 158
старых отчётов сверены 3 717 code ranges: 2 222 уникальных владельца IDA,
393 с автоматически подтверждённым полным листингом/CFG, 594 292 unique bytes.
Пять неразрешённых адресов исключены. Это backfill baseline, не сегодняшние
новые реализации; счётчики перенесённых/полностью эквивалентных функций null,
а не 0: старые групповые отчёты не дают такого числа. Не выдавать 5,87% охвата
за готовность BIN. Срезы сохраняют прирост; исходные 25%(20–35%) — только
грубая отдельная оценка по подсистемам. Проверены неполная пагинация, дубль,
обрезанный CFG/хвост и реальный raw156 (3 функции/225 инструкций).
Начиная со следующего участка нужна точная RVA→source symbol→scope/gaps→
runtime evidence связь, включая частичность. Не пересчитывать неизменённые
большие игровые suites ради статистики. Own156 не менялась, M6/M9 OPEN.

Освещение157 ещё не перенесено. Предварительный статический разбор
44D230→7CE7A0: у цели после GetMatLightFromColor инверсия направления,
ambient light RGB=1, добавки diffuse/ambient и specular/power10; у старого
CResObject этого нет. SetBlink7CEA00 пишет472 enable/476 DWORD color, а legacy
поле m_bIsHide ошибочно именует цвет. Не менять sizeof584/592 и не подменять
свет белым. Полные ASM/CFG и оба pins ещё нужно зафиксировать до переноса.
Частный preliminary: artifacts/client455-progress/lighting157-reference/preliminary.json;
он не является завершённым разбором и не включён в новый счётчик.
IDA b254c2c8 saved/closed, list0. Исходники/сборка/сервер не менялись.

# Частичная156: живой кадр выбора, неверное освещение —10.11.2026

Own68e02c3dcbf557c5a124e769c0c124884a71b50a367288b56efa3f6039807d55,
x86/entry17F710/2348032bytes. Gatecombat-transition-checkpoint PARTIAL.
Live launcher/game-entry/character reply проходят;полученнастоящийкадрвыбора
work/m9/68e02c3d/login-frame-live-taiwan001:364frames/8000ms,unhandled0.
Пользовательувиделанимацию;персонажвиден,нослишкомтёмный. Мирещёнедостигнут.
44BE00 переходоружия/щита восстановленбезстарогоUMSguard:animation2/1,
fade1/2,lowBYTE(intFPS),0→60;нативныйmounted/unchanged тестпройден.
Login используетtyped getters и12physicalslots. Target53BBCD/53BC1F
подтвердилиCreateEffect/DestroyEffect,которыхневхваталодляgradematerials.
Начальныйдиагнозтипапредметабылошибочным:общаяthrowветкавызываласьпри
неинициализированныхgrade materials. Этоисправлено;временнаядиагностикаубрана.
Полный455Login/SetActionнепринят;targetCreateхвостневерноразделёнIDA.
Nativework/m9/076242a0/player-owner-001;3assembledPNGравны155.
Before157 сохранена точная156,50файлов;before156=155,50файлов.
Следующее:реальноеосвещениекарты→CResObject→material/CharIF,безподменыцвета.
GameBarнеустановлен,GameDVRбыл1. По просьбепользователя AppCaptureEnabled
иGameDVR_Enabled выставлены0 толькоHKCU;пользовательподтвердил,чтозапрос
Storeисчез.Backup:artifacts/environment/game-capture-20261110-232356-911.json;
возврат scripts/Set-GameCapture.ps1 -Restore -BackupPath <backup>.
Пароли/ключи/rawpacketsнесохранены;handoffудалён;сервер/оригиналынетрогались.
IDA95d6f34d/43f6123f saved/closed. M6/M6F/M7/M9OPEN,25%(20–35%),0/12.
Нижеисторическиезаписи.

# Частичная155: игровой вход принят, выбор ещё падает —10.11.2026

Own da42b501a1ab0c68c9c47a3cf2c51479b43f251623de1d6d6813a4c9d743e4ad,
x86/entry17F660/2347520bytes,182client/67engine/20kernels,build/link0.
Gate inventory/client455-live-login-checkpoint.json PARTIAL. M6/M6F/M7/M9OPEN.
Обычный Taiwan Login/кадр PASS;реальный launcher-auth accepted иgame1/1→1/2
result0. Исправлены компактный1/9(178bytes) иlegacy registered upgrade.
Bounded14+164*count→506 normalizer не считаетсяunsafe overread equivalence.
462170 пишеттолькоBYTE113;16ASM instructions/1CFG обаpins,realpayload PASS.
Три assembledPNG равны154;fullCharacter clone/appearance по-прежнемуOPEN.

Live после1/9 доходитдовыбора иявноотказываетвlegacy GetEquipItem:
own10B23←CPlayer::SetAction555FE,SetCombatMode/CAvatar stack. Следующим переносить
combat-mode animation/fade черезtyped owner;унаследованный legacySetAnimation
новомуwrapper не подходит. Живой мир не достигнут;1/21payload1 не принятцеликом.
Live finalwork/m9/da42b501/login-frame-live-taiwan001;ordinary Login-frame-taiwan001;
native playerownerwork/m9/ae382ba2/player-owner-001. Пароль/rawpackets не сохранены,
handoff93 среальнымключом удалён. Сервер/оригиналы не менялись;IDA9079cdac saved/closed,list0.
Resource manifest добавляет только наблюдённые зависимости и сохраняетпредыдущие;
485missing catalog entries отсутствуютиуоригинала;ихблокирующаяроль не установлена.
Передследующимordinaryedit сохранить155 вbefore156. Before155=точная154,52файла.
Оценка25%(20–35%) неизменна,полныхобластей0/12. Ниже исторические записи.

# Проверенная база154 и живая сеть —10.11.2026

Own31d24ab9481f56218431661815cd58077b59fae7d79ad123dc0c5c8758bd5426,
x86/entry17F430/2347008bytes,182client/67engine/20kernels/build-link0.
Gate inventory/client455-player-owner-checkpoint.json PARTIAL.
Primary12-slot CPlayerProc подключён кnumeric/frame/pose/render иреальным
Avatar/condition/skillboard owners. Default garment возврат0..4 восстановлен.
Реальный кадр персонажа просмотрен;19draws/12657pixels;снятие3752changed,
повторное надевание даёт exactPNG. Controlled camera/light,не fullworld actor.

Member-copy404A40/4042D0 сохраняетстарыеactor/currentProc иpayload ссылки,
не rand/AddRef;queue527E70 отличается. C2280 исправлена отдельным owned state.
FullCharacter/Avatar clone lifecycle ещёOPEN:probe компенсация legacyowned
aliases/refs толькодляcleanup,не productionfix. Другие mixedGetNormal/Equip,
populatedcloak/Siege unlink/board35/UI/movement,Unit/particle/metrics OPEN.
Native final work/m9/5544e512/player-owner-001;render6ebebfad/equipment-draw-001,
6PNG равны153. Source proofs24functions/1859instructions/91CFG оба455pins.

OrdinaryTaiwan Create/Login/account3Avatar PASS. Login195/3000ms просмотрен,
ожидание/Beta0.738,7firstchance(6C++/1threadname),unhandled0. Korea повтор был
остановлен правилом одного экземпляра при открытом оригинальном клиенте.
Taiwan используетсвою штатную policy,не unconditional bypass.

Пользователь запустил rf455-v0.4.0 иподтвердил originalclient worldentry.
Read-only ports/processes/hash:именно0.4.0,27830game/27831launcher/8080web;
RFOnline/RF_Online.bin SHAprimaryb1b5…;rflauncher38e32658… совпалскомплектом.
OwnWinMain действительно TCPconnect27830→engine/Miles. Отдельныйlauncher
auth6C/03→6C/04 accepted,получен16bytekey сprefix rf1:(DWORD976316018).
Game-auth собственнойPE ещёНЕ проверен. Тестовые данные находятсятольковчате,
не сохранятьих,accountID/key/rawpacketsврепозиторий. Серверне менять/строить.
Новые отчёты:inventory/client455-live-server.json,client455-live-launcher-native.json.

Exact154 уже сохранена вbefore155/manifest.json,52файла;не перезаписывать.
Следующее:живойhandoff93bytes→ownclient,
первоефактическоерасхождениеworld-entry/bootstrap/registeredappearance→выбор.
Launcher private diagnostics artifacts/client455-progress/live-launcher155-reference;
GoIDA ownedf8bfc9ee иRF sessionb8517972 savedclosed;idb_list0.
Последняя storageописьостаётся20:56:14:158.84/43.19GiB,нефизическийзамер.
Удалений0,wholeclientcopy0;обычнаяоценка25%(20–35%),0/12fullareas,M6/M9OPEN.
Исследование:research/client455-player-owner.md иclient455-live-launcher.md.
Ниже исторические записи;их «текущая» база относится к указанной версии.

# Сверка готовности и текущих исходников — 10.11.2026

Проверенная база остаётся153/3296a413…;25%(20–35%),0/12полных областей.
Незавершённая154 не включена: текущий build_exit1,C2280cavatar.cpp:162,
Avatar copy/Clone после перехода к owned equipment state. Ранее154линковалась,
но runtime не проверена. Exact153 сохранена before154/manifest.json,53файла.
Далее: восстановить корректное копирование, собрать, проверить настоящий
player-owner путь;затем обычные appearance/selection. Никаких shallow owned copies.
Инструмент оценки теперь раздельно фиксирует preserved runtime,current failed
build и intermediate candidate;старый запуск не выдаётся за свежую154.
Свежая опись20:56:14:158.84GiB logical/43.19GiB unique file sizes,ошибок0,
удалений0. Это не точная физическая аллокация. IDA21aeaaf3 сохранена/закрыта,
idb_list0. Подробности:docs/progress-report.md иinventory/client455-progress-assessment.json.
Приоритет отчётов:изменение обычного клиента/standalone/ближайший остаток/
здоровье сборки/основание общей оценки. Полный455feature denominator ещё неизвестен.

# Текущая проверенная база153 — 10.11.2026

Own3296a413…/x86/entry17B430,182client/67engine/20kernels,unresolved0.
Gate inventory/client455-equipment-frame-checkpoint.json PARTIAL.
CMesh/CEquip получили реальные Animation/FrameMove/end transitions,
однократный dummy scan,always state иследование event magic за actor/Spine/yaw.
WAV использует equipment position,не actor position. Virtual120(kind2) false
для обоих текущих wrappers;byte4=2 не означает ground. Полный ground открыт.
Настоящие ANI/модели/Miles и21контролируемая ветка конца проверены.
Обычные6default owners Avatar теперьCEquip;основной12-slot CPlayerProc ещё
не подключён. Это зависимость полного персонажа,не закрытая appearance.
Create/Login/account3Avatar PASS. Login65/3015ms просмотрен:ожидание/Beta0.738,
безauth;профиль9first-chance прежний,unhandled0. Шесть render PNG равны150.
Полные player/condition/UI/particle registry/выбор/мир/gameplay/M9 OPEN.
Оценка25%(20–35%),0/12полных областей,без повышения.
Доизменений exact152 сохранена вbefore153/manifest.json,52файла.
Перед следующими ordinary edits snapshot154 сequipment-frame gate.
OwnedIDA57ba692a сохранена/закрыта ранее;новыеIDA sessions здесь не открывались.
Native jobs завершены. Оригиналы/server неизменны,входныеEXE не исполнялись.
Последнийполный storageaudit16:34:07 —156.14GiB logical/42.96GiB unique file
sizes,не замер кластеров. Первый153pool+280bytes,финальныеframe/renderpool0;
новые собственныеEXE/maps/results есть. Старые стенды не удалялись.
Доказательства research/client455-equipment-frame.md. Ниже сохранена история.

# Текущая проверенная база152 —10.11.2026

Own579bc166…/x86/entry179A40,182client/67engine/20kernels,unresolved0.
Gate inventory/client455-char-info-values-checkpoint.json PARTIAL.
УстраненыWORDусечение Gen/Force/Def и пустые Hit/Avoid setters. Настоящие
valueowners14..18 принимают fullDWORD/float;три ordinarybasic rows используют
ихприInit/childregistration/style/position. Nativeactualwindow/currentAvatar
caller PASS. 70000 сохраняется как70000,не4464. Полные455metric getters,
mount/buff/typedconditions/refresh и23fieldlayout всё ещё не перенесены.
LegacycomparativeWORDarray setters/upgradeannotations иCRT/FP/unsafe domains OPEN.
Primary12-slot CPlayerProc ownership/Animation/FrameMove/Render/providers,
particle registry,выбор/мир/gameplay/M9OPEN. Оценка25%(20–35%) неизменна.
Свежие Create/Login/account3Avatar PASS;Login65/3000ms просмотрен,
ожидание/Beta0.738,безauth;9прежнихfirst-chance,unhandled0.
Exact151runtime сохранена доизменений:before152/manifest.json,52файла.
Перед nextordinaryedits snapshot153 сchar-info-values gate. IDAe3deb20c
savedclosed/list0;nativejobs завершены,установок/удалений нет,originals/server
неизменны. ФинальныйsmallUIprobe:work/m9/5519fe61/char-info-values-001,pool0.
Последнийstorageaudit16:34:07,156,14GiB logical/42,96GiB uniquefiles,не новыйзамер.
Pcode-only26ownerfunctions сохранены рядомсraw длядальнейшего fullplayer bridge.
Доказательства research/client455-char-info-values.md;нижесохраненаистория.

# Текущая проверенная база151 —10.11.2026

Own d1e44bb9…/x86/entry179970,182client/67engine/20kernels,unresolved0.
Gate inventory/client455-premium-state-checkpoint.json PARTIAL.
Установлены owners ранее неизвестных condition providers:442440 —network
PremiumDWORD436028,40BCE0 —Avatar combat bonuses24712/24716. Настоящий
producer57/12 подключён к обычному dispatcher иowned CNetworkMgr/Avatar state.
Проверены включение/отключение/ignoredstatus,12ставок,DWORD иfloat-биты,
границы payload57/49/1;неписаные поля явноunknown. Native actualowners PASS.
Полные Premium UI/window/icon481/post-update condition refresh не подключены.
Full12-slot CPlayerProc/Avatar owner/Animation/Render/condition/UI,particle
registry,выбор/мир/игровойцикл/M9OPEN. Процент25%(20–35%) не меняется.
Свежие normalCreate/Login/account3Avatar PASS;Login65/3016ms просмотрен,
ожидание/Beta0.738,безauth.9прежнихfirst-chance,unhandled0.
Exact150runtime сохранена до изменений:before151/manifest.json,53файла.
Перед nextordinaryedits snapshot152 сpremium-state gate. IDAdfba038a savedclosed,
list0,nativejobs завершены,установок/удалений нет,оригиналы/server неизменны.
Новыефинальныеstaging pool0;полныйstorage audit по-прежнему16:34:07,
156,14GiB logical/42,96GiB unique file sizes,не новый физический замер.
Доказательства research/client455-premium-state.md;нижесохраненаистория.

# Текущая проверенная база150 —10.11.2026

Own0f671964…/x86/entry179660,182client/67engine/20kernels,unresolved0.
Gate inventory/client455-player-visual-checkpoint.json PARTIAL.
Полные ctor/dtor455 исправили ошибку146:12физических слотов,не13.
Index12 попадает в последующие поля;собственный явный отказ — известное
ограничение,не принятая эквивалентность небезопасной ветке эталона.
Перенесены visibility450810 и PRNG ctor/copy;24ветки видимости/3PRNG контракта
проверены с настоящими ресурсами. Frozen PRNG oracle взят из бинарника.
Свежие Create/Login/account3Avatar иdraw-regression прошли;6кадров совпадают149.
Login65/3016ms просмотрен:lobby/ожидание,Beta0.738,безauth;9прежнихfirst-chance,
unhandled0. Полное владение controller/Animation/Render/condition/UI в обычном
CPlayerProc/Avatar,полный particle registry,выбор/мир/M9 остаются открытыми.
FrameMove4513E0 реально пуст;семантика flag442440/bonus-owner ещё неизвестна.
Точная149runtime сохранена до изменений:before150/manifest.json,52файла.
Перед следующими ordinary edits сохранить150 вbefore151 с новым player-visual gate.
IDA6a9e2ee9 saved/closed/list0;native jobs завершены,установок/удалений нет.
Оригиналы/server неизменны. Оценка25%(20–35%),0/12полных областей без изменения.
Последний полный замер storage остаётся16:34:07:156,14GiB по путям/42,96GiB
уникальных файлов;не точное число занятых кластеров. Новые финальныеstaging pool0.
Доказательства:research/client455-player-visual.md;оценка:docs/progress-report.md.
Ниже сохранена история,её «текущие» формулировки относятся к своим версиям.

# Текущее продолжение149 —10.11.2026

Own f4e62e48…/entry179630/x86,182client-67engine-20kernels,unresolved0.
Gate inventory/client455-equipment-draw-checkpoint.json PARTIAL.
Source Render(default/matrix)/fade/alpha/overlay604 producer иqueue pose/owners
перенесены. Native actualmodel7/14/7draws,2659visible/changedRGB;6frames,
8realunit/siege metadata cases,keyDWORD>255,grade113notbool;queuealiases/Start/
retain/release/cap256 PASS. Base/overlay byte-equal preserved148fixture.
Обычные queue Clear/Render реально вызывают новыеentrypoints;secondarygeometry
теперь удержана PE. Full13-slot CPlayerProc/Avatar route ЕЩЁ НЕ ПОДКЛЮЧЁН.
Particle adapter используетlegacyg_Particle1024/5clones;targetvectors/6clones/
one-attempt failure. Ненулевыеparticle/entitydraws не проверены,полныйrendererOPEN.
Обычные Create/Login/account registered3Avatar PASS;Login65/3016ms просмотрен,
lobby/ожидание,Beta0.738.9прежнихfirst-chance,unhandled0;нетauth/selection/world.
Оценка25%(20–35%) неизменна,0/12полных областей;M6/M6F/M7/M9OPEN.
Далее ordinaryplayer/pose/animation/providers →appearance/selection;registry
миграция отдельнообязательна. Queue/source proof ужеесть,не повторять.
before149 содержитточную148runtime;16exact148sourceinputs дополнительно
сохранены по прежнимSHA вbefore149/recovered-source/. До новыхordinaryedits
snapshot150 сgateequipment-draw. IDA0a6749ce saved/closed/list0,jobsзавершены.
Native final work/m9/0fdac5c0/equipment-draw-001,newpool0;оригиналы/serverнетронуты.
Подробности:research/client455-equipment-draw.md. Нижеистория.

# Текущее продолжение148A — 10.11.2026

Переоценка по запросу пользователя: выбранная сборка обеспечена; полнота
исходников455/ресурсов/спецификации не установлена. Около25%(20–35%) —
плановое суждение по12фиксированным областям, остаток65–80%; не функция
числа проверок или номеров этапов. Полных областей0/12, полный маршрут
вход→выбор→мир→игровые действия не пройден. Надёжной датыM9 пока нет.
Свежая опись16:34:07:156,14GiB по путям/42,96GiB уникальных файлов,
ошибок0,удалений0. Подробные факты/остаток:docs/progress-report.md.

PROGRESS:реальный source/backend иновая обычная сборка,не повтор статуса.
Gate inventory/client455-grade-overlay-checkpoint.json PARTIAL.
Own03637d6a…/entry1771C0;engine4c6652a5…;182/67/20/link0.
4реальныхMST/DDS,UVshader9/10,c92,secondarygeometry92E140/92FBE0,
archive flag8E75D0/E0 иOpen/Exists перенесены;21fullfunc/2863instr/239CFG/5data.
Нативно:2104materialbytes/frozen oracle,shaderstate/lifecycle,layer6/malformed,
7actual geometrydraws/2659bright modelpixels/2659changedRGB иarchiveflag1/0/17.
Обычные source CreateEffect/DestroyEffect действительно CALL load/release.
НО secondary geometry linker удаляет изобычнойPE:нет player-render caller.
Полный mesh-object renderer иCPlayerProc/Avatar ещё отсутствуют;не завышать прогресс.
Create/Login/account3Avatar новойPE PASS;Login66/3031ms просмотрен,ожидание,
Beta0.738. Нетauth/selection/world.9старых first-chance,unhandled0.
Оценка25%(20–35%),0/12полных областей;M6/M6F/M7/M9OPEN.

Следующий148B:CMeshObject/CEquipObject Render()/matrix overloads/queue/shadow
→типизированные146controller/ANI/fade/conditions/effects/positions
→ordinary CPlayerProc/Avatar/frame/render/UI →Bselection.
Не повторять готовый21+27function аудит. Подробности research/client455-grade-overlay.md.
Archive sideeffect — НЕ SetReLoadState:проверены настоящие readers116E518,
первоначальное предположение исправлено до приёмки. Group publication включает
own adapter;полные455producer-writers ещё вM9backlog.

Диагностика queue527E70/528090/528190,shadow46CF10,ctors46BD60/46BE60/46DB30
есть в grade-overlay148-reference/additional-diagnostics.json (не полный ASM).
Queue physical stride4matrices/node при BlendNumloop:не заменить на30 молча.
Shadow делаетдвойной SetMaterial/SetMeshEffect. EffectList9298D0 keyDWORD,
несмотряна char впсевдокоде:caller push EAX и927790читаетDWORD.
Overlay604 неинициализирован ctor/init,нуженреальныйproducer;virtualgrade
46D8B0→payloadvirtual68 —отдельный путь. 4513C0 пустой/return1,не выдумывать defaults.

Перед ordinary edits:сохранить148 вbefore149;before148 уже содержит147.
Финальный GPUprobe work/m9/6d651ce9/grade-overlay-001;source/native/report/frame.
Послеосновного draw обязателен правильный caller state:одиночный overlay
давалпустойкадр. ПроверкаRGB исключаетложныйуспех. Чёрнаяполосаневходит вмодель.
Всеjobs завершены;IDA c6eeef7e savedclosed/list0;нет server/original изменения.
Ниже история,которая не переопределяет это продолжение.

# Текущее продолжение147/148 — 10.11.2026

Предыдущий goal-turn:PROGRESS — реальная поправка CCharacter,истинные native
иобычный runtime147;карта следующего полного renderer сохранена.
M9 определён:полный клиент455 без модернизации графики;не уточнять повторно.
Цель остаётся активной. Оценка25%(20–35%),0/12полных областей принято.

Последний runtime147:993978ffd58f5be96176f5ae03c36396048d04a27b4741c26582a5013268a5b1,
x86/entry175EA0;182client/67engine/20modules/unresolved0.
Gate:inventory/client455-character-palette-checkpoint.json.
Настоящий CCharacter20parts×30palettes/13dummy проверен:независимость2акторов,
рост/уменьшение/частичный отказ/освобождение. Avatar3локализации иregistered3Avatar PASS.
Own Create/Login PASS,кадр66/3031ms просмотрен:lobby/ожидание,не полный455UI/auth.
Девять известныхfirst-chance имеют тотже профиль145;unhandled0.
C2079 probe исправлен include datatable/cresourcedatamgr.h.
Account/Avatar maps теперь вуникальных run folders. Newassetpoolbytes0.

147 не подключает полный controller146. Следующий148 — полноценный typed mesh
renderer иordinary CPlayerProc/Avatar/slot/frame/animation/conditions/effects.
27fullfunc/1827instructions/213CFG иvtable176bytes равны2pins:
inventory/client455-equipment-render-reference.json;research/client455-equipment-render.md;
raw equipment-render148-reference/session.json. Не повторять готовый аудит27func.
ВАЖНО исправление:46D190 — Animation,НЕ Render;CEquipvtableAA8F64:
24→46E120,28→46E520,32→46DBC0,148→46E160,152→46E1E0,156→46E1A0,172→46D8B0.
46C200 — metadata getter. Render branches имеют отдельные scroll/time,
fade выполняется приRender,не выдумывать общий backend с потерей overloadразличий.
Далее проверить4overlaydescriptor×526bytes@113FC70/textures@11404A8,
их loaders/writers,engine SetMeshEffect/kit/unit/queue иполное подключение.
4513C0 targetпустой/return1:не придумывать здесь создание defaultmesh.

Проверенная147 уже сохранена вbefore148/manifest.json:49точныхфайлов.
Не перезаписыватьbefore148 иbefore146.
Research148 покаAUDIT_OPEN,не реализованная отрисовка. M6/M6F/M7/M9OPEN.
IDAeaa5fe38 saved/closed/list0;nativejobs завершены. Сервер/originals не менялись.
Ниже история;старые «current145»/«candidate147failed» больше не текущие.

# Продолжение после оценки — 10.11.2026

Главная задача следующего отчёта — наблюдаемый результат обычного клиента.
Плановая готовность25%(20–35%), остаток65–80%; 0/12полных областей принято.
Полные исходники/SDK455 отсутствуют. Сборочные входы выбранной конфигурации
обеспечены; полнота ресурсов и спецификации поведения ещё не установлена.
Документы:progress-report.md, roadmap.md, next-steps.md.

Последний проверенный runtime145/1a355372… сохранён в before146.
Кандидат147/993978ff… уже собран182/67/20/link0, но runtime не проверен.
Незавершённые изменения: CCharacter cache20parts×30palettes/13dummy.
Palette probe не компилируется: C2079/CCharResDataMgr в mainapp.h.
Не выдавать candidate за проверенную145. Три source-файла до изменения
сохранены в character-palette147-source-before; отдельный WIP-report в inventory.

Сначала исправить probe include и провести затронутые palette/Avatar/обычный запуск.
Затем соединять уже проверенные146компоненты с CPlayerProc/Avatar/кадром.
4513C0 SetEquipItemToDefaultMesh действительно пустой/return1 в455:
не придумывать default-substitution; найти настоящий producer внешнего вида.
Render diagnostics сохранены в character-palette147-reference/ordinary-render-diagnostic.json.
Они не все имеют полное ASM-подтверждение. Полные ctor/lifecycle ещё открыты.

IDA b6dd2ecb saved/closed/list0; активных native jobs нет.
Новая дисковая опись155,29GiB по путям/42,87GiB уникальных файлов; удаления0.
Сервер/originals не изменены. Большие неизменённые suites не повторять.
Следующий функциональный рубежB: правильный список/внешний вид/выбор;
послеB/C пересмотреть оценку и срок. Надёжного срокаM9 пока нет.
Ниже сохранена история; она не должна перекрывать это продолжение.

# Предыдущее продолжение146:числовая цепочка условий проверена

Gate inventory/client455-equipment-conditions-checkpoint.json PARTIAL_COMPONENT;
research/client455-equipment-conditions.md. Sourceclient455_equipment_conditions.h.
52fullfunctions/2323instructions/357CFG equal2pins;45newhelpers+7reusedcore
fromequipment-providers146.6dataregions:switches,weights,virtualslots pinned.
Native CPU source22realitems(21accepted),independent200modifierbytes/totals,
66smallfrozencontracts PASS/exit0. Actualdetached clone survives originalpayload
release andremoves special+upgrade. Only3assets/17921866logicalbytes,newpool7953.
Own fixture7953bytes,not originalEDF edits. Nativecallbacksare recorders,notUI/game.

Important numeric contracts:
- Modifiers atcondition16/216 are200bytes/7categories;forcepower index3,normal4,
  ranged5(category5/6/8/11),launcher6(category7). Do not reuselegacy5enum.
- Armour weights1..5=.23/.22/.18/.17/.20;legacythird/fourthswapwrong.
- Armour setpredicate virtual68→404EA0 isRUNTIMEpayload113,NOTmetadata160.
  Metadata160stillcontrols460680upgradability. Bothpaths testedasdifferent.
- Combine44C670 readsEMBEDDEDbaseplayerproc(CPlayer+5200),notcurrent44C630
  pointerat5196. TargetCPlayerconstructor confirms currentptr defaults toembedded.
- Specialhelpercase8signedbyte180,casttrunc/wrap thenowner virtual252. UIrefresh
  beforeweakpart;weakdefault1/tiesfirst. Siegephysicalmultiply beforeflatbonus,
  noforce multiply. ResetpreservesSFblock/setlevels/extra708..720.
- Mounteddefence456 uninitialisedbyctor/reset;requireproducer. Mountedpower452
  reset1,profilepower460/def464 reset1. Setvalues672..704 initiallyunknown,
  selectors664/668 start0. Don't silently assign guessedvalues.
- Noowner:outergatecanaccept/upgrade stillmutates;special/combine/weakskip.

Nextpriority:actualordinary CPlayerProc/CPlayer/Avatar/equipment/frame/render/
defaultsubstitution andregistered upgrades. Numericcoreand23positionhelpers
arealreadyimplemented;do not spend anotherturn re-auditing them.
Ownercallback:baseCPlayerAA8DDC/slot252→43E600 emptyverified;AvatarAA8C54/
slot252→41A060→board7/490EB0→490950/412020/463740 updatesSkillpayloadlevels.
AvatarRTTI:locatorB7A210/descriptorBCB0C0. Savedpcode+identities in
equipment-conditions146-reference/owner-bindings-diagnostic.json;thoseAvatar
calleesNOTyetfullASMconfirmed. GlobalAvatarUI41A8B0 andSF/potion/liveupgrades/
setproducers/consumers stillopen. Hostcallbacks cannot remainrecorders inordinary.
Useportrecipes forsourcecopies;do not reinterpretnewrows aslegacyITEM_DATA.
M6/M6F/M7/M9OPEN;ordinary1451a355372…unchanged. Estimate25%(20–35%),0/12accepted,
152overlappinghistoricalrecords. IDA71813681saved/closed/list0;nativejobsfinished.
PreviousgoalturnPROGRESS:typedsource/nativeproof;no server/inputEXEactivity.

# Предыдущее продолжение146:позиции эффектов проверены

inventory/client455-equipment-attachment-checkpoint.json PARTIAL_COMPONENT;
research/client455-equipment-attachment.md.23fullfunc/1953instructions/223CFG
equal2pins;21new +2reused7E0D10/7E22F0.17-entryswitch7E1134pinnedseparately.
Source scripts/native/client455_effect_positions.h. Real25bodymodels/25named
positions/5races/5cloakmagic/onearchivedAccretiaANI pass.28frozen coordinate
contracts coveryaw/scale/fallback/binding-index/NPC/default.1694assetpaths,
197618821logicalbytes,newpool0;ordinary145PE unchanged/no freshLoginneeded.

Important:playernamedbone usesparent/blendnames ofequip0..9 thenFIRSTactorcached
matrix fornode;returnedblendindex isnotused toselect contribution. NPCusesown
mesh names/matrices.17=Spine→Spine1;18default retainsactorposition.7/Damage/
weaponfallback usesworldbboxheight timesactorscaleagain,preserved455double-scale.
Some targetfailurebranches copyuninitialisedtemporary. OwnAPI reportsdefined=false
andmagicwrapperrejects;fullfailurefidelity explicitlynotaccepted. No inventedfallback.
Dummycache initiallyzero;7F2D60 fills255 andmaps effect1/2/fire1..4,lastwins.
Cacheproducer inordinaryframe isstillneeded. Headerrequiresactualnormaltypes.

Next:typed4411E0chain fromexistingfullprovider24proof,thenactualCPlayerProc/
Avatar/registered upgrades/frame/render/effectbackend integration. Do not re-audit
these23position functions. M6/M6F/M7/M9OPEN;estimate25%(20–35%)unchanged.
Registry151historicaloverlappingrecords. IDA5c1cdbca saved/closed/list0;
native90813 terminal0;noothernativejobs/noinputEXE/serveractivity.
PreviousgoalturnwasPROGRESS:sourceproviders+realnativeproof,notstatusonly.

# Предыдущая память —10.11.2026:оценка и146компоненты

Текущая обычная PE145 по-прежнему1a3553721149f8638812d636e2dfa3053d75b58a58c6310df72478050ab5670d;
equipment145gate current.182client/67engine/20modules/unresolved0.
Обычный Login —lobby/ожидание,не успешный вход. M6/M6F/M7/M9 OPEN.
ЦельM9 уже определена:полная приёмка клиента455 без модернизации графики.
Старый текст objective вget_goal не повод повторно спрашивать M9.

Оценка25%(20–35%),остаток65–80% известного функционального объёма.
12фиксированных весов,0/12полных областей приняты.150пересекающихся записей
реестра —не знаменатель возможностей. Статическая описьIDA37865функций
(включая1296library) сохранена,но полной карты переноса всех тел нет.
См.docs/progress-report.md иinventory/client455-progress-assessment.json.
Никакой датыM9 из этих процентов не следует.

146:добавлен отдельныйsourceMagic/sound ownership/cleanup/cloak looptracking.
Gate inventory/client455-equipment-effects-checkpoint.json;research/client455-equipment-effects.md.
22fullfunc/1489instructions/222CFG match2pins;realRPK/MagicSpt/Miles/nativePASS.
4magicstarts/4expires/4waverequests/3samplestops. Attachmentpositionpending,
ordinaryCPlayerProcfalse. Registry только отслеживаетостановку,неautoreplay.
Основные RVA6D3D0/6D660/3DBD50/4BD5E0/4BD6A0/4BD780.

Исправлена ошибкаheight:416940/RVA16940 читаетmetadataDWORD72meshID,
а не индексItemстроки. Headerhelperтеперь принимаетmeshID.
ANIprovider69cases/52ANI/16models/68poses/1expectedfailure/24liftsPASS.
4новыхреальныхdiscriminatorcases отличаютindexотmeshbits8.
Общийheaderзатронулcontroller;егоaudit/native/checkpointобновленыPASS.
Ordinary145PEне менялась,Loginне повторялся.

Общийпул достигNTFS1024links у280byteBBX. client455_asset_staging.py
теперь используетограниченныеownedрепликис900links;nativeповторPASS,+280bytes.
Репликаиrunоднафайловаязапись,оригиналотдельная/nlink1;capacitycheckpointсохранён.
Failedrunнеудалён. Свежаяstorageопись154.86GiBlogical/42.85GiBunique,
work/m9 26.70GiBunique/client-graphics-lab12.39GiB;группынельзяскладыватьиз-зассылок.
Старыефайлынеудалены,новыхполныхclientcopiesнет.

Следующийстык:полныйattachmentposition →typedconditions →actualCPlayerProc/
Avatar/registeredupgrades/frame/render/appearance →bootstrap/selection.
Подробнаяqueue толькоdocs/next-steps.md. Не повторятьуже доказанныеполныеbodies.
Rawattachmentdiagnostic7DD140/7E0B90 сохранён вequipment-effects146-reference.
IDA1049c6e2saved/closed/idb_list0;всенативныеjobsзавершены.
ОригинальныеEXE/серверы не запускались/неизменялись.

Ниже исторические записи. Их «current/next» относятся к своим прошлым версиям.

#146продолжение:реальные ANI/fade готовы;ordinary145не менялся

Новыйcomponentgate inventory/client455-equipment-providers-checkpoint.json;
research/client455-equipment-providers.md.24fullfunctions/2220instructions/
373CFG equal2pins.65realcases/48ANI/12models,64actualCResObject.Animation
posecalls,1expectedinnerfailure,20realownerlifts/fades PASS. Publicwrapper
returnsTRUE evenifinnerANIselectionfailed,targetbehaviorpreserved.
SourceRF455PlayerEquipmentObject implements6DF10/6D2F0/6D730 +6E220/6E3A0
andRF455_MountingHeight455(4B8F0/4B9B0). Do notrewrite theseagain.
Headerchangedclassstate;affected13slotcontroller/clone reference/native/gate
refreshed andPASS. Ordinary145PE1a355372…/engine137unchanged;no newLoginrun.
ActualitemAnimationEffect callback remainsrecorder,typedconditions andordinary
CPlayerProc/Avatar/registeredupgrades/render/selection notconnected. M6/M9OPEN.

RealAccretiaCloakDEFAULT/USE/UNUSE andsiegekitDEFAULT haveANImaximum0;notload
failure. Initialprobeassert(maximum>0) waswrong,correctoraclecomparesrealparsed
maximum. Failedrunwork/m9/476e69b4 retained. No productionforce-successfix.
ExporterpathsKoreanANSI:stripbasenameonbytesbeforeASCIIname decode.
Firstpool+53036735bytes,repeat0;1738assetrefs/219147433logicalbytes;nooldcleanup.
IDA4ce73361 saved/closed/list0;allnativehandles terminal0;noinputEXE/serveractivity.

Next146actualitemeffects:46D3D0/6D660→7E22F0→7D8FF0/GetMagicListFromID
and7E0D10 dummyposition,sound. Savedpcodecomplete inartifacts/client455-progress/
equipment-providers146-reference/item-effects-diagnostic.json;fullASMstillneeded.
406CB0=positionpointer80,4077E0=yaw108,NOTname/scale. IsExistFromMagicSpt
matches7D5A60 family. Existing EffectCore hasrealportedmagic scheduling.
Thenconditions4411E0 chain(fullASM24proof alreadycollected),ordinarycontroller/
GetNormalItem-upgrades/render/selection. Do notclaim equippedappearance yet.

FastfullASMworkflow nowavailable: nativeIDA basic_blocks +lookup_funcs +
func_profile → scripts/decode_client455_cfg.py ownedraw → independentIDA
instructioncount +allCFGbytes decodedbyinstalleddumpbin+bothpincomparison.
Analyze_batch maypreviewonly10asm/blocks despitefalse truncated flag;neveruse
itsASMpreview ascomplete. Newhelper accountswrappedlonginstructionbytes.
This avoidsdozensofsmallMCPdisasm callswhilepreservingfullevidence.
Overall25%(20–35%),0/12accepted;149overlappingrecordsnotdenominator.

## Предыдущий146контроллер иобычная145база

# Продолжение146 —компонент проверен,обычная сборка145

146PARTIAL_COMPONENT:typed13slotcontroller anddetachednormalclone implemented.
Gate inventory/client455-player-equipment-checkpoint.json;research/client455-player-equipment.md.
32fullfunc/1640instructions/225CFG equalbothpins;nativefullobject Item/Resource/
30actualcontrollerbasecreations/aliases8,9,10,11,12/bothwrapperoverloads/removal/
cloneconsumers PASS.32modelrecords/33GPUtextures throughsharedinputs;newpool0.
CurrentPE1a355372… andordinary145runtimegate unchanged;no new Loginrun necessary.

IMPORTANT:4539BD passes equipmentthis andplayerarg into453A80;itstoresowner588.
This is NOT Player.SetPrevAction despite misleadingpcode. Sourceclass exposes
GetOwner455/SetOwner455. Kind=metadata88,notheaderkind12.13storage/diagnostic12render.
Normalclone461CC0→404BC0→405CE0→405E70copieswrittenfields andreferencebyte;
no managerinsertion/nosource retain. Nativeconsumer verifies copiedIDs/data/name/
referencebyte afteroriginalslotrelease. Allocationpadding notnormalized.

Nativehost uses realRematchParent andsourceClone. Animation/fade/action/condition/
effect callbacks are recorders,NOT productionproviders. Controller not yetconnected
actualCPlayerProc. Keepordinaryruntime145current;do notreplacewithcomponentgate.
Next146phase:productionproviders46DF10/46D2F0/46D730/46D3D0 and4411E0typed
condition chain;thenCPlayerProc/CPlayer/Avatar/registered GetNormalItem/upgrades,
actual12slotframe/render/defaultsubstitution/ordinaryappearance andselection.
FullASM32raw saved;providerdiagnostics separate,441AC0needs nextcursor100.
Exact145before146(50files). IDA7c61237d saved/closed/list0;nativehandles terminal0.
No server/originalEXE activity.25%(20–35%),0/12fullaccepted,M6/M6F/M7/M9OPEN.

## Предыдущая актуальная база145 и ограничения

# Актуальная память —10.11.2026,145PARTIAL

Текущий gate:inventory/client455-equipment-checkpoint.json.
Own1a3553721149f8638812d636e2dfa3053d75b58a58c6310df72478050ab5670d,
x86/base400000/entry175F50/2299904bytes;182client/67engine/20modules/unresolved0.
Engine137 unchanged708c892e60c3bf7457389b40ac24b9a466958c9d232d9efaf497d1ac3232b870.
18fullfunc/630instructions/60CFG equal2pins.32realmodels/33GPUtextures/
30actualAvatar.SetDefaultItem calls/6retainedpayloads/0afterteardown PASS.
Strict meshlookup requires both LoadRealData return and m_Load;real type6/index32
metadata mesh00A10320 absent:Create true,mesh/bone null — preserved455quirk.
All33DDS requests resolve to realRFT. Resource group0meshes registered inmanager5.

Ordinary registeredreceiver uses GetDefaultItem455;6sourceownedtypedslots added.
FullCPlayerProc13slots/effects/rematch/fade/animation/draw,legacyGet/Unset/copy,
completeprivate644ABI andequippedappearance not accepted.
Affectedaccount/3Avatarclasses/currentPE PASS. OrdinaryWinMain/Miles/Login
frame70/3235ms viewed:lobby/waiting. Loopback received67bytes,RFresponses0,
authenticationfalse. Ordinarysuccessbootstrap/selection/world/gameplay stillopen.
Exact144before145(50files) preserved. Sharedfirstpool+57,508,702bytes;repeat0.
IDA7dd394bb saved/closed;nativejobs нет. Research:client455-equipment.md.

User requested a candid assessment after4days,not test totals. Current estimate
25%(20–35%),remaining65–80%known functional scope,0/12fullaccepted.
Sources/build dependencies ready for selectedconfiguration;fulloriginal455SDK0,
2pinnedPEavailable;fullfeature/packet/state/resource/scenario inventory incomplete.
Assessment is explicitengineeringjudgement,fixed12weights,not measuredcoverage.
Updated docs/progress-report.md and compactroadmap.md;historicalroadmap retained
inresearch/roadmap-before-assessment-2026-11-10.md. Do not treat oldhistorical
«next143/144/145» as currentwork. Do not reopenM9definition or developservers.

Next146:snapshot145 via snapshot_client455_runtime.py 146 client455-equipment-checkpoint;
thenactualPlayerProc13slots andappearance. Prioritize B selection,Cmap/control,
Dgameplay,EfullM9. ATitle/Login stillpartial. No newbulk159k unchangedsuites.
Reassess afterB/C. CalendarM9 notcalibrated. Current user-facingtask is assessment;
do not claimM9complete or inflate percent for eachsmallpartialcomponent.

## Сохранённая история и постоянные технические ограничения

# Память проекта

Текущий144 PARTIAL — inventory/client455-avatar-classes-checkpoint.json;
research/client455-avatar-classes.md. Own ea25eea5222039073ddf7e7823219336080ae298fd78afa0e99b38a65584f812,
x86/base400000/entry174FC0/2294784bytes;182client/20kernels/link0/unresolved0.
Engine137 unchanged. Before144 сохраняет точную143базу49files.
14fullfunc/460instructions/76CFG equal2pins;actual Avatar/165classes/3locales
и23textwidgets PASS. Numeric slot0/no slot1 меняеттолькоlabel4;string меняет
label4 thenbase/storedname5. Slot0/slot1exists меняетbase5;slot1 base0→label5
thenclass1→label4;slots2/3 namesunchanged. UIabsent storedname не меняется.
Copy32 zeroesall/copies≤31. CharInfolegacy Level/Guild/Attribute не затронуты.
Отдельные23valuewidgets пока НЕ отрисованыкак455layout. CreateClassSkill
callerесть,fullcallback ещёlegacy/unported;native tests board-absent Loginbranch.
Protected test access черезderivedProbeAvatar;public APIрадиtests не меняли.
SetClassName/SetAdvancedClassName455 inlined вproduction,не искатьотдельныйMAP.

Affected account/registered suite fresh:3real classindices fromCharacter165
примененыactualencrypted1/9receiver к3Avatar;UIabsent namesstayempty.
Actualordinaryreceiver CALL кnewsetter декодирован. Probeaccount теперьstages
Character/NDCharacter иAC44oracle. Fullappearance/auth не приняты.
Fresh WinMain/Miles/Login70/3219ms/640x500 viewed:lobby/waiting,nofatal;
ordinarysuccess bootstrap не исполнялся. Classstaging6refs/3.04MB/newpool0.
IDA01ef697a saved/closed;livejobsнет. Оценка25%(20–35%),0/12fullacceptance.

Следующий145:typed item/default/equipment→registered appearance,затем
remainingbootstrap/selection. Snapshot144 черезsnapshot_client455_runtime.py
145 client455-avatar-classes-checkpoint доизменений. LegacyITEM_DATA/CEquipItem
layouts отличаются:не cast455rows и не подменятьappearance syntheticмоделью.
Classskillcallback/полный23labelUI/остальныесценарии остаютсявbacklogM9.

## Историческая база143

Обновлено 10.11.2026. **143 PARTIAL; M6/M6F/M7/M9 OPEN.**
Gate: inventory/client455-character-tables-checkpoint.json.
Исследование: research/client455-character-tables.md. Оценка: docs/progress-report.md.
Own b41d50ffb5001c04a54dd0f16bd471c2bc0168e4b8757a52eca7a41067e0b4ec,
x86/base400000/entry174CD0/2293248bytes;182client/20kernels/link0/unresolved0.
Engine137 unchanged. Exact142 сохранён вbefore143.

Обычный CharacterDataMgr теперь читает PlayerCharacter→SF5→Store(selector)→
Character7+ND;реальные skill/force boards7/6packs×20,masteries12/24,SF100.
15fullfunctions/1737instructions/193CFG равны2pins. Четыре stock cases3locales
иодин changed-name DBCS fixture:14tables CRC/165class lookups/5typedSF wrappers
каждый PASS. Player5/Store1595(default),1651(_1);Character165/8/1999/36/324/81/648.
SFko/ru false,Storezh/ru default false,zhStore1 true;prefix/base сохранены.
Target Read1EE900 приshort не пишетdestination/cursor;CharacterND игнорирует
результат,ko203/ru682 failedreads. Не менять наmincounts/repair/resync.
Class lookup exactcase/code@12 илиindex@4,firstmatch;новыйaccessor probe-only.
Legacy CPlayerClass/Player/Monster/Store/SF_DATA consumers НЕ перенесены,
SF countslegacy0;boards выделены,ноне заполнены455items/classskills.

Fresh WinMain/Miles/Login70/3219ms/640x500 inspected:lobby/waiting,
unopenedpanels hidden,legacy label stays;no fatal. Success-response bootstrap
иselection/appearance не приняты. Неизменённые142 suites не повторялись.
Shared staging35refs/35.2MBlogical,+8.51MBnewpool/4.57MBadopt.
IDA5fe0894d saved/closed/list0;nativejobs нет.

Следующий144:actual Avatarclass setters/names,потом equipment/appearance и
остальнойbootstrap/selection. Raw143 содержит diagnostic Avatar pcode,
ноselectedfullASM/CFG дляsetters/UI ещё нужно собрать. MAX_AVATAR_CLASS_NUM=4.
Target412140:slots0/1 имеютразные обновленияимён;412580 storedname@24196
толькоеслиglobal1028B7C UIexists,412640 меняеттолькоUI. TargetUI66337023labels,
legacyCharInfo14labels:slots4/5 тамLevel/Guild,не писатьtargetиндексывних.
Не cast455raw вCPlayerClass. Full actor/item/UI/skills/bootstrap ещёopen.

Оценкаостаётся25%(20–35%),0/12 fullacceptance. Измерять A→B→C→D→E;
неизменённыеbulk suites не повторять ради счётчика. СрокM9 не калиброван.

## Историческая база142

Обновлено 2026-11-10. **142 PARTIAL; M6 открыт.**
Gate: inventory/client455-item-bootstrap-checkpoint.json.
Проверка: scripts/Invoke-Python.ps1 scripts/checkpoint_client455_item_bootstrap.py.
Доказательства: research/client455-item-bootstrap.md.
Последний commit до142: 72f7041 (Resource141).
Подробные старые факты: research/project-memory-before139.md и research/ по участкам.

## Цель и ограничения

CLIENT ONLY: поддерживаемые исходники и собственный RF_Online.bin с полным
функционалом/поведением закреплённого455. M9 уже определён: финальная приёмка
без модернизации графики. Старое goal-описание про M4/неизвестныйM9 не применять.
M0–M4/selectedM5 достигнуты; M6/M6F/M7/M9 OPEN; M8 не требуется.
Server только читать reference; не изменять/строить/восстанавливать даже копии.
Originals immutable; input EXEs никогда не выполнять. Работа под work/.
LocalGit, no push/remote/publication. Не делегировать без прямой просьбы.

## Текущий142

Own PE f0114c80b2a08bdb313113368c729b4a7cb4b4c0c05cdc193ee368edf627f2d1,
x86/base400000/entry172C30/2283520bytes.182client/20kernels/build/link0/unresolved0.
Engine137 SHA708c892e60c3bf7457389b40ac24b9a466958c9d232d9efaf497d1ac3232b870
unchanged. Обязательный normal-consumer proof обновлён.
Primary SHA b1b5febf0d0394712e2322350e19dafe60742e8642697b93cfb89135bac1fd8b;
secondary46528aac20499e3b3928d58658d7e0cefe26feba7cd193796d5cfbf7a2bbc558.

Обычный Login вызывает CItemDataMgr.LoadBootstrap455:cash→set→Item47+ND.
Порядок подтверждён декодированными CALL/JMP в production PE.
Cash selector -1/default иначе полный DWORD decimal suffix; ND overlay DWORD16.
При cashND count mismatch/отсутствующем ND base сохраняется; outer продолжает.
Все11 country vslot160=true,включаяKorea;не выводить это только изTaiwan.
4newfullfunctions/257instructions/27positiveCFG regions равны2pins;
RVA1F8EC0 cash,2089E0 set,4329B0/42C490 profile true methods.
Existing588instruction Item1FEE30 evidence089 переиспользован.
Raw artifacts/client455-progress/item-bootstrap142-reference/session.json.

Six real full-object runs:ko-default/zh-default/ru-default/zh1/zh10/ko1.
Cash1000rows,set1373,Item47/76049rows;independent alltable/name/description/
work arrays CRC/consumed bounds PASS. Twelve real CBoardObject/payloads каждый:
borrowed row/name,clone retains,last owner erases. Receiver world-entry supplies
selector through actual12-byte decoder,не реальная auth.
Russia cashND count mismatch иabsentkoND_1 дают false,base retained,Item PASS.
Новый GetData455 accessor сейчас удержан только probe;LoadData inlined вbridge.
Legacy ITEM_DATA/derived CBoardItem/CEquipItem/Avatar default/equipment consumers
НЕ перенесены. Нельзя cast455raw встарые layouts или заявлять appearance/selection.

Fresh WinMain/Miles/providers/ordinary Login PASS:work/m9/f0114c80/login-frame001,
created1/loaded1,frame70/3234ms/640x500,Renderreturn/exit observed,no fatal.
PNG276eb78c… просмотрен:lobby/ожидание,unopened panels hidden.
Обычный success-response bootstrap в этом запуске не выполнялся.
Wide unchanged account/resource/graphics suites не повторялись.
Exact141 snapshot49files before142;140before141 и139before140 сохранены.
IDAb958e3d1 saved/closed/list0;nativejobs нет.

## Следующий143: character tables/classes и выбор персонажа

Target53D0F0 result0/state6 calls1E7BE0. Initial item142 иResource141 интегрированы;
остальные таблицы/связи ещё legacy/partial. Далее PlayerCharacter,SkillForce,
Store(selector),Character7 иND/NDW overlays/class-tier lookup/names.
Переиспользовать RF455ItemDataStore.character иRF455SkillForceData;не cast raw
вlegacy CPlayerClass. Class setter412140 отличается отстарого helper.
Затем typed item/Avatar equipment consumers иordinary appearance/selection.
Не bypass waiting/не force success/не писать serverlogic.

Полный порядокbootstrap:ItemCash/ItemSetEffect/Item/Resource/character tables+
boards/Quest/EventShip/NDMsgMonster/ItemTimer/country slot296/NDMsgEvent/
EventSound/SpecialStore/ItemCollection/Map/5default effects/Avatar finalization/
registered request. Рольslot296 неизвестна;ItemTimer/SpecialStore не Exp/Combine.
Pcode root:artifacts/client455-progress/registered140-reference/session.json;
Resource141 raw содержит полный ASM root. All remaining loaders need own evidence.
Затем ordinary world/avatar/control/movement/collision→combat/items/chat/NPC/social.

## Сохранённые реальные участки139–141

World-entry request58/reply12 уже интегрированы. State m_worldEntry455 содержит
cashShop/npcShop/quest selectors (-1 илиuint16). Request keys XOR mask
(k0+k2-k1-k3)*12AB34CC modulo32,version126455,signature33bytes.
Reply result/grade/seen/selectors пишутся даже приerror;ReceiveResponseMsg доkind.
Registered request1/8/reply1/9,payload506=header14+3×164.
Name17/serialDWORD17/race21/slot22/class5@23/level28/dalant64@29/gold64@37/
baseShape45/equipment8×signed16@49/upgrade65/reserved83@73/lastConnection64@156.
Level0→1/skipTutorial0,else skip1;latest signed64 localmax0/strictgreater.
Count0 retainsactors/latest;parts1,2,3,4,5,7,6,8;class/appearance consumers open.
Standalone account skipsWinMain:explicit g_bIsWindowed,не путать сenginewrapper.

Resource.edf9groups/30623rows:1267bones/10484meshes/18872ANI. Registered1267/
10483/18872:oneNPC20483 missingparent skip. Five real playerBN shapes30/25/29/38/30
andfirstmeshname5;real playerANI fromRFS loaded. OtherANI metadata only.
Legacy260/328/244/84 rows match;bounded preflight/missing-player/shape checks added.
Own GetResourceList missingreturn fixed;otherlegacy getters/errorUI/quit open.
1120checked unresolvedrefs503BN/592BBX/25ANI afterloose/RFS lookup;not full asset
inventory or proof each path required. Seven archived members resolved.
Character manager keeps exact case/separate records;ANI normalizes/deduplicates.

## Оценка, память и работа

Около25%,диапазон20–35%,остаток75%:engineering estimate12systems,не tests/bytes.
0/12 full acceptance;144historical/overlapping records не знаменатель.
A Title/Login;B auth/selection;C world/control;D gameplay/NPC/social;E fullM9.
Отчёты разделяют:собирается/проверено отдельно/работает обычно/полностью принято.
Сборочные зависимости обеспечены;fullsource455/SDK0sets,referencePE2.
Feature/packet/state/resource/scenario inventory ещё неполон.
Не повторять159k unchanged suites. Проверять затронутое/обязательные зависимости.
CRT/FP/failures backlog сохраняется,но не заменяет связанный игровой сценарий.

VS2026/MSVCx86. Python scripts/Invoke-Python.ps1 file.py,не-c/-m.
Native/GPU sequential;timeout не termination,poll тотжеhandle.
IDA ownedworkcopies/sessioneverycall/ASM≤100+allpositiveCFG/tails/save-close.
MCP rawchunks≤20k;rg --files --no-ignore для ignored work,перед неизвестнымpath.
Не использовать PowerShell path wildcards вrg;filter через --glob.
Shared staging толькоownedcopies;никакихhardlinks originals;configs/exes private.
BN/BBX/ANI/MSH/RFS добавлены immutable. Resource firstpool+53.1MB,повторы0.
Item142 newpool509445bytes/adopt46.2MBexistingowned,29refs/165MBlogical.
Storage oldsnapshot150.95GiBlogical/42.29GiBunique,старое не удалялось.
Before cleanup verifyevidence/inputreachability. Windowsidentity os.stat(path),
неDirEntry.stat снулевыми inode/linkfields.

## Движок/UI: не потерять ограничения

FullFraction/particle/BBoShasi/INS/Empty/visibility/collision/device lifecycle OPEN.
Scene targets137/capturehelper есть;ordinarycapture caller не доказан.
Capture8CE020 retainsurface ref/ignoresHRESULT;толькоlab компенсирует.
SyntheticPerbMap не455asset;wrapper640x500/viewport640x480 open.
CLevel.SetViewMatrix неinverse/viewproj,publishcamera отдельно;temporaryCLevel
должен переживатьactivemap,destructor freesglobals.
Material526/serialized46/MAX2048;specular_flikering typo/ORbits сохранять.
ShaderPS6 fourthlane/unownedstack lanes не выдумывать.
FullTitle/movie/factory4/explicitnext OPEN;legacyfactory3/modulo остаётся.
Title557F80 exit/jump unconditional,не включатьdeadfade. RealAVI/CcrLogo.dat есть.
Login init5401D0 state6normal/7logout;country slot284false всех11,не force reconnect.
Create53BB20 brokenIDB/JUMPOUT/falseCRT annotation:читать реальныеinstructions.
Full455UI10windows/systemsprite5/layout/focus/input OPEN.
RootAdd138 Show(FALSE)/AlwaysTop ужеперенесён. Legacylabel0.738 косметически не менять.
