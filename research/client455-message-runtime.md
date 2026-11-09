# Общий вывод и живая отмена прицеливания — работа111

2026-11-09. **PARTIAL**. Подтверждённые в110 контракты перенесены в ordinary
source: общий formatter, actual Login member/draw и MainGame chat/center.
Обычный typed hover теперь отменяет настоящее прицеливание у actual Avatar,
останавливает Miles radar и выводит C1A до изменения предмета. Это конкретное
устранение прежнего pending1 refusal в инициализированном допустимом домене.
M6/M6F/M7/M9 остаются открыты; полная цель клиента455 не сужена.

## Опора и реализация

Статическая спецификация: [исследование110](client455-message-dispatch.md),
`inventory/client455-message-dispatch-reference.json`. Два x86 PE/base400000:

- `b1b5febf0d0394712e2322350e19dafe60742e8642697b93cfb89135bac1fd8b`;
- `46528aac20499e3b3928d58658d7e0cefe26feba7cd193796d5cfbf7a2bbc558`.

22 selected functions/22fullasm/1254instructions;22bodies и46-byte EH region,
23 relative calls. Gate111 независимо перепроверяет эти bytes. Source snapshot
checks старого audit110 относятся к прежнему source и после переноса исторические;
не запускать110 для проверки нынешней интеграции и не повторять IDA без нужды.
Новых сессий IDA111 не создавалось.

`client455_message_dispatch_port.py` меняет только own working copies:

- CMainApp получает getter фактического m_pGameProgress.
- CGP_LogIn владеет RF455LoginMessages:два buffer256, Init Clear, late Render Draw.
- Ordinary `_SetSystemMsg(constchar*,...)` передаёт va_list восстановленному
  formatter, который использует actual current-stage object/ID и globals.
- MainGame legacy2 переводится в target3 существующим bridge. Stage2 routing
  core имеет отдельный process counter и fixed style2/category3.
- Новые source functions отдельно компилируются в64-й facade unit, не дублируются
  в lab. ChatReady455 сообщает готовность реального окна, без нового fake sink.
- Actual typed SetHover calls RF455_CancelNuclearForHover при status predicate
  и pending. Clear(position/effect/sound/pending) предшествует localized C1A
  и последующей обычной clone/screen/backup mutation.

RF455LoginMessages воспроизводит byte truncation255, null primary clear,
null-secondary→primary-clear quirk, target ordinary font/colorFFFFA670/flags32/
scale1 и центрирование на UIScreen.width, Y=height−30. Это own source storage,
не overlay target field offsets/private ABI и не полная Login scene acceptance.

Process DWORD counters переживают stage changes; signed `%d` header сохраняется,
в том числе0x80000000→[-2147483648]. Category9 выбираетstyle25, ненулевой override
побеждает;26 обходит filters. Перенесены selected center/double/orange/friend
wrappers; двойной wrapper сохраняет два center Add в MainGame.

Own formatter ограничен1024 для допустимых входов и явно отказывает unsafe
overflow domain. Готовность actual app/font/center/chat/language проверяется
до item mutation вне допустимого initialization domain. Это safety boundary,
не доказательство target null/OOM/CRTstartup/reentrancy/privateABI behavior.
Numeric legacy `_SetSystemMsg(DWORD)` и остальные старые caller/ID/category
contracts этим переносом не исправлены и остаются обязательными gaps.

## Живая проверка83

`scripts/probe_client455_message_dispatch.py` собирает собственный console entry
с теми же182 клиентскими объектами/20kernels/64facades. Native source вызывает
обычный `_SetSystemMsg`, current MainApp context и реальные stage objects.
В offline lab вручную подключаются настоящие MainGame/Login/UIScreen providers;
полный обычный factory/Create_UI/auth/world scenario здесь не принят.

Финальный run: `work/m9/5e84374d/message-output-001`, natural exit0,83 checks.
Проверены:

- Title no-output/null format и valid null Login pointer.
- Actual Login member,6 byte boundaries0/1/254/255/256/600 и secondary-null quirk.
- Ordinary legacy2→target3 route, настоящий chat panes0/3 и center.
- Category9/style25, override26/all4panes и отдельный Tutorial counter.
- DWORD signed header boundary, double center и orange/friend behavior.
- Actual Avatar status2, настоящий предмет из EDF и его inventory icon,
  neutralAS1 BSP, шесть effect children и реальный Miles radar.
- CE7 core:request-state clear→message→start, повторное начало выводит сообщение,
  не перезапуская effect/sample.
