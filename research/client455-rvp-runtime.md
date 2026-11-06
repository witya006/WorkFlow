# Обычный исполнитель RVP: камеры и треки — участок 079

Пустые engine entry points заменены исходным исполнителем, который вызывается
обычным CLevel. На трёх учебных мирах работают создание RVP/CAM, подготовка,
запуск, пауза, выбор камеры, переходы затемнения, завершение и освобождение.
Это ограниченный домен проигрывателя: сценарии с персонажами, эффектами,
звуком, screen/timer_rate пока явно отклоняются при Create. Они остаются
обязательными частями восстановления; цель полного клиента не сокращалась.

## Эталон и исправление подписей

Эталоны x86/base0x400000, SHA-256:
`b1b5febf0d0394712e2322350e19dafe60742e8642697b93cfb89135bac1fd8b`,
backup `46528aac20499e3b3928d58658d7e0cefe26feba7cd193796d5cfbf7a2bbc558`.
20 полных диапазонов совпадают. Raw078 переиспользован; новые raw079 сохранены
в artifacts/client455-progress/rvp-runtime079.json и файле *-ranges.json.
Полностью сохранены 531 инструкция FrameMove, 23 Start, 14 float-clock setter
и 114 Release. IDA6a789f6f сохранена и закрыта.

В078 неверно подписали две функции. Их диапазоны и raw были правильными,
а подписи теперь проверены по телам и вызывающему коду:

| RVA | Подтверждённое назначение |
|---|---|
| 0x4d5510 | Render, вызывается level8E7C40 |
| 0x4d8340 | Release, вызывается level8E7730 |
| 0x4d4c10 / 0x4d4c20 | GetPlaying / SetPause |
| 0x4d5fa0 | Start: play выставляется до проверки loaded movie |
| 0x4d5ff0 | FrameMove: guards, pause/play/flags, extract, camera, actors/audio, blur |
| 0x4d1d90 | SetNowFrame с float seconds |
| 0x4e7910 | Level.FrameMove сначала вызывает RTMovieFrameMove |
| 0x4ce5d0 | Сброс двух material/light caches; пока не перенесён |

Предыдущий текст078 исправлен, raw не переименовывался задним числом.

## Исходник и сборка

client455_rvp_engine.inc предоставляет обычные RTMovie entry points.
client455_rvp_runtime.cpp находится в production facade и использует настоящий
CAniCamera/CLevel/ChInterface. Парсер078 теперь тоже компилируется в facade.
Новая функциональность не получена включением старого RTMOVIE define.

CAM имена связываются с реальными камерами; отсутствующее имя предупреждается
и пропускается. Track order сохраняется. No-camera4 окончательно потребляет
зависимые от камеры команды; их нельзя проиграть повторно простым снятием бита.
Код quake/blur перенесён к реальным engine calls, но полноценные RVP-сценарии
с этими командами ещё требуют отдельной проверки; stock-прогоны ниже покрывают
camera/fade. Полный fullscreen backend проверен отдельно.

Для паузы старый DWORD SetNowFrame не подходит. Создано производное объявление
anicamera455.h с дополнительным float overload, без изменения полей класса.
Оно принудительно включается в 58 legacy engine TU, обычные клиентские TU,
facade и используемые full-object probes. Девять независимых математических/
resource helper TU исключены из этого include: иначе using-directive старого
port shim мешает локальному имени less. База033 и исходный header сохранены.
Всего в движке осталось67 объектов и9 overlays; в facade стало36 TU.

SetNowFrame сохраняет именно формулу455: startTick=now-seconds-playStart/30.
Поэтому последующий playback имеет двойное смещение playStart/30. Это проверено
с start31 и seconds1.75; формула не заменена более привычным вариантом.
Пауза выполняет extract и float-clock setter, затем выставляет play=false,
no-camera4 и density0.25. Resume требует Start(FALSE). Flag16 пропускает
track/camera часть FrameMove; отсутствие loaded RVP тоже даёт ранний выход.

