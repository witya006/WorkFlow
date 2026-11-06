# Постепенный вывод текста455 — зависимость брифинга, участок070

Исправление071:60CAC0 вызывает base2262E0,который рисует собственный fill/image.
Прежний вывод об отсутствии self-fill неверен. SourceDraw иfixture исправлены;
проверены80000redpixels иfreshKo/Ru. Reference теперь19ranges/9asm. Подробности:
[briefing-controls071](client455-briefing-controls.md). Исторические hashes070
ниже относятся к предыдущей сборке;актуальные — вnative manifests071.

2026-11-07. Восстановлен исходный `CGUITextTypingBoard`, необходимый настоящему
CGUIBriefingWindow. Это отсутствующий в базе0.7 класс, а не ускорение старого
вывода. Сам briefing/key/portrait/frame provider и обычный Tutorial ещё открыты.
Typing source включён в normal facade; отдельного production экземпляра пока нет,
линкер может удалить неиспользуемые методы из RF_Online.bin. Force-link не применён.

Эталон x86/base400000 SHA-256
`b1b5febf0d0394712e2322350e19dafe60742e8642697b93cfb89135bac1fd8b`;
backup `46528aac20499e3b3928d58658d7e0cefe26feba7cd193796d5cfbf7a2bbc558`.
18 function ranges и primary vtable168байт совпали между pins; сохранены8 полных
assembly dumps. Собственная IDA37b9a025 закрыта с сохранением. EXE эталона не запускался.

| RVA | Контракт |
|---|---|
| 247470 | Constructor: WORD interval100, BOOL running/finished0, cursorFFFF |
| 2475A0 | Signed line range check, WORD storage, clock+delay, previous0 |
| 247640 | Force endpoint/end flag |
| 247690 | Update: shown/running/notfinished, timing and cursor advance |
| 247940/247BA0 | Full/clip Draw through partial fragment endpoint |
| 247BD0 | Virtual Clear resets cursor and base caches, retains flags/timers |
| 2F5BF0/2F5E50 | Shared interval setter/finished getter |
| 201F50/3B2450 | Resource codepage DBCS classifier, not ambient CRT |
| 245150/2450F0 | Shared inclusive-end partial/full line drawing |
| 333790/333920 | Actual briefing insertion/page range,80ms,first delay250 |
| 333A50/333C50 | Actual reveal/advance/close and per-frame consumers, unported |

## Реализация и наблюдаемые особенности

Source-owned class хранит WORD interval/range/cursor и DWORD start/previous.
Публичные semantic API не являются overlay исходного244-byte private object.
Start проверяет signed int boundaries до преобразования кWORD. Рanges вне числа
строк возвращаютfalse; отрицательный диапазон, который target пропускает до
невалидных marker/pointer reads, явно отклоняется. Это известная граница, не parity.

Update не вызывает base/child Update. Он проверяет IsShow, running и finished,
после чего читает часы. Start и loop используют **абсолютные DWORD сравнения**;
между ними есть unsigned elapsed check. Previous0 является sentinel, поэтому
реальное время0 не сразу начинает отсчёт. При wrap поведение не заменено
сравнением elapsed для всех веток. Interval0 допускает завершение на следующем
Update без обязательного ожидания, пока текст продвигается в валидной области.

Первый tick выставляет курсор на start marker, последующие двигают его.
DBCS lead определяется через codepage реального language pack и просмотр начала
строки, чтобы не принять trail за lead. Проверка с противоположным ambient CRT
подтверждает разделение resource949/1251 и `_mb*` codepage.

Пробел в новой позиции не увеличивает previousTime, поэтому вывод может пройти
несколько пробелов за один interval. После перехода fragment boundary target
смотрит `Str[newOffset]` **старого** фрагмента. Первая fixture для fragment `" "`
ожидала дополнительный tick; полный Update asm подтвердил, что старый пробел
может сразу провести курсор через следующий `BC`. Исправлена fixture, алгоритм
не менялся под тест. Начальный newline marker также участвует в продвижении.

