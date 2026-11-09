# Клиент455: профиль чата и вставка в четыре панели — работа109

Статус на 2026-11-09: **PARTIAL**. Восстановлены выбранные контракты профиля,
настроек, фильтрации, переноса строк и вставки текста в четыре настоящих
CGUITextBoard окна CGUIChatWindow. Это зависимость общего вывода системных
сообщений, а не приёмка всего чата или клиента. M6/M6F/M7/M9 открыты.

## Эталон и происхождение

Оба входа — x86 PE, image base `0x400000`, не исполнялись:

| Эталон | SHA-256 |
|---|---|
| Основной | `b1b5febf0d0394712e2322350e19dafe60742e8642697b93cfb89135bac1fd8b` |
| Второй | `46528aac20499e3b3928d58658d7e0cefe26feba7cd193796d5cfbf7a2bbc558` |

Выбраны44 диапазона функций;31 полная дизассемблированная функция,
3615 инструкций. Все44 диапазона и выбранные таблицы совпадают между двумя PE.
Основная сессия IDA `0fc06123`:41 функция/28fullasm/2708instructions.
Дополнение по lexer — `d8a4c249`:3 функции/907instructions.
Обе собственные сессии сохранены и закрыты; после закрытия список пуст.
Сырые выгрузки и состояния находятся в ignored
`artifacts/client455-progress/chat109-{reference,session,lexer-reference,lexer-session}.json`.
Манифесты с точными диапазонами/хешами —
`inventory/client455-chat-reference.json`; повторная проверка —
`scripts/checkpoint_client455_chat.py`.

Все адреса в таблице ниже — **RVA** относительно `0x400000`.
Диагностические декомпиляции не объявляются дополнительными выбранными
побайтно проверенными функциями.

| RVA | Подтверждённый контракт |
|---|---|
| `0x342190`, `0x342220`, `0x342490` | Font-owner ctor/Load/Release |
| `0x342550`, `0x342780` | Поиск стиля по marker; clamp INT→BYTE |
| `0x3427c0`, `0x343990` | Prefix18 writer/ctor |
| `0x342840` | Defaults, включая повторную запись header у style13 |
| `0x95010`, `0x95040` | FONT_INFO16 ctor/setter |
| `0x343410`, `0x3434c0`, `0x343550` | Font-provider load/release/getter |
| `0x343570`, `0x343790`, `0x343850` | Профиль MainGame ctor/dtor/Initialize |
| `0x14c9a0` | Getter singleton профиля |
| `0x343b20`, `0x343c00`, `0x3439e0` | ChatMode load, DefModeOn merge, ChatMode save |
| `0x343d30` | Настоящий ctor CGUIChatWindow, четыре панели |
| `0x345010`, `0x346dc0` | Default filter setup и raw filter storage |
| `0x345b80`, `0x345f40` | Typed InsertText и raw body insertion |
| `0x345ec0`, `0x345ee0`, `0x345f10` | Prefix/header/body providers |
| `0x346020`, `0x3462a0` | Wrapper и multibyte append |
| `0x20b030`, `0x20b150` | Число fragments в TextBoard |
| `0x3b23c0`, `0x3b2670` | Fill и byte fit с language lead-byte handling |
| `0x3facd0`, `0x3fbe40`, `0x3fbf40` | Script load, raw read и lexer |

Вызов профиля в target MainGame.Create_UI (`RVA0x1477c0`) находится у
`RVA0x1488ac`, после установки createdUI. `RVA0x343570` — ctor **профиля**,
а не окна; само окно создаётся в `RVA0x343d30`.
Полный UI filter setter `RVA0x346c50` и getter `RVA0x346e70`
изучены диагностически; side effects полного setter ещё не перенесены.

## Профиль и реальные входные файлы

Подтверждены36 стилей,14 категорий, prefix18 и font16. Font имеет BYTE size@0,
DWORD style@4, DWORD color@8, float scale@12; padding не объявлен значимым.
Prefix: WORD length@0 и char[16]@2. Marker-таблица36×32 находится у
`RVA0x6e6f40`, четыре256-byte settings key — у `RVA0x6e7400`:
All, Party, Guild, System. Literal `RVA0x6a8dd4` — пустая строка, не пробел.

