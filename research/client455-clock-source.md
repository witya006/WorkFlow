# Два счётчика времени455: исходники и проверка

Восстановлен численный участок M6: ускоренный game clock и независимый real-time
counter. M6 в целом, M6F/M7/M9 не завершены. Входные EXE/DLL не исполнялись.

## Доказанный контракт

Оба закреплённых PE: x86/base0x400000,currentSHA
b1b5febf0d0394712e2322350e19dafe60742e8642697b93cfb89135bac1fd8b,
backup46528aac20499e3b3928d58658d7e0cefe26feba7cd193796d5cfbf7a2bbc558.
inventory/client455-clock.json содержит VA/RVA, function/body hashes и каждую relocation.

| Участок | VA / RVA | Проверка |
|---|---|---|
| Rate set/get |8B12C0/4B12C0,8B12D0/4B12D0| Initial3.0, setter не пересчитывает base |
| Game HMS set/get |8B12E0/4B12E0,8B13B0/4B13B0| Unsigned modulo24/60/60, float spills, truncation |
| Game fraction get/set |8B1430/4B1430,8B1440/4B1440| Raw fraction и GetTickCount base |
| Real fraction get/set |8B15C0/4B15C0,8B15D0/4B15D0| Отдельные fraction/base, без simulation rate |
| Frame clock prefix |8B1F20/4B1F20,256bytes| Оба ticks, x87 calculation/spills, low32bits, game wrap, unwrapped real clock |

Own readable x86 source scripts/native/client455_clock.cpp:8scalar functions +256byte
prefix, всего773instruction bytes, совпали в обоих PE после проверки всех absolute
operands/constant values. У prefix собственный balanced epilogue: последующий lighting
код455 сюда не включён. Caller x87 precision/rounding сохраняются; integer conversions
временно включают truncation. Маскированные NaN/Inf/zero-rate quirks сохранены.

Standalone /MT component:1275checks в12PC/rounding modes. Те же1275checks прошли
в own entry полного клиента; GetModuleHandle до/после подтвердил отсутствие игровых DLL.
Проверены HMS wrapping, getters/aliased outputs, rate changes/negative/zero, unsigned
tick rollover, independent two tick calls, game modulo и real fraction>1, raw fractions
и masked nonfinite cases, x87 control/TOP. Это не полный unmasked-exception domain.

## Source integration и GPU

RF_CLIENT_455_CLOCK defaultOFF, driver явно ON и требует component proof/hash.
При ON общий weather API использует этот module; прежний C++ clock сохранён в OFF
branch. CLevel::FrameMove уже вызывает общий AdvanceDayClock. Новый module —61-й
engine object; normal build180+61+46JPEG=287modern x86 /MT.

Normal RF_Online.bin2440704bytes,entryRVA0x1BBAA0,SHA
f5f945160fe45255b9cea935cb3e27946a0a5ab531a18b1279abbd41164e18e5,
snapshot artifacts/client-first-build/clock455. Не исполнялся.
Own lab4085248bytes,entryRVA0x7DD8,SHA
bb441c5c3e393f98a298355b794e14bbb95d1efdd790c36e1356080d64c44e9b.
В normal PE retained2used routines/prefix; остальные отсутствуют из-за удаления
неиспользуемых функций linker. Lab retained9. Оба linked code paths/constants
проверены. MSVC устанавливает tick provider через .CRT$XCU: actual initializer
копирует KERNEL32.GetTickCount IAT в свой pointer; регистрация тоже проверена.
В standalone/full-client tests provider заменяется на deterministic testTick и
восстанавливается. Production init не устанавливает test provider.

Current lab повторно прошёл703weather,30resource и actual D3D8 device/Platform01
LoadLevel/FrameMove/render/release:2GPU cases/59checks,0errors/warnings,allocation/
COM balance0.23helpers/8interiors, два particles15/500, состояния[0,0]/[1,1]/[0,0]
сохранились; FPU007F во всём actual consumer path. Кадр просмотрен. Report
inventory/client455-clock-graphics-runtime.json. Полные13M5GPU cases остаются на
своём прежнем EXE; их evidence сохранён в artifacts/m5-checkpoint/ece2acccb434ef06.
scripts/verify_client_m5.py --saved проверяет тот historical checkpoint без объявления
его регрессией текущей сборки. Не повторять неизменённые140helper files без причины.

## Уточнение caller и оставшаяся интеграция

Прежнее предположение, что0x7E3E55 является сетевым Time/HMS handler, неверно:
это console %time, часы из atol, minutes/seconds0. %real_time читает hours/minutes
и вызывает отдельный real HMS setter0x8B14A0. Оба console paths пока не перенесены.
Действительный map caller0x7C8B60/RVA0x3C8B60 после load использует как минимум4cached
DWORD time fields, добавляет elapsed_seconds%60 к seconds и (elapsed_seconds/60)%60 к minutes,
считает totalSeconds. Затем accelerated game fraction через rate и real fraction
без rate передаются setters0x8B1440/0x8B15D0. Дополнительный hour carry в этом
fragment отсутствует; не исправлять по догадке. Структура/update origin cached fields
и полный CLand path ещё требуют восстановления. inventory/client455-time-callers.json
закрепляет3bodies/5calls/2strings в обоих PE; raw decomp в artifacts/clock455-analysis.

Окружение: новый current binary auto-analysis превысил300s timeout клиента MCP,
но worker завершил его позже; session восстановлена через idb_list, закрыта/save.
Для исследования использована готовая backup.i64 с run_auto_analysis=false.
Owned b336dffc/6c9c1ee9 закрыты/save; fallback adopted7fc260bd detach/save тоже выполнен.
Далее открывать сохранённый .i64, а не повторять полный auto-analysis бинарника.

Дальше M6: cached map time/packet origin/CLand caller, console commands, full sky/
lighting/materials и D3D9 restoration. Полные Character/particles/UI/network/sound/
gameplay/acceptance coverage остаются открытыми. M8 модернизация не требуется.
