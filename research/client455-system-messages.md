# Системные сообщения455 — исследование108, реализация ещё открыта

2026-11-09. Native IDA MCP `ffcaa552` saved/closed/list0.21 выбранная полная
функция:17 полных disassembly/2284 instructions и4 короткие функции с полным
pseudocode.21 диапазон совпадает в обоих закреплённых x86 binaries,base400000:
`b1b5febf0d0394712e2322350e19dafe60742e8642697b93cfb89135bac1fd8b` и
`46528aac20499e3b3928d58658d7e0cefe26feba7cd193796d5cfbf7a2bbc558`.
Сырой вывод: `artifacts/client455-progress/messages108-reference.json`;
hashes/RVA/размеры: `inventory/client455-system-messages-reference.json`.
Это статическое исследование, не новый runtime gate и не приёмка сообщений.
Текущий runtime gate остаётся107.

## Установленный порядок и обнаруженное расхождение107

| RVA | Что делает455 |
| --- | --- |
| `0x14a242` | MainGame.FrameMove вызывает center-message Update |
| `0x14a360` | Позже обновляются обычные эффекты |
| `0x14b034` | MainGame.Render вызывает UI virtual slot40 |
| `0x14b059` | Затем вызывается Frame контейнера ядерного прицеливания |
| `0x14b065` | Затем center-message Draw |

Собственный107 hook сейчас стоит перед FrameMoveAllEffectsList в foreffect.cpp.
Это **подтверждённое расхождение**: целевой controller Frame нужно переместить
в конец успешной ветки CGP_MainGame.Render, после UI Draw. Не включать его
одновременно в обе фазы. Полный мировой pipeline всё равно остаётся открытым.
Старый107 gate подтверждает20-byte core, выбранный BSP/Miles lab и сборку,
но не доказывает этот порядок; его full_world_frame_order=false остаётся верным.

## Владелец экранных сообщений

Ctor RVA1459e0 вызывается конструктором MainGame; destructor RVA14d7e0 — его
деструктором. Владелец содержит две list12: очередь64-byte chunks и активные
84-byte records. Ctor/dtor регистрируют/снимают singleton C0BD60 через
RVA14dd80/14dda0. До переноса уточнить точный source lifetime/field placement.

Активная запись:float x0/y4;text60@8;colorDWORD68;timeDWORD72;scaleFloat76=1;
alphaFloat80=0. Путь Add RVA5b1a0 показывает короткий текст сразу только при
пустой pending queue и strlen<=59, иначе режет его на59-byte chunks с настоящим
CRT `_mbsnbcpy` (RVA b1d0). Буфер60 заранее обнуляется. Нельзя резать UTF-8
или произвольно делить DBCS последовательность вместо этого контракта.

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

Далее: реализовать owner/queue/update/draw и stage lifecycle, исправить late
aiming hook; восстановить chat/style/wrapping и полноценный dispatch; затем
подключить live pending1 hover с реальным эффектом/звуком/локализованным сообщением.
После этого остаются command/response/list12/final position и все прежние
`docs/client-acceptance.md` gaps. M6/M6F/M7/M9 открыты. Входные EXE не исполнялись,
серверы и оригиналы не менялись.

Проверка: `scripts/Invoke-Python.ps1 scripts/audit_client455_system_messages.py`.
