# Текстовая панель455 — участок064

2026-11-06. В обычной клиентской копии заменены header/body `CGUITextBoard`:
старый счётчик символов фиксированной ширины уступил раздельным фрагментам
текста и кэшу строк, рассчитанному по пиксельным метрикам063. Обычные вставка,
перенос, хранение и Draw уже используются полной `RF_Online.bin`.
Форматированный ввод и расчёт неограниченного размера доступны как новые
source-методы; их реальные production callers ещё предстоит перенести.
Полный scrollbar/briefing/Tutorial и клиент455 этим участком не приняты.

Эталон x86/base400000 SHA-256
`b1b5febf0d0394712e2322350e19dafe60742e8642697b93cfb89135bac1fd8b`;
backup `46528aac20499e3b3928d58658d7e0cefe26feba7cd193796d5cfbf7a2bbc558`.
49 диапазонов функций, primary vtable и scroll-observer entry совпали между
pins. Сохранены17 полных assembly dumps. Собственные IDA-сессии958042ee,
aabab7c3/06c03ace закрыты с сохранением. Входные EXE не исполнялись.

| RVA | Контракт |
|---|---|
| 243400 | Constructor: fragment/line caches, лимит1000, WORD base/view |
| 243600/243650 | Margin/gap вызывают SetSize с текущими размерами |
| 2436C0/2453C0 | Подключение scrollbar и его scroll observer |
| 243740 | Перенос пересчитывается только при изменении фактической ширины |
| 243890 | Incremental/full pixel layout, newline markers и retention |
| 244030/244160 | WORD markers и rebase при base+fragment >=FFFF |
| 243D30/243860 | Unwrapped extent через все фрагменты |
| 244310 | Вставка и обновление диапазона/текущей строки |
| 244580/244800/244B50 | Markup, font attributes и закрывающий tag prefix |
| 244D00/244D80 | Начало и включительный конец строки |
| 244F60/245150 | Отрисовка видимых строк/фрагментов, highlight и auto-bottom |
| 3B1F40 | Копирование с BYTE capacity, подтверждено MOVZX BYTE |
| 240850/240940/240B60 | TextInfo28: cached WORD length, font16 по смещению12 |
| 239530/239560 | Scrollbar amount setters используют общий clamp/update |

## Реализованные правила

`FONT_INFO` теперь имеет16байт: size/style/color/float scale; defaults0/0/
FFFFFFFF/1.0. `CGUITextInfo` получил сохранённую WORD length и размер28байт.
Clear освобождает строку, сохраняя length, как в эталоне; SetFont(nullptr) не
меняет font. Входы свышеFFFF байт явно отклоняются: эталон выделяет память по
усечённой длине, затем делает небезопасный strcpy. Такая область не принята.
Обычные TextBoard/CGUIText Draw передают фиксированный scale1; наличие поля
не является доказательством реализации всех scale/FreeType consumers455.

Фрагменты сохраняют текст и font info отдельно от строк. Строка содержит WORD
номер фрагмента и offset. Append восстанавливает ширину последней строки;
полный layout запускается только при изменении width. Margin-only изменение
сохраняет старые markers, хотя доступная ширина уже другая. Очень узкая панель
может оставить фрагмент без строки до следующего изменения width. Эти quirks
сохранены по инструкциям, а не заменены обычным алгоритмом word wrap.

Newline marker указывает на сам байт newline. В частности, ведущий newline
может не создавать дополнительной пустой строки, а trailing newline создаёт
маркер. Лимит по умолчанию1000; удаление старой строки освобождает только
фрагменты, полностью предшествующие следующему marker. При достиженииFFFF
absolute fragment indices rebased; лимит0 оставляет минимум один marker.

Font/open и /font/close сравниваются как prefixes без учёта регистра.
Attribute keys color/style чувствительны к регистру. Флаги color/style
сохраняются: после color последующие значения могут продолжать попадать в
color branch. `%s` захватывает соседний символ `>`, поэтому style без пробела
перед ним может остаться прежним. Формат не заменён общей HTML-грамматикой.
Не продвигающиеся malformed tags и переполнение32-байтового token buffer
отклоняются явно; соответствие исходному hang/overflow не заявлено.

