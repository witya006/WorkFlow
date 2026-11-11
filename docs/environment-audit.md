# Сборка с созданием персонажа — 12.11.2026

`88e4b90c…` собрана в Release Win32. Собраны 182 клиентских объекта и
20 модулей из закреплённого набора. Линковка прошла без неразрешённых
символов. Живая проверка подтвердила создание Беллато и его сохранение
после повторного входа. Вылет при выборе расы из-за старого владельца
таблицы классов устранён. [Манифест](../inventory/client455-character-create-checkpoint.json).

# Контрольная сборка M6 — 11.11.2026

Сборка 213 (`593ea14`) закреплена перед изменением архитектуры. SHA-256
бинарника, прошедшего живые проверки, подтверждён у рабочего файла и копии в
`artifacts/client455-progress/before214`. Чистая сборка клиента и R3Engine
в отдельных выходных каталогах прошла на VS 2026 Professional, MSVC v145
(14.51.36231), SDK 10.0.26100.0, Release Win32. Линковка собрала 182 клиентских
объекта, 67 объектов движка и 20 модулей вспомогательных реализаций.
В `RF_Online.bin` совпали все байты, кроме четырёх байтов в двух полях
времени линковки. Новую копию в игре не запускали, живые доказательства
относятся к исходной сборке 213.

`work/m6-control-213/build-inputs-213.zip` содержит 801 сборочный вход
с проверенными SHA-256. Размер около 2,1 МБ. Это исходники и заголовки,
прочитанные компилятором, проекты CMake, параметры линковки и восемь готовых
библиотек. Архив хранится локально. Воспроизводимость проверена на рабочем
корне с установленным инструментарием. Распаковка и сборка в другом корне,
а также пересборка восьми библиотек в этой проверке не выполнялись.
[Манифест](../inventory/client455-m6-control-213.json) ·
[Живая проверка](../research/client455-avatar-movement.md).

Для повторения собрать из `work/client455-port/normal` цели
`RFClient455Consumers`, `RFClient455Facade` и `RFClient455Kernels`, из
`work/client455-port/startup-engine` — `R3Engine455Startup`. Генератор CMake
`Visual Studio 18 2026`, параметры `-A Win32 -T v145
-DCMAKE_SYSTEM_VERSION=10.0.26100.0`, конфигурация `Release`. На линковке
использовать сохранённый `normal-link.rsp` с путями к заново собранным объектам
и библиотекам, отдельными путями `/OUT` и `/MAP`. Включить каталоги `lib/x86`
MSVC и `ucrt/x86`, `um/x86` SDK в `LIB`. MSBuild использует FileTracker,
которому при ограниченном запуске отказано в доступе (`MSB4018`). В разрешённом
локальном запуске сборка завершилась успешно.

# Частичная проверка 213 — сетевое движение

11.11.2026. `e418869c…` x86, RVA входа `0x18c980`.
Сборка 182 клиентских модулей, линковка без неразрешённых
символов, проверка потребителей и ранний запуск Taiwan прошли.
Компонентная проверка читает обычное исходящее кольцо клиента.
Отдельно проверен разбор 431-байтового базового сообщения
с параметрами движения. Локальный сервер подтвердил движение
и остановку в живом прогоне. Сессии IDA закрыты.
[Доказательства](../research/client455-avatar-movement.md)

# Частичная проверка 212 — телепорт из инвентаря

11.11.2026. `14409124…` x86, RVA входа `0x18c0f0`.
Сборка 182 клиентских модулей, линковка и ранний запуск Taiwan
прошли. Компонентный прогон использует штатные объекты клиента
и архивный Item.edf. Живой прогон подтвердил позицию после
телепорта. Сессии IDA закрыты.
[Доказательства](../research/client455-base-portal.md)

# Частичная проверка 211 — вступительные ролики

11.11.2026. `48f0599a…` x86, RVA входа `0x18bb10`.
Сборка и линковка 182 клиентских модулей, потребители и ранний
запуск Taiwan прошли. Обычный оконный WinMain дважды дошёл до
кадра экрана входа после Esc на разных роликах. Сессия IDA закрыта.
[Доказательства](../research/client455-title-movies.md)

# Частичная проверка 210 — корректировка позиции

11.11.2026. `74c414e9…` x86, RVA входа `0x18abe0`.
Сборка и линковка 182 клиентских модулей, проверка
потребителей, отдельный ранний запуск Taiwan и компонентная
проверка `4/3` прошли. Живой прогон остаётся за сборкой 208.
[Доказательства](../research/client455-move-correction.md)

# Частичная проверка 208 — HP аватара и интерфейс

11.11.2026. `27bd3c5c…` x86, RVA входа `0x18ab00`.
Сборка и линковка 182 клиентских модулей, потребители и ранний
запуск Taiwan прошли. Компонентный прогон отрисовал обновлённую
шкалу. На NeutralB подтверждён обычный выстрел. Сессия IDA закрыта.
[Доказательства](../research/client455-avatar-health.md)

# Частичная проверка 207 — атаки монстра, анимуса и турели

11.11.2026. `120d435a…` x86, RVA входа `0x18a9f0`.
Прошли сборка, линковка 182 клиентских модулей, проверка
потребителей и ранний запуск Taiwan. Сессия IDA сохранена
и закрыта. Проверки прошли через штатный диспетчер боя.
Два входа на NeutralB завершились без исключений. В живых
прогонах выбрана одна цель, выстрелов и входящих атак нет.
[Доказательства](../research/client455-creature-attacks.md)

# Частичная проверка 206 — здоровье на кадрах обычной атаки

11.11.2026. `44eac749…` x86, RVA входа `0x18a980`. Сборка
и линковка 182 клиентских модулей прошли.
Проверены потребители и ранний запуск Taiwan. Компонентная проверка
прошла через обычные обработчики урона и здоровья. На NeutralB
Wing погиб после первого выстрела. Сессия IDA закрыта.
[Доказательства](../research/client455-ordinary-health.md)

# Частичная проверка 205 — цель, гибель и боевой режим

11.11.2026. `cb2c9c62…` x86, RVA входа `0x18a660`. Сборка,
линковка, потребители, ранний Taiwan и вход на NeutralB прошли.
Сняты два кадра попадания, подтверждён расход двух стрел и выход
без необработанного исключения. Две сессии IDA сохранены и закрыты.
[Доказательства](../research/client455-monster-target.md)

# Частичная проверка 204 — расход стрел и попадание

11.11.2026. `d8ad009f…` x86, RVA входа `0x18a720`. Сборка,
линковка, потребители, ранний Taiwan и вход на NeutralB прошли.
На кадре видны реакция цели и 22 урона. Остаток стрел обновлён
ответом сервера с 313 до 312. Зафиксирован один выстрел за вход.
Сессия IDA сохранена и закрыта.
[Доказательства](../research/client455-ammunition-impact.md)

# Частичная проверка 203 — обычная атака на NeutralB

11.11.2026. `083a7892…` x86, RVA входа `0x189fc0`. Сборка,
линковка, потребители, ранний Taiwan и вход на NeutralB прошли.
Выбраны стрелы из слота 12. Один запрос `5/1` получил
`5/7`, 22 урона поставлены в очередь. Отдельная x86-проверка
подтвердила границы декодера. Необработанных исключений нет.
[Доказательства](../research/client455-primary-ammunition.md)

# Частичная проверка 202 — начальная экипировка и инвентарь

11.11.2026. `f27d2498…` x86, RVA входа `0x1899f0`. Сборка,
линковка, потребители, ранний Taiwan и вход на NeutralB прошли.
Из 8 созданных предметов экипировки размещены 8, из 21 записи
инвентаря размещена 21. Ошибка отрисовки значка устранена, повторный
прогон завершил наблюдение без необработанных исключений.
[Доказательства](../research/client455-downloaded-items.md)

# Частичная проверка 201 — экипировка в обычной атаке

11.11.2026. `f3a101bf…` x86, RVA входа `0x1890f0`. Сборка,
линковка, потребители, ранний Taiwan и вход на NeutralB прошли.
Три проверки лука прошли без исключения и вернули отказ из-за
боеприпасов. Сессия IDA сохранена и закрыта.
[Доказательства](../research/client455-armed-attack.md)

# Частичная проверка 200 — живой выбор цели

11.11.2026. `c3c6df6b…` x86, RVA входа `0x188ad0`.
Сборка, линковка, потребители, ранний Taiwan и вход в мир прошли.
Штатный выбор цели работает. В обычной атаке зафиксировано исключение
в старом методе экипировки. Сессия IDA сохранена и закрыта.
[Доказательства](../research/client455-live-combat.md)

# Частичная проверка 199 — критическая реакция монстра

11.11.2026. `765fafe1…` x86, RVA входа `0x188650`.
Сборка, линковка, потребители, ранний Taiwan и ходьба прошли.
В проверке с теми же объектами подтверждены два клипа Wing и
эффект удара. Сессия IDA сохранена и закрыта.
[Доказательства](../research/client455-monster-critical.md)

# Частичная проверка 198 — отрисовка урона Силы

11.11.2026. `8e3035b7…` x86, RVA входа `0x1885e0`.
Сборка, линковка, потребители, ранний Taiwan и ходьба прошли. Сняты два
кадра с числами. Подтверждены три дорожки Prism Beam и звук Miles.
[Доказательства](../research/client455-force-damage-render.md)

# Частичная проверка 197 — боевые надписи и звук

11.11.2026. `1e64dd9f…` x86, RVA входа `0x1884f0`.
Сборка, линковка, потребители, ранний Taiwan и ходьба прошли. Сняты два
кадра со штатного графического устройства, проверен звук Miles.
Сессия IDA сохранена и закрыта. [Доказательства](../research/client455-combat-result-effect.md)

# Частичная проверка 196 — эффект попадания Силы с уроном

11.11.2026. `643554e2…` x86, RVA входа `0x188160`.
Сборка, линковка, потребители, ранний Taiwan и ходьба прошли.
Два кадра в штатной очереди эффектов подтверждены компонентно.
Сессии IDA сохранены и закрыты. [Доказательства](../research/client455-monster-force-impact.md)

# Частичная проверка 195 — реакция на попадание без урона

11.11.2026. `de40a4a1…` x86, RVA входа `0x1880d0`.
Сборка, линковка, потребители, ранний Taiwan и ходьба прошли.
Оба эффекта подтверждены в штатной очереди компонентно.
Сессия IDA сохранена и закрыта. [Доказательства](../research/client455-monster-force-reaction.md)

# Частичная проверка 194 — здоровье монстра

11.11.2026. `b8bd9f67…` x86, RVA входа `0x188030`.
Сборка, линковка, потребители, ранний Taiwan, вход и ходьба прошли.
Два входа HP и изменение по кадрам подтверждены компонентно.
Сессия IDA сохранена и закрыта. [Доказательства](../research/client455-monster-health.md)

# Частичная проверка 193 — цели и урон Силы монстра

11.11.2026. `1d3df8ea…` x86, RVA входа `0x187d40`.
Сборка, линковка, потребители, ранний Taiwan, вход и ходьба прошли.
Подтверждены пять записей целей и числовой урон на двух кадрах.
Сессия IDA сохранена и закрыта. [Доказательства](../research/client455-monster-force-damage.md)

# Частичная проверка 192 — приём события Силы монстра

11.11.2026. `2672e567…` x86, RVA входа `0x187860`.
Сборка, линковка, потребители, ранний Taiwan, живой вход и ходьба прошли.
Компонентно проверены обработчик 5/9, назначение Силы и оба клипа Wing.
Сессия IDA сохранена и закрыта. [Доказательства](../research/client455-monster-force-result.md)

# Частичная проверка 191 — клипы Силы монстра

11.11.2026. `53eaff44…` x86, RVA входа `0x187520`.
Сборка, линковка, потребители, ранний Taiwan и вход на NeutralB прошли.
Шесть компонентных случаев прошли на штатных таблицах и двух клипах Wing.
Сессия IDA сохранена и закрыта. [Доказательства](../research/client455-monster-force.md)

# Частичная проверка 190 — кадры Youngflem

11.11.2026. `a779670e…` x86, RVA входа `0x187410`.
Сборка, линковка, потребители, ранний Taiwan и живой вход прошли.
Штатный клип стояния Youngflem виден в трёх кадрах NeutralB.
[Доказательства](../research/client455-monster-view.md)

# Частичная проверка 189 — анимации монстров

11.11.2026. `f6816c3f…` x86, RVA входа `0x187340`.
Сборка, линковка, потребители, ранний Taiwan и живой вход на NeutralB прошли.
Найдены штатные клипы Wing. Сессия IDA сохранена и закрыта.
[Доказательства](../research/client455-monster-animation.md)

# Частичная проверка 188 — состояние атаки и модель монстра

11.11.2026. `c8151a03…` x86, RVA входа `0x186e20`.
Сборка, линковка, потребители, ранний Taiwan и нативная проверка
городской атаки прошли. Живое 4/34 доставлено аватару, кадр показывает
модель монстра. Сессия IDA сохранена и закрыта.
[Доказательства](../research/client455-town-state.md)

# Частичная проверка 187 — обновление отметок объектов

11.11.2026. `f16919a8…` x86, RVA входа `0x186d40`.
Сборка, линковка, потребители и ранний старт Taiwan прошли.
Четыре компонентных маршрута и 92 обновления в живом прогоне прошли.
Сессия IDA сохранена и закрыта. [Доказательства](../research/client455-world-refresh.md)

# Частичная проверка 186 — таблица монстров в обычном клиенте

11.11.2026. `22421c33…` x86, RVA входа `0x186cf0`.
Сборка, линковка, потребители, ранний Taiwan и пять проверок таблиц прошли.
Два ограниченных запуска остановились в Miles. В обычном контексте
Windows после добавления штатных архивов монстров живой прогон
завершился штатно. Сессия IDA сохранена и закрыта.
[Доказательства](../research/client455-monster-data.md)

# Частичная проверка 184 — вертикальный поворот камеры

11.11.2026. `dad137eb…` x86, RVA входа `0x186630`.
Сборка, линковка, потребители и ранний старт Taiwan прошли.
Три тестовых перетаскивания дали −89° и кадр с небом.
Сессия IDA сохранена и закрыта. [Доказательства](../research/client455-world-camera.md)

# Частичная проверка 183 — локализованная раскладка и движение

11.11.2026. `253767b6…` x86, RVA входа `0x186210`.
Сборка, линковка, потребители и старт Taiwan прошли. Живой прогон
сдвинул аватар и подтвердил стабильную позицию после движения.
Сессия IDA сохранена и закрыта. [Доказательства](../research/client455-world-walk.md)

# Частичная проверка 182 — ресурсы sky2 для живой NeutralB

11.11.2026. `c24a41d0…` x86, RVA входа `0x185f90`.
При одинаковом бинарнике и 2 010 одинаковых входных файлах
добавлены `.r3e/.r3m/.r3t` из `Map/NeutralB/sky2`. Местность
видна на двух кадрах. [Доказательства](../research/client455-neutralb-sky.md)

# Частичная проверка 181 — два захвата после стартовой позиции

11.11.2026. `c24a41d0…` x86, RVA входа `0x185f90`. Сборка и
линковка, проверка потребителей и ранний старт Taiwan прошли.
Живой прогон записал три состояния и два кадра 640 × 500 после
ответа `3/2`, завершился без фатального исключения.
[Доказательства](../research/client455-world-observation.md)

# Частичная проверка 180 — первый игровой кадр NeutralB

11.11.2026. `b001f830…` x86, RVA `185a60`. Собраны 182 модуля клиента,
67 движка и 20 общих. Прошли компонентные проверки и ранний старт.
В живом прогоне создался аватар, завершилась отрисовка сцены, принят
`3/2`, после него получено 276 сообщений. Фатальных исключений нет.
Сессия IDA сохранена и закрыта. [Доказательства](../research/client455-avatar-world.md)

# Частичная проверка 179 — загружена карта NeutralB

11.11.2026. `16b78443…` x86, точка входа RVA `185a60`, 182 модуля
клиента, 67 движка и 20 общих. Прошли тест списка и старт Taiwan. Живой
клиент разобрал `12/9` на 961 байт и загрузил BSP. Следом необработанный
`logic_error` при создании аватара. Сессия IDA сохранена и закрыта.
[Доказательства](../research/client455-store-download.md)

# Частичная проверка 178 — макросы, объявления и список гильдии

11.11.2026. Сборка `35e531e1…` x86, точка входа RVA `185a70`. Собраны
182 модуля клиента, 67 движка и 20 общих. Прошли компонентные тесты,
старт Taiwan и живой выбор. Разобраны `3/50` и `13/105`, получен
`27/112` на 2 байта. Фатальных исключений нет. Сессии IDA закрыты.
[Доказательства](../research/client455-macro-download.md)

# Частичная проверка 177 — настройки Linker и ответы продолжения

11.11.2026. Сборка `168d1414…` x86, точка входа RVA `1855a0`. MSVC собрал
182 модуля клиента, 67 движка и 20 общих. Прошли компонентный декодер,
старт Taiwan и живой выбор. Получены `3/50` на 954 байта и `13/105` на
650 байт. Фатальных исключений нет. Сессия IDA сохранена и закрыта.
[Доказательства](../research/client455-linker-download.md)

# Частичная проверка 176 — показатели развития и ответ Linker

11.11.2026. MSVC x86 собрал 182 модуля клиента, 67 движка и 20 общих.
Сборка `cd3f1c0d…`, точка входа RVA `185100`. Пройдены проверки форматов,
раннего старта Taiwan и локальный прогон. Семь записей сопоставлены с
`Quest.edf`. Пустые списки юнитов и добычи обработаны. Ответ `3/45` на
157 байт получен без фатального исключения. Сессия IDA сохранена и закрыта.
[Доказательства](../research/client455-mastery-quests.md)

# Частичная проверка 175 — базовые данные, инвентарь и Сила

11.11.2026. Сборка `0280bf77…`, x86, точка входа RVA `183f90`.
MSVC собрал 182 модуля клиента, 67 движка и 20 общих, линковка чистая.
Декодеры проверены на полных, пустых, ошибочных и усечённых записях.
В живом прогоне дошли до `3/8` на 322 байта без фатального исключения.
Заголовок инвентаря указал три сумки. Предметы и записи Силы не разрешились
через старые таблицы. Сессия IDA сохранена и закрыта.
[Доказательства](../research/client455-initial-download.md)

# Частичная проверка 174 — окна цели и базовые данные

