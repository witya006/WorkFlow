# Первый обычный WinMain: CRT, движок и звук

2026-11-06, Asia/Yakutsk. Участок M6 номер042 добавляет доказательство запуска
точной собственной полной PE041. Production исходники/бинарник не менялись.
CRT/WinMain/engine bootstrap и Miles init прошли. Процесс остановлен до D3D,
а вся инициализация и соответствие455 ещё не приняты. M6/M6F/M7/M9 открыты.

## Собственный бинарник и проверенная граница

Это RF_Online.bin, собранная из новой source Character/D3D9 ветки:
1966080байт, PE32 x86, image base0x400000, entry RVA0x149500, SHA-256
39062b2cbf18f5680fd1d59c3d73c22c020770c30e99c9107302cf6678a53a05.
Входные reference EXE не исполнялись. Адреса ниже относятся к нашей PE,
не к закреплённому455. MAP/response/SHA — inventory/client455-normal-link.json.

| Контракт собственной PE | VA / RVA |
|---|---|
| Обычный WinMain | 0x4B3CD0 /0xB3CD0 |
| Call InitR3Engine | 0x4B3CD9 /0xB3CD9 |
| Call ForceFullScreen | 0x4B3CDE /0xB3CDE |
| Call InitR3SoundSystem | 0x4B3CE8 /0xB3CE8 |
| После звука, до D3D | 0x4B3CED /0xB3CED |
| Call InitR3D3D | 0x4B3CFB /0xB3CFB |
| InitR3SoundSystem | 0x4D52D0 /0xD52D0 |

Own IDA2714f558 исследовала точный output и закрыта/saved=true. Raw disasm —
ignored artifacts/client455-startup/own-winmain.json. Перед каждым запуском
script сверяет хеш PE/MAP, символ WinMain, CALL и instruction bytes границы.

## Runtime providers и реальные входы

audit_client455_startup.py разбирает regular и delay-load descriptors,
имена/ordinal imports и exports PE32 providers. Все15групп имеют нужные имена.
Отложены MSS32.dll, ABuse.dll, Adv.dll, PDLL.dll. Само наличие имени не
доказывает ABI/поведение; выполненные вызовы отмечены отдельно.

Для lab обычные DLL берутся из SysWOW64, пользовательские delayed DLL
копируются из reference client. Фактически загруженные eager providers и
Miles сверены с audit по SHA. Исходная установка не меняется, runtime workingdir
находится под work/m9/39062b2c/startup002. В lab находятся собственный output,
копии runtime DLLs, WaveList.spt513339байт, mssmp3.asi и собственный R3Engine.ini.
Пользовательские аккаунты и конфигурация не копировались. DLL/asset bytes не
публикуются и находятся только в ignored work/.

Root DataTable/cryp.dat иadvr.dat, которые вызывает legacy WinMain, отсутствуют.
Настоящие кандидаты найдены в DataTable/ko-kr:38384 и20104байт. Их пути/хеши
сохранены в startup-audit.json. Они ещё не переименованы/скопированы в корень:
сначала нужна проверка locale selection эталона455. ABuse/Adv/PDLL в этом
прогоне не достигнуты и не загружены. Полная совместимость этих DLL открыта.

## Запуск и наблюдение

game-automation применён для изолированного запуска/логов. CDB не установлен;
собственный небольшой Win32 debugger собран современным MSVC. Он создаёт
только указанный staged OWN процесс через DEBUG_ONLY_THIS_PROCESS, не
подключается к другим приложениям и владеет его handles/PID.

Два временных software breakpoint находятся в памяти ребёнка: WinMain и
после InitR3SoundSystem. Первый восстанавливает byte/EIP и продолжает код;
второй фиксирует EAX и завершает только собственный процесс до D3D. Disk PE
не патчится. Лимит наблюдения20секунд, аварийное завершение ограничено по
времени; exit event наблюдается до закрытия handles.

Точный staged output прошёл CRT/global initialization, дошёл до обычного
WinMain, выполнил InitR3Engine/ForceFullScreen и настоящий sound path, который
вызывает AIL_startup, AIL_set_preference, LoadWaveList и AIL_open_digital_driver.
InitR3SoundSystem вернул1; source возвращает это только при ненулевом driver.
Эти результаты не требуют успешных фиктивных providers.

Достигнут marker0xB3CED, затем наблюдён planned exit0xE0434200. Графический
InitR3D3D/Create и основной network stage не достигнуты; игровой графический
window не создавался, ввод/фокус не управлялись. Полный shutdown не проверен:
это намеренное завершение ограниченного раннего прогона, а не нормальный exit.

В runtime зарегистрированы first-chance события40080201, E06D7363 и406D1388.
Debugger передал их приложению как DBG_EXCEPTION_NOT_HANDLED; runtime их
обработал и дошёл до успешного marker. Second-chance нет. Эти события не
выданы за отсутствие исключений или за доказательство всех error policies.

Raw events и все loaded modules — ignored JSONL в lab с SHA. Компактный
manifest содержит actual provider checks, markers, helper/source hashes,
inputs и результат: inventory/client455-startup-native.json. Проверка
checkpoint_client455_startup.py заново сверяет imports/exports, реальные DLL
файлы, exact output/lab inputs, instruction boundaries, trace и наблюдённый
exit. inventory/client455-startup-checkpoint.json имеет PARTIAL.

## Границы и следующий шаг043

Успех early path не является сверкой всей startup семантики455. Содержимое
WaveList и полный mapping, sample playback, codecs/music/3D audio ещё не
приняты. Header/API совместимость Miles подтверждена только достигнутыми
startup вызовами. Окно/D3D/Create/launcher/локализованные данные, UI/network/
gameplay и normal shutdown остаются открытыми.

Для следующего запуска нужно обеспечить контролируемый оконный lab режим:
Release WinMain вызывает ForceFullScreen и переопределяет ini FALSE до D3D.
Lab override не выдавать за восстановленную production семантику455. Сначала
проверить target455 startup/config/locale, затем actual normal D3D callbacks и
Create с настоящими ресурсами. Отсутствие.rsrc и engine icon RC остаются
отдельным вопросом callers, не объявленным доказанным startup blocker.

Production PE не менялась, поэтому прежние большие и короткие renderer/model
runtime suites не повторялись. Нужное новое доказательство — именно реальный
ранний запуск полной PE, не очередной подсчёт прежних assertions.

Повтор через scripts/Invoke-Python.ps1: audit_client455_startup.py,
probe_client455_startup.py, checkpoint_client455_startup.py. Запускается только
собственный output, из отдельного lab, без серверов и изменений originals.
