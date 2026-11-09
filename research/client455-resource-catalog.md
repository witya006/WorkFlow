# 141: штатная загрузка Resource.edf

2026-11-10. **PARTIAL, M6 открыт.**
Gate: `inventory/client455-resource-catalog-checkpoint.json`.
Команда: `scripts/Invoke-Python.ps1 scripts/checkpoint_client455_resource_catalog.py`.
Перенесена ветка ресурсов персонажей. Полный bootstrap и экран выбора не приняты.

## Подтверждённый контракт

Две закреплённые x86 PE/base400000:
primary SHA `b1b5febf0d0394712e2322350e19dafe60742e8642697b93cfb89135bac1fd8b`,
secondary `46528aac20499e3b3928d58658d7e0cefe26feba7cd193796d5cfbf7a2bbc558`.
Полностью прочитаны7 функций/934 инструкции/108 положительных блоков CFG.
Все реальные CFG regions, включая вынесенные EH tails, совпали в обоих бинарниках.
Не считать размер функции IDA непрерывным диапазоном при наличии chunks.

| RVA | Роль |
|---|---|
| `0x1e7be0` | Порядок общего bootstrap; в этом этапе перенесена только Resource-ветка |
| `0x2079c0` | Bone records, проверка отсутствующего player bone |
| `0x207cb0` | Mesh parent/default/model branches, проверка player skeleton |
| `0x2081c0` | ANI records и event metadata |
| `0x208550` | Внешний цикл девяти групп |
| `0x208490` | Конструктор84-byte event metadata |
| `0x208920` | Строковый find helper |

Raw: `artifacts/client455-progress/resource-catalog141-reference/session.json`.
IDA731ffc14 сохранена/закрыта,list0. Входные EXE не исполнялись.

Существующие legacy rows260/328/244,девять групп и84-byte ANI metadata уже
совместимы в проверенном участке. Они сохранены; новый формат для них не выдумывался.
Добавлены недостающие проверки455:

- `_access` failure и case-sensitive find `"/character/player/bone"` со signed result>0:
  путь с совпадением в позиции0 и отсутствующий non-player bone не входят в fatal-ветку;
- для явно указанного player parent ожидаются30/25/29/38/30 частей по ID0..4
  и длина первого имени mesh5; default parent-1 и model parent-2 идут своими ветками;
- при ошибке shape сохраняется обработка остальных mesh,после цикла идут log/
  grade>=2 dialog и quit request3000ms. Полная эквивалентность dialog/quit policy
  зависит от оставшихся UI/MainApp потребителей и не принята.

Перед штатным циклом добавлен bounded preflight payload/строк/положительных
event counts>10. Это собственная защита unsafe domains,не доказательство поведения
target на повреждённых файлах. Исправлен собственный GetResourceList accessor,
в котором отсутствовал return;он проверяет границу9. Остальные legacy getters открыты.

## Реальный каталог и исполнение

| Группа | Bone | Mesh | ANI |
|---|---:|---:|---:|
| 0 | 5 | 7079 | 2116 |
| 1 | 473 | 472 | 6960 |
| 2 | 40 | 40 | 480 |
| 3 | 17 | 17 | 122 |
| 4 | 726 | 696 | 4894 |
| 5 | 0 | 1988 | 1169 |
| 6 | 6 | 192 | 852 |
| 7 | 0 | 0 | 2239 |
| 8 | 0 | 0 | 40 |

Итого1267/10484/18872,30623 строки. Все raw rows проверены независимыми
Python fingerprints после ожидаемой мутации model parent-2→own ID.
Actual normal manager зарегистрировал1267 bones/10483 meshes/18872 ANI.
Единственный skip:group4/index20483,parent20483,
`CHARACTER/NPC/MESH/NEUTRALA_WEAPON_003.MSH`;parent ID отсутствует в каталоге.
Это соответствует подтверждённому continue до AddMesh.

Пять настоящих player BN загружены,shape/count/name проверены. Реальная player ANI
загружена из RFS: `ACCRETIA_COMBAT_ATTACK_DAXE_BOTTOM_01_00.ANI`,ID1090849056.
Остальные ANI здесь регистрируются с метаданными;все18872 файла не исполнялись.
Owner teardown проходит. Это full-object probe штатного менеджера,не обычная
авторизованная сессия и не визуальная приёмка экипированных персонажей.

Первая ошибка probe была его неверной нормализацией имён костей:character manager
сохраняет регистр и создаёт отдельные записи,animation manager нормализует имена.
Исправлен oracle: проверяются порядок/исходные имена/ID всех bones,а не ложная
case-insensitive dedup-модель. Product manager под ошибочный тест не менялся.

## Исходные ресурсы и место

Проверена часть ссылок каталога:все bone/связанные BBX и поиск выбранной доступной
ANI для каждой группы. Учитывается target RFSINFO/DATA lookup;7 members найдены
в архивах. После этого1120 проверенных ссылок не разрешились:503BN/592BBX/25ANI.
Это не полная опись всех assets и не доказательство,что каждая отсутствующая ссылка
обязательна для игрового сценария. Каталог может содержать неиспользуемые записи;
их назначение и fallback требуют проверки. Пять player BN присутствуют.
Полные списки и хеши — `inventory/client455-resource-catalog-reference.json`.

1668 assets/81,007,124 logical bytes staged через shared pool;5 мелких private files.
На первой подготовке добавлено53,117,239 pool bytes;повторный успешный run добавил0.
Расширены immutable suffixes BN/BBX/ANI/MSH/RFS. Связей с originals нет;
весь установленный клиент не копировался. Старые каталоги не удалялись.

## Обычная собственная сборка и остаток

Own PE SHA `b3f769a9b551a81099ca0ef01b92ac96b47bc5048d6ea9594e21a56a97d8d00c`,
x86/base400000/entry170760/2272768bytes.182client/20kernels,build/link0,unresolved0.
Engine137 SHA708c892e60c3bf7457389b40ac24b9a466958c9d232d9efaf497d1ac3232b870 unchanged.
Required normal consumer proof обновлён. Fresh WinMain/Miles/providers и обычный
Login проходят:frame70/3219ms/640×500,Renderreturn/exit observed,no fatal.
PNG3de508af… просмотрен:lobby/ожидание,лишние панели скрыты;selection не показан.
Account140 suite не повторялся;его точная PE/отчёты сохранены before141,49files.

Следующий142: оставшиеся bootstrap data owners,начиная с ItemCash/ItemSet/Item47
и локализации;нельзя интерпретировать455Item как старые C++ records. Затем character
tables/class tiers/appearance и обычный выбор→мир. Все прежние gaps сохранены.
Оценка остаётся25%(20–35%),0/12 полностью принятых областей,M6/M6F/M7/M9 OPEN.
