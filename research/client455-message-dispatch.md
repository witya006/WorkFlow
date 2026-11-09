# Общие сообщения и их реальные производители — исследование110

2026-11-09. **AUDIT_OPEN**, клиент455. Это подготовка непосредственного переноса
в обычный клиентский source111, не новая runtime acceptance. Последний runtime
gate остаётся109, `inventory/client455-chat-checkpoint.json`.
Предыдущий goal turn изменил authoritative source/evidence/docs и завершился
локальным commit591e882 — это progress, не no-progress/blocker.
M6/M6F/M7/M9 остаются открыты; M9 уже определён пользователем, не переуточнять.

## Проверяемая опора

Оба x86 PE, image base0x400000; входные EXE не исполнялись:

- primary SHA-256 `b1b5febf0d0394712e2322350e19dafe60742e8642697b93cfb89135bac1fd8b`;
- secondary SHA-256 `46528aac20499e3b3928d58658d7e0cefe26feba7cd193796d5cfbf7a2bbc558`.

22 выбранные функции имеют полные pseudocode и assembly:1254 инструкции.
22 основного body range и отдельная46-byte область EH конструктора совпадают
между двумя455; проверены23 relative E8 calls по настоящим PE bytes.
Нельзя называть это22 contiguous ranges, покрывающими всё listing:12 из1254
инструкций находятся в EH chunks у RVA62b110..62b13d. Последний E9 отдельно
декодирован до RVA471f63. Это побайтная опора, не runtime unwind acceptance.

Собственная IDA session79b91993 закрыта; итоговый список пуст. Первый ответ
close не был записан из-за Windows command-line length limit. Для сохранения
проверяемого ответа открыта та же work IDB в session5b785e72, затем успешно
save/close/list0. Данные записаны короткими частями; рабочая IDB сохранена.
Состояния и все исследования: ignored
`artifacts/client455-progress/dispatch110-{reference,session}.json`.
Сырые дополнительные диагностические декомпиляции не включены в счётчик22.

Воспроизведение статической проверки:

```powershell
.\scripts\Invoke-Python.ps1 scripts/audit_client455_message_dispatch.py
```

Результат — `inventory/client455-message-dispatch-reference.json`. Он проверяет
текущие pins, полноту выгрузки, отдельный EH range, native call encodings,
RTTI и неизменённый runtime109; не запускает большие native suites.

Все адреса далее — **RVA**, не VA.

## Formatter и общий dispatch

`RVA1e47a0` при null Format ничего не делает. Иначе форматирует общий буфер
через target vsprintf. Если current stage не0/1/2, добавляет текст в настоящий
center owner с цветомFFCC1F00. Затем всегда вызывает `RVA1e4a60(3,0)`.
Порядок center→common важен. Capacity shared formatter и unsafe overflow не
подтверждены в этом исследовании; не выдавать современный bounded buffer за
принятое target overflow behavior.

Общий dispatch `RVA1e4a60(categoryBYTE,styleOverrideBYTE)`:

| Target stage | Подтверждённое действие |
|---|---|
| 0 Title | Ни chat, ни login sink; formatter не добавляет center |
| 1 Login | Берёт actual current-stage pointer через RVA18f370; если pointer есть, пишет его message256 через RVA140400 |
| 3 MainGame и chat pointer есть | Увеличивает process DWORD counter RVA c28c04, header `[%d]`, style2; category9 выбирает25, любой ненулевой override заменяет style; передаёт caller category |
| 2 Tutorial и chat pointer есть | Другой process DWORD counter RVA c28c08, header `[%d]`; всегда style2/category3, caller category/override игнорируются |
| Иные либо нет chat | Common ничего не выводит; formatter для не0/1/2 уже вызывал center |

Значение incidental return EAX общего helper не трактуется как надёжный API
результата вывода. Counter xrefs подтверждают отдельные process counters:
все три ссылки каждого принадлежат этому common helper. Номер расходуется
до фильтров InsertText, не только когда на экране появился текст.
Формат `[%d]` у RVA6d8244, signed decimal интерпретация DWORD должна сохраняться.

Смежные wrappers:

| RVA | Поведение |
|---|---|
| 1e4850 | Форматирует и выводит только centerFFCC1F00, без stage guard |
| 1e48b0 | Вызывает предыдущий center wrapper, затем обычный formatter1e47a0; в MainGame это даёт два center Add, не один |
| 1e48e0 | Только centerFFFFD200 |
| 1e49a0 | Форматирует и вызывает common(3,26), без center; style26 обходит фильтры уже восстановленного чата |
| 1e49f0 | Common(3,0), затем отдельная raw chat insertion style33/category3; осторожно с потерянными/неиспользуемыми параметрами в decompiler prototype |

`RVA1e4940` и1e4ba0 изучены дополнительно, но не входят в выбранные22: у них
другие sink/board/message-box side effects. Не объявлять их восстановленными
простым перенаправлением в общий системный вывод.

## Настоящий Login sink и отрисовка

Getter current stage — `RVA18f370`, поле MainApp+619464; stage ID getter
`RVA13f780` читает BYTE+619468. Это не новое независимое состояние для теста.

