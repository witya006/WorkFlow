# Ближайшие действия — только клиент

Обновлено2026-11-09.

113 PARTIAL: в actual CCharacter/CPlayer восстановлены internal flags,
any/none и ordinary IsDeath guard; selected64bit control producer подключён
до преобразования статуса.173 целевые native проверки PASS; source clock
проверен на actual Avatar,полный movement/SetAction pipeline ещё открыт.
Новая own PE4c81042a…/entry1616c0/182client-20kernel-65facade/unresolved0/Create1.
Свежие status62/message83/center69/6hover и15 просмотренных GPU кадров;
10 center/hover кадров побайтно равны111. Engine67/decoder112 неизменены.
Уточнён реальный UI owner: три CGUINuclearBomb внутри существующей MiniMap,
а не отдельный dialog. Их source integration и обычный Nuclear receiver
остаются открытыми. Далее114 — marker owners/transforms/records,затем
group60/result branches/selection/send. Runtime gate113 current;111 и112
runtime assertions historical. M6/M6F/M7/M9 OPEN.

[Доказательства113](../research/client455-character-flags.md).

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

## Проверяемое текущее состояние

Текущий gate: inventory/client455-character-flags-checkpoint.json.
Команда: scripts/Invoke-Python.ps1 scripts/checkpoint_client455_character_flags.py.
Подробно: research/client455-character-flags.md;reference30ranges/29pcode/
14fullasm/760instructions+2EHtails/actual CPlayer,MiniMap,NuclearBomb RTTI,
оба x86 pins/base400000. Primary b1b5febf…/secondary46528aac….
Own PE4c81042a5a001d6a99ac33859061ae00ce6a55028da11797f7e3d845bb444393,
2197504bytes/entry1616c0/WinMainb9060/afterCreateb91d4,182/20/65/unresolved0.
173checks:8masks/16actionhighnibbles/8callback traces/actualAvatar/any-none/
clockbeforeOR/repeatedbit1/clockwrap/ordinary64bit setter. Trace actions use
kernel callback,not full loaded animation/effect/SetAction/movement pipeline.
Clock bit1 producer has actual lab calls,ordinary action caller/consumer absent.
Native:work/m9/cbbfcf95/character-flags-001. Fresh status62:82e752ae;
message83/5GPU:1f581f89;center69/4GPU:86a6aea7;6hover:bf9ece2f.
15fresh GPU viewed,10center/hover byteequal111;exactPE Create1:4c81042a.
Engine67 unchanged546a7529b51139e856b1a108fcad7849c14b2d00563b7abbfdcc8db10026fa5a;
033baseline present,082derivedsnapshot still absent. Chat385 historical109,
BSP29 historical108;magic36/resources66/runtime573/audio157/account/hotbar7/
storage3 historical107. Decoder2429 historical112 unchanged,no bulk159k/world/
audio/other32GUI reruns. Runtime111 gate historical;pre113 reports preserved.
IDA recovery1f253126 savedclosed/list0 after expired7760fad4 was confirmed absent.
Normal Nuclear receiver and MiniMap source markers remain unconnected.
C1A/fullobject CE7/order/ordinary message entry from111 remain verified in the
selected regression domain;full Login/auth/Tutorial/gameplay acceptance absent.
Full Character flags/SetAction/64bit status sideeffects and privateABI open.
Component112 checkpoint is historical for the old runtime111 PE;do not rerun
its unchanged-runtime assertion as a current runtime gate. Decoder source proof
remains valid;details research/client455-nuclear-protocol.md.

## Следующая очередь

1. Работа114: actual MiniMap owns3 CGUINuclearBomb. Завершить подтверждение
   layout/transform producers и virtual frame roles,перенести marker owners/
   record lookup в существующее окно. Не создавать выдуманный nuclear dialog.
   Затем обычный CNetMsgProcessor_Nuclear/group60: decoder112/core111 готовы;
   actual Character guard доступен113,но полная action pipeline ещё открыта.
   Сохранить result0/1/2/error/blocked,selected board item serial и actual send.
   Остальные opcodes/registry32/frame/draw и bit1 movement-controller producers
   обязательны;не объявлять их закрытыми по native173.
2. Nuclear command/response/list/finalposition,прочие input cancellation и
   fullworld placement/light/qualityUI/blur/advancedFX/device lifecycle.
3. Actual Tutorial/common UI/board/Avatar/Create/camera/QBI47/fourstage factory,
   полный Login/auth/game flow;оставшиеся Linker handlers/queue/Macro/Vending/
   inventory/equip/SF/Animus/Quest/36boards/Trunk/client protocol.
4. Закрыть остальные M6 gaps и матрицу полноты M6F,закрепить M7 и выполнить M9
   по client-acceptance.md. Компиляция/Create1/узкий lab не завершают цель.

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

Прежняя полная память/очередь: [before113](../research/next-steps-before113.md).