11.11.2026. MSVC x86 собрал 182 модуля клиента, 67 модулей движка и 20
общих модулей. Сборка `c85bd40d…`, точка входа RVA `184160`.
На стенде прошли четыре кадра Taiwan. В тестовую папку добавлены точные
`renewal.spr` и `dungeon.spr` из ресурсов 455. На локальном сервере после
выбора отправлен `3/3`, получен `3/4` на 431 байт. Остановка на этапе
обработки базовых данных, фатальных исключений в финальном прогоне нет.
Сессии IDA сохранены и закрыты.
[Доказательства](../research/client455-target-windows.md)

# Частичная проверка 173 — окно группы

11.11.2026. MSVC x86 собрал 182 модуля клиента, 67 модулей движка и 20
общих модулей. Сборка `59122c67…`, точка входа RVA `184300`.
После принятого выбора прошло окно группы 19. Следующий сбой в
`CGUISelectedMobInfoWin::SetSprite`, собственный RVA `130a9f`.
Два кадра Taiwan и пять сообщений прошли компонентную проверку.
Исправлен номер исходящего запроса базовых данных. Его отправка и
ответы пока не достигнуты. Сессия IDA сохранена и закрыта.
[Доказательства](../research/client455-party-window.md)

# Частичная проверка 172 — обмен валют, добыча и смена класса

11.11.2026. MSVC x86 собрал 182 модуля клиента, 67 модулей движка и 20
общих модулей. Сборка `917f69fb…`, точка входа RVA `183da0`.
После принятого выбора прошли три окна и подключение Linker. Следующий
сбой в строке окна группы, собственный RVA `13088f`. На стенде прошли
три кадра Taiwan, восемь сообщений и границы валютной котировки.
[Доказательства](../research/client455-service-windows.md)

# Частичная проверка 171 — изготовление и улучшение

11.11.2026. MSVC x86 собрал 182 модуля клиента, 67 модулей движка и 20
общих модулей. Сборка `c9aeaf27…`, точка входа RVA `1844e0`.
Оба окна инициализировались после принятого выбора персонажа. Следующий
сбой в окне обмена валют на собственном RVA `130fff`. На стенде
прошли четыре кадра Taiwan, 14 сообщений и три кадра регрессии магазина.
[Доказательства](../research/client455-item-work.md)

# Частичная проверка 170 — обмен между игроками и обработка руды

11.11.2026. Сборка `ad434f01…` x86, точка входа RVA `183AF0`.
Собраны 182 модуля клиента, 67 модулей движка и 20 общих модулей.
Линковка прошла. Три кадра Taiwan и три сообщения обмена проверены.
Оба инициализатора вернулись после принятого выбора. Следующий сбой
в окне изготовления предметов на собственном RVA `13066F`.
[Доказательства](../research/client455-trade-ore.md)

# Частичная проверка 169 — торговое окно NPC

11.11.2026. MSVC x86 собрал 182 модуля клиента, 67 модулей движка и 20 общих
модулей. Сборка `7d348e69…`, точка входа RVA `183430`, 2 367 488 байт.
Неразрешённых символов нет. Компонентно проверены три кадра на ресурсах
Taiwan. После принятого выбора обычный клиент прошёл торговое окно NPC,
следующий сбой в окне обмена между игроками, RVA `12FF6F`.
[Доказательства](../research/client455-shop-window.md)

# Частичная проверка 168 — навыки, Сила и граница торгового окна

11.11.2026. MSVC x86 собрал 182 модуля клиента, 67 модулей движка и 20 общих
модулей. Сборка `83b60d77…` имеет точку входа RVA `182D80` и размер 2 365 440
байт. Линковка прошла без неразрешённых символов.

Три кадра панели проверены на ресурсах Taiwan. Живой запуск после принятого
выбора дошёл до `CGUIShopWindow::SetSprite`, сбой на собственном RVA `12F8BF`.
Последние компонентный и живой запуски использовали ресурсы из общего пула.
[Доказательства](../research/client455-skill-force-window.md)

# Частичная проверка 167 — UnitTuning и UnitStorehouse

11.11.2026. MSVC x86 собрал 182 модуля клиента, 67 модулей движка и 20 общих
модулей. Линковка прошла без неразрешённых символов. `RF_Online.bin` `23332d3f…`
имеет точку входа RVA `183A80` и размер 2 370 048 байт.

Обе панели и три сообщения проверены на штатных ресурсах Taiwan. Живой переход
после выбора прошёл обе панели и дошёл до старого окна навыков. Точка сбоя
`CSprite::GetSpriteXL` на RVA `1305EF`. Вход в мир остаётся открытым.
В общий пул добавлено 1 131 504 байта ресурсов для компонентной проверки.
Живой запуск повторно использовал общий пул без новых файлов в нём.
[Доказательства](../research/client455-unit-windows.md)

# Частичная166 — пять банков Linker и следующий UnitTuning

11.11.2026. Own fe40637c…/x86/entry183720/2369024bytes;182/67/20,
сборка/линковка0. Linker MainGame создаёт5x10/window3; native7d430eab проверяет
50 владельцев, реальное сообщение через менеджер и8 просмотренных кадров.
Live выбор принят, Linker startup вернулся; следующий старый UnitTuning.Init
падает в GetSpriteXL ownRVA13028F. Мир не достигнут. Фабрика17 классов/37 missing,
полная семантика17 также не принята. 6full/3032instructions обоих pins.
Всего54 владельца: старый regex пропустил CBlackListBoard12bytes/slot30.
Анализ2463(+2)/657(+6), индекс37871 прежний;25%(20–35%),0/12 прежние.
38sharedassets/79608818linkedbytes/0newpoolbytes; IDAa06985c9/5c316b5a saved/closed/list0,
все own jobs завершены, handoff удалён. Сервер и originals не менялись.
[Доказательства/остаток](../research/client455-board-startup.md).

# История165 — новые окна и подтверждённая граница

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

# Частичная164 — проверенная сборка и новая живая граница

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

# Частичная163 —11.11.2026

MobControl455 подключён к обычному клиенту:16детей/3команды,real13/4/1skins,
signedHP-FP/stepEXP/resource/namepolicy/viewport. Общий MoveObjectMgr перенесён
по455:zero-start/duration,sinefloat/exactendpoint,waves/acceleration,realclock.
34fullfunctions/3119instructions bothpins,22countryvirtual53pointer proofs.
Native10c89a6e/4viewedGPUframes/3actualHWNDmessages/movementreplay PASS.
Own ae592e21…/x86/entry1821E0/2362368bytes,182client/67engine/20kernels/link0,
consumer/entry/startup/earlyTaiwanPASS. Передdeviceprobe обновитьearlyevidence;
guard старой162 не был продуктовым отказом. Live001 choice/result0,
MobControlInit пройден;nextoldOption.SetSprite/Init fatalown12ED3F.
Candidate stack scan corroborated caller/vtable/source,не unwind. Currentgate
mob-control-checkpoint PARTIAL_KNOWN_FAILURE. World/M9OPEN,0/12,coarse25% прежний.
FullAnimus/equipmentresourceproducer/tooltippolicy/edge domains открыты.
Функции2375(+28)/559(+30),IDA37870,91выборочныйpartialbinding.
Before163135files/7193032private+3623572sharedbytes. Native30assets/
17904385linkedbytes/0newpoolbytes. IDAe410717fclosed/list0/nativejobsdone.
Оригиналы/servercode/config не менялись;handoff удалён. Подробнее:
research/client455-mob-control.md;дальшеOptionWindow455/очередь164.

# История162 —11.11.2026

Recall455 window/rows подключены к обычному CGUIRecallWindow. Natural skins,
name/index/40byte record, HP/FP DWORD, EXP, cover, scroll/resize и target stale
content height восстановлены. 39fullASM/CFG/3039instructions совпали bothpins.
Пять ранее не выделенных setter heads определены в рабочей IDB; индекс37870,
не изменение input bytes. Positive-SP decomp warnings отмечены, использован ASM.
Native finala5e7bd7a/8controlledrecords/5GPUframes PASS, кадры просмотрены.
Первый oracle140px исправлен по реальным descriptor132/132/89; код не подменялся.
Own e929b1ec…/x86/entry181DA0/2360320bytes,182client/67engine/20kernels/link0.
Consumer/entry/startup/earlyTaiwan PASS. Live002 actualselection result0,
RecallInit пройден; следующий oldMobControl числовой consumer падает own12E81F.
Кандидаты стека corroborated own virtualcall/vtable/source order; не unwind.
Stack helper исправлен после unreadable cross-boundary1024byte read на до256
DWORD reads/ownPEaddresses only, rawstack/accountdata не сохраняются.
Gate recall-checkpoint PARTIAL_KNOWN_FAILURE, world/M9OPEN,0/12,25%(20–35%).
Полные Animus gameplay/table/network producers/settings/link/lifecycle открыты.
Функции2347(+37)/529(+39),69выборочных partialbindings. Before162124files,
7189195private+3487736sharedbytes;native34assets/81615873linkedbytes/0newpoolbytes.
IDA bac5c81d saved/closed/list0; originals/servercode/config без изменений.
Доказательства/очередь163:research/client455-recall.md,docs/next-steps.md.

# История161 —11.11.2026

CharInfo455 подключён к обычному CGUICharInfoWindow:3pages/23owners,real47/common,
race/mastery/resist/extras/input/wheel/resize.60полных ASM/CFG/6095instructions
совпалиbothpins. Nativefinaldb389785/3races/6GPUframes PASS,finalimages просмотрены.
Naturalheightheaderисправлена:1x4sheetтолькодляhighlight;nativegeometryassertions.
Ранние33923840/161a997cкадрынеподтверждаютгеометрию.18partialbindings;TabBoard ordinary.
Own 3ebd9a7d…/x86/entry181DA0/2360320bytes,182client/67engine/20kernels/link0.
Early/consumer/native PASS. Live actual1/14→1/15/22/result0,CharInfoInitпройден.
Следом unhandledC0000005/own12E8FF вoldRecall.SetSprite/Init. Мир не достигнут.
Gate char-info-checkpoint PARTIAL_KNOWN_FAILURE. Функции2310/490,coarse25%/0из12.
ПолныйMainGameUI/игровыепровайдеры/M9OPEN. Updated assessment не используетстарый159.
Before161113files сохранён;native30assets/15411905linkedbytes/0newpoolbytes.
Перваяlivea51непослала1/14(inactiveGetMessage),непринята. Контролируемыйown-child
background WM_ACTIVATEAPP передEnter восстановил тест без OSfocus/systemkeys.
Buttons disabled descriptorисправлен,повторены затронутыепроверки. IDAa2513525
saved/closed/list0;серверныйкод/настройки иoriginals безизменений.
Доказательства/следующаянавигация:research/client455-char-info.md.

# История160 —11.11.2026

Настоящий TabBoard455 восстановленкакclientdependency:17fullfunctions/1318
instructions bothpins;normalobject/libraries compiled/link0. Nativefinal
work/m9/a7aba19d/tab-board-001:раскрытие5sections/scroll/reflow/resize/ownership/
4GPUframes PASS. Generic native content — явныйпример,неfullCharInfo.
Новыйкласс НЕ удержанordinaryPE и ещё не подключён кстаромуокну. Gate
inventory/client455-tab-board-checkpoint.json PARTIAL_COMPONENT_ONLY.
Normal7354a931…/x86/entry17FA40/2349056bytes. Sectionsравны159кроме timestamp
IMAGE_DEBUG_DIRECTORY210254,проверенногоравнымCOFFtime. Новыйliveнепроводился.
Передправками exact159сохраненаbefore160/104files. Первыйminmacrocompileerror
и неверныйreload oracle исправлены;новыеGPUкадры/реальныеproviders проверены.
Функции2262(+16)/439(+17),14partialcomponentbindings. Оригиналы/serverбезизменений.
IDA5f9b1aa3 saved/closed. ДальшеподключениеouterCharInfo/3pages/23values.
Research:client455-tab-board.md;next-steps161. Полныйклиент/M9OPEN.

# История159 —11.11.2026

Own afb30309…/x86/entry17FA40/2349056bytes,182client/67engine/20kernels,
build/link0. Настоящая верхняя панель455:main/common/EtcUI,4полосы/17children,
image-text/уровень/пороговыецвета. NativeGPU3кадра/7threshold/reload/DmallocPASS,
кадры просмотрены. 19функций/1406инструкций полных ASM/CFG совпалиboth455pins.
Live Enter принят;прежний Gaugeсбой пройден. Следующийфатальныйотказ встаром
CharInfo.SetSprite/Init,own12C53F/GetSpriteOrgXL. World/MainGameUI/M9OPEN.
Gate:inventory/client455-hud-checkpoint.json,PARTIAL_KNOWN_FAILURE.
Раннийstartup/consumer bridge PASS. Свежие2246(+15)/422(+19)functionevidence,
пятьчастичныхbindings. Старые большие suites не повторялись. Before15992files
сохранён;сервер/оригиналы без изменений,секреты/handoffнесохранены.
IDA8c2a0833/7f0c7676 saved/closed. Research:client455-hud.md.

# История уточнения измерения прогресса —11.11.2026

Проверен дополнительный учёт функций:37865индекс/2231адресные материалы/
403полный листинг-CFG. Self-test неполных доказательств и реального156 PASS.
SHA семи последних sourcebindings совпадают с текущими файлами; это выборка,
не общий итог восстановленных функций. Отчёт теперь отдельно требует
показывать переходы старых RVA в исходники/обычную сборку/игровую проверку.
Метод:docs/function-coverage.md. Полная игровая приёмка не изменилась.

Разведка HUD159 сохранена отдельно; её RTTI/pointers/decompiler не включены
в доказанное восстановление. До source edits сделан before159/92files.
OwnPE158 не пересобирался. Owned IDA ae5a3b1a saved/closed/list0.

# Частичная158 —11.11.2026

Owndf69c7ef…/x86/entry17FCD0/2349568bytes,182client/67engine/20kernels/link0.
Actualaddressed Enter and1/14→1/15/22/result0 работают;typed Avatar gear handoff
дошёл доMainGame::Create_UI. Послеэтого unhandledC0000005/GetSpriteXL12C8AF:
стараяGaugeExp skin/atlas ещёнеперенесена на455. Gate selection-checkpoint
PARTIAL_KNOWN_FAILURE;worldnotentered. SDK/serverнепричинаэтогоотказа.
Nativewire/wallet/defaultretain/PRNG и3priorPNG PASS;M9OPEN.69-filebefore158
сохраняет157. IDAsaved/closed/list0. Секретынесохранены,handoffудалён,
сервер/оригиналынеменялись. Research:client455-selection.md. Нижеистория.

Own88dc3d11…/x86/entry17F850/2348544bytes,182client/67engine/20kernels,
build/link0. Gate actor-lighting-checkpoint PARTIAL. Исправлен actual actor
map-light/material consumer; engine library не менялась. Native actual lobby
12 случаев/gear/GPU и3прежнихPNG PASS. OrdinaryTaiwan Login иживой кадрвыбора
370/8000ms без unhandled/следующийRenderreturn PASS. Сравнение156/157 просмотрено:
персонаж больше не почти чёрный. Выбор/мир/full455stage ещёOPEN.
MCP полный ASM/CFG3functions/208instructions,оба455pins совпали. Реестр функций
2 225(+3)/396(+3);первые3sourcebindings сохранены,это не3полныхequivalence.
Тестовый auth принят;handoffудалён,серверныефайлы/оригиналынеменялись.
Послеисправленияформатаfunction-history общийprepare/build снова работает.
Подробности:research/client455-actor-lighting.md;next-steps.md. Нижеистория.

# Дополнение к аудиту прогресса —11.11.2026

Добавлен воспроизводимый реестр функций оригинала: 37 865 выделено IDA,
2 222 уникальных владельца имеют hash-verified code evidence в 158 отчётах,
393 имеют подтверждённые полный листинг/CFG. Это охват доказательствами,
не восстановленная доля клиента. Подсчёт выполнен чтением BIN/отчётов и
IDA MCP; входные EXE не выполнялись, own156 не пересобиралась. Проверки
неполных доказательств и реального среза156 PASS. IDA saved/closed/list0.
Метод/границы: docs/function-coverage.md; inventory/client455-function-coverage.json.

# Частичная156 и исправление Game Bar —10.11.2026

Own68e02c3d…/x86/entry17F710/2348032bytes,build/link0;gate
inventory/client455-combat-transition-checkpoint.json PARTIAL. Живой кадр
выбора получен,анимация подтверждена пользователем,unhandled0;свет неверный.
Win10Pro22H2/19045:GameBar package отсутствует,GameDVR_Enabled был1.
По запросу пользователя выставлены HKCU GameDVR/AppCaptureEnabled=0 и
System/GameConfigStore/GameDVR_Enabled=0;запросStore пересталпоявляться,
подтверждено пользователем. Backup artifacts/environment/game-capture-20261110-232356-911.json,
обратимый scripts/Set-GameCapture.ps1. Перезагрузки/переустановки не проводились.
Следующаяпроверка — получение света изкарты иматериал персонажа. Данные ниже исторические.

# Частичная155: реальный игровой вход —10.11.2026

Own da42b501…/x86/entry17F660/2347520bytes;182client/67engine/20kernels,
build/link0. Gate inventory/client455-live-login-checkpoint.json PARTIAL.
Launcher27831 и игровой запрос1/1→ответ1/2(result0) работают на сервере0.4.0.
Короткий1/9 ответ178 больше не отбрасывается;upgrade уtyped normal-item
пишетBYTE113 по462170. Native encrypted receiver/границы и3прежних кадра PASS.
Обычный Login проверен;живой выбор падает вequipped SetAction/legacyGetEquipItem.
Это клиентская миграция,не нехватка SDK/сервера. Мир/M9OPEN. Пароль/пакеты
не сохранены;временный ключевой handoff удалён. IDA session9079cdac saved/closed,list0.
Данные ниже исторические. Полная storageопись не повторялась.

# Проверенная154 и живая сеть —10.11.2026

C2280 устранена:own31d24ab9…/x86/entry17F430/2347008bytes,
182client/67engine/20kernels/build-link0. Gate player-owner-checkpoint PARTIAL.
Primary12-slot CPlayerProc/frame/render/defaultgarment/SFcallback/cloak проверены
на реальных ресурсах;полные appearance/selection/gameplay/M9 ещёOPEN.
Taiwan Create/Login/account3Avatar PASS;Login195/3000ms,7firstchance,unhandled0.
Пользователь запустил именноrf455-v0.4.0 ивошёлоригинальнымклиентом;порты/пути/
хеши подтверждены. Own TCP27830→engine/Miles иlauncher-auth27831accepted/key16
проверены отдельно;это не ownRFgameauth. Сервер не менять/строить.
См.research/client455-player-owner.md,client455-live-launcher.md и
inventory/client455-live-server.json. Ниже исторические записи,включаяисправленную
ошибку154компиляции. Последняяполнаяstorageописьостаётся20:56:14,не новыйзамер.

