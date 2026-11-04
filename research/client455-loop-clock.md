# Время кадра 455: source и подключение к обычному клиенту

2026-11-05. M6 продолжается; M6F/M7/M9 открыты. Это восстановление поведения
таймера, без модернизации графики. Серверы и оригинальные файлы не изменялись.

## Эталон и наблюдения

PE x86, image base 0x400000. Основной SHA-256:
`b1b5febf0d0394712e2322350e19dafe60742e8642697b93cfb89135bac1fd8b`.
Backup SHA-256:
`46528aac20499e3b3928d58658d7e0cefe26feba7cd193796d5cfbf7a2bbc558`.
Восемь выбранных диапазонов равны в обоих файлах, хеши в
inventory/client455-loop-clock-reference.json.

| Назначение | VA | RVA | Размер |
|---|---|---|---|
| QPC с повтором при нуле/fallback timeGetTime | 8B3AE0 | 4B3AE0 | 4A |
| GetDuration | 8B3B30 | 4B3B30 | 30 |
| Переключатель 30 FPS | 8B3B70 | 4B3B70 | 5A |
| Переключатель 15 FPS | 8B3BE0 | 4B3BE0 | 5A |
| Общий хвост переключателя 7 FPS | 8B3C50 | 4B3C50 | 5A |
| Установка коэффициента времени | 8B3CB0 | 4B3CB0 | B |
| R3CalculateTime, включая переход в хвост | 8B3CC0 | 4B3CC0 | 16A |
| Get/set loop/real time и min FPS | 8B3E30 | 4B3E30 | 4F |

При первом вызове запрашивается QPF; при неуспехе frequency=1000. Сохраняются
frequency, float frequency, .001f, frequency/1000 и начальные QPC ticks.
GetTicks повторяет QPC при успешном нулевом значении; при первом неуспехе
возвращает unsigned DWORD timeGetTime. GetDuration делит signed wrapped QWORD
delta на signed QWORD frequency через x87 и только затем сохраняет float.
Сам elapsed update использует timeGetTime, а не QPC.

Счётчики количества вызовов и суммы миллисекунд — DWORD с переполнением.
Только при сумме >10 производится усреднение. Оба DWORD преобразуются x87 как
unsigned, без промежуточного float округления; деление на count и double1000,
затем float spill. Далее: ограничение maximum/negative, умножение на коэффициент
BF7368, float spill, накопление real time, обновление трёх переключателей.
Defaults maximum=1, scale=1, toggle signs=1 подтверждены .data обоих PE.

Коэффициент применяется и когда новое среднее ещё не вычислено. Поэтому при
scale!=1 повторно масштабируется уже сохранённый loopSeconds. Порядок сохранён.
Порог переключателя — float; вычитание использует double, равный расширенному
значению того же float. Сначала остаток сохраняется float, затем повторно
сравнивается с порогом и при необходимости обнуляется. При точном вычитании
равных значений в режиме round-down сохраняется отрицательный ноль.

Подтверждён xref установки scale в 8D5351 внутри 8D4E70. Декомпиляция показывает
ветку 0x0B; полная RTMovie dispatch/record семантика и её normal consumer пока
не восстановлены. Наличие setter не объявляется готовой системой роликов.

## Реализация и доказательства

scripts/native/client455_loop_clock.{h,cpp} содержит собственное состояние 96B,
получение ticks, полный выбранный update и duration. Это тип исходного кода,
не overlay приватного глобального layout 455. Численные операции с наблюдаемыми
spill выполняются x87. NEG toggle реализован unsigned, включая INT_MIN.

Сравнения также выполняются x87: целевой пример с отрицательным subnormal
0x80000001 при включённых SSE DAZ/FTZ воспроизвёл ошибку обычного C++ сравнения
и прошёл после исправления. Это отдельный regression case, не сертификат всего
пространства IEEE exceptional values.

client455_loop_clock_bridge.inc включён в рабочую копию commonutil.cpp под
RF_CLIENT_455_LOOP_CLOCK; исходная ветка сохранена под else. Патч воспроизводим
через apply_client455_loop_clock.py поверх проверенных compiler port edits.
Кодировки и переводы строк legacy файла сохранены. Старые публичные getter/setter
и R3CalculateTime используют единое source state; прежние OS-provider pointers
сохранены. RTMovie scale setter доступен, его script caller ещё открыт.

Normal R3CalculateTime действительно вызывает source RF455_UpdateLoopClock из
R3EngineMT. В commonutil.obj также есть source call из GetDuration; в normal PE
неиспользуемый duration удалён линкером. Это различие отражено в link report.

144 whole-state случая в 12 masked precision/rounding режимах проверены против
Fraction oracle, составленного по инструкциям. Проверены границы окна, unsigned
wrap/high counters, clamp/scale, повторное масштабирование, toggle/reset/NEG.
Отдельно — три provider сценария: QPF/QPC успех, fallback, повтор нулевого QPC;
два signed duration примера и один DAZ/FTZ случай. Component: 448 assertions,
без ошибок; DAZ/FTZ случай также выполнен через actual engine bridge.

В own entry полного клиента тот же набор проходит через настоящий R3CalculateTime
и существующий ptimeGetTime callback; дополнительные 9 проверок вызывают реальные
getter/setter/toggle API и CResObject. Связка clock→R3GetLoopTime→actor даёт кадр309
при dt=.03f/current160/speed1. Начальная QPC ветка детерминированно проверена в
компоненте; original process timer trace не снимался. Game DLLs не загружены,
Dmalloc balance=0. Normal WinMain и входной клиент 455 не исполнялись.

Scoped Platform01/device: 2 сценария, 69 assertions, прежние frame SHA,
errors/warnings/COM/Dmalloc=0. Это прежний D3D8 lab, не Character455 D3D9 acceptance.
Неизменённые большие ANI/texture/buffer/manager suites не повторялись.

Normal snapshot character455-loop-clock-final: 2451456B, entry RVA1BC450,
SHA `c2ea6d497a4fa2e6ad9aec32d61127a79efb0908b5d44db75a85ec3a588431e8`.
RF455_UpdateLoopClock RVA1AF700. Normal180+65+46=291modern x86/MT objects.
Lab191clientTUs, 5233664B, entry RVA89CC,
SHA `66e7d75f977031ecea45da0deb49c9c61e81feb6b14d17a1fff3a2831e82f0d3`.
Обычный runtime намеренно изменён; byte identity с предыдущей ревизией не заявляется.

Gate: inventory/client455-loop-clock-checkpoint.json. Raw MCP:
artifacts/character-animation455/elapsed-*.json; owned c215239f закрыта/save.

Не доказаны arbitrary NaN payload/signalling/unmasked FP exceptions, полный CPU/FPU
process state и независимая эквивалентность original scheduling/timer traces.
Открыты full actor/secondary binding/normal455ABI/AnimationManager-worker,
skinning/draw/shaders/D3D9 renderer и остальные области client-acceptance.md.

Воспроизведение через scripts/Invoke-Python.ps1: audit_client455_loop_clock.py →
build_client455_loop_clock.py → probe_client455_loop_clock.py →
apply_client455_loop_clock.py → prepare_client_build.py →
probe_client_character_build.ps1 [normal/-HelperLab] →
verify_client455_loop_clock.py [--lab] → probe_client455_loop_clock_client.py.
После scoped graphics/COFF/snapshot: checkpoint_client455_loop_clock.py.
