# Обычная полоса прокрутки455 — участок065

2026-11-06. Заменены обычные `CGUIScrollbar` header/body и добавлен составной
`CGUIScrollbarButton`. Перенесены размеры/позиции, диапазон, pixel snapping,
кнопки, удержание, перетаскивание и отпускание. Эти классы уже используются
полной клиентской сборкой. Варианты EX/Var и весь родительский input pipeline
ещё открыты; это не приёмка полного scrollbar family или клиента455.

Эталон x86/base400000 SHA-256
`b1b5febf0d0394712e2322350e19dafe60742e8642697b93cfb89135bac1fd8b`;
backup `46528aac20499e3b3928d58658d7e0cefe26feba7cd193796d5cfbf7a2bbc558`.
23 диапазона функций, два vtable prefixes и divisor2 совпали между pins.
Сохранены15 полных assembly dumps. Собственные IDA bfcf8ee1/9775776a закрыты
с сохранением. Входные EXE не запускались.

| RVA | Подтверждённое поведение |
|---|---|
| 2389F0/238B40 | Составной thumb: три image objects, пары44/47,45/48,46/49 |
| 238BE0/238E30 | Caps+повтор одной строки середины; минимум6×18 |
| 238EE0/239270 | Auto thumb включён, minimum20; setter ограничивает minimum |
| 2392F0/239590 | Layout/amount и линейный размер thumb |
| 239860/23A130 | Track length вычисляется заново; позиция через signed32 product |
| 2398F0/239EC0 | Кнопки/удержание/drag/release; свободный pixel position |
| 239E50/23A0D0 | Pressed mode, queued scroll event и обновление времени |
| 23A1A0/472B70 | x87 snapping/float spill и CVTTSD2SI int32 на SSE2 |
| 2269A0 | UV middle strip: source row2 и одноэкранная строка |
| 4CFF90 | SetFrame ограничивает отсутствующий кадр последним допустимым |

## Геометрия и ввод

Auto thumb использует оставшийся размер после стрелок минус total amount,
затем minimum, а не пропорциональную формулу viewport/content. Минимум
составного thumb —6×18. Поэтому известный helper7B4E30, запрашивающий5×18,
фактически получает ширину6; участок062 ещё использовал обычную legacy кнопку.
Minimum20 по умолчанию не означает автоматическое исправление слишком короткой
панели: track может стать нулевым или отрицательным. Эти области не скрыты.

Track length читается из текущих размеров при каждом расчёте. UpdateBar
сначала умножает current*length как signed32 с wrap, затем делит на total.
Ручная смена thumb size не обязана сразу менять его позицию. Смена total
ограничивает current через общий SetAmount. При total0 thumb удаляется только
если число children равно3; дополнительный child меняет это поведение.

CalcCurrentAmount повторяет порядок x87: int→double для total/distance,
деление/умножение, float spill, затем helper conversion. На поддержанном
SSE2 host __ftol2_sse использует int32 CVTTSD2SI, а не общий int64 cast.
Сохранены modulo/half threshold и unordered upper-half branch для small range.
Проверены также signed-product overflow и float→int32 overflow с последующим snap.
Полные non-SSE2/unmaskedFP/numeric/error domains этим не сертифицированы.

Stroke читает часы и отправляет событие, которое читает часы ещё раз. Repeat
сначала проверяет elapsed, затем запрашивает новое время для расчёта шага;
умножение elapsed*unit выполняется с DWORD wrap. Source clock provider по
умолчанию вызывает timeGetTime; replay provider используется только в probe
и восстанавливается после неё. Порядок запросов и переход через FFFFFFFF проверены.

После движения по track или drag направление сравнивается с current уже после
SetAmount. Поэтому допустимое движение вверх может отправить DOWN31. Drag
сохраняет свободную pixel position внутри того же snapped amount; release
возвращает thumb к выровненной позиции без нового события, если amount не менялся.
Scroll events прошли через настоящую клиентскую очередь и IScrollObserver.

Legacy0.7 container не имеет полного455 parent event bubbling/show inheritance.
В этом переносе arrows получают явного observer, а новый thumb наследует show
своего parent. Это собственный адаптер к базе0.7, не утверждение о таком же
устройстве эталона. Полный parent input system остаётся открытым.

## Составной thumb и реальные ресурсы

Верх/низ используют кадры44/46 и47/49, middle —45/48, common action2. Середина
повторяет source row2 по одной экранной строке. Draw сначала рисует container,
затем thumb ещё раз — этот порядок сохранён.

В проверенных Korea/Russia common.spr у action2 **44 кадра**, то есть0–43.
Defaults44–49 отсутствуют. В455 SetFrame ограничивает запрос последним кадром,
поэтому составной normal/pressed на этих данных дают одинаковый кадр43.
Source сохраняет это ограничение, включая размеры выбранного кадра.
Файлы ресурсов не изменены; само это наблюдение не доказывает их версию и не
доказывает использование default composite skin в обычном игровом окне.
Реальные callers/skin overrides и resource parity остаются отдельной задачей.

Для проверки всех шести частей создан небольшой собственный synthetic SPR
в ignored lab. Normal caps красный/синий, middle row2 зелёная; pressed —
жёлтый/пурпурный и голубая row2. Остальные middle rows серые. Probe выбирает
POINT sampling только для этого fixture, проверяет фактический пиксель row2
и восстанавливает sampler state. Это тест алгоритма, не новый игровой asset.

Пять viewport640×480 кадров на профиль просмотрены: реальный plain bar,
реальный clamped composite normal/pressed и synthetic normal/pressed.
Korea/Russia кадры совпали по SHA. Изменённых пикселей478/279/279/478/478;
real normal/pressed совпали, synthetic normal/pressed различаются.

## Сборка, проверки и продолжение

Own probe SHA-256
`05e4466e3f8100129a1f40045cdf082d185a73c06b3ac752f9ac9550478fec9a`,
entry RVA E4020, natural exit0 для Korea/Russia. Проверены asymmetrical arrows,
vertical/horizontal geometry, minimum/manual/auto size, snapping boundaries,
NaN/overflow выбранных ветвей, clocks/wrap, queued callbacks, direction/order,
grab/drag/release, count3-removal и реальные/synthetic GPU images.

Production SHA-256
`d38d74e09a7b11801abec69ff90804ee89c6c5fa12818a1f55311b61414229a8`,
x86/base400000/entry14E350,2030080байт.182client/20kernel/26facade TU,
0unresolved; нормальные CUnity/CAnimation passed, engine archive неизменен.
Generator повторно создал тот же manifest/preparation.

Затронутые TextBoard/metrics/font/modal Korea/Russia и tutorial-board probes
прошли для текущего link digest. Точная новая PE прошла WinMain/TCP fixture/
engine/D3D/Character/existingCreate1 и остановлена до игрового цикла.
Это не аутентификация и не полноценная игра. Старые bulk suites не повторялись.
Gate `inventory/client455-scrollbar-checkpoint.json` — PARTIAL.

Следующий участок066: ScrollbarEX/Var, их callers и оставшиеся parent input
контракты; decomp уже сохранена в scrollbar-more/helpers065. Затем реальные
message sizing/rich callers, весь briefing и actual Tutorial/fourstage.
GetMinSize/SetScrollSpeed compatibility wrappers, остальные skin/alpha/clipping,
private ABI/lifecycle/unsafe/OOM/FP gaps и полный M6F/M7/M9 остаются открытыми.
