# ANI и загрузка Character455

2026-11-05. Клиентский source unit M6. Проверенный участок не закрывает M6/M9.
Серверные файлы и исходные установки не изменялись. Входные EXE не запускались.

## Основание

Два закреплённых x86 PE: current SHA-256
`b1b5febf0d0394712e2322350e19dafe60742e8642697b93cfb89135bac1fd8b`, backup
`46528aac20499e3b3928d58658d7e0cefe26feba7cd193796d5cfbf7a2bbc558`.
Image base400000. Полные16 диапазонов и SHA каждого —
inventory/client455-animation-reference.json. Тела одинаковы в обоих PE.
IDA работал на копии backup; owned45964631 закрыта/save. Raw инструкции,
декомпиляция, xrefs и worker/factory справка — artifacts/character-animation455/.

| RVA | Подтверждённый контракт |
|---|---|
| 532380/532690 | Animation record284: ctor и dtor |
| 53ACD0 | Сырой ANI RFS→loose, cumulative DWORD1189608 |
| 53AE20 | Максимум WORD102 всех дорожек, проверка allocation extent |
| 532400 | LoadAnimation, sticky loading4 |
| 53C050/53C1F0 | Применение дорожки/разбор и привязка ANI |
| 5352A0/535320/5351A0 | Две синхронные ветки extension dispatch и suffix |
| 5238A0 | Character dispatcher, parent/no-parent ветки |
| 51F150/51F250 | Лимит faces и MESH08/null gate |
| 5316C0 | MatchAnimation: model load→animation load→attachment→672=160 |
| 533280/531310 | Factory и unsafe direct-free wrapper, справка, не реализация |

## Восстановленная реализация

scripts/native/client455_animation.{h,cpp}, библиотека RFClient455Animation.lib,
x86/MT/O2/Gy/W4/WX. Отдельный флаг RF_CLIENT_455_ANIMATION, defaultOFF в CMake;
проверенный драйвер сборки включает зависимость. Legacy D3D8 consumers ещё не
переключены; несовместимые layout268/528/532 и272/532/536 нельзя cast-ить.

ANI: BYTE0 — количество, BYTE1 игнорируется, первая дорожка с2. Header140,
затем четыре WORD count и массивы с шагом20/16/16/8. WORD100 — active,
WORD102 — frame maximum. Семантика ключей/интерполяция здесь не заявлена.
Нулевая дорожка допускает один байт ввода, logical consumed2. Сохраняются
неиспользуемые байты и trailing; Python decode/encode lossless.

Record284: name5[256], ID264, owned raw268, descriptor cookie272, max276,
extra280. Ctor пишет только0/4/5/264/268/272/276/280; остальные байты сохраняются.
Dtor free/null268, cookie272-4,280; flags/max/name/id сохраняются.
Descriptor32 — четыре DWORD count/borrowed pointer. В mesh5095 current,
5099 previous; освобождаются только descriptors, ключи принадлежат ANI owner.
Завершать mesh lifetime до уничтожения используемых ANI. Внешние API
со старым heap не смешивать: `_msize` и free используют один собственный /MT provider.

Применение выбирает первый точный strcmp mesh name. Active: старый current
копируется в previous, прежний previous освобождается; новый current получает
новый descriptor. Inactive освобождает current, сохраняет previous; model676
только растёт. Общий max ANI учитывает также inactive/unmatched дорожки.
Если current пуст, новый active не удаляет существующий previous.

Raw RFS импорт увеличивает DWORD counter на `_msize`, loose на размер файла;
переполнение DWORD сохраняется, decrement при release нет. RFS читается раньше
loose, short archive member допускает fallback. Suffix без точки пропускает
первый символ, поэтому XANI принимается. ANI loading4 остаётся1 после failure,
следующий Load возвращает true даже при loaded0/rawNULL. MatchAnimation также
воспроизводит это false-success и сбрасывает model672=160 после null attachment.

