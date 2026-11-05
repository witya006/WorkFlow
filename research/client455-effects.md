# EFF: загрузка и применение в клиенте 455

2026-11-06, Asia/Yakutsk. Участок M6 номер039. В ordinary source facade
подключены binary EFF, registry/file lists, SetPartEffect/SetMeshEffect,
InitEffect и доступ к текущим particle/entity slots. Сценарий с настоящей DDS
и моделью проходит на D3D9. Полный клиент и полные particles не приняты;
M6/M6F/M7/M9 открыты.

## Эталон и контракты

Оба эталона x86, image base 0x400000. Current SHA-256:
b1b5febf0d0394712e2322350e19dafe60742e8642697b93cfb89135bac1fd8b.
Backup SHA-256:
46528aac20499e3b3928d58658d7e0cefe26feba7cd193796d5cfbf7a2bbc558.
15 основных диапазонов, три выбранных particle-consumer fragment и четыре
double literals закреплены с RVA/длиной/SHA в
inventory/client455-effects-reference.json. Диапазоны совпадают между эталонами;
отдельные EH/unwind chunks не объявляются полностью доказанными этим сравнением.
Raw decompile/disasm сохранены в ignored artifacts/eff455. IDA4a2e7cac закрыта
с запросом save; ответ saved=null. Входные EXE не исполнялись, серверные файлы
не менялись и для реализации этого участка не требовались.

| Контракт | VA | RVA |
|---|---|---|
| Binary EFF reader | 0x92B380 | 0x52B380 |
| Преобразование 176-byte record | 0x929070 | 0x529070 |
| Конструктор runtime record | 0x920E40 | 0x520E40 |
| Применение к mesh | 0x927040 | 0x527040 |
| Фильтр mesh имени | 0x9281A0 | 0x5281A0 |
| Применение файла | 0x9293D0 | 0x5293D0 |
| Reset mesh / model | 0x91C760 / 0x91F2B0 | 0x51C760 / 0x51F2B0 |
| Particle predicate mesh / model | 0x91C6D0 / 0x91FC00 | 0x51C6D0 / 0x51FC00 |
| Monster/Unit / item file lists | 0x92CD60 / 0x92CEA0 | 0x52CD60 / 0x52CEA0 |
| Animus caller, grade36 | 0x4572D0 | 0x0572D0 |
| Выбранные particle fragments | 0x7BC9B0 / 0x7BCEF8 / 0x7BD099 | 0x3BC9B0 / 0x3BCEF8 / 0x3BD099 |

## Формат и source представление

EFF состоит из записей с little-endian WORD длиной. Реальные длины 176 и172;
короткая запись дополняется до176, исходные bytes сохраняются для roundtrip.
Третий байт reader не проверяет. Строки начинаются с3/23/43/152: texture1,
texture2, directory, mesh filter. Исходный strlen может переходить границу
20-байтного поля. Это обнаружено на реальных файлах; собственный reader
ограничивает поиск концом176, не выдуманной границей каждого поля.

В source текст хранится в собственных современных std::strings; приватный
classic STL объект не приводится к современной библиотеке. 292-байтный numeric
view содержит подтверждённые draw/particle поля. Scalar bytes63..66 идут в
156..168, DWORD67→172, floats71→176 и75→180, flags79/80/81/82/83 в184/188/196/
200/204, bytes84..147 в208..271, float148→288, DWORD172→192.
Пустая строковая metadata и непрописанные opaque bytes имеют собственные
нулевые seeds; идентичность неопределённым исходным stack bytes не заявлена.

Registry: точное имя файла, затем ordered uppercase mesh filter. Пустой фильтр
применяется ко всем частям; более поздний подходящий именованный фильтр может
его перекрыть. Повтор file/filter заменяет запись, reload сохраняет другие
фильтры. Уже прочитанный prefix публикуется и при невалидном позднем suffix.
File-list ID первый выигрывает; reload дополняет список. Monster/Unit делают
access до проверки дубликата и пропускают отсутствующий путь; item список
сохраняет ID/path/mode и при отсутствующем EFF. Токен с начальным `;`
пропускается отдельно, не как вся строка.

## Применение, сброс и слоты

Применение использует настоящий восстановленный TextureManager renderer owner.
Cached pointer120/124 копируется в mesh5115/5119 без записи mesh texture ID.
Иначе непустое имя при attempt56/60==0 запускает загрузку и ставит sticky flag;
неудача не повторяется автоматически. Effect pointer публикуется в mesh5455,
factor в5147. ApplyFile возвращает0 и после успешного применения, как эталон.

