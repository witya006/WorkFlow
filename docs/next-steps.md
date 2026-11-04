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

Сохранены 11 compiler-only patches и 6 отдельных selectable behavior files:
DrawCharacter scale/scroll, EffectLog455, login success->lobby, helper loader455.
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
2 546 779 native/comparison checks, 4 import-parser tests. Игровые DLL не загружались.
Обычная ревизия также собрана: 2 436 608 bytes, entry RVA0x1BAA10, snapshot helper455.
Обычный запуск игры/LoadLevel/GPU/network НЕ выполнен; M5 пока не закрыт.

1. Сравнить численные math contracts с 455; текущая native binary32 проверка
   не доказывает совпадение с x87 rounding эталона. Max local roundtrip error .001953125.
2. Проверить полный путь использования EXT helpers. 455 после LoadExtDummy передаёт
   owner в BSP+744; старый клиент этой связи не содержит. Найти фактический consumer.
3. Выяснить lifecycle/error rules выбранного участка: reload-success/leak, unsafe
   malformed paths/locale/OOM пока не закрыты. Не исправлять quirks по догадке.
4. Вести feature/scenario matrix по client-acceptance.md. M6/M6F — полный functional
   coverage, M7 — закрепление сборки, затем M9. Не закрывать цель по одному EXE.

Известные дальнейшие gaps: D3D8 база против D3D9 reference; legacy EffectList9grades
против 455 map/36; полные Character sources/layouts/constructors/exception unwind;
реальная инициализация blend pointer+160; recursion CLevel::GetFrustumNormalPlane;
полный resource manifest; всё UI/сеть/игровые действия ещё не проверено.
Clear routine effect log0x7DF1B0 не привязывать к atexit по догадке.

## Команды текущего дерева

Обычная повторная сборка: scripts/probe_client_character_build.ps1.
Lab: тот же script с -HelperLab, затем Invoke-Python.ps1 scripts/probe_client_helpers.py.
Lab использует отдельные build-helper-lab/logs/reports, нормальный target не запускается.
Чистая: тот же script с -CleanRebuild. Он проверяет хеши dependencies и behavior ledger.
Для нового дерева: prepare_client_build.py -> apply_client_port_patches.py; затем
проверенные dependency builders по manifests. Не пересобирать неизменённые helpers.
Если меняется Character header: prepare_character_header.py -> check_character_header.py
-> build_character_setters.py -> build_character_managers.py -> probe_character_effect_loaders.py.
Logger: build_client455_effect_log.py -> apply_client_effect_log455.py.
Behavior branches: apply_client_draw455.py / apply_client_lobby455.py /
apply_client_helper455.py -> prepare_client_build.py
-> diagnostic build -> verify_client_draw455.py / verify_client_coff.py.

audit_client_executable.py --label NAME сохраняет immutable snapshot нормальной сборки;
initial/clean/helper455 уже заняты, перезапись другой сборкой запрещена. Для новой
ревизии выбрать новое короткое имя. Lab entry таким snapshot не принимается.
Все Python scripts запускать через scripts/Invoke-Python.ps1.

## Ограничения проверок

Character header 67 assertions/165 native refs; manager/empty renderer 3630 checks,
leaf setters 18, actual effect loaders 59, stdio 1828+3 COFF tests, exceptions 770,
logger 14 cases/66 checks. Это ограниченные component tests, не доказательство общего
соответствия 455. Old SDK loaders/exception paths не сертифицированы полностью.
Дополнительных SDK/PDB у пользователя нет; не ожидать их. Raw analysis — artifacts/,
source copies/IDB/large files — work/, Git — scripts/docs/small evidence only.