- Ordinary SetHover с pending1:coordinates/handle/pending очищены, sample DONE,
  реальный C1A находится в actual center/chat, clone использует реальный payload.
- Отменённые эффекты полностью уходят за74 ticks. Полный world/stage heap balance
  не заявлен; известные6 R3T release warnings сохранены, как в предыдущем effect core.

Пять GPU frames просмотрены:Login1184pixels,main4375,forced1916,cancel4401,
cleared0. Center текст в первом update ещё частично прозрачен по сохранённому
target fade kernel. Chat panels используют контрольную grid, не полный layout.
Tutorial проверен только через target-ID routing core на реальных MainGame
boards; это не actual Tutorial object или четырёхэтапная фабрика.

Windows legacy installer heuristic ошибочно требовала elevation для EXE с
"patch" в слове "dispatch"; regular lab назван `message-output-probe.exe`.
Перед запуском исправлены два недостатка lab:подключён реальный UIScreen provider,
ожидание коротких center Add соответствует немедленному active append.
Failed/intermediate runs не выданы за принятый83-check final. Input455 EXE не
исполнялись, original GameSetting.ini не читался целиком и не менялся.

## Обычная PE и затронутые регрессии

Новая RF_Online.bin SHA-256
`031df3676c9bed977f660d79fe535666af9cb52cfc4e5b1a61b3f04841df831c`,
2197504bytes/x86/base400000/entryRVA161590,WinMainRVAb9060/afterCreateRVAb91d4.
182client/20kernels/64facades,unresolved0. Точный own PE проходит startup и
существующий Create→1: `work/m9/031df367/{startup001,ui-startup001}`.

Gate декодирует собственные инструкции и проверяет E8/E9 targets/порядок:

| Own RVA / caller | Результат |
|---|---|
| 6efb0 / `_SetSystemMsg` | Вызывает actual ShowSystemMessageV |
| 24420 / CGP_LogIn.Render | Вызывает actual LoginMessages.Draw |
| c6ab0 / SetTypedHover455 | Вызывает реальную отмену, прежнего unconditional refusal нет |
| c7cb0 / CancelNuclearForHover | Clear раньше ShowSystemMessage |
| c7fd0 / ShowSystemMessageV | Center adapter раньше common Dispatch |
| c8040 / center adapter | Доходит до actual CenterMessages.Add |

Полные own disassemblies и decoded edges сохранены в checkpoint/artifacts.
`InsertText455` теперь **удержан ordinary linker** благодаря реальным formatter
и hover consumers. CE7 Begin helper по-прежнему **удалён linker**, потому что
обычная game-action registration ещё не перенесена; его lab успех это не заменяет.

Свежие regressions:

- Center69, `work/m9/2138e4ba/center-messages-001`,4frames.
- Board-hover256 routes/5kinds/6frames,
  `work/m9/5d68c8f4/board-hover-001`.
- Player-status62, `work/m9/021a0f81/player-status-001`; отсутствие providers
  по-прежнему явно отказывает до mutation, а готовая цепочка отдельно принята83.
- Все10 center/hover frames побайтно равны109; всего111 просмотрено15 кадров.

Engine67objects SHA-256
`546a7529b51139e856b1a108fcad7849c14b2d00563b7abbfdcc8db10026fa5a` неизменён.
033 baseline сохранён;082 derived snapshot по-прежнему отсутствует.
Chat385/288records/8files — historical109. BSP/Miles29 — historical108;
magic36/resources66/runtime573/audio157/account/hotbar7/storage3 — historical107.
Эти отчёты не выданы за свежие прогоны. Неизменённые большие159k/world/audio/
остальные32GUI suites не повторялись.

Текущий gate:

```powershell
.\scripts\Invoke-Python.ps1 scripts/checkpoint_client455_message_dispatch.py
```

`inventory/client455-message-dispatch-checkpoint.json` — PARTIAL. Gate109 теперь
исторический, снимки before111 сохранены под artifacts/client455-progress/.

## Далее112 — обязательная связь с игровым действием

Найти target callers/registration callback RVA1c5ab0 и подключить начало
прицеливания к обычному игровому действию. Использовать уже работающий CE7 core,
не переисследовать и не заменять его отдельным test-only состоянием. Затем
nuclear command/response/list12/finalposition и остальные input cancellation.

Full Login/auth/secondaryUI, actual Tutorial/fourstage factory,14filter UI/
input/send/IME/save/legacy chat callers, другие system wrappers и numeric ID
overload, full stage teardown/CRT/privateABI/OOM/FP/unsafe/concurrency/shutdown
остаются открыты. Все прочие client-acceptance gaps обязательны, M9 не достигнут.
