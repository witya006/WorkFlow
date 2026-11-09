# Камера119 — толчок от взрыва и покачивание

2026-11-09. **PARTIAL, M6.** В обычный клиент перенесены подтверждённые
алгоритмы толчка/покачивания камеры, затухания по расстоянию, порядок публикации
матрицы карты и остановка покачивания после успешной загрузки карты.
Проверена цепочка настоящего архивного эффекта взрыва → scheduler → quake →
реальный CLevel → D3D view. Это ещё не полный кадр мира и не приёмка M9.

Текущий gate: [client455-quake-checkpoint.json](../inventory/client455-quake-checkpoint.json).
Команда: `scripts/Invoke-Python.ps1 scripts/checkpoint_client455_quake.py`.

## Эталон

Оба455 x86/base0x400000. Основной SHA-256
b1b5febf0d0394712e2322350e19dafe60742e8642697b93cfb89135bac1fd8b;
второй46528aac20499e3b3928d58658d7e0cefe26feba7cd193796d5cfbf7a2bbc558.
18 полных тел/18 полных дизассемблирований/2600 инструкций и четыре участка
констант побайтно равны в обоих эталонах. Новые17/1971; scheduler629 повторно
использован из106 после проверки hash и полной выдачи. MCP выдача получена
страницами не более120 инструкций с проверкой количества/уникальности/итога.
LoadLevel pcode собран из320+76 строк; исходные страницы сохранены отдельно.

| RVA | Роль |
|---|---|
|0x4b4660|Запуск толчка: duration/remaining/density/phase/period|
|0x4b4390|Вектор толчка с промежуточными шагами и фоновым покачиванием|
|0x4b3f30|Отдельное изменение трансляции матрицы, общий remaining|
|0x4b40f0|Случайные цели покачивания и косинусная интерполяция|
|0x4b4090 / 0x4b40d0 / 0x4b40e0|Start/stop/active покачивания|
|0x4b5c90 / 0x4b4970|Затухание по расстоянию и положение камеры|
|0x4b3e30 / 0x4b3b60|Loop time и знак30fps, сами producer paths ещё открыты|
|0x502a60 / 0x474144|32-bit Noise1 и CRT rand LCG|
|0x4eb7f0|CLevel map view: сначала quake по предыдущей global view, затем publish|
|0x4ea220|Успешный map load вызывает stop8B40D0 на VA8EAAF9|
|0x4e7850|Empty-level view: другой порядок; этим переносом не принят|
|0x3da4b0|FrameMoveMagicEffects: track80 → distance → quake|
|0x3e2ad0|Клиентский control writer покачивания, пока только static audit|

Raw: artifacts/client455-progress/quake119-reference.json и quake119-session.json.
Собственная IDA05a13369 сохранена/закрыта, список0. Входные EXE не исполнялись.
Серверы не изменялись и не собирались.

## Восстановленное поведение

455 выбирает число промежуточных шагов из42ms/float(dt*1000)+double(0.999f),
усечения до целого и прибавления1. Вектор обновляет амплитуду на границе периода,
прибавляет её долю согласно phase и только затем уменьшает remaining. Отдельная
matrix функция уменьшает remaining до вычисления амплитуды и не использует sway.
Обе функции разделяют один remaining; тест чередования сохраняет эту особенность.

Карта берёт направление из предыдущей глобальной матрицы. Старый исходник сначала
публиковал новую матрицу и тем самым использовал направление текущего кадра.
Теперь CLevel копирует input в своего владельца, получает quake, меняет только
translation и публикует результат в global state. Тест с меняющимися направлениями
различает эти два порядка. В собственной обычной PE подтверждены реальные вызовы
SetViewMatrix→R3GetQuakeVector и LoadLevel→RF455_StopCameraSway.

