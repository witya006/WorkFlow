# Ближайшие действия — только клиент

Обновлено 2026-11-05. /Goal — M9: финальная приёмка клиента455 без модернизации
графики. M8 не требуется. Критерии docs/client-acceptance.md. Серверы/БД/GoMMO server
logic не разрабатывать; серверные исходники только читать как справочник.
Оригинальные EXE не исполнять, изменения только в собственных копиях/work/.

## Текущая точка

M0–M4 выполнены в описанных diagnostic compile пределах; M5 закрыт для выбранного
helper/interior/weather участка. M6 в работе. M6F/M7/M9 открыты. Compilation,
загрузка модели и uploads не являются финальной приёмкой клиента.

Последний source unit — промежуточный reader93C2F0/part720/model28 lifetime:
4606standalone checks/12realBN455records+5synthetic4records/1183guarded prefixes/
7allocfailpoints/12FPmodes;6Python tests. Полные importer/converter/BNruntime ещё
не подключены. research/client455-legacy-model-reader.md; client455-legacy-models*.json.
Предыдущий connected unit — Character455 record1188/manager4148/cache/rawMSH/refresh.
850CPU/1138HAL checks, полный клиент даёт те же1138;12models/393parts/276uploads/
59texture pointers, ownheap/COM/Dmalloc0.13 APIs вызваны из actual lab TU иsource lib.
24bodies equalbothpins; ctor1188bytes — oracle из92записанных инструкций+констант.
Реальный MESH08 из собственного RFS и11loose моделей проверены до парсинга по байтам.
Normal game dispatcher покаlegacy. Research: client455-character-manager.md;
gate inventory/client455-character-manager-checkpoint.json. Текущие PE identities там.

## Очередь M6 → M9

1. Подключить file importer93C770 и восстановить преобразование93CD60 в455mesh5803.
   Source reader93C2F0/part lifetime уже проверены standalone. Это следующий шаг
   к настоящему skeleton loader, вместо
   external names из tooling golden. Использовать записанные body/формат и real BN;
   проверять границы, malformed/compact physique и реальные матрицы. Полный181line
   parser сохранён artifacts/character-manager455/manager-plus-4.json. Начало
   converter — artifacts/character-gpu455/next-2.json(250lines) и
   artifacts/character-legacy455/converter-tail.json(328lines): все578сохранены.
2. Подключить полный dispatcher9238A0 после legacy reader/converter. Сохранить
   загрузочные flags, parent prerequisite, sticky failures и lifetime по эталону.
   MESH08-only successful stub недопустим. Затем FrameMove923A40, transforms,
   animation/skinning, 455declarations/shaders и normal typed consumers.
   Legacy parent/count/mesh268/528/532 отличается от455272/532/536; rawcast запрещён.
3. Восстановить полный D3D9renderer455/lighting/effects/device lifecycle вместе
   с consumers Character. Это обязательное соответствие M6, не модернизация M8.
   Продолжать другие M6 клиентские области по feature/scenario matrix: UI/input,
   клиентская сеть, game states, предметы/действия, звук и остальные выявленные.
4. M6F: полный реестр возможностей и расхождений; сценарии с одинаковыми ресурсами,
   настройками, входами и состояниями. Закрывать пробелы по client-acceptance.md.
5. M7: воспроизводимая поддерживаемая сборка, зависимости и проверки.
   M9: финальная приёмка функционала/поведения455 без модернизации графики.

## Уже выполнено — не повторять без новых входов

- Mesh lifetime и связанный MESH08 route:9953CPU/10021HAL,12pairedfiles/393parts,
  276uploads/59bindings. Последняя регрессия10021 прошла на текущем lab.
  research/client455-model-pipeline.md; inventory/client455-models*.json.
- Shared buffers36/64/INDEX16/first-fit/rebase/bind/lifetime:158336CPU/159173HAL,
  4synthetic draws. research/client455-shared-buffers.md.
- TextureManager/RFS/DDS/mips/fallback/lookup/cache:333CPU/8440GPU,80profiles,
  68texturepairs/137renders/97parts/59bindings. research/client455-character-textures.md.
- Mesh ctor/header/matrices/material requests:14562checks/12FP modes;
  parent/bone bindings2237checks/12pairs;31–50pointer/matrix overlap сохранён.
  research/client455-mesh-runtime-source.md иclient455-mesh-bindings-source.md.
- MESH08 framing:858files/12090parts lossless tooling roundtrip;
  6304native checks/1309guarded truncations/7Python tests.
  research/client455-mesh08-format.md. Не повторять858file/header census.
- Legacy InitVertex/CPU bindings:245+6732checks/144cases/12FP modes,
  4COFFtests/2actualSDKLoadRealData callers. research/character-init-source.md.
- Clock1443/map-time314/weather703/resource30, commands432cases/2628checks
  и20actual input checks прошли на предыдущей lab revision. Подробности в
  research/client455-clock-source.md, client455-map-time-source.md,
  client455-time-commands-source.md, client455-weather-source.md,
  client455-resource-io-source.md. Это исторические результаты, не повторять
  массовые проверки без изменения соответствующих входов/кода/неразрешённого риска.
- Текущие Platform01/device2cases/69checks,0errors/warnings/COM/Dmalloc,
  прежние frameSHA сохранены: inventory/client455-character-manager-graphics.json.
- M5 historical gate: verify_client_m5.py --saved. Старый13case report иего
  immutable lab сохранены. Текущую scoped GPU regression не подменять полным M5.

## Воспроизведение последнего модуля

Python — исключительно scripts/Invoke-Python.ps1:
test_character_ctor_oracle.py → audit_client455_character_manager.py →
build_client455_character_manager.py → probe_client455_character_manager.py [--gpu] →
prepare_client_build.py → probe_client_character_build.ps1 [без флага и с -HelperLab] →
verify_client455_character_manager.py [--lab] → probe_client455_character_manager_client.py.
После сопутствующих model/Platform01 проверок: checkpoint_client455_character_manager.py.
HAL/MSBuild требуют разрешённого запуска вне sandbox; исходные EXE не запускаются.

Нормальный snapshot character455-manager-io immutable; audit_client_executable.py
--label NAME принимает новое короткое имя, не перезаписывает отличающийся snapshot.
289normal modernCOFF x86/MT,185client labTUs. Normal source APIs покаunused/stripped;
runtime bytes равны предыдущему snapshot после исключения двух timestampDWORD.

## Память и ограничения

Детали сохранять в research/ и inventory/, решения — docs/project-memory.md.
Raw IDA/large traces/IDB/исходные копии — ignored artifacts/ и work/. Gitлокальный,
без remote/push. Ignoring не является backup. Дополнительных SDK/PDB/Character.h
у пользователя нет; ожидание этих файлов не следующий шаг.

Cache Character сохраняет freed pointers после delete/clear/dtor; не исправлять
по догадке и не разыменовывать их в tests. Полный ABI/exception unwind/OOM/logger/
unsafe input/failure equivalence ещё открыты. Private source container layout не
доказывает совместимость с heap/STL старого binary SDK. Не объявлять клиент готовым.