# Сверка20:56 — 10.11.2026

Проверенная обычная база153 сохранена до154вbefore154 (53файла).
Текущие исходники154 имеют C2280 вcavatar.cpp:162,копирование Avatar/владение
экипировкой;это ошибка незавершённой миграции,не нехватка SDK или компилятора.
Промежуточная154линковалась,но runtime-проверки не было. В готовность не включена.
Новая описьworkspace:158.84GiB logical/43.19GiB unique file sizes,ошибок0,
удалений0. Не физические кластеры. IDA21aeaaf3 savedclosed,list0.
Последний принятый partialgate/оценка ниже остаются действующими.

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

# Актуальная база149 —10.11.2026

Ownf4e62e48…/x86/182client-67engine-20kernels/link0. Обычные Create/Login
иaffectedaccount/registered3Avatar проверены;Login65/3016ms просмотрен.
Новые sourceequipmentRender/fade/alpha/overlayproducer/retainedposequeue прошли
actualGPU fixture. Обычные queueentrypoints/secondarygeometry удержаны PE.
Fullplayer/selection/particle-registry/M9OPEN;новыхустановокнет.
Сохранена148runtimeи16exactsourceinputs. IDA0a6749cesavedclosed/list0,jobsнет.
Оригиналы/serverнеизменны. Подробности:research/client455-equipment-draw.md.
Нижеистория;опись16:34:07 —последнийполныйзамер,не новыйпосле149.

# Актуальная база148A — 10.11.2026

Own03637d6a…/x86/182client-67engine-20kernels/unresolved0,
engine4c6652a5…;Create/Login иaccount/registered3Avatar PASS.
Grade materials/UV/secondarygeometry/archiveflag:source иGPUfixture
снастоящеймоделью иизмеренной RGB-разницей проверены. LifecycleCALLs удержаны
обычной PE;вторичная geometry функция ещё вызывается лишь probe.
Full mesh-object Render/CPlayerProc/selection/world/M9 OPEN. Новых установок нет.
IDA c6eeef7e savedclosed/list0;jobs завершены. Оригиналы/сервер не менялись.
Опись16:34:07:156,14GiB по путям/42,96GiB уникальных файлов, ошибок0,
удалений0. Новыефинальныеstaging не копировали ресурсы заново(newpoolbytes0).
Подробнее:client455-grade-overlay.md вresearch иdocs/progress-report.md.
Ниже история,не текущие статусы.

# Актуальная база147 — 10.11.2026

C2079 проверочной программы исправлен. Реальный CCharacter20×30/13dummy,
затронутые Avatar/registered receiver,обычный Create иLogin прошли.
Own993978ff…/x86/182client-67engine-20modules/link0;gate character-palette-checkpoint.
Кадр66/3031ms просмотрен,видна lobby/ожидание;полный455UI/auth/world не принят.
Девять перехваченныхfirst-chance имеют профиль145,необработанных0.
Map-файлы затронутых probes сохраняются отдельно отперезаписываемой папки сборки.
Новыхустановок нет;M9OPEN,оценка25%(20–35%) неизменна.
Renderer148:27полныхфункций/vtable подтверждены,реализация покаAUDIT_OPEN.
IDAeaa5fe38 saved/closed/list0;активныхruns нет.
Далее сохранена история;состояние147 «не проверена/C2079» относится кначальной попытке.

# Актуализация оценки — 10.11.2026

Последний проверенный обычный запуск:145/1a355372…; точная база сохранена
в artifacts/client455-progress/before146/. Кандидат147/993978ff… собран
182client/67engine/20modules, unresolved0. Его запуск ещё не проверен:
отдельная palette-проверка не компилируется с C2079 (CCharResDataMgr).
Это незавершённая работа, не новое достижение приёмки.

Опись14:12:21:155,29GiB по путям/42,87GiB уникальных файлов, ошибок0,
удалений нет. IDAb6dd2ecb сохранена и закрыта, idb_list0, активных runs нет.
Новых установок не нужно. Оценка25%(20–35%),0/12полных областей принято.
docs/progress-report.md и docs/next-steps.md содержат актуальное состояние.
Ниже история; прежние «текущие» сборки относятся к своим записям.

# Предыдущая актуализация146conditions —10.11.2026

Новыхустановокнет. Typed special/upgrade/combinedstats/weakpart source,
52fullfunctions/2323instructions/357CFG equal2pins,6dataregionspinned.
Native22realitems/independentmodifierbytes+totals/clone removal PASS.
ТолькоCPU,3assetinputs,newpool7953bytes;GPU/models/texturesнеиспользовались.
Ordinary145неизменна;owner skill/UI callbacks ещёнеподключены,fullM9OPEN.
IDA71813681saved/closed/list0;nativejobsзавершены.
research/client455-equipment-conditions.md;далееобычноеCPlayerProc/Avatarсоединение.

# Предыдущая актуализация146attachment —10.11.2026

Новыхустановокнет.23fullfunctions/1953instructions/223CFG иswitchтаблица
равны2pins. Sourceпозицииэффектов+25реальныхмоделей/5races/5cloakmagic
прошлиnative,новыеpoolbytes0. Ordinary145PEнеизменна;fullappearance/M9OPEN.
IDA5c1cdbca saved/closed/list0;nativejobsзавершены. Подробности:
research/client455-equipment-attachment.md;далееtypedconditions/ordinaryintegration.

# Предыдущая актуализация —10.11.2026,146компоненты

Новых установок не требовалось. Обычная145сборка1a355372…неизменна.
Отдельные controller/ANI/fade/height/effect ownership компоненты проверены;
fullappearance/selection/bootstrap/world/M9 ещё открыты.
Состояние и оценка:docs/progress-report.md;очередь:docs/next-steps.md.
IDA1049c6e2 сохранена/закрыта;idb_list0;nativejobsзавершены.

Sharedassetpool упёрся вNTFS1024links у280byteBBX;ограниченные собственные
реплики восстановилиstaging. ПовторныйnativePASS,+280bytes,оригиналотдельныйinode.
Свежаяreadonlystorageопись:154.86GiBlogical/42.85GiBunique,ошибок0.
Это суммафайловыхразмеров,не точнаяfilesystemallocation. Файлынеудалены.
Ниже история;старые значения и «текущий» относятся к соответствующим версиям.

146ANI/fade:новыхустановокнет.24fullfunc/2220instructions/373CFG equal2pins;
реальныеANI/pose/fallback/failure/fade/lift прошли.13slotprobeпересобранPASS.
IDA4ce73361savedclosed/list0;nativejobsнет. Ordinary145не менялся.
Использован установленныйdumpbin +nativeIDA CFG/count дляполнойASMвыгрузки.

146,10.11:новыхустановокнет.Отдельныйsourcecontroller13slots/normalclone
прошёлfull-object nativeпроверку.32func/1640instructions/225CFG equal2pins.
IDA7c61237d saved/closed/list0;nativeexit0.Ordinary145PEне менялся.
Actualproductionanimation/condition/effectproviders иappearance ещёopen.

# Актуализация аудита —10.11.2026

Последняя собственная x86сборка1a355372…/entry175F50:182client/67engine/
20additionalmodules,0unresolved. Новых установок не требовалось.
145PARTIAL:32реальные модели,33GPU-текстуры,30вызовов обычного базового
оснащения,6слотов Avatar; затронутый receiver и обычныйLogin проверены.
Login frame70/3235ms просмотрен: lobby/ожидание;авторизация не выполнялась.
FullPlayerProc/equipment/draw/selection/bootstrap/M9 OPEN.
IDA7dd394bb saved/closed. Оригиналы/server не изменялись.

Готовность исходных данных и оставшийся объём: [progress-report.md](progress-report.md).
Gate:inventory/client455-equipment-checkpoint.json;research/client455-equipment.md.
Далее сохранена история аудита; её прежние номера «текущего» не актуальны.

# Аудит окружения — 04.11.2026

Дополнение144(10.11.2026):own ea25eea5… собран182/20/link0;
Avatarclassindex/name writers165/3locales иencryptedreceiver3Avatarclasses PASS.
Fresh ordinaryLogin70/3219ms inspected,nofatal.23textwidgets провереныкак
ownerданных;полныйUIlayout/classskills/equipment/selection OPEN.
IDA01ef697a saved/closed;новыхустановокнет.
research/client455-avatar-classes.md;Gate inventory/client455-avatar-classes-checkpoint.json.

Оценка10.11.2026: [progress-report.md](progress-report.md). Сборочные входы
для выбраннойконфигурации обеспечены;полнота исходников/ресурсов/поведения455
не доказана. 143 PARTIAL:сборка b41d50ff… иобычный Login проверены;14таблиц,
165class lookups иреальные панели умений проходят выбраннуюпроверку.
Avatarclass/equipment/selection не приняты;точнаябаза142 сохранена вbefore143.
Текущие числа проверок не процент готовности.

Историческая база142: собственный клиент f0114c80… собирается и
показывает реальную lobby/окно ожидания в обычном Login. Root-регистрация окон
перенесена по455; лишние панели больше не открываются одновременно.
Восстановлены обычные запрос58/ответ12 входа455 и их encrypted dispatcher.
Восстановлены запрос1/8 и ответ1/9 списка персонажей:506 байт,3 записи по164.
Реальный receiver применяет имена/уровни/деньги64/tutorial flag к3 Avatar.
В probe добавлены настоящие Character shaders; их отсутствие было причиной
ошибки инициализации. Итоговый probe PASS, новые bytes shared pool0.
Resource141:полный каталог9 групп,регистрация1267bones/10483meshes/18872ANI;
5 реальных player BN и1 archived player ANI загружены. Fresh ordinary Login PASS.
Item142:штатное началоcash/set/Item47+ND подключено;6real cases/3locales/
76049rows и12real wrappers наслучай PASS. Cash1000/set1373,дваcashNDfailures
сохраняютbase и не останавливают Item loading. Legacy derived item consumers OPEN.
Полная приёмка остаётся открытой. Gate: inventory/client455-item-bootstrap-checkpoint.json.
Оценка всего клиента: около25% (20–35%), см. roadmap.md и
inventory/client455-progress-assessment.json. Для сборки неразрешённых зависимостей
нет; полного исходного комплекта455 и полной карты его поведения пока нет.
Последняя IDA сессияb958e3d1 saved/closed; idb_list count0. Новых установок нет.
4newfullfunc/257instructions/27CFG и11country slots160 равны2pins;Item588asm
переиспользован. Fresh ordinary Login frame70/3234ms/no fatal. research/client455-item-bootstrap.md.
9 полных функций/623 инструкции/72 CFG блока списка персонажей равны двум455.
Полные bootstrap/classes/appearance/selection ещё не приняты; см. research/client455-registered-characters.md.
Resource141:7fullfunc/934instructions/108CFG иEHtails равны2pins. Часть ссылок
каталога не разрешилась:503BN/592BBX/25ANI после RFS lookup;это частичная опись,
не все assets и не доказательство обязательности каждого пути. Пять player BN есть.
Shared suffixes расширены BN/BBX/ANI/MSH/RFS;на первом staging+53.1MB,повторы0.
research/client455-resource-catalog.md. Account140 evidence сохранён before141,
его неизменённый suite на новой PE не повторялся.
Исторические проверки137 ниже не являются повторной проверкой всех систем новой PE.

M6 — частично: восстановлены пять ресурсов кадра и их освобождение.
Собственная сборка RF_Online.bin:42213f08…;свежий existingCreate1 проходит.
Проверены восемь конфигураций ресурсов,два захвата кадра и прежний эффект.
Общие игровые ресурсы повторных проверок теперь используются через shared pool.
Текущая проверка: inventory/client455-scene-capture-checkpoint.json.
Следующий функциональный рубеж — обычные Title/Login455.
Полная приёмка M6/M6F/M7/M9 остаётся открытой.
[Доказательства137](../research/client455-scene-capture.md).

Ниже сохранена история предыдущих этапов; текущий gate указан выше.

Дополнение09.11,chat109: новых установок нет. Две native IDA сессии saved/closed/list0;44 ranges/31fullasm/3615instructions,8 script inputs.

Историческое дополнение09.11,center108: новых установок нет. IDA20210106 saved/closed/list0;
25 selected/21fullasm/2914instructions/25equalranges.
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


Исследование108,09.11: native IDAffcaa552 saved/closed/list0;21 выбранный диапазон
обеих455 совпадает,17fullasm/2284instructions. Новых установок/запусков inputEXE
нет. Выявлен подтверждённый early/late aiming hook gap; сообщения пока только
исследованы. Runtime gate107 остаётся current.
[Доказательства108](../research/client455-system-messages.md).

Дополнение09.11,nuclear107: новых установок нет. Native IDA session7cb76d0f
saved/closed/list0;19functions/1670asm/19equalranges/2pickslots обеих455.
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
[Доказательства](../research/client455-nuclear-aiming.md).


Дополнение09.11,effect-runtime106: по сохранённому выводу native IDA MCP от07.11 проверены16 полных
функций/2546 инструкций/16 равных диапазонов+2data обеих455;ed41bb12 saved/
closed/list0. Установок нет. Own effect512/scheduling/lifecycle/render passes
рисует настоящий прицел в controlled D3D scene:4 viewedGPU,ordinary cancel
drain62/clear0pixels;6hover viewed/byte-equal105. R3T warning и GPU release
подтверждены в оригинале. Native573 assertions/90ticks/capacity513→512/memory
balanced с отдельнымglobaltexture teardown проходят. Full nuclear owner/world
pass placement/blur/qualityUI/device lifecycle ещё OPEN. PE12ca86c5…/entry15ab00/
182-20-59/unresolved0/Create1/Fast2D7969;resources66/magic36/status58/audio157/
account/hotbar7/storage3 pass. Engine546a… неизменён. Original/server без изменений,
input EXE не исполнялись. Gate106 current,105 historical;M6/M6F/M7/M9 OPEN.
[Доказательства](../research/client455-effect-runtime.md).

Дополнение07.11, effect-resources105: native IDA MCP подтвердил14 полных
функций/1315 инструкций/14 равных диапазонов и41-byte initializer обеих455;
session e536890b saved/closed/list0. Новых установок нет. Ordinary effect archive
owner/selection работает; реальные6 R3E models/5 particle recipes/10 clones
и D3D textures загружены.66 checks проходят.6 legacy R3T warnings остаются
gap;9728 байт process-owned texture tables отдельно освобождены public API
в стенде,Dmalloc balanced. Full GPU effect/FrameMove/nuclear ещё OPEN.
Новая PE015a25c2…/entry15a320/182-20-59/unresolved0/Create1/Fast2D ready:7969;
magic36/status58/audio157/account/hotbar7/storage3 и6 viewed byte-equal104
hover frames проходят. Engine546a… неизменён. Original/server не менялись,
input EXE не исполнялись. Gate105 current,104 historical;M6/M6F/M7/M9 OPEN.
[Доказательства](../research/client455-effect-resources.md).

Дополнение07.11, magic104: установленный native IDA MCP дал19 полных функций,
2988 инструкций,19 равных диапазонов и41-byte initializer обеих455; session20a3b068
saved/closed/list0. Новых установок нет. Own parser64/process3004/EffectInfo56/
runtime456 и реальный шестидорожечный cue из EffectEntity59.rpk проверены36 CPU
checks. Обычный cache Start/Disappear работает; группа архива пока задаётся стендом.
PE0419f2c0…/entry15a1f0/182-20-59/0unresolved/Create1 с прежним Fast2D ready:7969.
Status58/audio157/account/hotbar7/storage3 и6 viewed byte-equal103 hover frames
проходят. Engine546a… неизменён. Full effect render/bootstrap/nuclear cancel
остаются OPEN. Original/server не менялись, input EXE не исполнялись.
Gate104 current,103 historical; M6/M6F/M7/M9 OPEN.
[Доказательства](../research/client455-magic.md).

Дополнение07.11, tagged-audio103: действующий native IDA MCP подтвердил
18functions/1520asm/18equalranges;session6a70bd2b saved/closed/list0. Установок
нет. В копиях доступны реальные Miles M3D providers; фактически открыт Fast2D.
Новый CMainApp sound owner проходит157 проверок WAV/30channels/64LRU и обычный
Create→1 (debug ready:7969). Source PEcf7ac5e0…/entry159670/182-20-58/0unresolved.
Status58/account/hotbar7/storage3 проходят;6 viewedGPU byte-equal102. Engine546a…
не менялся. Для обнаружения providers путь нужно задать до AIL_startup;
неуспешные пробы сохранены отдельно, в итоговую приёмку не включены. Новый
native audio harness закрывает Miles через RAII. Полные nuclear effect/cancel,
весь звук/startup/unsafe/shutdown ещё OPEN. Original/server/inputEXE без изменений/
не исполнялись. Gate103 current,102 historical;M6/M6F/M7/M9 OPEN.
[Доказательства](../research/client455-tagged-audio.md).

Дополнение07.11, player-status102: действующий nativeIDA MCP подтвердил
17functions/2036asm/17equalranges и1diagnosticrange обеих455;session100f46bb
savedclosed/list0. Новых установок нет;engine546a… неизменён. ActualAvatar
status producer/getter/falsepredicate иordinaryhover проходят58CPU/6viewedGPU;
6кадров byte-equal101. SourceSetServerStatusFlag теперьULONGLONG,остальныеeffects
покаlegacy;full455wire receivers иnuclear cancelowner ещёOPEN. NewPE5f1f0f77…/
entry1587b0/182-20-57/0unresolved/Create1;account/hotbar7/storage3 pass.
ПервыйCPUlab безnetworkowner упалвlegacySetTextColor;стенд исправлен штатным
Create/Destroy,безподменыproduction. Original/server/inputEXE безизменений/
неисполнялись. Gate102current/101historical;M6/M6F/M7/M9 OPEN.
[Доказательства](../research/client455-player-status.md).

Дополнение07.11, board-hover101: native IDA MCP подтвердил23 functions/1156asm/
23equalranges. Sessionf131119f savedclosed/list0. Новых установок нет;engine546a…
не менялся. Copy620/dualbackups/ordinarymanager-screen/ReturnHover в source,
5payloadkinds+bare/256boardIDs/6viewedGPU проходят,32previousframes byte-equal.
Offline native network owner инициализируется штатно,безauthentication/remote.
182-20-57/0unresolved/PEe77ec7e7…/entry1586b0/Create1;hotbar7/storage3/account pass.
LiveAvatar state/cancel,operationqueue,three-layer tooltip/gameplay не приняты.
Original/server без изменений,inputEXE не исполнялись. Gate101current,100historical;
M6/M6F/M7/M9 OPEN. [Доказательства](../research/client455-board-hover.md).

