# M6 launcher049 — входные данные launcher перед языковой инициализацией

06.11.2026. Только клиент. Оригинальные EXE не исполнялись. Серверы не
изменялись. Все входные профили в проверках синтетические и offline; реальная
аутентификация не выполнялась.

## Подтверждённый эталон

Основной x86 PE SHA256
`b1b5febf0d0394712e2322350e19dafe60742e8642697b93cfb89135bac1fd8b`,
дополнительный
`46528aac20499e3b3928d58658d7e0cefe26feba7cd193796d5cfbf7a2bbc558`,
imagebase0x400000.19диапазонов функций и11полных countryETCAction vtables
совпали поSHA. [Метаданные](../inventory/client455-launcher-reference.json).
IDA sessionf2fdf71d работала с work-копией IDB,closed/save=true. Псевдокод,
slotmatrix и инструкции сохранены в ignored artifacts/client455-launcher/.

WinMain VA7D04E0/RVA3D04E0 вызывает ETCAction slot196 после nation и перед
language. У9стран это8392E0/RVA4392E0; Russia836CB0/RVA436CB0 и
Europe83B4F0/RVA43B4F0 получают CRTargc/argv. Europe временно копирует строку
в CString; DNSresolver там отсутствует,далее тот же inet_addr.

CCRloader zeroes93bytes и читает93из `System/DefaultSet.tmp` через
CreateFile(GENERIC_READ,share0,OPEN_EXISTING). ReadFile result не проверяется;
лишние bytesигнорируются. XORoffsets и размеры подтверждены инструкциями:

| Offset | Содержимое | XOR |
| --- | --- | --- |
| 0 | DWORD IPv4 | CB9C4B3A |
| 4 | WORD port | 4FB6 |
| 6 | char identifier[51] | без преобразования |
| 57 | DWORD account | 6E65E0AF |
| 61 | 4×DWORD keys | CFCF22E6,5BBCDE6F,ACDF5EDA,BCCD1B37 |
| 77 | WORD worldindex | lowWORD(CB9C4B3A)=4B3A |
| 79 | DWORD personalreference | C89C183A |
| 83 | DWORD premium | файл игнорируется,принудительно0 |
| 87 | DWORD modevalue | D29C283B |
| 91 | WORD nation | 32D7 |

Target вызывает setter endpoint1/id/account/keys/worldindex/premium ещё до
сравнения nation с текущей страной. При несовпадении возвращает0. При совпадении
modevalue==1 задаёт отдельный mode3,а personal=(reference==account).
Семантика полного downstream UI/network пока не сертифицирована.

Россия/Европа требуют argc==5: argv1IPv4,argv2port,argv3identifier,argv4password.
Выбирается endpoint0,inet_addr и atol→WORD. InvalidIP и отрицательный/вышедший
заWORDport не отклоняются отдельной валидацией. Эти пути не задают account/
masterkeys/premium/mode. Helper5E5920/RVA1E5920 zeroesdest и копирует максимум
capacity−1: identifier50bytes в51,password32в33. Никакой перекодировки.

## Source и границы переноса

Добавлен source-owned RF455LauncherConnection и CCR/argument loaders. Все
разобранные поля сохраняются. В valid-input области API воспроизводит
decodedvalues. Bounded stringscan/size0guard и отсутствие небезопасного
чтения строк за буфером отличаются от unsafe/OOM доменов455.

Normal WinMain теперь вызывает настоящий CMainApp.GetDataFromLauncher между
nation и language. Старое повторное чтение поздно вCreate удалено. Bridge
публикует endpoint/id/password(ifargv)/account+keys(ifCCR) реальному member
CNetworkMgr. Его storage51/33 и setter boundaries теперь согласованы с455,
Init использует sizeof. Worldindex/personal/premium/mode остаются в455state;
потребители ещё обязательны к восстановлению.

