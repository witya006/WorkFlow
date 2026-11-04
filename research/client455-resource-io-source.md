# RPK: исходниковый перенос и native проверка

Работа только над клиентом. Архивный reader/group/fopen/exists восстановлены в
читаемом C++ и подключены к выбранному resource path полного проекта. M5 ещё открыт:
обычный LoadLevel/GPU, реальные entity/particle render и clock integration не выполнены.

## Источник поведения

Current455 SHA-256 b1b5febf0d0394712e2322350e19dafe60742e8642697b93cfb89135bac1fd8b;
backup46528aac20499e3b3928d58658d7e0cefe26feba7cd193796d5cfbf7a2bbc558.
Оба x86/base0x400000. Базовые15function bodies и форматы:
inventory/client455-map-resources.json, research/client455-map-resources.md.
Дополнительно10functions/8call sites сверены в обоих PE:
inventory/client455-resource-reference.json, scripts/audit_client_resource455.py.
Это статические контракты; входные EXE не запускались.

| Участок | VA / RVA | Перенесено |
|---|---|---|
| File release |0x8E6D60 /0x4E6D60|free tables, clear pointers; count/name/base остаются |
| Group release |0x8E7440 /0x4E7440|release всех archives, очистка count/pointer |
| Group exists |0x8E7510 /0x4E7510|lowercase и offset lookup без открытия archive file |
| Active group |0x8E75D0 /0x4E75D0|один mutable global pointer |
| Resource exists |0x8E75F0 /0x4E75F0|null/empty guard, group lookup, loose fopen fallback |
| Binary material |0x90B1C0 /0x50B1C0|archive-aware opening selected R3M path |
| BSP group load/select |0x8FE2ED /0x4FE2ED,0x8FE2F3 /0x4FE2F3|после geometry, перед environment |
| Entity group select |0x8F9532 /0x4F9532|после ненулевого count и allocation |
| BSP group release |0x8F9AD9 /0x4F9AD9|до остальных release этапов |
| Level group resets |0x8EA245,0x8EA735,0x8EAA73 /RVA=VA-0x400000|начало, lightmap и helper paths |

IDA session f9c03779 использовалась для проверки. К концу работы supervisor сообщил
Session not found; idb_list подтвердил0sessions. Повторный worker не запускался;
сохранённые IDB/предыдущие raw decomp и воспроизводимые PE checks остаются в workspace.

## Реализация

scripts/native/client455_resource_io.h/.cpp: own RF455_RpkFile/Group, manual Release,
RF455_OpenResource/ResourceExists и ParticleScriptEnd. Node64, owners276/268 имеют
x86 static_assert. Таблицы выделяются настоящим engine Dmalloc/Dfree. Собственные
file objects начинают C++ lifetime через placement construction с нулевым состоянием.
Не подставляются offsets455 в старый CBsp: добавлен собственный group member.

Сохраняются first-result skip Windows enumeration, порядок без сортировки,
проверка последних3букв rpk без требования точки, post-collection limit255,
lowercase caller buffer и отрезание prefix по длине без проверки текста.
Открытый FILE* имеет EOF физического архива, declaredSize не ограничивает чтение.
Повторный successful load не получает придуманного implicit release. Source сохраняет
unchecked reads/unsafe invalid-domain quirks. Небезопасные таблицы/строки/OOM/>256
archives/повторные successful loads в native тестах не исполняются.

RF_CLIENT_455_RESOURCE_IO defaultOFF; локальный build driver явно ON. Семь copied
files: r3bsp.h,bsp.cpp,level.cpp,entity.cpp,r3particle.cpp,r3material.cpp,r3d3dtex.cpp.
Ветви legacy сохранены. Выбранные читатели: entity geometry+material existence,
R3M/R3X, R3T info/load, particle SPT. Остальные resource consumers пока не объявлены
перенесёнными: plaintext MST, дополнительные texture/sky/archive groups и другие paths.

Particle parser проверяет точный lowercase end перед поиском [Particle] и в основном
цикле до strlwr. Uppercase END не останавливает цикл. Это необходимо для positioned
FILE*: старый parser мог съесть следующие archive members. Новые curve/light/прочие
particle455 tokens и финализация за пределами старого parser ещё не перенесены.

scripts/apply_client_resource455.py воспроизводит byte-preserving overlays после
compiler/weather. Weather renderer выделен в render_weather; повтор weather script
сохраняет проверенный downstream resource overlay. Ledger содержит upstream SHA и
compiler input SHA.18behavior files всего;7верхних resource overlays включают5weather
files,2новых файла. Compiler patches и исходные Korean bytes не нормализовались.

## Проверки

Standalone собирает тот же production module /O2 /MT /W4 /WX, с test-only allocator/
warning instrumentation.3775members из78pinned real RPK: actual FILE position, полный
SHA-256 каждого inferred extent, прочитанная длина и следующий byte/physical EOF.
Native проверки также покрыли group priority, loose fallback, отсутствие active group,
missing member, caller mutation, неправильный prefix с той же длиной, oddXrpk filename,
directory исключение, exact Windows order через независимый Win32 enumeration,
missing/empty directory, wrong version,256archives limit, repeated release/balance.
Итого18 907checks, inventory/client455-resource-io.json. Input game EXE/DLL не запускались.

Full-project CPU lab вызвал actual CParticle::LoadParticleSPT на трёх соседних SPT:
num3/end/num900, uppercase END/num4/end, end до [Particle]. Проверены count, early
failure, warning callback, modified names и отсутствие entity allocations. Actual
LoadR3X прочитал R3X внутри того же RPK и применил два слоя/scene flags.30checks,
0failures, итоговый Dmalloc balance0. Game DLL GetModuleHandle checks прошли.
inventory/client455-resource-runtime.json; scripts/probe_client_resources455.py.

Обе full-client сборки успешны.286modern x86 /MT objects =180client+60engine+46JPEG.
Normal RF_Online.bin2440704bytes,entryRVA0x1BBA50,SHA-256
a761c930a5ff86025d0a68ab195bd9253855b1d7887f3d9d0f6b9639fec8970c.
Snapshot artifacts/client-first-build/resource455-runtime; ранний resource455 сохранён.
Lab4067328bytes,entryRVA0x7DE7,SHA-256
c23d4bc8634cd2d49c31753b85ec9d876ba35d053096497840a9a8198656a8b9.
Normal EXE не запускался. Его13direct DLL providers найдены статически.

verify_client_resource455.py проверил selected references в6реально скомпилированных
engine objects обоих builds,7source ledgers и linked DDS header mask128bytes:
он совпадает с455, включая байты legacy string literal после современного компилятора.
Linked x87 math proofs и draw/logger/lobby selections снова прошли.65R3X+4fixtures/
703weather checks на этой lab revision прошли;140helper inputs не повторялись, их
последняя полная native проверка остаётся на предыдущей weather revision.

Первый MSBuild вызов в sandbox остановился на FileTracker E_ACCESSDENIED до compiler.
Повтор разрешённой сборки с sandbox escalation успешен; исходники не менялись для
обхода. Это ограничение процесса сборки, не клиентский link/runtime blocker.

## Следующий шаг

Проверить actual entity/texture/particle загрузку и обычный LoadLevel с собственным
GPU entry. Начать с real device/FPU initialization и изолированных ресурсов; не
запускать reference EXE. Сохранять возможности/ошибки эталона и запись known gaps.
Далее clock numeric/HMS client caller и остальные M6 подсистемы. Missing Tower
weather SPT остаётся отдельным входным пробелом; похожим файлом не подменялся.