Дополнение07.11, item-lock100: установленный IDA MCP подтвердил17 функций/
1610 инструкций/17 равных диапазонов обеих455. Session5eef459d savedclosed/list0.
Новых установок нет;engine546a7529… не менялся. Typed GUIItem получил actual
sprite52/8×12 lock child;CBoardObject refresh иобычныйLinker.Add подключены.
256raw/256normalized/18geometry/6viewedGPU и35byte-equal прежних кадров проходят.
Новая PE49882fc3…/entry157aa0/182-20-56/0unresolved/Create1;hotbar7/storage3/
account проходят. Из4 прежних provider refusals остаются3:SF/Animus callbacks
иpotioncache. Originals/server без изменений,inputEXE не исполнялись.
Gate100 current,099runtimehistorical;M6/M6F/M7/M9 OPEN.
[Доказательства](../research/client455-item-lock.md).

Дополнение07.11, ready-cooldown099: установленный IDA MCP подтвердил ещё8
функций/248asm/12равных диапазонов обеих455, поверх статических79/5906/82.
Sessionfa7d0341 savedclosed/list0. Новых установок нет. Derived startup engine
пересобран с общим CSprite header overlay и own inline texture accessor;
engine033/source сохранены. Новая library546a7529… заменяет derived0829caa…;
отдельный snapshot старой082lib не сохранён, исторические EXE/кадры остаются.
132state/48grid/6просмотренныхGPU,ordinarycache/originlookup/FrameMove/Remove,
20byte-equal прежних кадров,hotbar7/storage3/account/newPE6b30676b…/Create1 pass.
SFgroup проверен на actualglobalForce pack с synthetic CPUicons,не fullSFUI.
Gate099 current,098runtimehistorical;M6/M6F/M7/M9 OPEN. Originals/server не
менялись,inputEXE не исполнялись. [Доказательства](../research/client455-ready-cooldown.md).

Дополнение07.11, аудит099: действующий nativeIDA MCP подтвердил79 выбранных
функций/5906asm/82equalranges,20customLinkervtableentries и ready-sheet geometry.
Session31e85147 savedclosed/list0. Новых установок/изменений production нет;
текущая PE/engine/gate098 сохраняются. Original/server/inputEXE без изменений.
Это STATIC_ONLY_NOT_IMPLEMENTED, не новый runtime milestone. Следующая зависимость:
targetGUIanimation/readycue/mode3 перед cooldowncache и handlers.
[Доказательства](../research/client455-linker-cooldown.md).

Дополнение07.11, gui-timer098:32 equal ranges/29functions/2791asm; установленное
IDA MCP работает, session316a9b70 savedclosed/list0. Новых установок нет.
Typed timer в ordinaryCGUIItem:175state/112label/57radial(171triangles),actualcopy/
Update/empty/registryfanout/Linkerquery проходят.29GPUframes просмотрены:6 новых
и23 затронутых. Grade-frame order исправлен по455;11 прежних кадров изменились,
12 byte-equal, изменения учтены отдельно.182/20/54TU,0unresolved;PEd943ef46…/
entry156570/Create1 pass;hotbar7/storage3/account проходят. Originals/server
без изменений,inputEXE не исполнялись. Gate098 current,097 runtimehistorical.
[Доказательства](../research/client455-gui-timer.md).

Дополнение07.11, linker-window097:51 equal ranges/36functions/3509asm/14doubles/
signed50C branch. ActualCLinkBoard window member заменён на banked455 view;
21layout/1050icons/320cycles/48events/1792glyphs/8 просмотренных GPU проходят.
096owners/094metadata fresh,6rawframes byte-equal;hotbar/storage/account/newPE
9d8b57ad…/entry155690/182-20-53/0unresolved/Create1 pass. IDAa69bf228 и message
session savedclosed/list0. Новых установок нет;originals/server без изменений.
Fullgame actions/timers/livecallbacks/Macro remainopen;Use nativecallbackrecording.
Gate097 current,096 runtimehistorical;unchangedworld/audio/159k/bulk не повторены.
[Доказательства](../research/client455-linker-window.md).

Дополнение07.11, linker-owners096:21 equal ranges/1105asm;IDA bb7e4b5e savedclosed,
list0. Actual CLinkBoard Add/Remove/Clear/50clones/5×10/window icon owner/registry
и3 просмотренных GPU проходят. NormalPE613a6e97…/entry153bd0/182-20-51/0unresolved/
Create1;registration теперь retained в ordinaryPE.095registry/094metadata fresh,
6 raw кадров byte-equal. Hotbar/storage/account проходят. Полное window layout/
input/livecallbacks/cooldown/Macro ещё open;4missingproviders явноотказывают.
Новых установок нет;originals/server без изменений. Gate096 current,095 runtime
historical;world/audio/159k/старые bulk не повторялись.
[Доказательства](../research/client455-linker-owners.md).

Дополнение07.11, icon-links095:22 equal ranges/1154asm/160 key oracles;
IDA22f5e8a7 savedclosed/list0, configured MCP probe прошёл. Новых установок нет.
182client/20kernels/50facade,0unresolved;PEe2741f24…/entry1530e0/Create1.
ActualMainApp registry/typed fanout/duplicates/remove/3 просмотренных GPU прошли;
094 metadata повторён, его3 raw кадра byte-equal. Hotbar/storage/account проходят.
SetNum/SetUsable/find живут в ordinaryPE; register/unregister пока unused,
actualLinker/Macro Add-Remove не подключены. Gate095 текущий,094 runtimehistorical.
World/audio/159k/старые bulk не повторялись;originals/server без изменений.
[Доказательства](../research/client455-icon-links.md).

Дополнение07.11, item-icon-metadata094:28 equal ranges/1138asm/15 decoded reads,
IDA4f540aaf savedclosed/list0;configured MCP probe прошёл. Новых установок нет.
182client/20kernels/49facade TU,0unresolved;PE85a909e3…/entry152d60/Create1.
566 real metadata/520 race-level/16 actualinventory iconowners/3 просмотренных
GPU кадров, clone/clear/Dmalloc,hotbar/storage/account проходят. Common fields
core сохранён в ordinaryPE; полный payload handoff пока только own-entry caller,
обычный CItemBoard.Add не перенесён. Его host-контракты Linker6/Macro35/Vending27
закреплены. 159k/world/audio/старые bulk не повторялись. Gate094 текущий,
093 historical. Originals/server без изменений.
[Доказательства](../research/client455-item-icon-metadata.md).

Дополнение07.11, item-atlas093: обычный клиент собирает настоящий автоматический
выбор страницы/ячейки.18 equal ranges/1001 asm/47 decoded stores;880 сценариев,
4 просмотренных GPU кадра,9 byte-equal кадров092, owners/data/SF/hotbar/storage/
account и новая PE dbd71f6a…/Create1 проходят. IDA4c6c7c2c savedclosed/list0.
Дополнительно configured MCP probe подтвердил66 tools/10functions/decompilation/
smoke close. Его первый worker code2 в sandbox устранён разрешённым повторным
запуском того же probe; переустановки и правки конфигурации не было. Новых
установок нет; originals/server не менялись. Текущий gate093,092 historical.
[Доказательства](../research/client455-item-atlas.md).

Дополнение07.11, item-icon092: новых установок нет. IDA aa30c75c сохранена/
закрыта, список сессий пуст;22 диапазона/1740 инструкций и RTTI закреплены.
Поле GUIItem1240 уточнено: это цветная рамка, прежняя гипотеза caption неверна.
Новая PE e540395b…/entry152a30,182 client/20kernels/0unresolved/Create1.
256 цветов/120 количеств/8 размеров/9 просмотренных GPU кадров, Dmalloc reload
и предметы2013/data575/SF1447/hotbar/storage/account проходят. Общая GUI база
не менялась на новый ABI; typed core и отдельный target sprite cache ограничены
принятым доменом. Автоматический atlas/полныйGUI/bootstrap/game открыты.
Текущий gate092,091 runtimegate исторический. Карты/audio/159k не повторялись.
[Доказательства](../research/client455-item-icon.md).

Дополнение 07.11, item-object091: новых установок нет. IDA157b5ed2 сохранена
и закрыта, список сессий пуст. Закреплены21 диапазон/444 инструкции. Обычные
классы CItemObject592/CBoardObject620 и менеджер CMainApp собраны:182/20/46
объектов,0 unresolved. PE7d7ff847…/entry152070, Create=1. Проверены2013
владельцев/клонов через реальный pack,575 payload/SF1447 из production facade,
hotbar/storage/account. Новые runtime checks больше не линкуют вторую item.lib.
Начальные конфликты имён array/byte и флаги старых заголовков исправлены в порте.
Иконки, normal bootstrap и mixed consumers явно остаются открытыми. Gate091
текущий,090 исторический. Неизменённые GPU/audio/159k suites не повторялись.
[Доказательства](../research/client455-item-object.md).

Дополнение07.11, resource-object090: новых установок нет. IDA65c60c5d saved/
closed/list0;23equalranges/765asm/21decodedstores/7floatconstants. Ordinary
CObject80/CResObject584 перенесены;182/20/42objects/0unresolved. NewPEdc6f2c62…,
2093568bytes/entry1500e0/WinMainB5B40/Create1;engine082 неизменён. Whole-record/
160flags,hotbar/storage/account,actorFX/3worlds и renewed575/1447payloads прошли.
15GPUframes просмотрены. Первый world run выявил пропуск Character shaders
встаром lab runner;staging исправлен,production этойправкой не менялся.
Текущий gate090;086/088/089 runtimegates исторические.159k/audio безпричины
не повторялись. Реальные itemwrapper/gameowners и M9 ещёOPEN.
[Доказательства](../research/client455-resource-object.md).

Дополнение07.11, item-payloads089: новых установок нет. IDA877755f1 saved/closed/
list0;50equalranges/1796 полных инструкций, EH windows закреплены отдельно.
Ownx86/MT library: realItem76049/47tables,Quest12/Character7,3полных NDItem,
575factory/clone/lifetime и99AnimusXP проходят standalone/full-object.
UnchangedSFprobe1447 проходит с той же новой библиотекой;все4exit0,build warnings0.
088runtimegate исторический после изменения общего header;staticreference сохранён,
SFregression подтверждён089. Ordinary086/егоgate неизменны;GPU/startup/159k
не повторялись. Никакого нового разрешения или установки для следующего шага
не требуется. Gameowners/fullpayloads/Queststrings/Tutorial/M9OPEN.
[Доказательства](../research/client455-item-payloads.md).

Дополнение07.11, skill-force088: новых установок нет. IDAcd8baa1a saved/closed/
list0.35equalranges/1224actualasm,включая отдельно pinned EH-tail windows.
Concrete SF factory/manager/087clone-release:1447actualpayloads и ownedwrappers,
whole five-table byteoracle,standalone/full-object,exit0. Host уже concrete дляSF.
Original R3Engine.ini выбираетTaiwan;zh-tw counts совпадают сroot1447,ko/ru
fail наtable4/1 ссохранениемprefixwrites. Новая earlyTaiwan PE проверка950/
6997NDLanguage/localTCP/sound1 прошла доD3D. Production086 неизменна,егоgate
current;неизменённыеGPU/Korea-startup/159k suites не повторялись. OrdinarySF/
Linker/остальные payloadfactories/game/M9OPEN.
[Доказательства](../research/client455-skill-force-items.md).

Дополнение07.11, item-ownership087: новых установок нет. IDA65f54fa4 сохранена/
закрыта/list0;24 equalpinranges/579 полных asm,8 constructor stores декодированы
в oracle. Sourceбиблиотека x86/MT:3whole-record сравнения92/620bytes,12 lifetime
сценариев и7 границ BYTE прошли отдельно и через ту же библиотеку с полным
набором клиентских объектов. Host менеджера recording; обычный Linker/полные
factory/destructor ещё не связаны. ProductionPE086/его gate не менялись;
неизменённые GPU/startup/159k suites не повторялись. M6/M6F/M7/M9OPEN.
[Доказательства](../research/client455-item-ownership.md).

Дополнение07.11, hotbar086: новых установок нет. IDA811039d6 saved/closed/list0;
45 выбранных диапазонов равны между pins,640 полных asm instructions сохранены.
Обычный Linker delta-save/периодическая отправка проверены на настоящих объектах
и send ring/AES:7 пакетов,50 ячеек,максимум202байта. Три storage запуска,
account и exactnewPE/Create1 прошли. PE82625b3e…/entry14FD60/182-20-42TU/
0unresolved;engine9caa283a… неизменён082, contracts reused. Старые GPU/159k suites
не повторялись. FullLinker ownership/UI/input/oldbelt/Tutorial/M9 открыты.
[Доказательства](../research/client455-hotbar.md).

Дополнение07.11, storage085: новых установок нет. IDA64b119a2 saved/closed/list0;
10 дополнительных диапазонов обоих pins/25 полных asm physical-item guard и
53 primary-vptr/RTTI из084 проверены. Реальная source фабрика имеет17 классов
под правильными455 IDs/limit56;старый CBeltBoard удалён из фабрики. Три native
запуска, account и exactnewPE/Create1 прошли. PE89924a1c…/entry14F490/182-20-41TU,
0unresolved. Engine9caa283a… неизменён, его contracts reused;старые GPU suites
не повторялись. Неперенесённые oldbelt callers явно отклоняются, fullfactory/
itemprotocol/Tutorial/M9 открыты.
[Доказательства](../research/client455-storage.md).

Дополнение 07.11, tutorial-integration084: установок и изменений runtime нет.
IDA14d8cac3 сохранена/закрыта, список пуст. Проверены92 диапазона обоих pins,
1514 полных asm instructions четырёх функций и primary-vptr/RTTI53 объектов.
Source-only probe создаёт18 досок с настоящим CNetworkMgr; восемь финальных
запусков одинаковы/exit0. Начальные ошибки окружения probe (не создан network
owner, затем большой объект на стеке) исправлены только в проверке.
Подтверждены несовпадающие Force/Animus IDs, отдельные quest/Tutorial владельцы
и новые зависимости общей инициализации. PE083/engine082 не менялись; GPU и
старые большие suites не повторялись. M6/M6F/M7/M9 открыты, аудит AUDIT_OPEN.
[Доказательства](../research/client455-tutorial-integration.md).

Дополнение 07.11, money083: новых установок нет. IDA b55212f6 сохранена и
закрыта, список сессий пуст. 21 диапазон совпадает между закреплёнными x86
бинарниками; сохранены 382 инструкции десяти функций валюты. В собственных
копиях перенесены 64-битные поля/API Avatar и инвентаря; новая PE 8b516183…,
entry RVA 151490, 182/20/41 объектов, без unresolved. Korea/Russia: по 92
проверки в четырёх режимах округления, шесть просмотренных кадров. Account,
actor/FX и точная PE/Create=1 проверены заново; девять actor кадров просмотрены.
Движок 9caa283a… не менялся; проверки трёх карт/Miles из 082 не повторялись.
Полные обучение, вход и игра не приняты. M6/M6F/M7/M9 открыты.
[Доказательства](../research/client455-money.md).

Дополнение07.11, rvp-audio082: новых установок нет. IDAf1d662d0 saved/closed/list0;
18equalranges/1665actualasm/770Create decompilelines. Actual Miles driver/MP3
decoder clock/volume/loop и ordinary RVP ambient/event/timer проверены; WAV immediate
branch в455 подтверждённо не создаёт handle. Nativeexit0/warn0/Dmalloc785169balance.
Engine9caa283a…/67objects/12overlays,PE7489e8c7…/entry1512B0/182-20-40TU/
0unresolved/exactCreate1;3maps/actorFX/15reviewedframespassed. 8D6900 — destructor,
прежняя acquire-подпись081 исправлена. Fullsound/Tutorial/game/M9 OPEN.
[Доказательства](../research/client455-rvp-audio.md).

Дополнение07.11, rvp-effects081: новых установок нет. IDA2710bd78 сохранена/
закрыта;18 ranges совпадают между pins,2960 полных asm instructions сохранены.
Собственные CParticle/CEntity1296/212, полный ctor oracle и базовые RVP FX
проверены:269ticks/148particle/6entitydraws,15просмотренных кадров,3карты и
exactPE/Create1. Исправлена heap corruption Cora: weather helper выделял старые
1148/208 байтов; actual allocation instructions проверены до/после исправления.
Engine14af5e53…/67objects/11overlays,PE0165bf16…/entry151000/182-20-39TU/
0unresolved. Baseline033 сохранена;fullFX/audio/Tutorial/game/M9 OPEN.
[Доказательства](../research/client455-rvp-effects.md).

Дополнение07.11, rvp-actor080: установок нет. IDA f9d34033 сохранена и закрыта;
16 ranges совпадают между pins,1051 asm instructions получены полностью.
Сцена12actors/4models и отдельные позы общей модели прошли проверки:
9ticks/459parts,11просмотренных кадров,3camera regressions и exactPE/Create1.
PEa03ae596…/entry150DC0/182-20-38TU/0unresolved; движок079 не менялся.
MSBuild FileTracker и GPU InitR3Engine требуют запуска вне sandbox; два
первых GPU timeout не считаются успехом. FullFX/audio/Tutorial/M9 остаются OPEN.
[Доказательства](../research/client455-rvp-actor.md).

Дополнение07.11, rvp-runtime079: установокнет. IDA6a789f6fsavedclosed;20ranges
equalpins,full531+23+14+114asm. Engined85c8678…/67objects/9overlays +ownedfloat
cameraheader сохраняет033. OrdinaryRVP3maps/27events/82commands, intro26,
46viewedframes/Dmallocpassed. PE83c1793b…/entry150b20/182-20-36TU/0unresolved/
exactCreate1/freshcontracts. Fullactors/audio/Tutorial/M9OPEN;подписи078исправлены:
8D5510Render/8D8340Release. БольшиеunchangedGUI/kernel suites не повторялись.
[Доказательства](../research/client455-rvp-runtime.md).

Дополнение07.11, rvp078: установок нет. IDAa265e239savedclosed,15ranges equalpins,
полные1722+85asminstructions. Новая x86 source library/probe проверила44RVP
(615actor records/1569commands)+2fixtures/all12kinds/interpolation. Именованные
поля совпали с независимым Python. Exact-path resources:77refs/34missing;
это не подтверждённый blocker. OrdinaryPE/engine/Create evidence остаются077,
runtime player/Tutorial/M9 открыты. [Доказательства](../research/client455-rvp.md).