Покачивание сохраняет прошлые цели при stop/start; period0 превращается в0.02f.
Случайные цели используют rand()%range и cos интерполяцию. Успешный map load
выключает sway, не обнуляя прошлые значения. Для толчка attenuation полная до200,
линейно снижается до800, дальше0. Сохранены float stores и 32-bit wrap Noise1.
Общий Noise1 других подсистем не менялся; quake использует свой подтверждённый helper.

## Проверка

CPU full-object entry work/m9/3a4d089f/quake-001:142 события, включая101 vector,
5 matrix,10 start,8 смен view,10 distance случаев и sway/stop/seed.2921 scalars
совпали численно точно с отдельным Python oracle. Проверены отключённый output,
несколько dt, phase/period, завершение/перезапуск, отрицательная density,
чередование matrix/vector, сохранение sway целей, zero-period default,
предыдущая view и расстояния около200/800. Toggle в этом lab равен+1.
Host libm tolerance указан явно; тест не доказывает все x87/старые CRT случаи.

Реальные архивные impact15tracks и launch1track, MainGame-owned registry,
neutralAS1 BSP, Miles audio и пять GPU captures проверены в
work/m9/6a40c8ac/quake-effects-001.545 кадров: quake запускается ровно на79,
потому что track interval использует строгий верхний предел time<now.
Duration5, script density150; actual camera position даёт135.14439392089844.
151 активный/смещённый кадр, затем remaining0.26160 scalar observations
с отдельным oracle совпали точно; D3D GetTransform побайтно равен published view.
World load действительно остановил предварительно включённый sway.
Пять кадров просмотрены: flight/radar, late explosion, countdown и две пустые
после drain/destructor. Это эффекты на lab background, не весь отрисованный мир.
Штатные20 R3T warnings сохранены; полный texture649 на119 не повторялся.

Во время изготовления probe исправлены конфликт имён с legacy using namespace,
порядок вычисления аргументов диагностического JSON и подсчёт перемещения по
числам вместо memcmp(-0,+0). Неудачные запуски сохранены в work/m9/98d85469 и
bb29bc51; После удаления пробела в diagnostic template контрольный запуск повторён;
в gate принят только итоговый6a40c8ac. Предыдущий успешный76438880 сохранён.

Engine67 SHA9ae6ace8b0f34718c7708c4d62847b54b6310d3e0c254216028f0bb317279b74.
Изменены только r3util.obj и level.obj; остальные65 членов побайтно равны118.
Точный118 engine dce960bd… и PE6992349e… сохранены в engine-before119.lib и
normal-before119.bin. Baseline033 сохранён; отсутствие old082 snapshot не исправлено.

Own RF_Online.bin406b400eca46385e7c436e5beca1275e8a519a9b4794c3bf9fa49d362b7933c4,
2225664bytes,x86/base400000/entry167320;182client/20kernel/70facade/unresolved0,
без CharacterMR и /FORCE. Свежие map2692/330/canonical bytes, ANI/BBX consumers,
own startup/contracts/window/device/existingCreate1 проходят. WinMainb98b0,
afterCreateb9a24. Старые receiver/aim/hover/texture649/Character/bulk suites
исторические и не повторялись без причины. Число scalar observations не является
процентом готовности, количеством AI вызовов или полной приёмкой.

## Остаётся

Control writer7E2AD0 и его игровые activation/input состояния; настоящий timer
producer/отрицательный toggle/переменный игровой dt; Empty/INS camera variants.
Новый native sway API пока имеет ordinary stop consumer, но не весь start/control
gameplay consumer. Full camera/movement/Character/special effects ещё не приняты.

Полный кадр мира/lighting/compositing/trajectory/quality/blur/device reset/shadow/
render-targets/independent texture flag8 и все прежние client-acceptance gaps.
Не приняты arbitraryFP/NaN/zero-heading/modulo0/overflow/OOM/privateABI,
CRT global RNG interleaving и старые трансцендентные функции на всём домене.
M6/M6F/M7/M9 открыты. Далее120: реальный world frame/camera timer/control/light;
не повторять уже доказанную metadata-only проверку quake.