Получатели путей проверены для11 country vtables, virtual byte slot364.
Fallback19 country flag — slot240, установлен только для nation2/China.
Точные пути и доступность:

| Nation | Путь в DataTable | Вход |
|---|---|---|
| 0 | ko-kr/Cska.txt | Есть |
| 1 | pt-br/Csba.txt | Есть |
| 2 | zh-cn/Cscu.txt | Есть |
| 3 | en-gb/Csea.txt | Отсутствует |
| 4 | en-id/Csia.txt | Есть |
| 5 | ja-jp/Csju.txt | Есть |
| 6 | en-ph/Cspa.txt | Есть |
| 7 | ru-ru/Csra.txt | Есть |
| 8 | zh-tw/Csta.txt | Есть, UTF16LE BOM |
| 9 | en-us/Csua.txt | Отсутствует |
| 10 | th-th/Csth.txt | Отсутствует |

Восемь файлов скопированы побайтно в ignored
`work/client455-reference-inputs/chat/nationNN.txt`; оригиналы проверяются по SHA.
Сходное имя в другой папке не считается нужным target input. Отсутствующие три
пути — конкретные региональные data gaps.

Script row: marker, четыре signed INT channel с clamp0..255, quoted prefix.
Оба шрифта получают size12/style32/scale1. Prefix ограничен15 байтами через
ambient CRT `_mbsnbcpy`; под949 length может быть15 при14 содержательных байтах.
Fallback13 дважды записывает header; body остаётся constructor white/size0/style0.
Fallback19 — China `0xffff0000`, остальные `0xffffd0a0`.
Fallback localized prefixes используют настоящие NDLanguage IDs84f..857,878,9ff,850.

**Намеренно сохранена byte-lexer особенность Taiwan.** Target пропускает UTF16
BOM, но не декодирует UTF16: interleaved NUL не дают совпасть ASCII style markers.
Незавершённый quoted token в конце отбрасывается. Реальный Csta.txt поэтому
даёт36 default records. Это подтверждено полным loader/read/lexer, а не
исправлением или перекодированием исходного файла. Собственный tokenizer
воспроизводит этот выбранный домен, не объявлен полной заменой общего lexer455.

## Подключение к обычному клиентскому source

В actual CGP_MainGame добавлен RF455ChatProfile перед actual m_uiChatWindow;
он владеет массивами source и bind/unbind provider. Современные контейнеры
не объявлены совместимыми со старым STL/private ABI.
`InitializeChat455` вызывается один раз в обычном Create_UI после createdUI,
читает literal country script и safe runtime settings. В собственной итоговой
PE декодирован единственный CALL к нему: **RVA `0x25d30`**.

Профиль и initialization удержаны в normal PE. **Новый InsertText455 пока не
имеет обычных игровых producers и удалён linker из normal PE**. Native lab
с полным набором клиентских объектов вызывает его на настоящем MainGame/окне.
Старые InsertText и network/input callers не перенаправлены молча: у старой
версии иные style/category contracts, их ещё надо перенести.

Filter kernel хранит raw DWORD[4][14], currentPane начинается сFF. Own-category
pane1/2/3 принудительно включена. Четыре нулевые ChatMode masks дают все14
категорий pane0 и forced own+category5 остальных панелей. DefModeOn добавляет
неизвестные bits к pane0 и записывает merged mask **signed `%d`**.
Default fixture даёт16383. Высокий input bit `0x80000000` сохраняется как
`-2147467265` (`0x80003fff`); отдельный native case это проверяет.
Реальный пользовательский GameSetting.ini не копировался целиком и не менялся;
стенд создаёт собственные безопасные fixture INI.