При rejectedCCR ownbridge не публикует decodedvalues в network member,
тогда как455уже вызывает рядsetters. Это явно оставшийся error-sideeffect gap.
Политики MessageBox/errorlogging и старыйCRT/nonASCII/atoi overflow domains
не объявлены полностью эквивалентными. FullETCAction factory не подменён
фиктивным provider. Основной network bootstrap/connect ещё старый.

Legacy sender structs пока используют max_id_len12/max_pw_len12 и memcpy13.
Они не объявлены протоколом455. Новый storage50/32 не доказывает готовый
wire/auth; перенос пакетов обязателен перед игровой приёмкой.

После удаления позднего блока современный MSVC свернул Create вWinMain.
Явный __declspec(noinline) сохраняет разовую production init boundary для
диагностики. Return/ветви не подменяются;this не переинтерпретируется.

## Сборка и проверка

RF_Online.bin SHA256
`a64601c891cade91395fa285945320c115d15aa7621258391b4571e0112dd64a`,
x86/base400000/entryRVA148860,2001408bytes.182client/20kernel/17facade,
0unresolved,без CharacterMR или /FORCE. Derivedengine879f9b75... и033base
не менялись.

`probe_client455_launcher.py` линкует normalobjects с собственным entry.
Три процесса Korea/Russia/Europe проверили реальный ordinary GetDataFromLauncher
и member network setter/getter API черезcompiler-typedmember pointer. Сеть
не создавалась,connect не вызывался,все процессы естественно exit0.

Проверены9CCRcountryprofiles,19boundaryshortreads,missing/exclusive-sharing/
extra-tail cases,nation mismatch,argc bounds,inet/port casts,50/32 byte strings,
сохранение password вCCRветке. Fixtures не содержат реальных пользователей или
ключей. [Отчёт](../inventory/client455-launcher-native.json); labswork/m9/a20f2085.

Точная ownPE отдельно прошла обычный WinMain:

- Korea:DataRoot→Launcher:ccr:1→NDLanguage949→engine/Miles1;
- Russia:DataRoot→Launcher:argv:0→NDLanguage1251→engine/Miles1.

Own debugger передаёт rawcommandline только из явно staged labfixture
`launcher-commandline.txt` собственному child черезCreateProcess,безshell.
К реальным account/launcher-файлам не обращается. Подмена auth/return/ветвей
не выполнялась. Порядок проверен фактическими debug events,не только исходниками.

Новая граница — после CALL существующего CMainApp.Create. Ownentryaudit
декодирует реальный CALL иследующую инструкцию,без фиксированныхoffsets.
Create вернул EAX1 вownRVA B3DB4,CALL B3DAF,targetB3440. Latest
work/m9/a64601c8/ui-startup001: ready1/windowed1/render32,device53E4B80 равен
Characterdevice,ownerA6A36F0. Затем controlledstopE0434200 до фильтров/игрового
цикла. Это не naturalexit/full455Create/UI/вход. `--after-create` заменяет
прошлый `--before-launcher`; marker after_client_create.

Прежние font/sprite кадры совпали побайтно с048;короткие model/effects/shadow/
clock/accounting/lifecycle сценарии прошли.16scoped checkpoints PASS/PARTIAL,
большие исторические suites не повторялись. M6/M6F/M7/M9 открыты.

## Дальше

050: FG_CB/USEFG7D0CD0,instance policy7CF8A0,client NetworkMgr.Create7D10A0 и
Connect7D1150→562350,packet/statecontracts. В455 network/connect стоят перед
engine;вownклиенте это ещё не перенесено. Начать сoffline client transport/
packetfixtures,не создавать фиктивный authsuccess и не разрабатывать серверы.
Затем targetmanagers/video/fullUI/login/game tables;FT/ANSI/IME/layout/ILevel/
world/shutdown остаются обязательными M6.

Повтор: audit_client455_launcher;prepare/build normal;normalconsumers/link;
probe_client455_launcher;ownentry/startupaudits;startup/contracts/device/
--create/--after-create;font/lifecycle/sprites;shortdependent probes;scoped
checkpoints. ВсеPython через scripts/Invoke-Python.ps1.