У helper7B1F40 capacity действительно BYTE: в двух местах опкод `0F B6 45 10`.
Значение256 превращается в0 и оставляет прежнее содержимое destination.
Formatted insert и final-fragment Draw используют общий scratch панели;
проверен повтор старого текста после wrapped capacity. Копирование следует
ambient CRT `_mbsnbcpy`, отдельно от codepage языковых ресурсов. Взаимодействие
с другими исходными пользователями глобальной области102DAB0 пока открыто.

Scrollbar total/current setters теперь оба делегируют SetAmount, поэтому смена
total также ограничивает current. TextBoard использует defaultHeight+gap для
range/view, обновляет текущую строку по scroll event и умеет auto-bottom.
Геометрия/авторазмер thumb и полный ввод scrollbar остаются legacy до065.

## Проверки и исправленные предположения

Собственная full-object probe использует настоящие обычные клиентские классы,
NDLanguage Korea/Russia, GDI HFONT и D3D9. Проверены predefined marker sequences,
два фрагмента в одной строке, reflow, DBCS boundary, ведущие/конечные newlines,
margin-only stale layout, narrow recovery, retention внутри/между фрагментами,
scroll range/view/clamp/clear, grammar quirks и BYTE overflow/reuse.

Для достижения WORD rebase выполнены65536 последовательных вставок с
лимитом1. Это один короткий тест реальной границы, а не65536 независимых
проверок/запросов к ИИ. Старые большие runtime suites не повторялись.

Первоначальный тест ошибочно отождествлял язык ресурсов и CRT multibyte mode.
Затем значение `_getmbcp()==0` ошибочно было принято за отличие от ANSI startup.
Проверены getter эталона и установленные исходники UCRT10.0.26100.0: обе CRT
выбирают systemANSI; getter возвращает0 и для SBCS1251. Экспериментальный
ранний adapter удалён. Native test проверяет `_setmbcp(949)`/1251 отдельно и
восстанавливает `_MB_CP_ANSI`, а не неоднозначный результат getter0.
На этом ПК GetACP=1251, ambient getter=0. Полные locale/thread/OOM domains открыты.

Прежняя Tutorial-board fixture читала удалённый private `m_listText` и удаляла
newlines при сравнении. Она переведена на публичный fragment API; теперь
сравнивает полный исходный NDLanguage441/444, включая newline bytes. Проба
реальных modal2/3 прошла. Rich/stage providers этой061 пробы остаются тестовыми.

Для каждого профиля сохранены viewport640×480: red/green fragments, markup,
bottom-aligned локализованная строка и highlight. Все кадры просмотрены;
это подтверждение selected source behavior, не pixel parity всего GUI455.
Korea:204/575/271 изменённых пикселя в первых трёх сценариях; Russia:160/620/304.
Собственная probe PE SHA-256
`256cbbe73ad1de562bf8b7e8a39b23aa9681917c944d275ed678444af285bbfc`, entryE4610,
естественный exit0 для двух профилей.

## Production и границы приёмки

Production PE SHA-256
`3a209cdc328c7fb20313233ba3f58745685344c0521bbe69c071e020a2e71485`,
x86/base400000/entry14DD30,2028032байта.182client/20kernel/26facade TU,
0unresolved. Сохранились реальные CUnity/CAnimation consumers; R3Engine archive
не изменился. Малый copy helper inlined в production DrawLine; внешний entry
проверен прямыми вызовами из full-object probe.

Linker удаляет ещё не используемые в production formatted/extent методы.
Их наличие и исполнение доказаны в full-object probe; не объявлены подключёнными
к обычным окнам. Legacy messagebox.SetMsg по-прежнему вычисляет часть размеров
по byte count. Следующий перенос должен заменить реальные callers по455,
а не насильно включать символы или менять plain InsertText на markup.

Затронутые metrics/font/modal Korea/Russia и tutorial-board probes прошли на
текущем link digest. Точная новая PE прошла WinMain/TCP fixture/engine/D3D/
Character/existingCreate1 и остановлена до игрового цикла. Это не аутентификация
и не полное соответствие455. Gate client455-text-board-checkpoint.json PARTIAL.

Следом065: общий scrollbar — auto thumb sizing, геометрия, таймеры и mouse/input,
включая variants/callers. Затем production message sizing/rich callers и весь
briefing; actual Avatar/world/local handlers/Tutorial/fourstage. FreeType,
shared scratch consumers, unsafe/numeric/errors и весь M6F/M7/M9 открыты.
