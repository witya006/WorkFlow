# Локальные команды времени455 и путь ввода

Восстановлены %time и %real_time, два недостающих real-HMS clock API и selected
grade-gated input hook. Actual CHAT_INFO::SendMessage/CNetworkMgr lifecycle проверены
в own entry полного клиента; %time также управляет actual weather FrameMove/GPU.
Это продолжение M6, не полная приёмка M9 и не восстановление всех chat/local commands.

## Контракт и ограничения сравнения

Эталон x86/base0x400000:current SHA
b1b5febf0d0394712e2322350e19dafe60742e8642697b93cfb89135bac1fd8b,
backup46528aac20499e3b3928d58658d7e0cefe26feba7cd193796d5cfbf7a2bbc558.
Оба pinned bodies/calls проверены audit_client_time_commands455.py.

| Участок | VA / RVA | Факт |
|---|---|---|
| Input send |433050/33050| NULL/empty guard; signed grade>=1 перед privileged path |
| Grade gate |433096/33096|83F8017C41:cmp1/jl; не переносить local commands перед этим gate |
| Privileged input |4335A0/335A0| local parser7E3B10 вызывается прежде GM/network fallback |
| Local parser |7E3B10/3E3B10| strncpy256,terminator256,lowercase copy; input неизменен |
| Game command |7E3E55/3E3E55| HMS(hours,0,0)→8B12E0 |
| Real command |7E3F3A/3E3F3A| HMS(hours,minutes,0)→8B14A0 |
| Conversion |874F6A/474F6A| atol wrapper вызывает strtol(input,NULL,10) |
| Real HMS set/get |8B14A0/4B14A0,8B1540/4B1540| независимый real clock, modulo24/60/60 |

Clock теперь имеет10scalar functions+256byte frame prefix:1037instruction bytes
совпадают с обоими PE после проверки каждого absolute operand/constant.1443native
checks/12FP modes standalone/full-client; GetRealDayTime alias writes и unsigned
wrapping проверены. Linked normal retained7routines/prefix,lab11;unused APIs linker
может удалить. Clock provider по-прежнему KERNEL32.GetTickCount, test override только в lab.

Time parser — собственный C++ source, не instruction-identical перенос. Его contracts
сверены статически;432ASCII fixtures/2628checks в12FP modes прошли отдельно и внутри
полного клиента. Reference EXE никогда не исполнялся; прямого dynamic differential
oracle для parser нет. Совпадение всей старой CRT/locale/non-ASCII области не заявляется.

Сохранён length-only cursor advance, а не strtok/обычная нормализация пробелов.
Например leading space в " %time 12" даёт hours0, двойной space перед argument в
"%real_time  12 34" даёт minutes2. Проверены case, signs/trailing junk, decimal-only,
signed32 saturation→unsigned HMS,missing arguments,256byte cutoff/truncated minutes,
first handled command/ignored unknown tokens/end и barriers других recognized keys.
%fov/%change_rgb/%max_cam_dist/%floor_dist здесь не реализованы: время после такого
directive не исполняется, но остальные effects/return/fallback всего parser открыты.

## Source integration и actual input

Own source client455_time_commands.cpp/.h;RF_CLIENT_455_TIME_COMMANDS defaultOFF,
driver явно ON после native/hash proof. apply_client_time_commands455.py добавляет
hook в copied character/avatar/cavatar_relationinfo2.cpp после существующих history/
prefix updates и до прежней классификации. Explicit GetAvatarGrade()>=1 сохранён;
original source/branch bytes не нормализованы. Behavior ledger22files. Полная455chat
реализация/new handlers/история/форматирование/ошибки не объявлены эквивалентными.

Actual CHAT_INFO object через SendMessage принял "%TIME 12" и "%real_time 6 0" при grade1,
сохранил original text/history,prefix empty и независимые clocks; grade0 отказал и
не изменил время.20input/access/lifecycle checks прошли. Настоящий CNetworkMgr ctor/
dtor и Winsock initialization выполнены; Create/SetNetSystem/Connect не вызывались,
число network processes0, соединений и отправки сообщений нет. Game DLLs отсутствуют.
Source ledger, actual chat object→parser и parser object→two clock API references
проверены в обоих builds. Это method-boundary проверка, не live GUI/key-event/network тест.

## GPU и артефакты

Current own graphics entry использует "%time 0"/"%time 12" в actual Platform01 weather
scenarios.2GPU cases/69checks,0errors/warnings,Dmalloc/COM balance0,FPU007F;
23helpers/8interiors и two particle states[0,0]/[1,1]/[0,0] сохранены.
1443clock/314map-time/703weather/30resource регрессии
прошли; каждый report имеет отдельную область.289modern x86 /MT objects проверены.

Normal2450432bytes,entryRVA0x1BC330,SHA
d656498a2465feec8c9b4fb44149f01e38aa8e4288e4cc9e4bb4c555ec490919,
snapshot artifacts/client-first-build/time-commands455;не исполнялся.
Lab4131328bytes,entryRVA0x7E9B,SHA
d19ea1193dbfd546e68eadb3332e145de3d42d83e5429155726c807cfd3a1c24,
snapshot work/client-time-commands-lab/d19ea1193dbfd546/RF_Online.bin.
Reports inventory/client455-time-command-reference.json,client455-time-commands*.json.
Raw artifacts/clock455-analysis/command-*.json; owned IDA1bf47ee9 закрыта/save.

Повтор: audit_client_time_commands455.py → build_client455_clock.py →
build_client455_time_commands.py /build_client455_map_time.py →
apply_client_time_commands455.py →prepare_client_build.py →normal/lab build driver →
verify_client_time_commands455.py [--lab] →probe_client_time_commands455.py.
Последний runner требует Winsock constructor, на этой машине разрешён вне sandbox.
GPU report: probe_client_graphics455.py --level Platform01 --output
inventory/client455-time-commands-graphics-runtime.json (HAL вне sandbox).

Далее critical path M6: восстановление исходников Character перед полным D3D9 port.
Current recovered SDK header/old library ABI использует IDirect3DDevice8; простая
смена engine API оставит несовместимые binary consumers. Дополнительного SDK/PDB нет;
использовать уже кешированные207definitions/данные455, не повторять массовый decomp.
Полные particles/camera/color commands/lighting/Character/UI/network/audio/gameplay,
calendar/CRT и canonical Release/M6F/M7/M9 открыты; M8 modernization не требуется.
