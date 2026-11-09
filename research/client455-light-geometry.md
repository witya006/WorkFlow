# Световая геометрия BSP — участок121

2026-11-09. PARTIAL M6: перенесены выбранные подтверждённые отличия обычного и
магического света. Это не приёмка полного renderer, мира или клиента.
Текущий gate: `inventory/client455-light-geometry-checkpoint.json`.

## Подтверждённый объект исследования

Два закреплённых PE32 x86, preferred base `0x400000`:

- primary SHA-256 `b1b5febf0d0394712e2322350e19dafe60742e8642697b93cfb89135bac1fd8b`;
- secondary SHA-256 `46528aac20499e3b3928d58658d7e0cefe26feba7cd193796d5cfbf7a2bbc558`.

Полные тела12 функций совпадают между ними:7 новых asm/712 инструкций и
5 повторно использованных asm/1013 инструкций из точного raw120. Всего1725.
Для каждого asm проверены страницы<=120, реальные числа строк, уникальность и
полнота. Pcode выбранных функций получен полностью; остальные поисковые pcode
в raw не объявлены полными доказательствами. Новые bounds/RVA/body hashes и
декодированные прямые calls хранятся в `client455-light-geometry-reference.json`.

| RVA | Назначение подтверждённого тела |
| --- | --- |
| `0x4fe980` | Обычная световая геометрия |
| `0x4fec90` | Магическая световая геометрия |
| `0x4fdca0` | Копирование world и inverse, по64 байта |
| `0x4f66b0`, `0x4f67d0` | Инициализация и constructor BSP |
| `0x4fc230` | Подготовка8 углов BBox и ограничение списка leaf |
| `0x4fbad0`, `0x4fbb60` | Ветвление и рекурсивный обход leaf |
| `0x4bbed0` | Включающий границы тест точки в short BBox |
| `0x4eaf60`, `0x4eb040` | Два проверенных caller setter матриц |
| `0x4c4ec0` | Создание используемой декларации вершин |

В target world находится в CBsp+372, inverse — в+436. Setter выполняет два
`rep movsd` по16DWORD, не вычисляет обратную матрицу. Инициализатор вызывает
identity для обоих. Найдены12 xref-caller кандидатов; у двух выше полный
body/asm и прямой CALL проверены. Имена классов остальных wrappers и вся цепь
игровых владельцев ещё не приняты. Поиск смещений ограничен диапазоном BSP;
он не доказывает отсутствие других writers или alias-записей.

## Что перенесено

Обычный свет: максимум128 leaf, signed leaf→unsigned проверяется с mLeafNum,
Attr0x10 исключается, уникальные face ID учитываются до5000, в том числе face
с0..2 вершинами. Fan triangulation, цвет0 и stride16 сохранены. Flush после
целого треугольника при3000 вершинах; остаток отправляется в конце.

Магический свет: проверяется ширина только поX<=1000, обе конечные точки BBox
внутри root node1 включительно, полностью вырожденный BBox отклоняется.
Не добавлены проверки шириныY/Z: target повторяет сравнениеX. Максимум256 leaf,
Attr0x30 исключается, NormalY должен быть>0. Shared seen table насыщается на
индексе2999 с перезаписью последней записи: вытесненный ID может появиться
повторно. Flush после целого треугольника при>=2000, фактическая полная порция2001.

Оба метода используют собственную world матрицу BSP и настоящую COM-декларацию:
stream0/offset0 FLOAT3 POSITION0, offset12 D3DCOLOR COLOR0, END.
Она создаётся обычным путём устройства и освобождается при его teardown.
Путь отказа CreateVertexDeclaration в source возвращает HRESULT; эквивалентность
всей target Error/OOM цепи не заявляется.

Source расширяет свой CBsp двумя матрицами на128 байт. Это поддерживаемое
source-owned хранение, не наложение на target offsets или privateABI-клон.
Единый header принудительно подключён ко всем engine/client consumers.
Поэтому пересобраны все67 engine TU и182 клиентских TU с20 kernel objects.
Функции draw/create/release удержаны обычной PE по MAP. Setter доступен source
и проверен в lab, но игровые transform producers ещё не восстановлены.

