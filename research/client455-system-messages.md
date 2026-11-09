# Экранные сообщения455 — работа108, полный dispatch ещё открыт

Дополнение110: профиль/selected insertion109 готовы; полный dispatch/callers
исследован в [client455-message-dispatch.md](client455-message-dispatch.md).
Следующий перенос111; старый runtime108 здесь исторический,текущий gate109.

2026-11-09. **PARTIAL, M6.** В ordinary MainGame восстановлены владелец сообщений,
очередь/движение/fade/medium GDI Draw. Прицел перенесён в late Render после UI.
Full C1A/chat/live hover открыты; игровых message producers ещё нет.

Native IDA MCP `ffcaa552` и`20210106` saved/closed/list0.25 полных выбранных
функций:21fullasm/2914instructions и4 коротких с полным pseudocode.
25 диапазонов совпадают в обоих закреплённых x86 binaries,base400000:
`b1b5febf0d0394712e2322350e19dafe60742e8642697b93cfb89135bac1fd8b` и
`46528aac20499e3b3928d58658d7e0cefe26feba7cd193796d5cfbf7a2bbc558`.
Сырой вывод: `artifacts/client455-progress/messages108-reference.json` и
`messages108-implementation-reference.json`;
hashes/RVA/размеры: `inventory/client455-system-messages-reference.json`.
Текущий gate:`inventory/client455-center-messages-checkpoint.json`.
107 runtime gate исторический;его snapshot сохранён до изменения текущих reports.

## Установленный порядок и исправление расхождения107

| RVA | Что делает455 |
| --- | --- |
| `0x14a242` | MainGame.FrameMove вызывает center-message Update |
| `0x14a360` | Позже обновляются обычные эффекты |
| `0x14b034` | MainGame.Render вызывает UI virtual slot40 |
| `0x14b059` | Затем вызывается Frame контейнера ядерного прицеливания |
| `0x14b065` | Затем center-message Draw |

107 hook стоял перед FrameMoveAllEffectsList. В108 он удалён из foreffect и
ровно один раз вызывается в конце успешной ветки CGP_MainGame.Render после UI
и перед center Draw. Center Update добавлен после GBM.FrameMove до effects.
Dumpbin декодировал текущую own PE;каждая инструкция сверена с её байтами:
own CALL RVA:centerUpdate262dd <effects265f8,lateaiming27207 <centerDraw27212.
Старый FrameMoveEffect не вызывает nuclear Frame. Сохранены disassembly и
hashes выбранных own function ranges. Полный world pipeline этим не доказан.

## Владелец экранных сообщений

Ctor RVA1459e0 вызывается конструктором MainGame; destructor RVA14d7e0 — его
деструктором. Владелец содержит две list12: очередь64-byte chunks и активные
84-byte records. Ctor/dtor регистрируют/снимают singleton C0BD60 через
RVA14dd80/14dda0. Дополнительный проход подтвердил target member+177440
(0x2b520). Свой member создан после UI members;проверены настоящий MainGame
ctor/dtor и bind/unbind. Modern STL не объявлен старым24-byte private ABI.

Активная запись:float x0/y4;text60@8;colorDWORD68;timeDWORD72;scaleFloat76=1;
alphaFloat80=0. Путь Add RVA5b1a0 показывает короткий текст сразу только при
пустой pending queue и strlen<=59, иначе режет его на59-byte chunks с настоящим
CRT `_mbsnbcpy` (RVA b1d0). Буфер60 заранее обнуляется. Правила зависят от
ambient CRT multibyte mode,а не автоматически от NDLanguage codepage.
В SBCS корейские bytes могут делиться,в режиме949 неполная DBCS пара переносится
в следующий chunk. Оба режима проверены;стенд восстанавливает исходный.
Production не меняет CRT mode. Не подменять это Unicode/UTF-8 splitting.

Update RVA14d900 переносит не более одного chunk в active за вызов: если active
пуст, либо возраст самого нового active>500ms, либо pending queue>5. Active
ограничены тремя, старейший удаляется при переполнении. Обход для движения —
от новых к старым; Draw RVA14dcb0 — от старых к новым.

