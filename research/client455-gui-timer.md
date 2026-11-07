# Таймер иконок — 098

2026-11-07. M6 PARTIAL, M6/M6F/M7/M9 OPEN.
Current gate: `inventory/client455-gui-timer-checkpoint.json`.
Только клиент; оригиналы/серверные файлы не менялись, входные EXE не исполнялись.

Обычный typed CGUIItem получил собственный RF455GuiTimer: состояние, запуск,
отдельное обновление, копирование, условный сброс при очистке, круговой индикатор
и подпись. Реестр MainApp передаёт запуск/сброс зарегистрированным копиям.
CGUISFItem и реальный Linker query используют новый timer для typed icons.
Это выбранная функциональная часть иконки; игровые cooldown/use handlers ещё
не восстановлены полностью. Stopfanout проверен сproduction objects,но пока
удаляется обычным linker как unused.

## Бинарная опора

Оба входа x86, image base0x400000:

| Вход | SHA-256 |
|---|---|
| current | b1b5febf0d0394712e2322350e19dafe60742e8642697b93cfb89135bac1fd8b |
| reference-backup | 46528aac20499e3b3928d58658d7e0cefe26feba7cd193796d5cfbf7a2bbc558 |

32 равных диапазона:29 функций/2791 инструкции, CW,pi и inline formats.
Полная выбранная assembly и внешние instruction windows закреплены хешами.
Raw: ignored artifacts/client455-progress/gui-timer098-reference.json.
IDA316a9b70 сохранена/закрыта, list0; запись gui-timer098-session.json.

| RVA | Контракт |
|---|---|
| 0x229730 / 0x229880 | ctor/reset, частичные записи vertices |
| 0x229920 / 0x229960 | start/update, wrapDWORD и signed remaining |
| 0x229a10 | подпись, строгие пороги и context geometry |
| 0x229d70 / 0x22a3c0 | радиальные треугольники, whole-rect clip |
| 0x21ad60 / 0x21ae10 | копирование timer/base selected fields |
| 0x21bc20 / 0x21bd10 | реестр start/stop; self/duplicate entries |
| 0x21bb80 | reset только активного timer при Empty |
| 0x21b590 | обычный GUIItem.Update вызывает timer.Update |
| 0x21b6b0 / 0x21b910 | разный порядок image/grade в normal/clip Draw |
| 0x21ce00 / 0x21cf00 | подпись через medium font, отдельный clip |
| 0x47bd90 / 0x22a390 | CRT default finite FPTAN и float spill |
| 0x72b128 / 0x6da958 | CW027f / double pi3.141592741012573 |

Decompiler ошибочно показывал квадрат tangent в629D70: использована assembly,
где результат tan умножается на half-width/height. Начальная гипотеза CW133f
отклонена после чтения настоящих байтов7f02. Восстановлен finite default CRT
path; CPU-selected SSEtan, FP exceptions/NaN/unsafe numeric domains не приняты.

## Подтверждённое поведение

- Start меняет timestamp/offset/started; offset-1 означает0,прочие LONG хранятся
  rawDWORD. Каждый элемент реестра читает clock отдельно; duplicates/self
  запускаются повторно. Нет рекурсивного fanout.
- Update использует DWORD elapsed с wrap, но remaining считает из signed32
  разности. Завершение проверяет unsigned elapsed>=duration, оставляет angle.
  Draw не читает clock и не обновляет state. Started хранится rawBOOL.
- Timer Reset очищает selected28 bytes; положение/show/vertices сохраняются.
  Ctor оставляет vertexXY нетронутыми. SetData копирует child и заново ставит
  позицию назначения. Empty сбрасывает только started timer; stopped remainder
  может остаться. Другие GUIItem children ещё не перенесены полностью.
- Пять независимых секторов45/135/225/315/360 рисуют оставшуюся маску.
  Частичный clip отвергает весь timer. Подпись проверяет собственный квадрат16
  сscale, независимо от геометрии timer.
- Подпись при0,60000,3600000 пустая. Для секунд floor(ms/1000)+1:45000→46.
  Менее10 — красная, остальные секунды — жёлтые, minutes/hours — белые.
  Context0/1/5,2/3,4 имеют разные offset/scale; unknown context оставляет
  часть outputs нетронутой, такой draw source явно не принимает.

## Проверки и ограничения

175 state cases,112 label cases,57 radial cases/171 triangles проверены независимыми
Python fixtures против production C++ objects. Границы включают clockwrap,
INT32/UINT32 divergence, sentinel-1/-2, строгие пороги, соседние float angles,
прямоугольные иконки и отрицательные координаты. Native дополнительно проверяет
ctorXY, реальный SetData/Empty/Update, typed derived GUI, original+2owned Linker
clones, registry duplicates/self с5 clock calls, actualtyped Linker query.

Просмотрено29 GPU кадров:6 timer,8 window,3 owners,3 metadata,9 icon.
Timer reset byte-equal idle. Старые23 кадра сравнены:11 изменились после
исправления нормального порядка image→gradeframe;12 byte-equal (glyph3,
metadataempty1,icon8). Исправление подтверждено455 assembly; это не reference
executable capture. Подробные delta counts/bounds — visual-review manifest.
092 повторён из-за конкретного риска layering/alpha/clip; неизменённые world/
audio/159k/093atlas/2013owner/SF1447/095manual suites не повторялись.

Новая RF_Online.bin: SHA-256
`d943ef46fdd2dcc700ad051502462fe056e7464eff7dcf7458ddc746f4cc0d21`,
2134016bytes,x86,entryRVA156570,WinMainb74a0,afterCreateb760a.
182client/20kernels/54facade TU,0 unresolved. Engine082 SHA неизменён.
OwnPE early/Create1,hotbar7/storage3/account и затронутые window/owners/metadata/
icons проходят. Create1 не является полнотой клиента.

Далее099: Linker cooldowncache501C30,actualuse/remove/swap/hoverhandlers,
liveSF/Animuscallbacks/lock/Macro35/Vending27/fullCItemBoard.Add/bootstrap.
FullGUIItem children/shake/copy-empty/lifecycle/privateABI и все прежние
Tutorial/Login/auth/game/renderer/client gaps обязательны. Общий процент не измерен.
