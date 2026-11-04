# Два слоя погоды: исходники и CPU-проверки

Работа исключительно над клиентом. Получен source перенос погодного участка;
M5/M9 не закрыты, обычная загрузка карты/GPU ещё не выполнены.

## Эталон и контракты

Оба PE x86/base0x400000: current SHA-256
b1b5febf0d0394712e2322350e19dafe60742e8642697b93cfb89135bac1fd8b,
backup SHA-256 46528aac20499e3b3928d58658d7e0cefe26feba7cd193796d5cfbf7a2bbc558.
Доказательства/повторяемые byte checks: inventory/client455-weather-helper.json,
scripts/audit_client_weather455.py. Raw asm/decomp: artifacts/weather455-*.

| Участок | VA / RVA | Подтверждено |
|---|---|---|
| Text material | 0x90A4D0 / 0x50A4D0 | ENVIRONMENT/ID и ENVIRONMENT2/ID2, верхний регистр ключей, регистр значения имени сохраняется |
| R3X reader | 0x90AED0 / 0x50AED0 | версия float1.1, zeroed payload1032, fread result не проверяется |
| Load environment | 0x8F8C90 / 0x4F8C90 | оба слоя, IsParticle, runtime flag0x1000, InitParticle/START |
| Release level | 0x8F9AD0 / 0x4F9AD0 | два slots, particle release затем entity release/delete, очистка IDs/pointers |
| Update environment | 0x8CAD00 / 0x4CAD00 | CPU state/Loop отдельно от draw; interior и night |
| Draw environment | 0x8CB0B0 / 0x4CB0B0 | два layers, identity + camera translation, DrawCParticle |
| Frame hook | 0x8E7910 / 0x4E7910 | clock update перед weather update |
| Night flag | 0x8DBC13 / 0x4DBC13 | SPT token night устанавливает0x10000 |
| Clock | 0x8B12C0 / 0x4B12C0,0x8B12E0 / 0x4B12E0 | изменяемая скорость, первоначально3.0; HMS setter оборачивает24/60/60 |

R3X file =float version4bytes +body. Исследованные65real files имеют1028 или1036bytes;
reader455 запрашивает1032bytes body для обоих вариантов. Недостающие8bytes старого
body остаются нулевыми. Новая структура: name0+256[128],id0+384,opaque DWORD+388,
name1+392[128],id1+520,sceneFlags+524,remaining spare504. Имена/IDs обоих слоёв
применяются при общем flag0x20; sceneFlags копируется отдельно. Версия не менялась.
Старый sizeof(_EXT_MAT)=1024 сохранён в legacy branch. Layout1032 имеет static_assert.

## Реализация

RF_CLIENT_455_WEATHER defaultOFF, официальный локальный build driver явно ON.
scripts/apply_client_weather455.py воспроизводит patches девяти copied files,
сохраняет original branches, кодировки и compiler-overlay chain r3bsp.h/bsp.cpp.
Own source: scripts/native/client455_weather.cpp и client455_weather_format.h.
Состояние/CBsp получают свои двухэлементные arrays, а не offsets объектов455.
285modern objects =180client +59engine (58legacy +1own weather) +46JPEG, x86 /MT.

Перенесены R3X/text environment fields, resets, load/release, night token, helper
owner binding после LoadExtDummy. Update вызывается из CLevel::FrameMove, draw
остаётся отдельным render этапом. Type1 origin =camera +third column of view*50,
а bbox проверяется в самой camera position. Type2 сохраняет fixed world bbox.
Enable flag и именно первый raw environment ID гейтят оба слоя, как в455; вариант
«второй слой без первого» не был произвольно включён.

Clock имеет normalized fraction, mutable rate, HMS/fraction setters и frame advance
по GetTickCount с rate3 initial. Сетевой Time/HMS caller455 ещё не перенесён в старый
клиент; точное x87 rounding clock и полный lighting/day state не сертифицированы.

Failure quirks не исправлялись: particle load failure обнуляет local/global ID,
оставляя inactive raw pointer; non-particle failure не очищает ID. Native fixtures
эти unsafe failure edges не исполняют. Header read меньше4bytes остаётся unchecked,
как в455/legacy; indeterminate stack behavior не объявлен восстановленным и не тестируется.
Wrong-version и valid short-body сценарии проверены отдельно.

## Проверки

Обычная RF_Online.bin:2 438 144bytes,entryRVA0x1BAF50,SHA-256
45690c220e37be7e34d234ffdd90f11d31703271e1fd12d37567fb6916c67542.
Snapshot artifacts/client-first-build/weather455-cpu, inventory/client-first-build.json.
Более ранний weather455 snapshot сохранён отдельно. Нормальный EXE не запускался.
Прежние draw/logger/login selections и linked instruction identity двух math kernels
снова проверены. Нет /FORCE или _DEVELOPER_ обхода.

Lab SHA-256 e9ae5fa895742de2ff49b2b2c7f52c9748e7717d9ff21a623dc7d13bcdf3f361,
entryRVA0x7DBF. Собственный lab entry полного клиента, original EXE/game DLL не запускаются.
Он имеет --rf-weather-read и --rf-weather-scenario; все game DLL delay imports и
GetModuleHandle checks прошли. Никакая новая текстура/модель/GPU draw не тестировалась.

Shared production reader проверен на65pinned real R3X. Для58файлов без lens flag
вызвана настоящая LoadR3X с проверкой applied environment/scene state. Семь lens
samples проверены только общим reader, чтобы CPU lab не требовал GPU. Среди real
samples есть настоящие два активных слоя Platform/fe.spt +fe2.spt. Ещё4fixtures:
wrong version, version-only, short body, env flag off/trailing bytes.

37native scenario checks используют настоящие CParticle load/init/state/Loop/release
для двух собственных one-element CPU particles, без entity/GPU. Покрыты interior
stop/restart, matrix column origin, time thresholds и соседние float values,
night token, global enable, first-layer gate, type2 bbox, text tokens/case,
rate/HMS basic API, повторный release и итоговый Dmalloc balance после CBsp destructor.
Первый test balance был взят до уничтожения ещё живого CAlpha с4buffers: fixture
исправлена, production allocator не менялся. Итого703weather checks.
inventory/client455-weather-runtime.json, scripts/probe_client_weather455.py.

140helper SPT/97 543records заново прошли2 546 931checks в этой же lab revision
после изменения shared engine state/layout. Это regression, не процент полноты455.

## Открытые границы

GPU behavior всего DrawCParticle/particle455, дополнительные SPT опции/кривые,
full R3X fog2/lens/weather/haze scene behavior, archive-aware fopen4550x8E7680,
error/failure domain, clock/server-time integration и normal LoadLevel остаются
открыты. Старый D3D8 renderer против D3D9 reference — отдельный functional gap M6.
Следующий шаг — проверить реальные particle/entity dependencies и формат BSP для
обычного клиентского пути, затем normal isolated runtime. Серверы не затрагивались.
