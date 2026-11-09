# Память проекта

Обновлено2026-11-09. Root E:\RFOnlineTrash\Source\WorkFlow.
Предыдущая длинная память сохранена полностью в
[research/project-memory-before111.md](../research/project-memory-before111.md).

## Цель и ограничения

Только клиент RF_Online.bin и его R3Engine/asset dependencies. /Goal M9 уже
определён: финальная приёмка полного функционала/поведения pinned455 без
модернизации графики. M0–M4 diagnostic и выбранный M5 завершены; M6/M6F/M7/M9
открыты, M8 не требуется. Не переуточнять M9 по устаревшему тексту Goal.
Серверные исходники только читать;не менять,не собирать и не восстанавливать.
Originals immutable,input EXE не исполнять. Работать в own copies под work/.
Git локальный,remote/push/publish не разрешены. Субагенты не разрешены.
Python через scripts/Invoke-Python.ps1. Проверять изменённый участок и его
зависимости;159173 assertions не являются запросами к ИИ и не нужны каждый раз.
Число проверок не показатель полноты. Raw assets/IDB/traces в ignored work/
artifacts/; ignoring не backup. Источник истины — файлы,хеши и текущие результаты.

## Последний проверенный результат

111 PARTIAL: обычный formatter подключён к actual Login и четырём панелям
чата/центру экрана. Обычный typed hover у настоящего Avatar с pending1 теперь
отменяет реальный прицел/звук,обнуляет координаты и выводит C1A до item mutation.
83 целевые проверки с реальным EDF предметом/BSP/6effects/Miles проходят.
Новая PE031df367…/entry161590/182client-20kernel-64facade/unresolved0/Create1.
Свежие center69/status62 и15 просмотренных GPU кадров;10 center/hover побайтно
равны109. InsertText455 теперь удержан обычной PE. CE7 core проверен вlab,
но его game-action registration ещё нет и helper удалён ordinary linker.
Gate111 current,109 historical. Tutorial только routing kernel;полные stages/
Login/auth/chat UI и прочие client-acceptance gaps открыты. Далее112 — привязка
начала прицеливания к обычному игровому действию. M6/M6F/M7/M9 OPEN.

Текущий gate: inventory/client455-message-dispatch-checkpoint.json.
Команда: scripts/Invoke-Python.ps1 scripts/checkpoint_client455_message_dispatch.py.
Подробно: research/client455-message-runtime.md; target spec110:
research/client455-message-dispatch.md и inventory/client455-message-dispatch-reference.json.
22functions/22fullasm/1254instructions,22bodies+46-byteEHregion,23decodedcalls
совпадают на двух x86 pins/base400000. Primary b1b5febf…/secondary46528aac….
Own PE031df3676c9bed977f660d79fe535666af9cb52cfc4e5b1a61b3f04841df831c,
2197504bytes/entry161590/WinMainb9060/afterCreateb91d4,182/20/64/unresolved0.
Обычные formatter/InsertText455/typed-hover C1A и Login Draw удержаны linker;
decoded own CALLS подтверждают Clear→message и center→common.
Native83: work/m9/5e84374d/message-output-001;5GPU/1184-4375-1916-4401-0pixels.
Actual MainApp context с настоящими MainGame/Login/UIScreen и manually bound
providers в offline lab,actual Avatar/status2/EDF item/inventory icon/BSP/Miles6FX.
Это не полные ordinary factory/Create_UI/Login/auth/world flow. Tutorial2 только
kernel с actual MainGame boards; actual Tutorial/fourstage factory пока нет.
CE7 request-clear→message→start и repeated-arm сохранены,но game action producer
не подключён,helper удалён ordinary PE. Не объявлять это полным началом прицела.
Center69/player-status62/6hover/Create1 свежие;15GPU просмотрены,10center/hover
побайтно равны109. Chat385/288records/8scripts — historical109,BSP29 — historical108;
magic36/resources66/runtime573/audio157/account/hotbar7/storage3 — historical107.
Неизменённые большие159k/world/audio/остальные32GUI не повторены. Engine67
546a7529b51139e856b1a108fcad7849c14b2d00563b7abbfdcc8db10026fa5a неизменён;
033baseline сохранён,082snapshot по-прежнему нет. Gate109 historical,before111
snapshots сохранены. Ошибочные lab attempts не выданы за final83 run.

## Следующая работа

1. Работа112: получить target callers/registration callback RVA1c5ab0 и
   подключить начало прицеливания к обычному игровому действию. CE7 core и его
   effect/Miles/message цепочка уже готовы; не повторять исследование110.
2. Nuclear command/response/list12/finalposition,прочие input cancellation и
   fullworld placement/light/qualityUI/blur/advancedFX/device lifecycle.
3. Actual Tutorial/common UI/board/Avatar/Create/camera/QBI47/fourstage factory,
   полный Login/auth/game flow; оставшиеся Linker handlers/queue/Macro/Vending/
   inventory/equip/SF/Animus/Quest/36boards/Trunk/client protocol.
4. Закрыть остальные M6 gaps и матрицу полноты M6F,закрепить M7 и выполнить M9
   по docs/client-acceptance.md. Компиляция/Create1/узкий lab не завершают цель.

## Сохраняемые gaps

Обязательные границы:14filter UI/colors/GM/category7 sideeffects,input/send/
IME/save/legacy chat callers и numeric _SetSystemMsg(DWORD) пока не перенесены.
Точные country paths en-gb/Csea.txt,en-us/Csua.txt,th-th/Csth.txt отсутствуют;
не подменять похожими именами. Taiwan UTF16BOM byte-lexer fallback13/defaults,
DBCS prefixes и signed masks — сохранённые особенности,не исправлять молча.
Full Login/secondary UI,actual Tutorial и legacy uncreated-stage teardown,
shared lifecycle/reset,CRT startup,privateABI,unsafe/null/OOM/FP/overflow/
concurrency/shutdown остаются открыты. Новая cap1024 safety boundary и ready
provider checks не принимают unsafe domain. Все прочие известные gaps сохраняются
в client-acceptance.md,client-features.json и подробных research;ничего не снято
из конечной цели. Серверы не являются блокером клиентского восстановления.