Дополнение 07.11, movie-state077: новых установок нет. 13 ranges/4 asm equalpins;
IDA70b16df7 закрыта, idb_list пуст. Engine67TU/9overlays/18086e42… сохраняет033.
Flags8/GPU6/intro3worlds26cameras/fullscreen18/40 просмотренных кадров прошли.
PEb377d2ac…/entry1508a0/182-20-34TU/0unresolved/exactCreate1, свежие startup contracts.
Подтверждено: RTMOVIE player отключён при компиляции, state/display API перенесены
вне featureguard. FullRVP/Tutorial/game и M9 открыты; wrapper500/480 и %fov
не исправлены. Большие неизменённые suites не повторялись.
[Доказательства](../research/client455-movie-state.md).

Дополнение07.11,fullscreen-effect076: установокнет.11ranges/default0.25 equalpins,
4fullasm;IDAf1ac7cc2savedclosed. Derivedengine67TU/7overlays/2df1e50e… сохраняет033.
RealFSE GPU18/lowVRAM512/failedBegin/target-depth-viewport-UIpassed;realintro3worlds
26cameras/Dmalloc/34viewedframesPASS. PE4553f401…/entry150860/182-20-34TU/
0unresolved/exactCreate1,freshstartupcontracts. Runtimechanged,075timestampreuse
неприменим;oldGUI/kernelhistorical. Fullpostprocess/stage/QBI/M9OPEN,40080201unknown.
[Доказательства](../research/client455-fullscreen-effect.md).

Дополнение07.11,tutorial-intro075: установокнет.15ranges/3tables equalpins,
4fullasm,IDAb92074d1savedclosed. Realcamera/fade/screen/mouse/world сAvatar
race/stage:26cameras/29viewedGPUframes/skip/reload/DmallocbalancePASS. Исправлен
ENGINE_DEFINITIONS только новойcamera TU для согласованногоengine state layout. PE51666436…
182/20/34TU/0unresolved/exactCreate1;runtime equal074 except2linktimestamps.
Fullstage/QBI/newengine controls/fourstage иM9 OPEN;40080201unknown.
[Доказательства](../research/client455-tutorial-intro.md).

Дополнение07.11,world074:установокнет.10ranges/vtableprefix48/6asm equalpins,
IDA60286d36savedclosed. RealCLand3maps/load/render/reload/release/collision,
6GPUframes иDmallocbalance passed. Engine67TU/6overlays c00d9d4d… сохраняетbase033.
PEfd8b038d…/entry150790/182-20-32TU/0unresolved/exactCreate1;freshstartupcontracts,
account/Avatar/MainApp/KoRuWindowpassed. FullILevel/INS/Tutorial/игра OPEN.
40080201unknown.[Доказательства](../research/client455-world.md).

Дополнение07.11,avatar-stage073: установокнет. ConfiguredIDAprobe внеsandbox
прошёл66tools/list10/decompile/close;внутри sandbox workerexit2. NativeMCP
работал,сессияb3b8653dsavedclosed.34ranges/2vtables/15fullasm equalpins.
ActualAvatar/MainApp/account routing,window/board иexactCreate1PASS;
22кадра равныreviewed072. FinalPE3d1f8c32…/entry150550,182/20/32TU,
0unresolved. FullTutorial/world/handlers/factory ещёOPEN;40080201unknown.
[Доказательства](../research/client455-avatar-stage.md).

Дополнение07.11,briefing-window072: установокнет.32ranges/vtable212 equalpins,
19listedfullasm+2captureasm;IDA18f99dcdsavedclosed. Sourcewindow/provider,
realScreen capture,actualboardrich/key иKo/Ru22GPUframes проверены. Fresh
gui-input/modal/minimap passed. PEbd50df91…/entry150350,182/20/31TU,
0unresolved/exactCreate1. Runtime changed,071timestamp-onlyreuse неприменим;
прочиеoldGUI отчёты оставленыhistorical. ActualTutorial/Avatar/world иполная
приёмкаещёOPEN.40080201unknown.
[Доказательства](../research/client455-briefing-window.md).

Дополнение07.11,briefing-controls071: установокнет.29ranges/3vtablesequalpins,
8fullasm,IDAs e0103d83/38abac4e savedclosed. Frame/key/animation иtyping basefill
Ko/Ru native/GPUpassed,20frames/12uniqueviews. Final PEfea692b9…/entry150290,
182/20/30TU,0unresolved/exactCreate1. Runtime bytes equal070 except2timestamps:
oldGUI evidence reused explicitly,не перезаписано какfresh. Newcontrols/window
instance ещёunused;currenttyping/controls gates PARTIAL. Exception40080201unknown.
[Доказательства](../research/client455-briefing-controls.md).

Дополнение07.11,text-typing070: установок нет.18ranges/1vtable equalpins,
8fullasm;IDA37b9a025 savedclosed. Typing source compiled normalfacade,исполнен
в full-object probe,ordinarybriefingещё OPEN. NativeKo/Ru/GPU traces passed,
14frames saved/8viewed,44existingGUIhashes equal069. Production8f009924…,
entry150290,182/20/29TU,0unresolved/existingCreate1;10gatesPARTIAL.
[Доказательства](../research/client455-text-typing.md). Exception40080201unknown.

Дополнение07.11,message-sizing069: установок нет.21ranges equalpins,15fullasm;
IDAb852f877 saved/closed. Productionc22502fa…/entry150290,182/20/28TU,
0unresolved/existingCreate1. Ko/Ru12групп real modal/GDI и10viewedGPUframes;
rich/extent production providers retained naturally. Все затронутые GUI passed,
9gatesPARTIAL. Empty fragment extent иglobalvirtualSetSize остаются OPEN.
Firstchance40080201 черезKernelBase повторяется;causeunknown,не полнаяfailures
приёмка. [Доказательства](../research/client455-message-sizing.md).

Дополнение07.11,gui-input068: установок нет.34ranges/1vtable prefix equalpins,
15completeasm,IDA6eadfaf3 savedclosed,idb_list0. Productionde76223c…/entry14F4A0,
182/20/28TU,0unresolved/existingCreate1. Ko/Ru realGUI input/focus/queue и
затронутые GUI probes прошли;40GPUreadback hashes совпали с предыдущими
просмотренными кадрами. Новый trace содержит firstchance40080201 через
KernelBase (причина не установлена),checkpointCreate1 пройден;это не приёмка
всех exception/failure domains. Старые крупные suites не повторялись.
[Доказательства](../research/client455-gui-input.md).

Дополнение06.11,minimap-opacity067: установок нет.17ranges/2vtable regions
совпали между pins,10complete asm;IDA7b53e450/b947042c closed/save,sessioncount0.
Main sprites:Ko fallbackCommon DXT1,Ru localizedARGB;frames5:0=400×18/5:32=400².
Common8style0=194×13/style1=192×15. Production0def3dce…/entry14EFF0,
182/20/27TU,0unresolved/existingCreate1. Ko/Ru real owner/queued mouse/GPU passed;
source EX and opacity facade retained in production. Полный мир/карта OPEN.
Удалён старый ignored client455_crt_multibyte.obj от эксперимента064:27CMake
facade sources/27актуальныхobjects;LIB/LIST и production map не содержат этого
адаптера. Найденные __acrt_multibyte symbols принадлежат обычному libucrt.
[Доказательства](../research/client455-minimap-opacity.md).

Дополнение06.11, scrollbar-variants066: установок нет.37function ranges и2vtable
regions совпали между pins,13complete asm. IDA68442489/ef4ffb43 closed/save.
Productionb24f1f09…/entry14E290,182/20/26TU,0unresolved/existingCreate1;
Ko/Ru EX/Var full-object/queue/GPU и затронутые GUI probes passed. Target
loader8CFB90 требует actions<16;изменять этот предел ради Var action15 нельзя.
Ранний invalid16action fixture завершился через Error;исправлен fixture15actions,
production guard сохранён. [Доказательства](../research/client455-scrollbar-variants.md).

Дополнение06.11, scrollbar065: установок нет.23ranges/2vtable prefixes/divisor
совпали между pins,15complete asm; IDAbfcf8ee1/9775776a closed/save. Новая PE
d38d74e0…/entry14E350,182/20/26TU,0unresolved/existingCreate1. Ko/Ru ordinary
scrollbar/queued input/GPU и затронутые GUI probes passed. Common action2
имеет44frames,defaults44–49 clamp to43;synthetic sprite только для теста.
[Доказательства](../research/client455-scrollbar.md).

Дополнение06.11, text-board064: установок нет.49 диапазонов и2vtable regions
совпали между pins,17полных asm. IDA958042ee/aabab7c3/06c03ace closed/save.
Полная PE3a209cdc…/entry14DD30,182/20/26TU,0unresolved/existingCreate1.
Korea/Russia TextBoard/GPU и затронутые GUI probes прошли. Исходники UCRT SDK
10.0.26100.0 доступны локально: getter0 допустим для SBCS ANSI1251, отдельный
startup adapter не нужен. [Доказательства](../research/client455-text-board.md).

Дополнение06.11, text-metrics063: установок нет.15 диапазонов и empty literal
совпали между pins,5полных asm; IDAe13a414e closed/save.182client/20kernel/
26facade,0unresolved; production71bc4b21…/entry14D7C0. Собственная GDI/CGUIText
проба Korea/Russia exit0, финальные кадры просмотрены. Ранний null-provider
сбой0.7 исправлен ожиданием реального шрифта. Font/modal/existingCreate1
регрессии прошли. [Доказательства](../research/client455-text-metrics.md).

Дополнение06.11, modal062: установок нет.43 диапазона/3vtable совпали между pins,
8полных asm; IDA124615b8/14980562 closed/save.182client/20kernel/24facade,
0unresolved, production PEa5b1da0b…/entry14D300. Modal Korea/Russia own native
exit0, кадры осмотрены; GDI regression passed. Точная PE прошла D3D/Character/
existingCreate=1, stop до игрового цикла. [Доказательства](../research/client455-modal.md).

Дополнение06.11, tutorial-board061: установок нет.32 диапазона и board vtable/
selection strings совпали между pins;9 полных asm. IDA774fd3f4 closed/save.
Собственная x86 PEed4fbf9d…/entryEBD30 завершилась exit0. Настоящие GUI-диалоги
отрисованы на D3D, viewport640×480 проверен отдельно от backbuffer640×500.
Визуально подтверждены старые назначения кнопочных спрайтов — это открытый gap.
Production PE056 не менялась. [Доказательства](../research/client455-tutorial-board.md).

Дополнение06.11,tutorial-actions060: установок нет.50ranges/equip16/virtual
bindings equalbothpins,11completeasm; IDA758bbebc closed/save. Own x86 lib
71c8d650.../PEac630491.../entry13F80 naturalexit0;recordinghost,не actual UI.
99programs/39864records prepare;spatial fixture regression exit0. Production
56905e68... unchanged. [Доказательства](../research/client455-tutorial-actions.md).

Дополнение06.11,tutorial-spatial059: установок нет.32function ranges/47category
bytes/counters/constants equalbothpins,7asm functions complete. IDAc60c1913/
5b89854f/7dedc5cb/cfea0c20 closed/save. Own x86 lib19d337cb.../PEdb7706b3.../entry9B30 exit0;
recording host, не world. Common-context regression058 passed. Production
PE56905e68... unchanged. [Доказательства](../research/client455-tutorial-spatial.md).

Дополнение06.11,tutorial-runtime058: установок нет.42function ranges/10vtables
совпали в pins,7полных asm функций проверены. IDAf84ad03d closed/save.
Own x86 library/native9618bd36.../entry8100, naturalexit0. Recording host,
не actual UI/Avatar. New reports совместимы с discovery20kernels; production
PE56905e68... не менялась. [Доказательства](../research/client455-tutorial-runtime.md).

Дополнение06.11,tutorial-scripts057: новых установок нет.19диапазонов функций,
CQBI RTTI и selector strings совпали между pins. Own x86 SCP library собрана,
99realfiles/47synthetic selectors/semantic fields/bounds проверены, naturalexit0.
IDA c257ee18/b0309dad закрыты/save. Production PE не менялась; Tutorial runtime
не принят. [Доказательства](../research/client455-tutorial-scripts.md).

Дополнение06.11,camera056: установок нет.12ranges equalbothpins;IDAc449e061
closed/save. Derivedengine67units/5overlays91bdf0c7...;033unchanged. FullownPE
56905e68.../entry14ACA0,182client/20kernel/23facade,0unresolved. RealCAM1.2/
synthetic1.3/play/GPUprojection/release nativeexit0;existingCreate=1. Full
Tutorial/fourstage/M9 open. [Доказательства](../research/client455-camera.md).

Дополнение06.11,progress-base055: установок нет.18function ranges equalbothpins,
IDA3bc31778 closed/save=true. Actual CGameProgress/Title/particlecount probe
naturalexit0. Fullx86PE5302f71a.../entry14A750,182client/20kernel/22facade,
0unresolved;existingCreate=1. Fullfourstage/Tutorial/M6F/M9 открыты.
[Доказательства](../research/client455-progress-base.md).

Дополнение06.11,progress054: установок/пересборки нет.28function ranges,
RTTI/vtables четырёх stage classes совпали в455pins; IDA3915694c closed/save.
Mode2=Tutorial подтверждён через Avatar setter/фабрику/RTTI. Raw static scan
не нашёл callers старого INI reader; computed calls остаются неизвестными.
Runtime/source сборки053 не изменены. [Доказательства](../research/client455-progress.md).

Дополнение06.11,account053: новых установок нет.26функций/11country selectors
совпали между455pins; IDAf2469475 closed/save=true. Собственная x86PEa12b10f7...,
entry14A980,182client/20kernel/22facade,0unresolved. Пакеты account/gateseed,
bounded dispatcher и pending dialog проверены реальными методами на owned
in-memory fixture; естественный exit0. Точная PE сохранила existingCreate=1.
Настоящий вход и full455 ещё открыты. [Доказательства](../research/client455-account.md).

Дополнение06.11,connection052: установок нет.15функций/11vtables совпали между
455pins; IDAbed1c136 closed/save=true. Полная собственная x86PE0733cce1...,
entry14a3f0:182client/20kernel/21facade,0unresolved. Настоящие Connect/events/
wait идут до engine; собственная CCR-проба подтверждает TCP-peer и existing
Create=1. Локальная тестовая TCP-точка не отправляет RFпакеты и закрывается
после каждой пробы. Три native режима естественно exit0, включая реальные
диалоги ошибок; hook установлен только на поток собственной проверки.
Russian WinMain trace теперь честно останавливается перед Connect: текущий
argv endpoint1 не заполнен; полный профиль455 ещё не доказан. M6/M9 открыты.
[Доказательства](../research/client455-connection.md).

Дополнение06.11,network-codec051: установок нет.33функции/7диапазонов данных
совпали между455pins; AES192 schedules обоих направлений проверены полностью.
IDA4c89c7ab closed/save=true. Собственная библиотека реализует AES; Windows CNG
использован только в проверочной программе. Буферы/формат пакетов подключены
к normal CNetProcess; два процесса, вместимость6. Full PE71e644eb.../entry149ef0,
182client/20kernel/20facade,0unresolved; зависимости движка сохранены. Own
native codec/ring tests naturalexit0; существующий Create вернул1. Full455
transport/handlers/auth/UI/M9 ещё открыты.
[Доказательства](../research/client455-network-codec.md).

Дополнение06.11,bootstrap050: новых установок нет.28диапазонов функций и11
country vtables совпали между455pins; IDA d716d7fa/8102ad50 closed/save=true.
MSVC x86 собрал182client/20kernel/19facade; ownPE3b93b0eb.../entry149010,
0unresolved. ActualNetworkCreate теперь передengine ивыполняетсяодинраз.
Ownnative FG/name/process/mutex/state probes естественно exit0, включая вторую
собственную RF_Online.bin. Реальный закрытый TCPпорт:10061 доclosesocket,
0после — совпадаетсAPIпорядком455;connectedfalse,аутентификации нет. Exactown
Korea/Russia bootstrap/D3D/existingCreate прошли;отладчик остановилдоцикла.
17scoped gates PASS/PARTIAL. Полный455transport/framing/crypto/UI/M9 открыт.
[Доказательства](../research/client455-bootstrap.md).

Дополнение06.11,launcher049: установок нет.19функций и11country vtables
совпали в обоих pinned455PE;IDAf2fdf71d closed/save=true. Modern MSVC x86
собрал182client/20kernel/17facade;full PE a64601c8.../entry148860,0unresolved.
Три own offline launcher-пробы естественно exit0,сеть не создавали. Exact
WinMain Korean/Russian прошёл nation→launcher→language→engine/Miles;обычный
Create вернул1. Остановка на ownRVA B3DB4 до фильтров/игрового цикла. Debugger
передаёт аргументы только из labfixture,не читает реальные account-файлы.
Полный455bootstrap/connect/auth/gameplay ещё открыт.
[Доказательства](../research/client455-launcher.md);M6/M9 открыты.

Дополнение 06.11, sprites048: установок нет. Сессия IDA64d5aa70 работала с
копией эталона, закрыта/save=true.14диапазонов sprite/texture/manager и55имён
совпали в обоих pinnedPE. Производный движок сохраняет033;67units/4CPP overlays,
новый source texture uploader поддерживает реальный DXT5. Две own GUI пробы
с normal CMainApp.LoadData/CGUIMouse естественно exit0,COMrefs сохранены.
Точная ownPE d431094d.../x86/entry148390 дошла до новой проверенной границы
RVA B354A перед CreateFileA(DefaultSet.tmp);остановлена собственным debugger,
launcher-данные не читались. Полный455bootstrap/вход ещё открыты.
[Доказательства](../research/client455-sprites.md);M6/M9 открыты.

Дополнение 06.11, lifecycle047: установок нет. IDA session dae004fd открыла
копию эталона, закрыта с save=true. Девять диапазонов Land/ILevel совпали
в обоих закреплённых PE; null-level branch RVA3C8F3F подтверждён инструкциями.
Новая собственная x86 PE SHA11833d1e... / entry1485A0: 182 объекта клиента,
20 kernel, линковка без unresolved. Три отдельных процесса с реальным
глобальным CMainApp и две GUI-пробы без Land завершились с exit0 без отладчика
и TerminateProcess. Обычные startup/device/Create checkpoints также сохранены,
но эти отдельные запуски остановлены отладчиком. Полный WinMain/shutdown не
принят. [Подробности](../research/client455-lifecycle.md); M6/M9 открыты.

