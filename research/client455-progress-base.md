# Progress-base055: обычный базовый цикл этапов клиента

2026-11-06. Только клиент. M6/M6F/M7/M9 открыты.

Эталон x86/base400000 SHA-256
`b1b5febf0d0394712e2322350e19dafe60742e8642697b93cfb89135bac1fd8b`,
backup `46528aac20499e3b3928d58658d7e0cefe26feba7cd193796d5cfbf7a2bbc558`.
18 function ranges совпали между pins. Owned IDA3bc31778 закрыта/save=true;
входные EXE не запускались. Raw в ignored artifacts/client455-progress-base/.

В обычный CGameProgress перенесён подтверждённый базовый контракт:

| RVA455 | Контракт |
|---|---|
| 138F70 | Init очищает четыре BOOL, сохраняет DWORD следующего этапа |
| 138FB0/138FD0 | Create/Destroy возвращают1 без вызова LoadData/UnloadData |
| 13F6B0/3D1470 | Set/Get next DWORD по target offset20 |
| 13F6D0 | Установить exit BOOL |
| 138FF0 | Input; если exit — return1; иначе FrameMove,Render,сброс particle counts,return0 |
| 157B60 | Title constructor задаёт next1 после Init |

Собственный базовый класс теперь24байта x86 с явными SetNextStage455,
GetNextStage455 и RequestStageExit455. Init не трогает next. Собственный
constructor задаёт nextFFFFFFFF для безопасного начального состояния;
оригинальный base constructor оставляет next неинициализированным. Это
разница вне проверенного Set/Get/Init домена, а не доказанная эквивалентность
первого чтения исходного неинициализированного поля.

В MainLoop нет условного вызова Render по активности окна. Сохранён owned
source API MainLoop(BOOL), но аргумент не используется базовым телом. Target
оригинальная функция такого аргумента не имеет; это source port, не overlay
оригинального объекта. Focus/device/render поведение конкретных stages
требует отдельной приёмки.

Если InputProcess запросил выход, FrameMove/Render/reset пропускаются.
Если выход запрошен в FrameMove, текущие Render/reset всё равно выполняются,
цикл возвращает0, а выход будет замечен после следующего InputProcess.
Возвраты Input/FrameMove/Render игнорируются. Старый дополнительный вызов
после reset отсутствует в pinned455 body и удалён из обычного базового цикла.

RVA139050 обходит vector records7836 и очищает count7832 каждого типа.
В текущем source пока fixed1024 particle owner; используется его реальный
ResetParticleCount. Общая операция сброса проверена, новая динамическая
организация владельца455 ещё не перенесена. Полную particle parity не заявлять.

Native probe слинкован с настоящими182client objects и текущими библиотеками.
Подкласс задаёт только виртуальные входы/кадр/отрисовку и фиксирует их порядок;
вызван настоящий CGameProgress::MainLoop из cgameprogress.obj. Проверены оба
значения active, input/уже установленный/frame exit, ошибка возвратов virtual
методов, сохранение5значений next через Init, отсутствие Load/Unload в base
Create/Destroy, реальный Title constructor next1 и настоящие particle counts
в начале/середине/конце массива. Процесс естественно завершился0.

Полная собственная RF_Online.bin SHA-256
`5302f71a07bb7b895971dc18e43ae676d2901aeaf7fa737d79d9d0c86144d8b5`,
x86/base400000/entry14A750/2012160bytes;182client/20kernel/22facade,
0unresolved. Engine033 и startup library не менялись. Точная PE сохранила
настоящий TCP→engine/Miles/D3D/Character/existingCreate=1; остановка до цикла.
Russian profile по-прежнему beforeConnect; endpoint0/1 не перенаправляется.

Полная фабрика по-прежнему legacy3/modulo. Поле next теперь восстановлено,
но его чтение обычным MainApp для переходов ещё не подключено. Перенос ID2
в Tutorial должен идти совместно с настоящим Tutorial/Avatar и основным ID3,
чтобы не направить основной мир в учебный message dispatcher. Текущие
Title/Create/Input, LoginUI и полный игровой цикл ещё не приняты.

В raw дополнительно сохранены семь Tutorial методов. Видны отдельные Create/
Destroy/FrameMove/LoadData/UnloadData/device/input сценарии, race-selected
camera и стартовые координаты. Это зависимости будущего переноса, не готовый
Tutorial. Decompiler local arrays/скрытые this требуют проверки инструкциями;
последняя страница TutorialInput сохранена отдельно.

Доказательства: inventory/client455-progress-base-reference.json,
client455-progress-native.json и client455-progress-base-checkpoint.json.
Воспроизведение через scripts/Invoke-Python.ps1: audit_client455_progress_base.py,
обычные prepare/build/consumers/link/own-entry/startup, затем
probe_client455_progress.py и checkpoint_client455_progress_base.py.
Никаких серверных изменений и фиктивного входа нет.

Все21 текущих scoped checkpoint scripts завершились0/PARTIAL. Короткие
зависимые runtime probes обновлены; большие неизменённые исторические
kernel/math suites не повторялись. Owned native процессов после проверок нет.
