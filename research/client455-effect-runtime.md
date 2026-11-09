# Обновление и отрисовка прицела455 — работа106

Runtime gate106 исторический после [nuclear107](client455-nuclear-aiming.md).
Новые runtime/visual evidence сохранены в gate107; ниже история106.

В обычном клиентском effectcore восстановлены выбранные scheduling/lifecycle
контракты, ёмкость512 и два прохода выбора эффектов. Настоящий шестидорожечный
ядерный прицел теперь обновляется и рисуется в контрольной D3D сцене. После
обычной отмены исчезают дочерние эффекты и master. Это не приёмка всего ядерного
контроллера: pending/position, звук, C1A, игровой ввод и мировой pipeline ещё открыты.
M6/M6F/M7/M9 остаются открытыми.

## Статическая опора

Native IDA MCP, session `ed41bb12`, saved/closed/list0. Получены16 полных функций
и2546 инструкций; все16 диапазонов и2 data ranges совпали в двух закреплённых
x86 бинарниках с base400000. Основной SHA-256
`b1b5febf0d0394712e2322350e19dafe60742e8642697b93cfb89135bac1fd8b`,
второй `46528aac20499e3b3928d58658d7e0cefe26feba7cd193796d5cfbf7a2bbc558`.
Диапазоны с SHA-256: `inventory/client455-effect-runtime-reference.json`;
сырой вывод: `artifacts/client455-progress/effect-runtime106-reference.json`.

| RVA | Назначение |
| --- | --- |
| `0x3d78f0` / `0x3d7bd0` | StartEffect / compaction |
| `0x3d8410` / `0x3d8800` | Исчезновение child / удаление master с уведомлением children |
| `0x3d9a80` / `0x3d9aa0` / `0x3da4b0` | FrameMove wrapper / child / magic scheduling |
| `0x3dae30` / `0x3daec0` | Track start / общий draw |
| `0x3db4e0` / `0x3db640` | Opaque / alpha и финальный fade pass |
| `0x3d7220` / `0x3d7640` / `0x7ddcac` | Изменение качества / getter / начальный WORD2 |
| `0x4e08f0` / `0x4e09a0` / `0x4f2d10` | ReleaseTexMem / ReleaseEntity / texture release |
| `0x7394c4` | Точный warning R3T,37 байт вместе с NUL |

Шесть предупреждений R3T из105 имеют подтверждённый target branch: предупреждение
не отменяет освобождение GPU handle. Сверены и код, и точные bytes строки с legacy
источником. Это закрывает выбранную неопределённость предупреждения; общая приёмка
texture cache/reset/shutdown не объявляется завершённой.

## Обычные исходники

`client455_effect_runtime_port.py` переносит bodies из трёх собственных `.inc` в
копии effectcore.h/.cpp через штатный prepare. Engine546a7529… не менялась.

- CEffectList остаётся136 байт, активных записей512 вместо256. Перед вытеснением
  самого старого particle вызываются ReleaseParticle и delete, затем compaction.
- На границе257/256 master принудительно освобождаются его children, затем
  сдвигаются все255 сохранившихся записей и добавляется новая. В legacy code
  счётчик уменьшался до compaction: это теряло одного master и дублировало другого.
  Теперь проверены немедленное освобождение живых children и наличие всех256
  актуальных уникальных ID. Опора — дополнительно закреплённый диапазон
  RVA3d8970 из сохранённого static reference104; его bytes сверены повторно.
- Удаление master уведомляет каждый child с time0 или time-1. В time0 particle
  прекращает эмиссию и получает NO_LOOP; отрицательное время освобождает shell
  немедленно. У непартикла time<=0 удаляет запись сразу. Завершение particle в
  обычном FrameMove теперь также вызывает ReleaseParticle перед delete.
- Scheduling учитывает quality0/1/2, whitelist и независимые ветви оригинала,
  включая повторный вызов для двух forced cue IDs и запись special fields в
  последнюю запись при её наличии. Master cleanup учитывает state0/2/4.
- Начальный quality2 подтверждён по data. ApplyEffectOption455 получает low WORD
  option явно; его kernel проверен непосредственно в native. Поле options455/UI
  ещё не подключено, обычный процесс пользуется default2. Standalone setter
  может быть удалён линкером из обычной PE до появления реального UI caller.
- Opaque pass сохраняет override mask0x4c4b400 и фильтр states3/5; alpha pass
  затем выполняет отдельный entity-fade pass без такого фильтра. Fog восстанавливается
  после проходов. Legacy RenderAll пока вызывает оба прохода подряд: правильная
  расстановка между остальными мировыми проходами ещё требует переноса.
- Screen-blur runtime теперь явно отказывает вместо молчаливого запуска обычного
  entity. Сам blur provider ещё обязателен для полной455 приёмки.

## Проверка реальными ресурсами

`work/m9/b971bd0b/effect-runtime-001`:573 assertions, из них512 проверяют
освобождение каждого shell в проверке границы513/512. Это быстрый native run,
не запросы к модели и не повтор159k suite.

Реальные EffectEntity59.rpk и таблицы,6 R3E/R3M/R3T и5 recipes. Обычный
FrameMove выполнен90 раз, создал все6 tracks; динамический свет вставлялся
90 раз. Три GPU кадра на1/2/3 секунде и отдельный кадр после отмены просмотрены:
видны зелёный вращающийся радар и меняющаяся волна. Суммарно600461 изменённый
пиксель; после отмены0. Child/master drain занял62 ticks. Свет вставлен в обычный
список, но его compositing на поверхности мира в этой сцене не проверен.

Проверены quality option0→0/3→1/disabled→2 и подавление children прицела на0,
настоящая граница513/512 с вытеснением, отрицательное исчезновение и release.
После owner destroy GPU handles освобождены;9728 байт process-owned texture
tables отдельно убраны через public R3ReleasePreTextures. Dmalloc270592→270592.
Шесть target R3T warnings сохранены. Это выбранный lifecycle, не полный shutdown.

Новая собственная PE
`12ca86c5445bb7c89e58864d653c72020095b3136d3f0832e7245cccdca65b1a`,
2156544 байта, x86/base400000, entry15ab00, WinMainb8de0, afterCreateb8f54.
182 client /20 kernel /59 facade, unresolved0; прежний offline Create→1 до game
loop с настоящим Fast2D ready:7969. Повторены resources66/magic36/status58/audio157/
account/hotbar7/storage3. Шесть новых hover кадров просмотрены и byte-equal105.
Всего просмотрены10 новых кадров; другие32 GUI кадра и большие неизменённые
world/audio/159k suites не повторялись. Gate105 исторический. Originals/server
не менялись; входные EXE не исполнялись.

Текущий gate: `inventory/client455-effect-runtime-checkpoint.json`.
Воспроизведение: `scripts/Invoke-Python.ps1 scripts/checkpoint_client455_effect_runtime.py`.
Изображения: `work/m9/b971bd0b/effect-runtime-001/effect-contact.png`.

## Дальше107

Связать actual nuclear pending/position/frame/cancel owner с восстановленными
эффектом и tagged sound, затем C1A/hover true predicate. Ещё обязательны full
world pass placement/dynamic-light compositing, quality UI producer, blur,
advanced axis/parabola/multi/curve/shared pointers, device reset/FP/RNG/unsafe/
OOM/concurrency/shutdown и все прежние client-acceptance gaps. Графика не
модернизировалась, M9 не переопределён.