Дополнение06.11,font046: установок нет. Настоящие CreateFontA/ExtTextOutW/
GDI metrics/D3DX36 atlas работают сcountry params;Hangul/кириллица просмотрены
вкадрахреальногоCGUIText. Собственный font probe создаёт Land передвыходом и
завершаетсяexit0;старый early-abort nullLand gap зафиксирован отдельно.
OwnPE88942d08.../x86/entry1485A0 прошла GDI/D3D/Character;lab fontregistration
очищена. Derivedengine67units,033сохранён. IDAa9adfb47 closed/save=true.
Полные FT/text/UI/IME/window sizing/early-abort/shutdown ещё открыты.
research/client455-font.md; M6/M9 открыты.

Дополнение 06.11, language045: новых установок нет. Actual MSVC CRT LC_COLLATE
для11country names дал ожидаемые codepages.9realNDLanguage EDF/bytes/index/DBCS
проверены;en-us/th-th пакеты здесь отсутствуют,не заменять другими. New own PE
SHA1fc267d5.../x86/entry14A920 прошла Korean+Russian language init/Miles и
Korean D3D/Character startup. Debugger повторно использован по SHA. Lab
work/m9/1fc267d5;IDA34ab1c2b closed/save=true;short regressions/кадры прошли.
Полные font/text/UI/Create/launcher/network/shutdown ещё открыты.
research/client455-language.md; M6/M9 открыты.

Дополнение 06.11, nationpaths044: новых установок нет. Полная собственная PE
SHAcb64af10.../x86/entry1496C0 собирается без unresolved. Выбор страны/корня
данных проверен по обоим455PE; штатный Create дошёл до Character и менеджеров
на реальном D3D9. Точный stop до _CreateCharDataMgr, exit наблюдён. Breakpoint
адреса теперь определяются dumpbin по инструкциям текущего PE/MAP; fixed offsets
удалены. Свой debugger/CPU layout обновлены, short regressions/кадры прошли.
IDA5f01f0d1 закрыта/save=true; lab work/m9/cb64af10/create-startup001.
Полные locale/NDLanguage/launcher/UI/network/shutdown впереди.
research/client455-nation-paths.md; M6/M9 открыты.

Дополнение 06.11, devicestartup043: установок нет. Отдельно собрана библиотека
R3Engine455Startup из67units с двумя подтверждёнными правками;033source/lib
сохранены. Full normal PE линкуется, новый SHA51fd3f49..., entry149510.
Реальный WinMain дошёл до window/D3D/device ready1 в оконном режиме32бит;
свой debugger с SW_HIDE запросом остановил процесс до CMainApp::Create,
exit наблюдён. Source snapshots CPU и exactPE traces под work/, короткие
Character/renderer regressions прошли, прежние кадры сохранены. Reference
IDA1c8c37b3 closed/saved=true. Locale/launcher/network/bootstrap order455
ещё не восстановлены. research/client455-device-startup.md; M6/M9 открыты.

Дополнение 06.11, startup042: установок не требовалось. Собственный Win32
debugger собран VS2026 и запускает только точную staged own RF_Online.bin.
Все15 regular/delayed import descriptors имеют x86 providers/нужные exports;
фактически загруженные eager DLLs и Miles совпали по SHA. CRT/WinMain/engine/
Miles startup прошли, sound return1. Отладчик остановил процесс до D3D/window;
exit наблюдён. Три first-chance события обработаны runtime, second-chance нет.
Lab inputs: копии DLL/WaveList и собственный ini, оригиналы не менялись.
CDB не устанавливался; raw trace под work/m9/39062b2c/startup002. Own IDA
2714f558 closed/saved=true. Нормальная graphics/Create/launcher приёмка впереди.
research/client455-startup.md; checkpoint PARTIAL; M6/M9 открыты.

Дополнение 06.11, accounting041: без новых установок. 182 client / 11 facade /
20 canonical kernel CPP x86/MT собираются; новый полный normal RF_Online.bin
успешно линкуется с 0 unresolved и без принудительного разрешения. PE32 x86,
1 966 080 байт, entry RVA149500, SHA/response/MAP — normal-link.json.
Общие counters и actual ANI/multiple owners/mesh lifetime/GPU descriptors
проверены; release/новый renderer не обнуляют cumulative значения. Старые
цветные/effect/shadow кадры сохранились, COM/Dmalloc0. Входные EXE и normal
WinMain не исполнялись; runtime DLLs/обычная инициализация ещё не приняты.
IDA6b33fc0a closed/saved=true. research/client455-normal-accounting.md;
checkpoint PARTIAL; M6/M6F/M7/M9 открыты.

Дополнение 06.11, characterclock040: без новых установок. Отдельный таймер
Character 91EA80 и _R3CalculateTime подключены к современному x86/MT facade.
168 численных случаев/12 режимов FPU, QPC/fallback и независимость engine clock
прошли. 182 client / 10 facade / 20 kernel CPP собираются; полный линк теперь
только g_ChMemoryInfo. Короткие ANI/BBX/model/effect/shadow сценарии прошли,
прежние кадры сохранились, COM/Dmalloc 0. IDA a91e5275 closed/saved=true.
research/client455-character-clock.md; checkpoint PARTIAL; M9 открыт.

Дополнение 06.11, effects039: новых установок нет. 182 клиентских, 8 facade и
20 canonical kernel CPP собираются x86/MT. Загрузка и применение EFF работают
с прежним source TextureManager на D3D9 HAL. Эффект с реальной DDS изменил кадр
модели; прежние цветные кадры и теневой проход сохранились, COM/Dmalloc 0.
Полный линк: только g_ChMemoryInfo и _R3CalculateTime, других ошибок нет.
IDA 4a2e7cac закрыта с запросом save; returned saved=null. Оригинальные EXE
не исполнялись, серверы не менялись. research/client455-effects.md;
inventory/client455-effects-checkpoint.json: PARTIAL, M9 открыт.

Дополнение06.11 effecttables038: без новых установок. Два reader иquery работают
вnormalfacade с source owners. Проверены реальные2246patterns/4600items,
неизвестные stacktail grades9..35 явно выявлены.182client/6facade/20kernelCPP
собираются, полный линк15символов. Короткая renderer/ANI/BBX/shadow регрессия
прошла; больших неизменённых suites нет. IDA3ce41498closed/saved=true.
research/client455-effect-tables.md; checkpoint PARTIAL/M9OPEN.

Дополнение06.11, normalshadow037: новых установок нет. BeginShadow/EndShadow
и512x512targets на прежнем D3D9HAL/pinnedD3DX9_36 работают в собственном проходе.
Реальная модель дала силуэт;3прохода/reuse/COM0/прежние цветные кадры проверены.
Begin возвращает0 на успехе, а настоящие455callers используют BOOLпроверку;
normal shadow lifecycle ещё не принят. Полный линк20символов. IDA63e04581
closed/saved=true. research/client455-normal-shadow.md; checkpoint PARTIAL/M9OPEN.

Дополнение06.11, normalcontracts036: новых установок нет. Пять методов модели
и сброса анимации455 подключены к обычному x86/MT facade. Реальные BBX и модель
после reset/reattach/rematch прошли, прежние два GPUкадра совпали. Сборка182client/
3facade/20kernelCPP успешна; полный линк22метода/данных, M9OPEN. Большие
неизменённые suites не повторялись. IDAb8160cd3closed/saved=true.
research/client455-normal-contracts.md; inventory/client455-normal-contracts-checkpoint.json.

Дополнение 05.11, normal renderer035: новые установки не требовались. Обычные
CUnity/модель/поза/CRender рисуют два кадра на D3D9; координатная и матричная
обёртки дали одинаковые кадры, COM/Dmalloc после явного завершения 0. Макросы
GPU-теста согласованы с engine/client, включая RF_CLIENT_455_WEATHER.
Полный линк пока 27 методов/данных, M9 открыт. IDA1bcd6f24 закрыта, save запрошен,
saved=null. research/client455-normal-renderer.md и соответствующий checkpoint.

Дополнение 05.11, normal port034: без новых установок компилируются 180 исходных
клиентских единиц на D3D9/типах455; после выделения CUnity/CAnimation — 182 объекта
x86/MT. Реальные потребители загружают ANI. Полный линк пока LNK1120:39 символов
методов/данных, CharacterMR не подключён. База/engine033 сохранены, игровые DLL
в тесте не загружались. inventory/client455-normal-checkpoint.json (PARTIAL);
research/client455-normal-port.md. Сессий IDA не открывали.

Дополнение05.11 engine9port033: local Microsoft.DXSDK.D3DX9.29.952.8 headers,
Author/Repository подписи проверены. PackageSHA/files inventory/d3dx9-headers.json.
Никакие_43runtimeDLLs неустановлены; x86importarchive retargeted36 иactualimports
проверены поpinnedDLLexports. НастоящийD3D9R3Engine67units x86/MT,device/Platform01
иsource Characterowner наодномdevice прошли. Originalnormalсборка не менялась.
Gate inventory/client455-engine9-checkpoint.json. CDBexe отсутствует,ошибкаownrun
разобрана через собственныйSEHreport/MAP. Full180client migration ещёоткрыта.

Дополнение05.11: source renderer owner032 использует прежние MSVCx86/MT,
pinnedD3DX9_36 иD3D9HAL. Constructor/caps/destructor иreal model→pose→draw путь
прошли component/fullclient,ownheap/COM/Dmalloc0;новых установок нет.
Lab197TUs,normal293MTobjects/runtime прежний кромеtimestamps. IDA8ad1c657closed/save.
inventory/client455-renderer-owner-checkpoint.json;research/client455-renderer-owner.md.

Дополнение05.11: source scene-frustum использует прежнюю pinned x86 D3DX9_36,
устанавливать ничего не требовалось. Нормальные SetCharacterClipping/CResObject
подключены к source math;72matrix/204AABB/9actor scenarios икороткая Platform01
регрессия прошли. Normal293MTobjects,lab196clientTUs. Named Character API audit
247objects завершён;39oldSDKfunctions ещё вызываются. Native IDA session закрыта/save.
inventory/client455-frustum-checkpoint.json;research/client455-normal-character-interface.md.

Последнее дополнение: основной Character draw/эффекты/deferred paths source
проверены на том же D3D9HAL/pinnedD3DX9_36 отдельно и в полном client lab:
16targeted scenarios/185assertions,2realmodel frames,COM/heap/Dmalloc0. Lab195TUs,
normal291MTobjects/тот же engine archive/runtime прежний кромеtimestamps.
Новых SDK/установок нет. Старый staticCRT sin/cos ещё не сертифицирован.
inventory/client455-character-draw-checkpoint.json;research/client455-character-draw.md.

Предыдущее дополнение: source Character draw primitives проверены на настоящей
анимированной модели с3textures/D3D9HAL/pinnedD3DX9_36. Два кадра совпали отдельно
и внутри client lab; heap/COM/Dmalloc0. Новых установок нет. Lab194clientTUs,
normal291modernCOFF/MT, прежний engine archive; normal renderer ещё D3D8.
inventory/client455-draw-checkpoint.json;research/client455-draw.md.

Предыдущее дополнение: source Character shader bootstrap работает на настоящем
D3D9 HAL и pinnedD3DX9_36:12SHO/12VS+3PS/2declarations,119checks standalone и в
полном client lab. COM counts0, gameDLLs не загружены; normal renderer ещё D3D8.
Новых SDK/установок нет. Lab193clientTUs,normal291MTobjects/runtime прежний.
inventory/client455-shaders-checkpoint.json;research/client455-shaders.md.

Последнее дополнение: source AnimationManager4554028/11APIs проверен standalone
и full-client lab на коллекции/кэше/владении/одном real ANI. Новых установок нет.
Normal291MTobjects/прежний engine archive, lab192clientTUs. Normal runtime равен
предыдущему после исключения timestamps: старые consumers ещё не переключены.
inventory/client455-animation-manager-checkpoint.json;
research/client455-animation-manager.md. Несвязанные большие тесты не повторялись.

Дополнение после timing: source elapsed clock подключён в normal R3EngineMT.
144 состояния/3 provider сценария прошли; actual R3CalculateTime→CResObject
проверен в полном client lab. Platform01/device прошёл, прежние frame SHA.
Normal291modernCOFF x86/MT, lab191clientTUs; новые установки не требовались.
Текущий gate inventory/client455-loop-clock-checkpoint.json;
research/client455-loop-clock.md. Исторические snapshots ниже не обновлялись.

Актуальное дополнение 05.11: восстановленный расчёт кадра и CAnimation ctor
подключены к обычному клиенту через R3EngineMT. Проверены 612 численных случаев,
16 actual CResObject сценариев и короткая Platform01/device регрессия (2 случая).
Normal290modernCOFF x86/MT, lab190clientTUs; установки не менялись. Runtime обычной
сборки намеренно изменён выбранными вызовами, полный Character455/draw ещё открыт.
Gate inventory/client455-animation-timing-checkpoint.json;
research/client455-animation-timing.md. Старые большие runtime suites не повторялись.

05.11 modelpipeline source:connectedMESH08route/lifetime10021HALchecks вcomponent
иполномclientlab,393parts/276realuploads/59texturebindings,ownheap/COM/Dmalloc0.
ТотжеpinnedD3DX9_36/HAL,no new installs;normalgame manager/renderer integration
ещё открыта. research/client455-model-pipeline.md.

Следующее дополнение05.11:source sharedVB36/VB64/INDEX16 работает втомжеHALD3D9;
159173nativechecks standalone/fullclient,12files/393parts/276real uploads,
4syntheticindexed draws,COM/Dmalloc0. Зависимости/установки не менялись.
Full Character shaders/normal loader ещё открыты. research/client455-shared-buffers.md.

Дополнение05.11: physical Character texture source работает с pinned x86
D3DX9_36 иHALD3D9 через отдельную TU внутри полного client lab.8440checks,
68texture pairs/137renders/97material parts,COM/Dmalloc0;новый SDK неустанавливался,
d3d9.h из WindowsSDK10.0.26100.0/shared. Полный client/Character GPU ещё открыт.
research/client455-character-textures.md;inventory/client455-texture*.json.
IDA configured stdio повторно проверен в user context:66tools,страница10client
functions,декомпиляция/close-save. Probe теперь client-only IDB,без server smoke.
Native MCP также работает. Restricted workercode2 исчезает при привычной
escalation;переустановка не нужна. docs/ida-mcp.md.

Дата по Asia/Yakutsk. Машинные отчёты используют UTC. Это снимок состояния,
а не непрерывный мониторинг. Работы выполнены в `E:\RFOnlineTrash\Source\WorkFlow`.

## Итог

Работа исключительно над клиентом и его зависимостями. Серверные сведения ниже —
история проверки инструментов/инвентаризации, не задачи и не блокеры клиента.
Серверные исходники разрешены для чтения как справочник, без изменений и сборки.
Целевой результат — исходники RF_Online.bin с полным функционалом и поведением
закреплённого клиента 455; степень соответствия пока не установлена.

Рабочая область и локальный Git подготовлены. GoMMO MCP работает через stdio.
IDAPython восстановлен на Python 3.11.16; IDA MCP установлен, зарегистрирован в Codex
и проверен через stdio и нативные инструменты чата после перезапуска: 669 функций
и декомпиляция получены на рабочей копии PE x86. Установлен universal-modder:
13 навыков с валидными метаданными и работающий CLI um 0.2.0.
Установлена и проверена Visual Studio Professional 2026 18.11.3: MSVC x86,
Windows SDK и CMake. Основной путь — перенос клиента под современный MSVC;
VC6 остаётся резервным инструментом. DirectX 8.1b SDK проверен и подключён локально;
R3Engine собран под VS 2026 x86 с двумя успешными чистыми пересборками.

Статический аудит сборки завершён: 14 DSP / 14 DSW, 41 конфигурация, 832 SOURCE,
6 отсутствующих записей в CameraExporter/R3MapExp. Все 180 C++ клиента уже компилируются
с диагностическим восстановленным Character.h. JPEG 6b/Miles подключены.
Получена полная diagnostic RF_Online.bin и успешная чистая пересборка, unresolved нет.
Выбранные 455 ветки имеют отдельные flags/ledger, исходные legacy branches сохранены.
Это не проверка запуска/полного поведения 455. Подробности research/client-first-build.md.
Последующее M5: helper loader455 найден, три отличия перенесены отдельным flag.
Обычная ревизия собрана, отдельный own lab entry полного проекта выполнил загрузку
140 реальных файлов/97 543 записей и CPU transforms/bbox;12 fixtures,2 546 779 checks,
4 import-parser tests. В lab игровые DLL отложены и не загружались. Обычный игровой
запуск/LoadLevel не проверены. Последующее: две x87 math функции восстановлены
с совпадением всех инструкций455, проверены в обоих linked clients и338 native
checks/12FP modes. Повтор140files после выравнивания Release options успешен,
2 546 931checks, FP control0x027F. Weather source перенесён:2слоя,R3X/text config,
load/release/update/draw split,interior/night.65real R3X +4fixtures/703checks,
37actual CPU lifecycle checks,285modern objects /MT. GPU/normal map/clock integration
остаются открыты. research/client455-weather-source.md.
Последующий resource audit:78RPK/3775files,70BSP+93EBP,20weather assets закреплены
с SHA.8parser tests прошли. Выявлены1067неверных size fields RPK и stale offsets
Dungeon00;455 использует offset-only fopen и sequential BSP reads соответственно.
На этом статическом этапе Source VFS/end ещё отсутствовал. Один weather path missing для
трёхTower R3X, directory component не найден во всех162RPK indexes. Игровые EXE/DLL
не запускались; сборки не менялись. research/client455-map-resources.md.
Следующий цикл восстановил RPK source/group/fopen/exists и particle end:18 907native
module checks на3775members/78RPK и30actual full-project archive/SPT/R3X checks.
Обе сборки успешны,286modern x86 /MT objects; selected compiled branches и DDS mask
проверены.703weather checks прошли на новой lab revision. Normal LoadLevel/GPU не
выполнены. MSBuild FileTracker sandbox E_ACCESSDENIED устранён escalation того же
build command. research/client455-resource-io-source.md.
Область работы уточнена: исключительно клиент. Выбор LoginServer отозван;
первая цель клиентской зависимости — R3Engine RTMovie Release, затем RF_Online. Детали: [build-audit.md](build-audit.md),
этапы: [roadmap.md](roadmap.md), актуальная память: [project-memory.md](project-memory.md).

## Инструменты