Draw сначала рисует собственный fill/image и child objects, затем текст до
inclusive cursor. Однако partial line вызывается только при start<cursor.
Поэтому первый одиночный ASCII byte ещё невидим; следующий tick показывает
два байта. Первый DBCS glyph получает cursor1 и виден целиком. Эти особенности
сохранены по инструкциям, не исправлены как предполагаемые ошибки интерфейса.

Общий CGUITextBoard получил protected DrawLineTo455, выделенный из прежнего
DrawLine, и virtual Clear для правильного derived dispatch. Clear typing-панели
сбрасывает cursor и base caches, сохраняя running/finished/start/previous, как
target247BD0. Малый full-line adapter теперь inlined; проверка production map
переведена на реальный общий endpoint renderer, а не force-retention символа.

## Проверки

Собственная full-object x86 probe использует настоящие ordinary GUI/TextBoard,
language pack, GDI и D3D9. Трассы состояния заданы по assembly:250delay/80interval,
точные границы ticks, invalid-range no-query, spaces/fragment-crossing/newline,
resource DBCS против ambient CRT, zero sentinel/DWORD wrap/zero interval,
виртуальный Clear и сохранённые flags/timer, hidden/finished gates, child Draw
без child Update и собственная заливка (исправление071). На профиль пришлось42 clock queries; это
детерминированная трасса, не число запросов к ИИ/мера полноты455.

Korea: partial64/full90/colored90pixels, first localized glyph43pixels.
Russia: partial68/full96/colored96, first localized cursor0 ещё пустой кадр.
Типизированный partial `AB` побайтово совпал с отдельно нарисованным plain `AB`.
Сохранены14 кадров640×480;8 partial/full/localized/colored кадров просмотрены,
expected-prefix кадры проверены hash equality, blank cases — native pixel count.
Обе пробы завершились естественно exit0. SHA-256:
`feb7b853ad6cb27e99249f83f74cb9b11ec4657fe3c325df805cd985cb49460e`, entryE4A60.

Normal PE SHA-256
`8f009924c882d5c87c2f6872c3c99b07ff98a9085bd6ca9643bf13832d6f0b4c`,
x86/base400000/entry150290,2041856байт.182client/20kernel/**29facade** TU,
0unresolved. Подтверждена компиляция typing source в archive; его исполнение
проверено full-object probe, **не объявлено ordinary production briefing**.
Общий renderer используется обычным клиентом. Preparation idempotent:
`f7a4826fa75c4c815acfc827f424a90d305f2e9b8239f9fca89582acd8db7340`.
Engine056 без изменений.

Точная PE прошла WinMain/TCPfixture/engine/D3D/Character/existingCreate1, stop до
игрового цикла. Firstchance40080201 через KernelBase остаётся unknown,как068/069.
Текущие затронутые GUI probes прошли;44GPU hashes совпали с предыдущим commit
7115112 и его просмотренными кадрами.10 scoped gates PARTIAL,не полная приёмка.
Большие неизменённые particle/runtime suites не повторялись.

## Далее

071: CGUIBriefingBoard/CGUITutorialKeyBoard/portrait/frame helpers и настоящий
CGUIBriefingWindow, реализация RF455TutorialBriefingView. Черновая карта:
[briefing-analysis](client455-briefing-analysis.md). Затем actual Avatar/world/
Tutorial host/fourstage. M6/M6F/M7/M9 открыты. Clear while active with missing
markers, negative/WORD overflow/foreign pointer/OOM/reentrancy/failure domains
остаются unsupported либо unverified; не заменять их молчаливым успехом.

Доказательства — inventory/client455-text-typing-{reference,native,checkpoint}.json,
scripts/native/client455_gui_text_typing_board.*, общий TextBoard и собственная
probe. Raw — artifacts/client455-tutorial/*070.json, кадры — work/m9/feb7b853.