Typed insertion: style26 обходит filters; raw insertion — нет. Header и body
вставляются отдельными real fragments; header не двигает view, body двигает.
Первый header в пустом board удаляет leading LF. Формат body `%s : %s`.
Wrapper использует width pane0 минус два marginX, реальные text metrics/fit,
ambient CRT `_mbsnbcat`. Indentation count target всегда0. Сохранены
category8 branch, двойной LF при некоторых явных newline и отбрасывание
непоместившегося остатка segment при невозможности вместить glyph.

14 UI filter controls/colors/GM/category7 network side effects, input/send/IME,
полный save producer и legacy caller migration ещё открыты.

## Проверка109

`inventory/client455-chat-native.json`:385 targeted assertions на actual
MainGame profile и четырёх настоящих панелях. Восемь script inputs ×36стилей =
288 records сверены с отдельным Python oracle; defaults выводятся из
подтверждённой target функции, не дублируют C++switch вручную.
Восемь файлов загружены explicit path overrides в инициализированном Korean
language context; это **не восемь полных региональных bootstrap**.

Проверены profile layouts/prefixes/default quirks/DBCS/settings/filter storage,
ordinary typed insertion, прямой реальный C1A input, wrap/newline/style26,
очистка panel fragments и unbind profile. Пять GPU кадров просмотрены:
2704/2596/2592/10118/0 непустых pixels. Последний кадр пуст после cleanup.
Final lab: `work/m9/2f82b06d/chat-001`.

Свежие целевые регрессии на этой сборке:

- Center messages69: `work/m9/38931334/center-messages-001`, четыре просмотренных
  кадра, pixels1673/4455/4236/0.
- Board-hover: `work/m9/67f36085/board-hover-001`, шесть просмотренных кадров.
- Все10 center/hover кадров побайтно совпадают с108. Всего109 просмотрено15 кадров.
- Точная собственная normal PE проходит прежний startup/Create→1,
  `work/m9/ef33b250/{startup001,ui-startup001}`.

Новая PE: SHA-256
`ef33b250cdaba110d4cb22c726aa6a82703c41de34a98d2a7b6902532a4279c1`,
2190848bytes, x86, base400000, entry RVA160400, WinMain RVAb9060,
afterCreate RVAb91d4.182client/20kernel/63facade, unresolved0.
Движок неизменён: SHA-256
`546a7529b51139e856b1a108fcad7849c14b2d00563b7abbfdcc8db10026fa5a`,67objects.
033 baseline сохранён;082 derived snapshot по-прежнему отсутствует.

BSP/Miles29 и status62 сохранены как historical108. Magic36/resources66/
effect-runtime573/audio157/account/hotbar7/storage3 — historical107.
Большие159k/world/audio/остальные32GUI не повторялись без изменения зависимостей.
Предыдущие failed/intermediate labs не выданы за принятый final385 run.

Текущий gate — `inventory/client455-chat-checkpoint.json`, gate108 исторический
(`artifacts/client455-progress/client455-center-messages-checkpoint-before109.json`).
Для проверки сохранённого результата:

```powershell
.\scripts\Invoke-Python.ps1 scripts/checkpoint_client455_chat.py
```

## Открытая граница и следующий шаг110

Общий system-message dispatch target RVA1e47a0/1e4a60, реальные C1A/CE7 callers,
login/Tutorial sinks и live pending1 hover ещё не подключены. Существующий
отказ pending1 до мутации сохранён. Прямой C1A lab input не подтверждает
полную цепочку пользовательского действия. Не заменять её пустым setter или
только center-message выводом.

Следующий выбранный участок110 — общий dispatch и отмена прицеливания через
настоящие chat/center sinks; затем nuclear command/response/list12/finalposition.
Полные filter UI/callers/input/send остаются обязательны, но их оформление
не является поводом блокировать уже доступный selected insertion sink.
Legacy uncreated-stage Destroy всё ещё не освобождает другие старые allocations;
полный teardown, CRT initialization, private ABI, unsafe/null/OOM/FP,
malformed scripts, shared scratch/concurrency и общий lifecycle не приняты.
Все прочие client-acceptance gaps сохраняются; серверы не изменялись.