Для grade36 factor=(intensityFloat-epsilonDouble)*UINTMAXDouble; другие signed
grade используют grade*2^32Double*точную double-константу rate. Константы взяты
из эталонов; x87 intermediate precision/rounding и signed64 truncation перед
lowDWORD сохранены. CW восстанавливается. Nonfinite/unmasked failure domains
не объявлены принятыми.

Reset обнуляет hidden5567, ставит alpha5131=1, очищает secondary pointers и
ставит IDs=FFFFFFFF, затем InitEffect модели применяет inline record5163 с36.
Текущий record5455 даёт particle slots208/224/240 и entity256. Слоты packed16;
IsHaveEffect проверяет три particle ID и entity ID. Это другой predicate,
чем render-material/transparency91C710. В единственном активном source loop
particlelist.cpp добавлен подтверждённый null-current-effect guard. Полная
математика emitter и дополнительные flags этой функцией не восстановлены.

SetMeshEffect пользуется status-aware выборкой038 и настоящим renderer context:
неизвестный pattern tail grades9..35 вызывает явную ошибку. Mode0 даёт36,
ненулевой mode использует grade. MAX_PATTERN_SIZE=36 подтверждён Animus caller.

## Проверка и подключение

Формат/имена прочитаны во всех обнаруженных EFF: 19 766 записей, из них58 по172.
Это инвентаризация, не GPU-проверка каждого эффекта. Native sample —12 различных
реальных файлов,28 записей, lossless roundtrip. Независимый Fraction/x87 oracle
сверяет132 factor cases в12 режимах precision/rounding. Малые сценарии проверяют
границы и поздний malformed prefix, duplicate/reload, точное имя файла, upper
mesh filter, generic/named precedence, cached IDs, sticky failed attempt, reset,
particle/entity views, реальные file lists и normal globals.

GPU сценарий использует производственные InitEffect→EFF reader→file tables→
SetMeshEffect→TextureManager→main model draw. Настоящая512x512 DDS загружена один
раз, shared cache применён к51mesh с сохранением особенностей ID. Проверены
mode0/nonzero, SetPartEffect и Monster SetEffect; particle ID17 виден через
текущий view, но сами частицы этим тестом не рисуются. Кадры до/после отличаются
на5814пикселей; after BMP визуально проверен. Прежние два цветных кадра совпали,
теневой силуэт сохранился. После явного cleanup COM/Dmalloc0, игровые DLL не
загружались. Native MAP проверяет providers across CPU и GPU: /OPT:REF удаляет
entitySlot из GPU entry, этот метод реально вызывается CPU slot сценарием.

182 client +8 facade +20 canonical kernel CPP собираются x86/MT. Реальный
normal link оставил только g_ChMemoryInfo и _R3CalculateTime; других ошибок нет.
CharacterMR и /FORCE не используются. Старые input/baseline source не менялись.
Evidence: inventory/client455-effects-reference.json, client455-effects-native.json,
client455-normal-renderer-gpu.json, client455-normal-link.json и
client455-effects-checkpoint.json. Последний PARTIAL. Связанные normal/renderer/
contracts/shadow/table checkpoints проходят; большие неизменённые suites не
повторялись. Это собственные test entries с production components, не normal
WinMain или полное соответствие оригинальному игровому кадру.

## Открытые границы и продолжение

Bounded malformed/OOM/overlong string/error UI/logging/unwind policies отличаются
от unchecked эталона и не приняты как его поведение. Приватный STL ABI, opaque
bytes, полные particle/entity consumers и их игровой lifecycle открыты.
Borrowed record views при замене registry требуют дальнейшей проверки lifecycle.
Pattern tail038, shadow/HRESULT caller, timed blend producers, static CRT и
нормальные UI/network/gameplay/device-reset сценарии остаются открытыми.

Следом040: восстановить реальные Character accounting и clock, проверить28/32
байта CHMEMORYINFO и источник counters, избежать пустого глобала/no-op и
двойного продвижения clocks. После этого — normal full link и инициализация.

Повтор через scripts/Invoke-Python.ps1: audit_client455_effects.py,
prepare_client455_normal.py, build_client455_normal.py, probe_client455_effects.py,
probe_client455_normal_renderer.py, link_client455_normal.py (пока ненулевой exit),
checkpoint_client455_effects.py. Остальные короткие consumer/table/checkpoint
проверки повторять только при изменении их зависимостей.