Множитель движения — float(loopTime*4.5), без clamp. Новая строка стремится к
scale1, прочие к0.8; targetY=200-index*fontHeight, X центрируется с учётом scale.
До возраста3600ms alpha target=1-index/3, затем0. Цвет получает alpha из текущего
float*255. Из active удаляется максимум одна старейшая строка за update, только
если age>3600ms и alpha<=0.01. Draw использует flags0x80000010 и scale записи.
FP/переполнение времени/нулевые строки/OOM должны сохраняться или быть явно
непринятыми доменами, а не молча менять правила.

В прежнем decompiler prototype8C6380 скрыт четвёртый аргумент. Full asm
подтвердил flags80000010 и выбор medium16pt font для metrics/Draw. Добавлены
helpers выбора metrics и ANSI scaled Draw;main-font APIs не менялись. Draw
каждой строки отключает Z,затем включает,как target wrapper8C6020.

## Полный путь C1A

RVA1e47a0 форматирует общий буфер; в stage вне0/1/2 направляет его в center
с цветом `0xffcc1f00`, затем всегда вызывает common dispatch RVA1e4a60.
Тот использует настоящий login sink в stage1; отдельные счётчики header в
stage3 и Tutorial2; stage3 обычно выбирает style2, category3.

Chat InsertText RVA345b80 в455 имеет четыре панели,14 message categories,
style records по18bytes и отдельный wrapping RVA346020. Legacy chat overload
с тремя параметрами не воспроизводит эту цепочку. Нужен перенос этих providers,
а не запись текста в отдельный журнал вместо экранного поведения. NDLanguage
provider уже существует; C1A/CE7 нужно читать по его подтверждённому индексу.

## Реальная проверка108

69 checks:actual MainGame member и offline network.Create без Connect,реальные
NDLanguage C1A/CE7,GDI/D3D9;84/64-byte records,capacity3,два CRT режима,
500/501ms,flood>5,3600/3601ms,одна eviction/update,unsigned age,unclamped factor.
Medium metrics сверены независимыми Win32 calls с фактическим16pt font.
Просмотрены4GPU кадра:C1A/queued/fading/cleared,pixels1673/4455/4236/0,
финальный drain6ticks. Readback использует реальный640×480 viewport без20px
backbuffer margin. Run:`work/m9/f8d36a53/center-messages-001`.
Это прямой Add в реальный stage member,не запуск полного C1A dispatcher.

Создание MainGame требует готовый клиентский network manager;стенд вызывает
обычный Create. Выявлен старый gap:Destroy не созданного stage возвращается
до удаления других allocations Init. Center records/registry освобождены;
полный stage teardown и глобальный memory balance не заявлены.

Own RF_Online.bin SHA-256
`5ad0b484484113803e2620a0a46eb91dd0ec11d918cf9e72cde5bc39a3d87c02`,
2160128bytes,x86/base400000,entry15b6d0,WinMainb8f30,afterCreateb90a4;
182client/20kernel/61facade,0unresolved,Create1. FrameMove/Draw retained;
Add без игровых producers удалён linker. Engine546a7529…/67 unchanged;
033baseline сохранён,старого082derived snapshot нет.

BSP/Miles29/status62 проверены заново;6 fresh hover frames viewed/byteequal107.
Неизменённые magic/resources/effect-runtime/tagged-audio/account/hotbar/storage
reports оставлены historical107,а не current runtime acceptance. Большие159k/
world/audio suites и остальные32GUI не повторены.

## Далее109

Восстановить4pane chat/category14/style18/wrapping346020,data providers и
lifecycle,common5E47A0/5E4A60 с login/Tutorial sinks,затем C1A/CE7 callers иlive
pending1 hover с реальными effect/sound/message. Pending1 пока явно отказывает
до мутации;center-only не является полным dispatcher. Затем command/response/
list12/final position ипрочие cancels. Все прежние client-acceptance gaps
обязательны:world/lighting/qualityUI/blur/advancedFX/device/font reset,stage
teardown,privateABI/FP/OOM/CRT startup/concurrency/unsafe. M6/M6F/M7/M9 OPEN.
Входные EXE не исполнялись,оригиналы/серверы не менялись,публикации нет.

Проверка: `scripts/Invoke-Python.ps1 scripts/checkpoint_client455_center_messages.py`.