Character dispatcher: prerequisite загруженного external parent проверяется до
loading264. При parent используется MSH-only raw reader и MESH08 gate; без parent
используется legacy extension importer, поэтому unparented MESH08 не получает
новый route. Успех оставляет loading1/loaded1. Ошибки разных веток сохраняют
разные флаги и lifetime: parent validation failure уменьшает loading, удаляет
parsed model, но теряет raw buffer. Тест сначала наблюдает оставшуюся allocation,
потом отдельно освобождает её своим harness; эта очистка не является поведением455.
Без parent аналогичный отказ оставляет loading1 и освобождает parsed model.
Лимит `3*WORDfaceCount >64000` сохранён.

## Проверка

- 22 настоящих companion ANI для11 BN/MESH08 пар и5 синтетических файлов:
  27files/1062tracks, lossless roundtrip;6 Python tests.
- Native14513CPU/15181D3D9HAL checks, включая PAGE_NOACCESS truncations,
  whole record284 ctor/dtor state и ordered frees, exact32byte descriptors,
  inactive/duplicate/first-match, max monotonicity,2 allocation failures,
  RFS/loose/accounting/wrap/short fallback/extension/sticky retry/type guards.
- 22 MatchAnimation по настоящим ANI, исходная BN строится source dispatcher,
  дочерняя MESH08 — parent route;794 total parts,660 physical uploads,
  current/previous key pointers и counts сверены с независимым framing golden.
- Полный собственный RF_Online.bin выполняет те же15181HAL checks. Все13C APIs
  имеют actual UNDEF callers в test TU и source archive provider в map.
  Игровые DLL не загружаются, Dmalloc0, D3D/COM release0. Heap0 после явного
  наблюдения и отдельной harness-очистки одной reference leak.
- Текущие регрессии: legacy runtime14896, manager1138, Platform01/device69;
  прежние frame hashes равны. Normal180client/289modernCOFF/MT, lab187clientTUs.
  Normal runtime bytes равны предыдущему snapshot после исключения timestamps;
  новая библиотека в normal пока unused/stripped, это не runtime интеграция.

Все текущие PE identities/числа/хеши evidence —
inventory/client455-animation-checkpoint.json. Normal snapshot
artifacts/client-first-build/character455-animation; lab immutable копия в work/m9/.
Gate: scripts/checkpoint_client455_animation.py. Воспроизведение:
test_ani455.py → audit_client455_animation.py → build_client455_animation.py →
probe_client455_animation.py [--gpu] → prepare_client_build.py →
probe_client_character_build.ps1 [обычный/-HelperLab] →
probe_client455_animation_client.py → scoped regressions → checkpoint.
Python только через scripts/Invoke-Python.ps1.

## Границы и следующий шаг

Bounded read/status/type guards не идентичны AV/OOM/unchecked parse/partial
attachment/std::bad_alloc/exception unwind эталона. Tagged union безопасно
отклоняет ANI-as-ObjectData28 и MSH-as-ANI; такое reference reinterpretation
не сертифицировано. Guarded parser валидирует до attachment; повреждённый файл
может оставить другое промежуточное состояние. `_msize` padding не означает,
что неинициализированные байты неправильного файла доказаны эквивалентными.
Numeric arg в reference InitVertex log отсутствует: собственный код печатает
детерминированное количество, исходное undefined formatting не воспроизведено.

Factory533280 и async worker535450 изучены как зависимости, полный source
AnimationManager/worker lifecycle не реализован. Unsafe531310 освобождает raw
сразу после borrowed attachment — не переносить как нормальный owner route.
Логические контексты не доказывают полный private C++/STL/heap ABI. Примеры
companion filenames не доказывают runtime выбор ресурсов. HAL upload не является
рисованием анимированного персонажа или сравнением с запущенным эталоном.

Далее FrameMove523A40: определить состояние/тайминг и downstream transform,
key evaluator/pose/interpolation. Затем skinning/declarations/shaders и normal
typed consumers с настоящим455 D3D9 renderer. M6/M6F/M7/M9 открыты; M8 исключён.