## Проверка

`work/m9/cf87be57/light-geometry-001`:33 воспроизводимых небольших случая.
Настоящие методы CBsp вызываются из полного собственного набора182 клиентских
объектов. На время CPU-примеров документированные DrawPrimitiveUP/SetTransform/
SetVertexDeclaration собственного D3D9-устройства перехватываются для записи,
после чего vtable восстанавливается. Это не запуск и не перехват входного455.

Независимый Python oracle сравнил все1580880 байт реально отправленных вершин,
все границы порций, фильтры, дубли, polygons0/1/2/3/4/5/255, leaf caps128/256,
face cap5000 и saturation3000, ширину1000/1000.25, только высокуюY, выход изroot,
разные world/inverse, identity и независимость двух владельцев. Настоящие
GetDeclaration и обычный teardown подтвердили создание/освобождение COM owner.

`work/m9/6047792e/world-frame-001`: настоящая Bellato,76 операций очереди,
16 измерений OS clock с обоими знаками30fps, архивный прицел и оба вида света.
Все три световых прохода: bind/ValidateDevice S_OK,1pass,CULL3,ZFUNC4.
Пять GPU кадров просмотрены и побайтно равны соответствующим120. Base==clear;
от clear отличаются151256 байт magic,146637 regular,646571 FX.
Это подтверждает сохранение выбранного identity-world примера, не parity с
запущенным455. Сохранены6 штатных texture warnings; ничего не подавлялось.

Свежие карты2692 проверки/330 geometry cases/110 maps/canonical bytes PASS;
обычные ANI/BBX consumers PASS. Точная новая PE прошла imports/decoded entry,
startup sound1, contracts, window/device и существующий Create→1.
Обработанные first-chance exceptions сохранены. Это не полный bootstrap/auth.

## Сборки и сохранность

Engine67/14 derived SHA-256:
`12534d28dfeccda98c5e2cdffecc6621ffde7b3a95810501f2a513f01911e810`.
Own PE SHA-256:
`933c276a79a6dce22677bb9b09aefef07f5b8e062b6f146aff770d878fe85df3`;
2226176bytes,x86/base400000,entry RVA167630,WinMainb98b0,afterCreateb9a24.
182 client/20 kernel,unresolved0,без CharacterMR/FORCE.

Точные120 engine7c828f77… и PE0806b113… сохранены в engine-before121.lib и
normal-before121.bin; отчёты — `artifacts/client455-progress/*-before121.json`.
Новый общий header вызвал более широкие COFF отличия:8 members byteequal,
24 отличаются только timestamp,35 — другими payload bytes. У19 отличаются
runtime sections либо сырые relocation records; это не утверждение, что у19
изменилось поведение. Нельзя писать «изменились только3 объекта» без отдельной
нормализации символических relocations/debug/type metadata. Точные списки в audit.
Baseline033 сохранён; ранее отсутствующий082 snapshot по-прежнему gap.

IDA `bec9ad05` saved/closed; после закрытия list0. Raw/session:
`artifacts/client455-progress/light-geometry121-reference.json` и
`light-geometry121-session.json`. Оригиналы и серверные файлы не изменялись.
Старые CPUquake/explosion/texture/receiver/Character/159k suites не повторялись;
их evidence историческое, свежие world queue/clock отдельно указаны выше.

## Открытые вопросы и следующий участок122

Полные ILevel/Empty/INS и игровые владельцы world/inverse, oblique leaf recursion,
invalid IDs/NaN/все FP режимы/CRT/reentry/concurrency остаются открытыми.
Также full projection/sky/alpha/shadow/device lost/reset/recreate/error,
trajectory/quality/blur/advancedFX/independent texture flag8 и все прежние
client-acceptance gaps. M6/M6F/M7/M9 OPEN.

Далее проверить реальные transform owners по ctor/vtable/callers, затем
подключить подтверждённые world/inverse writers к ordinary owner. Не придумывать
ILevel/INS layout по именам и соседству. Геометрия света не закрывает всю
подсистему BSP или renderer. Сохранить исправление120 ordinary current-view;
предыдущая view принадлежит INS, ошибочное утверждение119 отозвано.