Ctor `RVA13b860` явно записывает primary vptr; PE complete-object RTTI даёт
**CGP_LogIn**. В соответствующем vtable slot+32 находится настоящий Render
`RVA13cb40`. Точное decorated name/locator/type descriptor записаны в inventory.
Init `RVA13b9b0` обнуляет основной message256 по+372, DWORD+628,
вторичный message256 по+632 и DWORD+888.

`RVA140400`: nonnull source копируется через1e5920 в основной buffer+372.
Copy kernel обнуляет весь destination256, затем копирует
`min(strlen(source)+1,255)` bytes; строка длиной255+ обрезается побайтно, не по
границе DBCS символа. Null setter очищает весь основной buffer.
Соседний `RVA140450` при nonnull пишет secondary+632, **но при null очищает
primary+372**, сохраняя secondary. Это фактическая особенность455.

Render после обычного UI проверяет primary[0], затем:

1. Вычисляет ширину текста через RVA3b24b0(text,65535).
2. X = signed `(UIScreen.width-textWidth)/2`, Y = UIScreen.height−30.
3. Рисует RVA4c6020 с colorFFFFA670,flags32,scale1.
4. Затем передаёт secondary string другому UI consumer.

Здесь flags32 выбирает обычный font, а не medium80000010 экранных сообщений.
Существующих font/metrics достаточно для этого sink; полная Login/auth/scene/UI
acceptance и secondary UI consumer остаются отдельными обязательными работами.
Не заменять видимый sink только сохранением строки в журнал.

## C1A: отмена при переносе предмета

В `RVAfe020` guard = actual Avatar status predicate и pending DWORD.
При true порядок таков:

1. `RVA12ab50` очищает position12, выключает effect/sound через12ac40(0),
   затем сбрасывает pending.
2. Получает настоящий localized message ID C1A через NDLanguage.
3. Вызывает общий formatter1e47a0: center, затем chat/login маршрутизация.
4. Только после этого выполняет обычную замену/очистку hover object.

Существующий typed SetHover455 пока отказывает до мутации именно здесь.
Готовые effect/audio/Clear и profile/4pane insertion позволяют заменить отказ
реальной цепочкой. Target null/unsafe provider domain не принят, но не должен
быть поводом оставлять работоспособный путь с готовыми providers незавершённым.

## CE7: начало прицеливания

Полный immediate search нашёл единственное выбранное использованиеCE7:
`RVA1c5ab0` (constant push RVA1c5aca). Порядок:

1. Вызывает `RVAfe610(0,0)` — очищает request-process flag и его time.
   Это не ClearOperation и не SetHover(nullptr). Второй target аргумент не
   используется. Выбранный0-case соответствует существующему обычному
   CBoardManager::SetRequestProcessState(FALSE), это надо проверить в связке.
2. Получает localized CE7 и вызывает общий formatter.
3. Читает pending и только при0 вызывает SetPending(1).

Следствие: повторное действие при уже активном pending **снова выводит CE7**,
но не создаёт второй эффект и не перезапускает звук. Нельзя ставить early return
до сообщения. Это отличается от порядка выключения в C1A.

## Разрыв текущего source и следующая работа111

Существующий обычный `_SetSystemMsg(constchar*,...)` всё ещё использует legacy
трёхпараметрический InsertText и собственный256-byte formatter; `_SetSystemMsg(DWORD)`
остаётся старым no-op. Не считать его готовым message ID provider и не подменять
старые ID новыми NDLanguage IDs без подтверждения конкретных callers.

Legacy factory имеет MainGame ID2 и три stages; target Tutorial2/MainGame3.
Уже имеющийся `RF455_FromLegacyStage` переводит legacy2→target3. Это надо
использовать на ordinary route; нельзя направить настоящий MainGame в Tutorial
branch из-за равенства цифр2. Actual current-stage getter и Login message field
в source ещё не добавлены. Actual Tutorial/four-stage factory по-прежнему нет.

**Следующий участок111 — реализация**, не ещё один повтор этого аудита:

- Перенести common formatter/dispatch в ordinary source, process counters и
  точные stage rules, используя actual chat/center и видимый actual Login sink.
- Подключить настоящий typed hover C1A и выбранный CE7 producer вместе с
  request-state/effect/Miles; сохранить порядок и повторное arm behavior.
- Проверить обычный MainApp stage mapping, null chat/login cases, две counters,
  style/category overrides, actual window fragments и целевые GPU frames.
- Проверить actual Avatar+typed item+loaded BSP+live effect/Miles cancellation,
  затем exact own PE/Create1 и затронутые регрессии. Старый pending1 refusal
  заменять только вместе с рабочими providers; полная цель не сужена.

Полная Tutorial и Login/auth цепочка, остальные message wrappers/producers,
nuclear list12/command/finalposition и все прежние client-acceptance gaps
остаются обязательны. Не превращать selected route в fake stage или message log.
Runtime109 PE `ef33b250cdaba110d4cb22c726aa6a82703c41de34a98d2a7b6902532a4279c1`
и engine `546a7529b51139e856b1a108fcad7849c14b2d00563b7abbfdcc8db10026fa5a`
этим исследованием не изменены; новые native проверки не заявлены.
Серверные файлы и originals не изменялись.