| Компонент | Проверка | Результат |
|---|---|---|
| ОС | Environment.OSVersion | Windows NT 10.0.19045; редакция не определялась |
| Git | git --version | 2.53.0.windows.3; работает |
| GitHub Desktop | процесс и путь | запущен, каталог app-3.6.10 |
| IDA Pro | реестр и FileVersion | 9.2; файл 9.2.25.0908 |
| Hex-Rays | IDAPython и реальный MCP-вызов | плагин 9.2.0.250908 работает; декомпиляция функции PE x86 подтверждена |
| IDAPython | реальный запуск скрипта | Python 3.11.16; 669 функций, декомпиляция успешна |
| IDA MCP | initialize, tools/list, idb_open, list_funcs, decompile | установлен ida-pro-mcp 2.0.0, 66 инструментов; основные вызовы прошли |
| GoMMO Studio | initialize и studio_status | 2.0.1, несмотря на папку/README 1.3.0 |
| Python для аудита | прямой запуск | 3.12.14 из комплектного runtime Codex |
| Python для IDA | idapyswitch и запуск внутри IDA | 3.11.16, постоянная установка uv в AppData/Roaming/uv/python |
| Системный Python 3.10 | реестр и проверка файла | запись есть, C:\Program Files\Python310\python.exe отсутствует |
| Python 3.14 | цель launcher и проверка файла | launcher ссылается на отсутствующий pythoncore-3.14-64/python.exe |
| Visual Studio | vswhere и реальная сборка | Professional 2026 18.11.3, установка завершена, перезагрузка не требуется |
| MSVC | VsDevCmd x86 и компиляция | toolset 14.51.36231, compiler 19.51.36260.0; x86 проверен |
| MSBuild / CMake | реальная конфигурация/сборка | 18.11.1.51303 / 4.3.1-msvc1, генератор Visual Studio 18 2026, Win32 |
| Windows SDK | VsDevCmd и Win32 smoke | 10.0.26100.0, заголовки и линковка проверены |
| VC6 / DX8.1 SDK | стандартные каталоги и установленные программы | не обнаружены; переносные установки на других дисках не исключены |

Наличие Visual C++ Redistributable и Visual Studio Installer не означает наличие
компилятора. PATH не менялся. IDAPython явно привязан к найденной установке 3.11.16;
остальные Python-установки не заменялись. MCP изолирован в local/ida-mcp-venv.

## GoMMO MCP: подтверждено

- У запущенного приложения найден локальный instance descriptor.
- В момент проверки адрес: `http://127.0.0.1:64359/mcp`, версия 2.0.1.
- Порт динамический. Токен из descriptor не копировался в рабочую область.
- Использован официальный stdio bridge: `gommostudio.exe -mcp`.
- Успешны `initialize`, `notifications/initialized`, `tools/list`, `studio_status`.
- Сервер объявил 663 инструмента. Это проверка обнаружения, а не испытание каждого.
- `studio_status` показал пустой список документов; клиент и проект не открывались.
- Изменения ассетов, Install, запуск сервера и публикация не выполнялись.
- Схемы и результат: `inventory/gommo-mcp.json`.

В нативном наборе инструментов текущего чата GoMMO не зарегистрирован.
Доступ через наш stdio-клиент уже подтверждён. Пример для последующего подключения
Codex сохранён в `config/codex-mcp.example.toml`; глобальная регистрация GoMMO не добавлялась.

## IDA и MCP: восстановлено после первоначального аудита

На момент начала аудита процесса IDA и слушающего MCP-сервера IDA не было.
До восстановления в пользовательском config.toml Codex не было регистрации
IDA/GoMMO; mcp.json LM Studio не содержал настроенных серверов.

Проверены:

- `C:\Program Files\IDA Professional 9.2\plugins`;
- `C:\Users\Admin\AppData\Roaming\Hex-Rays\IDA Pro`;
- `C:\Users\Admin\AppData\Roaming\Hex-Rays\IDA Pro\mcp\instances` — пусто;
- стандартные `.idapro` и `AppData\Roaming\IDA Pro` — отсутствуют;
- несколько обычных мест расположения `ida-pro-mcp` — не найдены.

Повторный поиск также охватил Downloads, Documents, uv/tools и RFOnlineTrash.
Рабочая старая установка IDA MCP не обнаружена; в найденном Python пакет
ida-pro-mcp отсутствовал. Поэтому выполнена новая установка совместимой реализации.

Скрипт `scripts/probe_ida.py` копирует старый `LoginServerSR.exe` в `work/ida-smoke/`
и запускает только статический анализ через idat.exe. Сам серверный EXE не запускается.
В песочнице IDA завершилась с кодом 2 без диагностического лога. Повтор вне песочницы
завершился с кодом 1 и дал диагностический лог:

```text
failed to load Python runtime: skipping IDAPython plugin
Hex-Rays Decompiler plugin has been loaded (v9.2.0.250908)
.../scripts/ida_smoke.py: unknown file extension
```

Это исторический результат первого аудита. При восстановлении idapyswitch обнаружил
рабочую установку `C:\Users\Admin\AppData\Roaming\uv\python\cpython-3.11.16-windows-x86_64-none`.
После явной привязки к её python311.dll скрипт IDAPython завершился с кодом 0,
получил 669 функций и выполнил декомпиляцию. Переустановка Python не понадобилась.

Установлены:

- ida-pro-mcp 2.0.0, commit `c133c3853faa111a9b00ee615c013b720d0c4acd`;
- зависимости idapro 0.0.12 и tomli-w 1.2.0 в `local/ida-mcp-venv`;
- GUI-плагин в `%APPDATA%\Hex-Rays\IDA Pro\plugins`;
- stdio supervisor в секции `[mcp_servers.ida_mcp]` пользовательского Codex config.

Последняя проверка использовала команду непосредственно из зарегистрированного
Codex config. Успешны initialize, tools/list (66 инструментов), idb_open,
server_health, list_funcs (все 669 функций), decompile и idb_close с сохранением базы.
Пример: `sub_401E60`, VA `0x401E60`, RVA `0x1E60`, image base `0x400000`.
SHA-256 входа: `9874cbada393244db1d02c1549eb02434f6d376e7cea33fc97e8424bfb1cc7a2`.
Пакет сообщает версию 2.0.0, MCP serverInfo — 1.0.0; обе версии зафиксированы.

Отчёты: `inventory/ida-runtime.json`, `inventory/ida-mcp-tools.json`,
`inventory/ida-mcp-verification.json`. `pip check` не выявил конфликтов зависимостей.
Команда `codex mcp list --json` подтверждает `ida_mcp: enabled=true`.
Рабочая база: `work/ida-mcp-smoke/LoginServerSR.exe.i64`.
Запуск проверял статический анализ; серверный EXE не исполнялся.

После перезапуска Codex появились 66 нативных инструментов IDA. Через них проверены
idb_open, server_health, list_funcs (669 функций), decompile (полный код sub_401E60)
и idb_close. Состояние ok, auto_analysis_ready=true, hexrays_ready=true.
Сессия закрыта без сохранения изменений. Доказательства:
`inventory/ida-native-verification.json`. Подробности: `docs/ida-mcp.md`.
GoMMO по-прежнему доступен через stdio-проверку, его глобальная регистрация не менялась.

## Universal Modder: установлен и проверен

Источник: https://github.com/rehan-remade/universal-modder,
commit `9811709d950979f1b5012dddf10b7ec122d7e95e`.
Все 13 навыков установлены skill-installer в `C:\Users\Admin\.codex\skills`.
CLI um 0.2.0 установлен через uv tool install --editable из закреплённой локальной
копии в local/universal-modder-install, вместе с локальной базой знаний.

Все навыки прошли quick_validate.py. Единственная адаптация: `<game>` заменён на
`this game` в description навыка game-recon, поскольку валидатор Codex не принимает
угловые скобки. Тело навыка не изменено; остальные файлы совпадают с источником.

Проверены um --version, --help, поиск базы знаний и um scan RFOnline --json:
проиндексировано 30 311 файлов. Сканер сообщил unknown native engine и признаки
nProtect GameGuard. R3Engine по имени не распознан; RF_Online.bin не перечислен
среди исследованных EXE. ASI loader — эвристика, а не доказательство мод-загрузчика.
Поиск RF Online выдаёт в том числе нерелевантные материалы о Red Faction.

Игра не запускалась, клиент не менялся. Генерация через fal/Sprixen/Voidless,
3D-рендер, управление игрой и видео не проверялись; ffmpeg и Blender в текущем PATH
не обнаружены. Внешние MCP и API-ключи не подключались. Это установка навыков и CLI,
а не полного плагина с fal MCP. Навыки доступны для выбора со следующего сообщения.

См. `docs/universal-modder.md` и `inventory/universal-modder-installation.json`.

## Материалы RF Online

| Каталог | Файлов | Байт | Что зафиксировано |
|---|---:|---:|---|
| Старые исходники | 962 | 17 763 094 | SHA-256 каждого файла |
| Клиент RFOnline | 30 554 | 11 401 335 169 | сводка дерева и хеши выбранных бинарников |
| rf455-v0.4.0 | 216 | 1 129 623 002 | сводка дерева и хеши выбранных бинарников |

В старом комплекте: 329 cpp, 463 h, 14 dsp, 14 dsw. Найденные проекты включают
движок, клиент, служебные серверы и утилиты; полнота игрового ZoneServer не установлена.
Версия «0.7 / 2004» пока является описанием пользователя, а не результатом атрибуции.

`RF_Online.bin` и его backup — PE x86. `gameserver.exe` из пакета 455 — PE x64.

- Текущий клиент: `b1b5febf0d0394712e2322350e19dafe60742e8642697b93cfb89135bac1fd8b`.
- Backup: `46528aac20499e3b3928d58658d7e0cefe26feba7cd193796d5cfbf7a2bbc558`.
- Backup совпадает с SHA-256 клиента, указанным в README серверного пакета.
- Происхождение различий текущего клиента и backup ещё не установлено.

Манифесты: `inventory/legacy-files.json`, `inventory/reference-binaries.json`,
`inventory/roots.json`. Полный хеш-манифест 11.4 GB ресурсов и резервное копирование
всех игровых данных в этот этап не входили. Базы, конфиги с паролями и игровые
ресурсы не добавлялись в Git.

## Границы проверки

Полная сборка клиента, восстановление протокола,
распаковка клиента и изменение игровых файлов не выполнялись. Статический аудит
входов/зависимостей всех проектов выполнен; пригодность SDK/ABI и фактическая
линковка ещё не подтверждены. Восстановлены
IDAPython и MCP; реальная проверка выполнялась на старом LoginServerSR.exe.
Полный анализ клиента 455 через IDA пока не выполнялся.
Свободно на E: около 1776 GiB на момент проверки.

## Дополнение: аудит собираемости 2026-11-04

- inventory/build-audit.json содержит конфигурации, SOURCE, include-кандидатов,
  библиотеки, RC-ресурсы, SHA-256 проектов/.lib и сравнение серверных деревьев.
- 12 проектов имеют все перечисленные SOURCE; все DSW разрешают DSP.
  Это не означает, что 12 проектов уже собираются.
- Вложенные AccountServer/LoginServer совпадают с внешними по исходникам/проектам;
  различаются только .ncb/.opt/.plg. Канонический каталог — внешний RF_Server.
- 26 .cpp не входят ни в один DSP. Полный ZoneServer-проект и исходная БД не найдены.
  MySQL-схемы GoMMO не считаются подтверждённой заменой исходной серверной БД.
- Уточнение ADO: четыре #import есть в непроектных обёртках; серверные проекты
  используют ODBC (rfnewdatabase.h/cpp). msado15.dll найден на хосте в обоих стандартных
  Program Files-каталогах; совместимость с будущей VM не проверялась.
- cl/msdev/nmake/rc/link не найдены в PATH; поиск cl/msdev/nmake под RFOnlineTrash пуст.
  Windows Kits в проверенном стандартном каталоге не обнаружен.
- Пять тестов сканера прошли. Все 962 исходных файла сохранили прежние SHA-256.
  Оригиналы и конфигурации системы не менялись в этом этапе.

## Проверка VS 2026 после установки

Проверка: `scripts/Invoke-Python.ps1 scripts/probe_msvc.py`.
Отчёт: inventory/msvc-verification.json. Генерируются только собственные smoke.cpp
и CMakeLists.txt в work/msvc-smoke. Скомпилированы windows.h/Win32 API и static_assert
32-битного указателя; линковка/запуск завершились с 0, вывод x86 Win32 OK.
SHA-256 и entry point RVA тестового PE x86 записаны в отчёте.
Сырые журналы в artifacts/msvc-smoke не включены в Git.

В песочнице MSBuild FileTracker завершался с E_ACCESSDENIED; тот же тест вне
песочницы прошёл. Это не неисправность установки. Глобальный PATH не менялся:
используется VsDevCmd с host x64 / target x86. Также найден toolset 14.44.35207,
но он не испытывался. Проверка не охватывает RF-код, старый DirectX и ABI .lib.

Исторические записи выше о ненайденных компиляторах относятся к состоянию до
установки VS. Блокер отсутствия современного компилятора закрыт.

## Начало клиентского переноса

Подготовлены 492 побайтово проверенные копии RF_Client/R3Engine. Современный проект
движка (58 C++/1 RC) успешно сконфигурирован. Первая компиляция завершилась с 1:
12 COFF x86 объектов получены, отсутствуют DirectX 8 headers, есть C2065/C7732 в
двух legacy-файлах. Библиотека ещё не собрана. Инвентарь client-build-inputs.json и
client-build-result.json, подробности research/client-port-first-build.md.
Отсутствие DirectX-заголовков теперь подтверждено компилятором, а не только поиском.

## Последующее M5: настоящий GPU и map path

M5 закрыт для первого helper-data участка, gate inventory/client-m5-checkpoint.json.
Own entry полного client project выполнил настоящий D3D8 HAL на RTX2080Ti, загрузку/
отрисовку5RPKentities и5real particle scripts, CLevel::LoadLevel/FrameMove/render/release
для lobby и Platform01.13cases/321checks,0warnings/errors, allocation и COM balance0.
Platform01:23helpers/8interiors и два weather layers15/500; inside/night stop,
outside/night start,outside/day stop проверены настоящим FrameMove. GPU BMP прочитаны
из backbuffer, hashes сохранены, кадры просмотрены. Control words027F→027F→007F;
map/particle/render/helper consumer не изменяют007F. Reference startup state неизвестен.
Sandbox HAL creation дал0x8876086A, тот же EXE вне sandbox прошёл без изменения source.
Game DLL delayed и не загружались; звук/сеть/normal WinMain/input EXE не запускались.
703weather/30resource/23 337targeted helper regressions прошли на final lab SHA
ece2acccb434ef06ee0aba3d35a15778f3bdf87e5b70589221f8f34732aed3ae.
Normal build a761c930... не менялся. IDA reference graphics analysis:3functions/6exact
instruction checks на обоих pinned PE; owned77bfa3a2 закрыта с save.
research/client455-graphics-runtime.md. D3D9/full Character/particles/clock/UI/network
и M6/M6F/M7/M9 открыты; M8 modernization не требуется.

## M6: численный clock455

Собственный x86 clock module восстановил8scalar functions и256byte clock prefix
из0x8B1F20/RVA0x4B1F20.773instruction bytes совпали в обоих pinned PE после
проверки absolute operands/constants.1275checks/12FP modes прошли standalone и
в полном lab клиенте. Normal retained2used routines/prefix,lab9; linked code,
constants и .CRT$XCU initializer KERNEL32.GetTickCount проверены в обоих EXE.
Обычный RF_Online.bin2440704bytes/entryRVA0x1BBAA0,SHA
f5f945160fe45255b9cea935cb3e27946a0a5ab531a18b1279abbd41164e18e5,не запускался.
Lab SHA bb441c5c3e393f98a298355b794e14bbb95d1efdd790c36e1356080d64c44e9b:
703weather/30resource regression checks и2real GPU cases/59checks на Platform01
прошли. Helper/interior/night states прежние,FP007F,release balance0;game DLLs отсутствуют.
287normal modern x86 /MT objects проверены; дополнительный61-й engine object —clock.
Уточнение:0x7E3E55 это console %time; настоящий clock map caller0x7C8B60.
Cached time/packet origin/CLand/console и full lighting ещё открыты.
research/client455-clock-source.md; inventory/client455-clock*.json/client455-time-callers.json.
M6/M6F/M7/M9 открыты. Historical M5 evidence сохранён отдельно и проверен --saved.

## M6: client map message8/5 → CLand time

Восстановлен selected source path client packet8/5,CLand timestamp/receipt tick cache
и successful map-load clock hook. Source overlays трёх client files,21behavior files
total; own MapTimeState16bytes не применяется как binary455layout. Критический130byte
numeric fragment0x7C8DC4/RVA0x3C8DC4 совпал с обоими pinned PE.314component/full-client
checks/12FP modes/UTC+JST; actual linked helper/CLand/packet object references проверены.
Own GPU entry выполнил реальный CNetMsgProcessor_Map8/5,CLand Create/LoadLevel(char*)
и public post-load hook, Platform01 FrameMove/render/CLand Destroy/UnloadLevel.
Synthetic timestamp43200 при UTC0 дал fractions0.5/0.5,mapDay1 для synthetic mapIndex12.
Это не full byte-index UI/camera/effects path и не root network/socket verification.
2GPUcases/66checks,0errors/warnings,allocation/COM balance0; FPU007F,frame просмотрен.
1275clock/703weather/30resource regressions и288modern x86 /MT checks прошли.
Normal2448896bytes,entryRVA0x1BBDF0,SHA
a1b9dd5d7e45313ef414d90dff198717e66bc5d58e5ed95bcb72fba601cf456a,не исполнялся.
Lab SHA ad3a17d3d54372c4a05962ae0088b3f44d3d96b438f0873e94c06317cae5f441.
Localtime32 old-CRT timezone/DST/invalid/Init domains,opaque fields/other consumers,
full CLand/console/lighting и M6/M6F/M7/M9 открыты. Owned IDA92d1827c закрыта/save.
research/client455-map-time-source.md; inventory/client455-map-time*.json.

## M6: local clock commands и actual input

