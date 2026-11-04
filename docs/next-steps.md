# Ближайшие действия — только клиент

Обновлено 2026-11-04. /Goal — M9: финальная приёмка клиента 455 без модернизации графики.
Критерии docs/client-acceptance.md; M8 не требуется. Серверы/БД не разрабатывать.
Серверные исходники — только read-only reference. Оригинальные EXE не запускать.

## Полученный сборочный результат M4

RF_Online.bin успешно скомпилирован/слинкован и чисто пересобран под VS2026 x86.
Размер 2 436 608, entry RVA 0x1BA9E0. Два результата различаются только двумя timestamp
DWORD. Все 284 modern COFF x86 /MT;13 direct DLL providers найдены, runtime не проверен.
Это diagnostic /Od build старой базы с selected455 branches, а не готовый клиент 455.
Pure legacy OFF branches, canonical optimized Release, весь Character ABI ещё открыты.
Документ research/client-first-build.md; inventory/client-first-build.json.

Сохранены 11 compiler-only patches и18 selectable behavior files:
DrawCharacter scale/scroll, EffectLog455, login success->lobby, helper loader455,
x87 math и двухслойная погода (9 files).
Их инструкции сверены
по обоим pinned PE, исходные ветки сохранены. _DEVELOPER_ и /FORCE не включены;
CheckFiles/SendLog не заменены пустыми functions. По исследованным reference callers
455 не вызывает их в этих двух местах. Не делать вывод об остальных file checks.

## M5 в работе: получена native CPU-проверка helper данных

Loader455 VA0x90BBF0 найден, весь body/инструкции сверены в обоих pinned PE.
Три отличия перенесены отдельным flag: missing-input count reset, lowercase каждой
записи, interior4. research/client-helper455-runtime.md; inventory/client-features.json.
Полный проект с own lab entry загрузил 140 файлов/97 543 записи и 12 fixtures.
Проверены raw fields, ненулевые coordinate transforms, inverse, bbox/list/release.
Текущая x87 ревизия:2 546 931 native/comparison checks,4 import-parser tests.
Две math функции совпали с инструкциями 455 на COFF и в linked normal/lab PE;
338 own native checks в12 FP modes и3 COFF parser tests. FP control lab0x027F.
Игровые DLL не загружались. Обычная ревизия собрана:2 436 608bytes,
Последующий weather port:65real R3X +4fixtures,703checks,37actual CPU lifecycle
checks для двух one-element particles. Настоящий LoadR3X применён для58real files
без lens flag;7lens samples проверены shared production reader без GPU.
Обычная версия:2 438 144bytes,entryRVA0x1BAF50,snapshot weather455-cpu.
285modern objects /MT. research/client455-weather-source.md.
Обычный запуск игры/LoadLevel/GPU/network НЕ выполнен; M5 пока не закрыт.

Ресурсный аудит:78MapEntity RPK/3775entries и70BSP+93EBP проверены tooling с
lossless container round trip.20real weather assets закреплены в work/.1067RPK
size fields неверны относительно extent; Dungeon00 имеет stale overlapping offsets,
455 читает BSP последовательно. Один weather SPT отсутствует для трёх Tower R3X;
его directory component не найден во всех162RPK indexes. Не подменять похожим файлом.
8parser tests прошли. research/client455-map-resources.md,
inventory/client455-map-resources.json. Runtime/сборки в этом цикле не менялись.

Следующий source перенос выполнен: RPK file/group/fopen/exists и case-sensitive
particle end boundaries подключены в7copied files.18 907standalone native checks
на3775real members/78archives и group/boundary fixtures;30full-project actual SPT/
R3X checks.703weather regression checks прошли на текущем lab.286modern /MT objects,
обычный2440704bytes,entryRVA0x1BBA50,snapshot resource455-runtime. Normal EXE не
запускался. research/client455-resource-io-source.md; inventory/client455-resource-*.json.
Общий RPK код есть; все другие resource consumers/archives и GPU не объявлены готовыми.

1. Проверить actual entity/texture/particle и normal LoadLevel/GPU на реальных данных:
   собственный graphics entry, device/FPU initialization и изолированные copies.
   RPK module и selected consumers уже source-integrated/native-tested; не повторять
   static audit вместо следующего runtime этапа. Полные particle455 options/curves,
   остальные resource consumers/groups, locale/error/OOM/unsafe domains ещё открыты.
