# Light direction131 — преобразование света LitGrass

2026-11-10. **PARTIAL M6**. Обычный CEntity теперь использует подтверждённые
455 affine inverse/transform и тело нормализации направления света. Для конечных
неотрицательных аргументов sqrt восстановлена политика PC/RC старого CRT.
Полный CRT, игровые владельцы flag40 и полная приёмка клиента остаются открытыми.

Gate: `inventory/client455-light-direction-checkpoint.json`.
Повторяемая проверка: `scripts/Invoke-Python.ps1 scripts/checkpoint_client455_light_direction.py`.
Runtime130 исторический; его статические доказательства и изображения сохранены.

## Что подтверждено

Primary455 SHA-256 `b1b5febf0d0394712e2322350e19dafe60742e8642697b93cfb89135bac1fd8b`;
secondary455 `46528aac20499e3b3928d58658d7e0cefe26feba7cd193796d5cfbf7a2bbc558`.
Оба x86/base0x400000. Десять полных assembly функций:315 инструкций основной
цепочки и96 инструкций CRT context. Одиннадцать диапазонов, включая общие
CRT tails, совпали между обоими бинарниками. Проверены все положительные CFG
block starts, уникальность инструкций и завершение страниц размером не более100.
Пять основных декомпиляций полные. Hex-Rays не декомпилировал CRT start_3;
для него используется assembly, полнота его pcode не заявляется.

| RVA | Подтверждённая роль |
|---|---|
| 0x4bfbc0 | Affine inverse, guards0.001, порядок cofactor/determinant и spills |
| 0x4c0980 | xyz transform с сохранением x87 intermediates |
| 0x11d5d0 | Нормализация light vector, x*x+y*y+z*z и double spill sqrt |
| 0x1db70 / 0x1db90 | Два float sqrt wrappers |
| 0x474514 / 0x47451d | CRT sqrt entry и обработка обычных/специальных аргументов |
| 0x488e05 | Загрузка double/специальных значений |
| 0x488dd5 | Временный CW: `(callerCW & 0x300) | 0x7f` |
| 0x488dec | CRT NaN conversion context |

Raw/session: `artifacts/client455-progress/light-direction131-*.json`.
Сессия1ff3df20 сохранена и закрыта; после закрытия список сессий пуст.
Входные EXE не запускались. SHA-256 raw и диапазонов закреплены в reference JSON.

## Изменение исходников

`client455_light_direction.inc` подключён к настоящему renderentity unit.
Вместо D3DXMatrixInverse используется существующий RF455_MatrixInvert.
Он уже был восстановлен ранее: повторная реализация не создавалась.
Исправлена неточность отчёта130: Vector3fTransform в рабочем source уже вызывал
точный RF455 x87 backend.131 использует его прямо и заменяет отдельный normalizer
геометрии на правильную нормализацию light vector. Геометрический normalizer
не менялся: это другая цепочка с другим порядком операций.

Тела inverse485bytes, transform132bytes и normalizer136bytes в текущей собственной
PE совпадают с455, кроме проверенных relocation:epsilon0.001 и CALL к выбранному
sqrt backend. Такие же тела проверены в CPU probe. Это не означает идентичности
всего CRT вызываемой sqrt-функции.

CRT временно сохраняет точность PC вызывающего кода, маскирует исключения и
выбирает nearest rounding для FSQRT. Затем восстанавливает исходный CW,
и float wrapper округляет результат в binary32 уже с исходным RC. Эта политика
восстановлена для выбранной конечной области. Обычный fsqrt с неизменным CW
не воспроизводит её во всех12 режимах.

Как в455, translation inverse зануляется до преобразования направления.
Возврат inverse игнорируется. При отказе affine guards target потребляет
неопределённые stack bytes; fallback не добавлен. Проверка direct guards
доказывает отсутствие записи в output, но не принимает поведение такого caller.

## Проверки и ограничения

- 240 CPU случаев:96 normal vectors,96 affine directions и48 отказов guards.
  PC24/53/64 × четыре режима округления. Независимый Fraction oracle воспроизводит
  округление каждого x87 шага и sqrt через целочисленное сравнение midpoint.
  Выбранные конечные outputs совпадают побитно; нулевой вектор сохраняет
  indefinite NaN вместо придуманного направления. CW и баланс x87 stack проверены.
- 72 настоящих indexed LitGrass draws:шесть world transforms ×12 FP modes.
  Повороты, неравномерный масштаб и shear. Константы shader19.xyz совпали
  побитно с независимым расчётом из фактических world/light inputs.
  В draw callback подтверждены stride36 и настоящий300-byte LitGrass1 shader.
- Пять исходных fixed/Grass/LitGrass кадров и25 world/sky/weather кадров получены
  заново. Raw и PNG побайтно равны просмотренным130. Сохранена явная provenance
  повторного использования просмотра; новый просмотр изображений не заявляется.
- Нормали5328 vertices,8 material states,3 bump times,76 world queue operations,
  16 clock samples,90+27 fade,60 sky profiles/36 material cases,
  867 lighting colors/3 aggregates/27Mie и90 weather cases проходят.
- Свежие короткие ANI/BBX и точная PE:imports, WinMain, sound1, window/device,
  startup contracts и existing Create1 проходят. Полный игровой цикл не принят.

Обновлён только payload renderentity:1 изменённый/66 побайтно равных engine objects.
Shared headers не изменены,182 клиентских/20 kernel объектов сохранены; повторная
полная компиляция не требовалась. Engine SHA-256
`9f33478968c77b1a81acd031c50acd2175e7e37d129a067d16257e810175011e`.
RF_Online.bin x86/2255872bytes/base400000/entryRVA16C9B0:
`d1738f4e7516f33867c9fa7d3dc3219e684843dc49fec456e01eaa96783496b5`.
Unresolved0; no CharacterMR/FORCE. Точные130 engine/PE/MAP/rsp/reports/shared
camera+vertex headers сохранены до изменений. Ignored не означает backup.

Полный CRT matherr/errno/precision-error dispatch, немаскированные исключения,
все NaN/Inf и status flags ещё не перенесены и не приняты. Геометрический
decompressor/GetNormal имеет отдельные FP gaps. Другие открытые области:
игровые writers flag40, material runtime extra8/capacity, shader caps/failure/reset,
unused shader register lanes, lensflare/localfog, INS/Planet, world/camera/UI,
stages/auth/protocol/Character/gameplay и остальная client-acceptance matrix.
M6/M6F/M7/M9 OPEN. Серверы и оригиналы не изменялись, публикации нет.