Восстановлены time/real_time,grade>=1 input hook в actual CHAT_INFO::SendMessage и
real HMS set/get. Clock10scalar functions+256byte prefix:1037instruction bytes
совпали с обоими PE;1443checks/12FP modes standalone/full-client. Parser432ASCII cases/
2628checks/12FP modes,20actual input/access/history/lifecycle checks прошли:grade1
accepts,grade0 rejects. CNetworkMgr ctor/dtor/WSAStartup выполнены;Create/SetNetSystem/
Connect не вызывались,network processes0,соединений/отправки нет. Game DLLs отсутствуют.
Две команды в own graphics entry управляют actual Platform01 weather FrameMove:
2GPUcases/69checks,0warnings/errors,Dmalloc/COM balance0,FPU007F,23helpers/8interiors.
289modern x86 /MT,314map-time/703weather/30resource regressions прошли.
Normal2450432bytes,entryRVA0x1BC330,SHA
d656498a2465feec8c9b4fb44149f01e38aa8e4288e4cc9e4bb4c555ec490919,не исполнялся.
Lab SHA d19ea1193dbfd546e68eadb3332e145de3d42d83e5429155726c807cfd3a1c24.
Other local directives/full chat/GUI input/locale/calendar/lighting остаются открытыми.
Owned IDA1bf47ee9 закрыта/save;research/client455-time-commands-source.md.
Следующий critical path — Character sources/ABI перед D3D9; current header/import
contract использует IDirect3DDevice8. M6/M6F/M7/M9 не закрыты.

## M6: первый Character source unit

Четыре legacy CPU mesh bindings восстановлены source и подключены normal/lab.
245checks standalone/full-client и4COFFtests;три actual InitVertex E8 calls доходят
до source. Skinned/unskinned CPU meshes3vertices/0faces загружаются/освобождаются.
Pointer+160 задаёт штатный FindBlendParent,включая count0;constructor patch не сделан.
455mesh5803/vertex64/inline blends отличаются от legacy1072/36/heap;first-match455
противlast-matchlegacy учтён как gap. Full Character455/render/real assets открыты.
Normal2450944bytes,entryRVA0x1BC340,SHA
9cb2329eda37ff61548f7b24fcb70b617b85a151623e867ced71439972e3a794,не исполнялся.
Lab4146176bytes,entryRVA0x7EAA,SHA
d59233bc12b46799bc8cc5311acfeb6dcb09f3e900624eb3b1933d08458b1c46.
289modern client/engine/JPEG x86/MT иown binding archive /MT проверены.
1443clock/314map-time/703weather/30resource,432command cases/2628checks+20actual input,
Platform01/device2GPUcases/69checks прошли.0GPUwarnings/errors,Dmalloc/COMbalance0,
FPU007F,frame просмотрен;это map/weather regression,не CharacterGPU acceptance.
Owned IDAc99d5253closed/save;8reference bodies/11instruction sites в обоих PE.
research/character-mesh-source.md;inventory/character-mesh-source*.json.

## M6: full legacy InitVertex source,2026-11-05

Source Character unit расширен до8functions/full InitVertex/vertex/physique.245binding+
6732InitVertex checks/144cases/12FP modes standalone/full-client,4COFFtests и2actual
LoadRealData→source calls прошли. Actual SDK MakeVB использует test-only COM capture,
physical Character GPU не сертифицирован. Нормальный WinMain не исполнялся.
Normal2451456bytes,entryRVA0x1BC4B0,SHA
a070e9fb4350290fc8877940ae6cfbce417b0cc12b5a12b8a6a82ba5e121d573.
Lab4167680bytes,entryRVA0x7EC8,SHA
ce6a1bb826d11f219218d4361f923ba1b11de9b31fe998b65b98696b68104cce.
289modern COFF +source bindings/init objects x86/MT;clock/map-time/weather/resource/
time-input regressions прошли. Platform01/device2GPUcases/69checks,0warnings/errors,
Dmalloc/COMbalance0,FPU007F;frameSHA равен прежнему просмотренному frame.
455vertex normals инвертированы,64byte layout иMESH08path91F250→922A00 подтверждены.
7bodies/field/magic instructions/2calls в обоих pinned PE;3model samples закреплены.
В этой ревизии MESH08реализация ещё отсутствовала;старая693frame схема не подходит кShield065.
Owned IDAab009b3b/012583e5closed/save;research/character-init-source.md.

## M6: MESH08 format source и реальный corpus, 2026-11-05

В loose model tree прочитано2708files:858MESH08 и1850other-prefix, не включённых в
данный форматный аудит.858/858 прошли точный byte roundtrip:515096894bytes,
12090meshes,5153052vertices/indices,412222bone records. Archive/RFS модели иполный
resource inventory не покрыты. Source C++ bounded reader/writer x86/MT проверен:
6304checks/12real samples/393parts/1309guard-page truncations standalone/full-client;
7Python tests.3reference bodies/12instruction sites сверены в обоих pinned PE.
Материалы, bone resolver иshared GPU state не восстанавливаются форматным модулем;
normal LoadRealData его ещё не вызывает, обе API в normal EXE удалены linker.
Lab decoder/encoderVA6B0400/6B0700, RVA2B0400/2B0700;source,неbyte-identical port.

Normal2451456bytes,entryRVA0x1BC4B0,SHA
43863bc4334d896a91888f0b132b79d7e85974b519073c2ebad8a4995b89c6af;
snapshot mesh08-format,не запускался. Lab4483072bytes,entryRVA0x8125,SHA
d8edc962d7985e2598cd1ed4080c416e03ff94ae88f2d4875cf3473657d4f1a6.
289modern COFF иformat object /MT. Character245+6732checks,clock1443,map-time314,
weather703,resource30,time-command432cases/2628checks+20actual input прошли.
Platform01/device2GPUcases/69checks,0warnings/errors,Dmalloc/COMbalance0,FPU007F;
frameSHA равен прежнему просмотренному. Это map/weather regression,неCharacterGPU.
GameDLLs/referenceEXE/normalWinMain не запускались. Owned IDAeb76ecefclosed/save.
research/client455-mesh08-format.md;inventory/character-mesh08-corpus.json,
inventory/client455-mesh08*.json. M6/M6F/M7/M9 открыты.

## M6: packed455 parent/bone source, 2026-11-05

Четыре455CPU kernels (lookup/parent array/rematch/MESH08bones) восстановлены source.
4bodies/12instruction sites сверены в обоих pinned PE;owned IDA6f091546closed/save.
2237checks/12real mesh-skeleton pairs/393meshes/455skeleton records прошли standalone
иfull-client own entry;вfixtures0missing influences,max4unique/mesh.20cases count31–50
сохраняют подтверждённое перекрытие pointer copy/matrix fields;owncap50 не доказательство
официальной безопасной capacity. Plain BN framing/names проверены tooling;полный
skeleton/model loader,selection/transforms/animation/material/GPU ещё открыты.
Normal используетlegacyCharacterABI,unused455APIs stripped;lab4APIlinked fromsource /MT.

Normal2451456bytes,entryRVA0x1BC4B0,SHA
d52d1e6889e679af1262182088e6f648affd7a0f73d89b23c35c975f310ac30b;
snapshot mesh455-bones,не запускался. Lab4534784bytes,entryRVA0x81D4,SHA
0a1dbe6d2f069b436556e7933648b3ce44ac877a0e808653cc1ed7d93d92b79d.
Regressions:mesh08 6304,legacy245+6732,clock1443,map-time314,weather703,resource30,
time-command432cases/2628checks+20actual input прошли.289modern COFFx86/MT.
Platform01/device2GPUcases/69checks,0warnings/errors,Dmalloc/COMbalance0,FPU007F;
обаframeSHA равны прежним просмотренным кадрам. Это map/weather,неCharacterGPU.
Source macro ограничен labfile,все180old units без причины не пересобираются.
GameDLLs/referenceEXE/normalWinMain не запускались. M6/M6F/M7/M9 не закрыты.
research/client455-mesh-bindings-source.md;inventory/client455-mesh-bindings*.json,
character-mesh08-bone-pairs.json,character-mesh455-bindings-graphics-runtime.json.

## M6: mesh constructor/header/material request source,2026-11-05

3CPU API constructor final state/counters,header scalars/names/matrices/material
request flow восстановлены source.14562checks/12real files/393parts/12FP modes
standalone/full-client прошли. Матрицы вызываютactual D3DX9_36;texture provider
вtests scripted,физическийTextureManager/sharedGPU/normal loader ещё открыты.
Header domain858files/12090meshes:8659empty primary,3431DDS/backslash;0unterminated/
nonASCII/% strings,nonfinite/nonaffine/zero numeric3x3det. Это ограниченнаяклассификация.
5bodies совпали вbothPE;thunks854130/85412A IAT resolveD3DX9_36;ownedIDA716ae4faclosed/save.
SysWOW64 DLL иclient-local DLL byte-equal,SHA
c12f0ab0338eb5031d3d04beaf7208ac848f7e037d21ff963d2af90221cbe935,x86/3734536bytes,
version9.19.949.2111,Microsoft AuthenticodeValid. Direct export подтвердил1ULP offset:
inverse diag(2,2,2,1) bits3EFFFFFF x3/3F7FFFFF. Сохранятьquirk;reciprocal approximation
предполагается какпричина,внутренниеинструкцииDLL не исследованы.

Normal2451456bytes,entryRVA1BC4B0,SHA
6f486f1f4ef950d207d9fd9cba9d2e647d7538954185c39adfeec7d5c9316a0b,
snapshot mesh455-header-material,не запускался. Lab4585984bytes,entryRVA828D,SHA
f55fdb172661cbcfdf131aa3d7a0ddba1413b2039151ff866c88f78f2a3c42cb.
Lab3API fromsource;normal unused APIs stripped.289modern COFF/MT. Regresions:
mesh086304,binding4552237,legacy245+6732,clock1443,map-time314,weather703,resource30,
time-command432cases/2628checks+20actualinput. Platform01/device2GPUcases/69checks,
0warnings/errors,Dmalloc/COMbalance0,FPU007F;обаframeSHA равны просмотренным.
Это map/weather regression;CharacterGPU ещё открыт. GameDLLs/normalWinMain/referenceEXE
не запускались. M6/M6F/M7/M9 не закрыты. research/client455-mesh-runtime-source.md;
inventory/character-mesh08-headers.json,client455-mesh-runtime*.json,
character-mesh455-runtime-graphics.json.

## Документация интеграций

- [GoMMO: stdio bridge и studio_status](https://oldschoolops.com/docs/gommo-studio/automation/ai-assistants/).
- [Codex: настройка MCP](https://learn.chatgpt.com/docs/extend/mcp?surface=cli).
- Локально: `IDA Professional 9.2/README_python3.txt`, справка `idapyswitch`,
  `docs/user-guide/configuration/command-line-switches.html`.

Результаты локальных запусков имеют приоритет над устаревшим названием папки/README.

## M1 и закрепление клиентского эталона

M1 выполнен по compile/archive: 58 COFF x86 объектов, R3Engine.lib, две чистые
пересборки. Дальнейшие CRT/ABI/поведение проверяются отдельно. DirectX 8.1b SDK имеет
действительную подпись Microsoft и архивный хеш; установщик не запускался.
Результаты: inventory/directx81b-sdk.json, client-source-patches.json,
client-build-result.json, research/client-port-m1.md.

Два клиентских файла отличаются 5 байтами; область ветвления и общий double
исследованы в IDA, собственная сессия закрыта с сохранением. Текущий клиент закреплён
эталоном по SHA-256 в config/client-target.json. Версионная константа не считается
доказательством атрибуции. Полный манифест ресурсов ещё не создан.

M4: 207 определений Character кешированы, 30 операндов инструкций проверены.
Диагностический Character.h: 67 layout assertions и 165 публичных decorated names
проверены; все 180 C++ клиента скомпилированы. Конструкторы/inline/STL ABI ещё открыты.
Отдельно собран настоящий /MT R3EngineMT.lib; 180+58 COFF x86 /MT проверены.
LNK2038 устранён корректной сборкой, genuine DX8 .lib подключены. JPEG 6b /MT прошёл
28 ABI сравнений и 2 точных golden decodes; 26 Miles импортов есть в 455 DLL.
Проверены 284 x86 /MT объекта. Diagnostic link и clean rebuild успешны.
Native собственный тест подтвердил: старый FILE EOF доступ Character не работает с UCRT;
classic CRT прошёл только этот частный тест. На том этапе RF_Online.bin ещё не был
получен; последующая полная сборка описана выше. Input EXE/DLL не запускались.
research/client-dependencies-m4.md и client-port-m4.md;
inventory/client-character-diagnostic.json, client-mt-variant.json,
character-header-recovery.json. Четыре проверки COFF прошли.

Последнее дополнение: адаптер 8 stdio API прошёл 1828 собственных native проверок и
3 теста COFF; инструкции/релокации 10 входных объектов сохранены. Runtime старых
двух Pattern/Item загрузчиков проверен на valid fixtures (49 checks). CObjectManager
constructor восстановлен; AnimationManager
получил empty-vector constructor + реальный Init. 3102 проверки реальных SDK операций
на unloaded records прошли. Реальные _Xlen/_Xran /MT exceptions прошли 770 сравнений
с classic system exports; aliases в тестах удалены. Link gaps в выбранной сборке закрыты.
Полный Character unwind/loaded data/render не проверен. Header: 67 layout assertions.
research/character-effects-and-exceptions.md.
Новое: SetTexPath/SetMipMap и empty renderer construction восстановлены; 18 ABI
byte checks, 8 instances/136 part managers, всего 3630 combined native checks прошли.
Последующее продолжение: 455 DrawCharacter calls под отдельным flag/ledger,
bounded legacy SetEffect bridge и 59 native checks с CPU mesh effect application.
Последующее продолжение: 455 logging и success->lobby edge перенесены отдельными
flags с сохранением legacy bodies. Нет заглушек CheckFiles/SendLog или _DEVELOPER_ bypass.
Native logger 14 cases/66 checks; полная сборка и clean прошли. 455 map/36-grade
effect behavior ещё не перенесён. research/client-first-build.md.
research/client-draw-and-legacy-effects.md.
Конструкторы используют реальные SDK Init, но исходный inline/sizeof не доказан.
research/character-setters-and-construction.md и inventory/character-setters.json.
research/character-managers.md и research/character-stdio-adapter.md.
Для завершения последней /Goal повторно получены две чистые сборки R3Engine x86;
runtime sections/relocations 58 объектов совпали. Хеши исходных PE/копий и 5 различий
повторно проверены, 140 SPT / 97 543 записи прошли round trip. goal-checkpoint.json.
Предыдущая ограниченная цель выполнена уведомлением о начале пункта 4.
Активная новая /Goal — M9, финальная приёмка клиента 455 без модернизации графики.
Полный клиент ещё не готов.

Последний клиентский source unit (2026-11-05): Character455 record1188/manager4148,
IDcache/rawMSH/texture refresh.24body ranges equalbothpins; ctor92instructions
вмаленьком trackedmanifest.850CPU/1138HALchecks standalone,1138вполномlab;
12models/393parts/276uploads/59texturepointers,COM/heap/Dmalloc0. Source x86/MT,
/W4/WX.13C APIs происходят изsource archive ивызываются вlab;normal unused/stripped.
Normal сборка289modernCOFF/MT,lab185clientTUs;проверены модели10021 иPlatform01/device69,
прежниеframeSHA равны. PE identities:inventory/client455-character-manager-checkpoint.json.
Normal EXE не запускался;его runtimebytes кромеtimestamps равны предыдущейrevision.
IDAownedc3f13f8bclosed/save. ПолныйBN/dispatcher/animation/D3D9renderer остаются M6.
research/client455-character-manager.md. Изменений исходного installation/server нет.
Следующий standaloneunit: legacyMSH/BN intermediate parser/lifetime source,
4606checks/17samples459records/1183guarded prefixes/7allocation failures/12FPmodes,
6Python tests,heap0.7bodies pinned;importer/converter покаpending. SourceO2/W4/WX
x86/MT. Fullclient PE не менялся;owned IDA926983beclosed/save. Reports
inventory/client455-legacy-models-reference/build/cpu.json;research/client455-legacy-model-reader.md.
Последующийconnectedunit:legacyMSH/BN converter/importer/MTG/weights/indexing/binding,
66627capture/14896HALchecks standalone/fullclient;34runs972parts/832HALuploads,
2CPUretained,12actualBN→MESH08pairs393parts276uploads.9bodies equalbothpins,
10sourceAPIs verified,heap/COM/Dmalloc0. SourceO2/W4/WX/x86/MT;fullclient186labTUs,
289normalmodernCOFF/MT. Current manager1138/model10021/Platform01-device69passed,
frames иnormalruntimebytes (excepttimestamps) сохранены. Всеidentities/evidence:
inventory/client455-legacy-runtime-checkpoint.json;research/client455-legacy-model-runtime.md.
Normaldispatcher/ANI/animation/shaders пока открыты. Owned0d9553e1/08d81b2fclosed/save.
Последующий unit:ANI/rawIO/record284/lifetime/attachment/Character dispatcher.
16bodyranges equalbothpins;14513CPU/15181HALchecks standalone/fullclient,
27ANI1062tracks/6Python tests/22real switches/11BN→MESH08pairs794parts660uploads.
13sourceC API actual caller/archiveproof;sourceO2/W4/WX/x86/MT. Stickyflags иrawleak
проверены (отдельнаяharnesscleanup после наблюдения). COM/Dmalloc0;normal289modernCOFF,
lab187clientTUs. Current legacy14896/manager1138/Platform01-device69passed,
frames/normalruntimebytes кромеtimestamps сохранены. Normalconsumers/pose/shaders/
AnimationManager/asyncworker остаются открытыми. Owned45964631closed/save.
Gate inventory/client455-animation-checkpoint.json;
research/client455-animation-dispatch.md. Original/server inputs без изменений.
Последующий source unit: pose evaluators/основные FrameMove phases,sourceO2/W4/WX/
x86/MT.11realpairs/132updates/2298skin matrices standalone иfullclientownentry,
5sourceC APIs actualcaller/archiveproof,heap/Dmalloc0. CPUonly,безGPUdraw.
Normal180client/289modernCOFF,lab188TUs. Старые runtime suites не повторялись;
normalruntimebytes кромеtimestamps сохранены. Secondary/producer кадров/manager/
worker/normal consumers/shaders открыты. Gateinventory/client455-pose-checkpoint.json;
research/client455-pose-source.md. НовыхIDA sessions нет,оригиналы/серверы не менялись.
Следующийunit:secondary91E270/borrower7CD430,3bodyranges и18doubleconstants pinned.
Source state84/globals28/5effects,O2/W4/WX/x86/MT;36scalarcases/2realCoraBN/6updates
component/fullclientownentry,6APIs sourcecaller. Relatedpose11pairs/132updates
passed;прочиеoldbulk suites не запускались. Heap/Dmalloc0,CPUonly/noD3Ddraw.
Static__CIsin reference поканеsource,mandatorycallback;labmodernMTsin прямоотмечен.
Normal180client/lab189TUs;normalruntimebytes прежниеexcepttimestamps. Owned8115e37c
closed/save. Gateinventory/client455-secondary-checkpoint.json;
research/client455-secondary-motion.md. Оригиналы исерверы без изменений.