2. Перенести client-side time/HMS caller4550x7E3E55 и проверить clock numeric/FPU
   environment. Setter/rate/basic API есть, network/lighting не объявлены готовыми.
3. Проверить обычный LoadLevel и FPU initialization. Сами inverse/transform теперь
   инструкционно совпадают с 455; окружающая среда игры/GPU ещё не проверена.
4. Выяснить lifecycle/error rules выбранного участка: reload-success/leak, unsafe
   malformed paths/locale/OOM пока не закрыты. Не исправлять quirks по догадке.
5. Вести feature/scenario matrix по client-acceptance.md. M6/M6F — полный functional
   coverage, M7 — закрепление сборки, затем M9. Не закрывать цель по одному EXE.

Известные дальнейшие gaps: D3D8 база против D3D9 reference; legacy EffectList9grades
против 455 map/36; полные Character sources/layouts/constructors/exception unwind;
реальная инициализация blend pointer+160; recursion CLevel::GetFrustumNormalPlane;
полный resource manifest; всё UI/сеть/игровые действия ещё не проверено.
Clear routine effect log0x7DF1B0 не привязывать к atexit по догадке.

## Команды текущего дерева

Обычная повторная сборка: scripts/probe_client_character_build.ps1.
Lab: тот же script с -HelperLab, затем Invoke-Python.ps1 scripts/probe_client_helpers.py.
Перед native runner: verify_client_x87_math455.py --lab для текущего linked EXE.
Weather native: Invoke-Python.ps1 scripts/probe_client_weather455.py.
Map/RPK tools: Invoke-Python.ps1 scripts/test_map455.py, затем
Invoke-Python.ps1 scripts/audit_client_map_resources455.py. Это static tooling;
его round trip не доказывает native loader/GPU parity.
Source RPK: audit_client_resource455.py -> build_client455_resource_io.py ->
apply_client_resource455.py -> prepare_client_build.py -> обычный/lab build driver.
Native full-project: probe_client_resources455.py; compiled branches/DDS mask:
verify_client_resource455.py. Все Python commands через Invoke-Python.ps1.
MSBuild FileTracker E_ACCESSDENIED в sandbox устраняется разрешённой escalation
того же build command, не изменением исходников/удалением build cache.
Lab использует отдельные build-helper-lab/logs/reports, нормальный target не запускается.
Чистая: тот же script с -CleanRebuild. Он проверяет хеши dependencies и behavior ledger.
Для нового дерева: prepare_client_build.py -> apply_client_port_patches.py; затем
проверенные dependency builders по manifests. Не пересобирать неизменённые helpers.
Если меняется Character header: prepare_character_header.py -> check_character_header.py
-> build_character_setters.py -> build_character_managers.py -> probe_character_effect_loaders.py.
Logger: build_client455_effect_log.py -> apply_client_effect_log455.py.
Math: build_client455_x87_math.py -> apply_client_x87_math455.py; driver после сборки
сам проверяет linked instructions. Не пересобирать неизменённый archive без причины.
Behavior branches: apply_client_draw455.py / apply_client_lobby455.py /
apply_client_helper455.py / apply_client_x87_math455.py -> prepare_client_build.py
-> diagnostic build -> verify_client_draw455.py / verify_client_coff.py.
Weather selection: audit_client_weather455.py -> apply_client_weather455.py ->
prepare_client_build.py; driver выбирает RF_CLIENT_455_WEATHER=ON.

audit_client_executable.py --label NAME сохраняет immutable snapshot нормальной сборки;
initial/clean/helper455/helper-x87/math455-release/weather455/weather455-cpu/
resource455/resource455-runtime уже заняты;
перезапись другой сборкой запрещена. Для новой
ревизии выбрать новое короткое имя. Lab entry таким snapshot не принимается.
Все Python scripts запускать через scripts/Invoke-Python.ps1.

## Ограничения проверок

Character header 67 assertions/165 native refs; manager/empty renderer 3630 checks,
leaf setters 18, actual effect loaders 59, stdio 1828+3 COFF tests, exceptions 770,
logger 14 cases/66 checks. Это ограниченные component tests, не доказательство общего
соответствия 455. Old SDK loaders/exception paths не сертифицированы полностью.
Дополнительных SDK/PDB у пользователя нет; не ожидать их. Raw analysis — artifacts/,
source copies/IDB/large files — work/, Git — scripts/docs/small evidence only.