Release455 не обнуляет loaded/play/pause scalars. Этот случай воспроизведён и
проверен при Destroy реального уровня. Для неудачного camera-only load свой
владелец дополнительно отсоединяется, чтобы не пережить CLevel; это отклонение
в failure domain явно не принято как полная эквивалентность455.

Новый RVP renderer создаёт настоящий второй ChInterface. Исправлена собственная
facade-последовательность activeRenderer: при вложенном Destroy восстанавливается
предыдущий владелец. Проверен обычный вложенный порядок; произвольный порядок
удаления владельцев не объявлен принятым. Пробы теперь копируют проверенные
Character .sho, которые нужны этому реальному renderer owner.

## Проверки

| Мир | Camera events | Fade-in / fade-out | Ticks |
|---|---:|---:|---:|
| Bellato | 10 | 9 / 10 | 364 |
| Cora | 9 | 9 / 10 | 330 |
| Accretia | 8 | 8 / 9 | 262 |

Все82 camera/fade команды трёх исходных RVP потреблены. Числа сверены независимо
с файлами; всего27 camera events, не число уникальных камер. Для каждого мира
проверены float pause, flag16, завершение, camera-only/no-RVP, явный отказ для
неперенесённого actor provider, повторная загрузка и восстановление внешнего
renderer owner. Предупреждений0, exit0, Dmalloc270592 до/после.

Просмотрены6 scene/end-fade кадров этих миров. Конечный fade кадр не обязан
быть полностью чёрным в момент остановки камеры: затемнение имеет свой clock.
Это проверка собственного GPU-пути, а не pixel comparison с запущенным эталоном.

Intro одновременно использует реально созданный обычный RVP: добавлена явная
проверка его наличия. Прошли26 intro cameras, 357/325/258 ticks, Dmalloc balance.
Штатный RVP во время level.FrameMove может сбрасывать FOV и fullscreen mode;
он не защищён придуманным flag16. Новые GPU views изменились относительно077,
поэтому старые hashes не переиспользовались. Полный порядок обычного Tutorial
owner и соответствие всего кадра455 ещё открыты; stage/QBI/follow в probe
остаются recording callbacks.

Movie-state flags8/GPU6 и fullscreen GPU18 повторно прошли на текущей сборке.
Просмотрены46 кадров: 6 RVP, 29 intro, 6 movie-display, 5 fullscreen.
RTMovieFrameMove в собственной пробе больше не пуст: RVA0xd0ad0,
bytes `558bece828f10300905dc3cccccccccc`. Это доказательство наличия body,
а не полноты проигрывателя.

## Результат и оставшиеся разрывы

RF_Online.bin:
`83c1793bc8a6b2bb9e1fde2b42b986132f12c077ecaa4f42f75ad0c41037c117`,
x86/base0x400000/entry RVA0x150b20/2071552 bytes.
182 client /20 kernel /36 facade TU,0 unresolved.
Derived engine SHA
`d85c86784516872f8818c92d556bdf63a9dffaf6da559499cb3b3fddd772c347`.
Точная новая PE прошла существующий Create=1 и свежие startup contracts.
Контрактная проба теперь берёт реальные source libraries из canonical link,
поскольку engine→RVP использует современные Character kernels. Большие
неизменённые GUI/kernel suites не повторялись; старые gates исторические.

Следующий080: RVP actor/Character resource/animation/effect/audio bindings,
ambient/event waves, trace/screen/timer_rate и полный Create/Release/shared caches.
Затем настоящий CGP_Tutorial, Avatar/QBI/follow/local handlers/four-stage/Login.
Render material/light cache reset, deferred particles, недоопределённый matrix
при pause с автоматической камерой, scanner fallthrough078, численные/ошибочные
домены и все прежние gaps остаются открытыми. Startup first-chance исключения
не выданы за доказательство failure parity. М6/М6F/М7/М9 не закрыты.

Проверяемый итог: scripts/checkpoint_client455_rvp_runtime.py и
inventory/client455-rvp-runtime-checkpoint.json. Входные EXE не запускались,
серверные исходники не изменялись.
