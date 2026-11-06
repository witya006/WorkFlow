# Размеры и форматирование сообщений455 — участок069

2026-11-07. Обычный `CGUIMessagebox::SetMsg` заменён по клиенту455: цвет текста,
выбор plain/formatted, расчёт естественного размера, порядок scroll/layout.
Форматированный ввод и ResizeToText теперь вызываются обычным production
методом, а не только самостоятельной пробой. Полный GUI, обучение и M9 открыты.

Эталон x86/base400000 SHA-256
`b1b5febf0d0394712e2322350e19dafe60742e8642697b93cfb89135bac1fd8b`;
backup `46528aac20499e3b3928d58658d7e0cefe26feba7cd193796d5cfbf7a2bbc558`.
21 диапазон функций совпал между pins; сохранены15 полных assembly dumps.
IDA b852f877 закрыта с сохранением. Входные EXE не исполнялись.

| RVA | Подтверждённый контракт |
|---|---|
| 301870 | SetMsg(char*,bool): null guard, replace, color, extent, scroll, dialog size |
| 2444D0/244270 | Plain replace вызывает виртуальную вставку с цветом |
| 244540/244510 | Formatted replace/insert, отдельный FONT_INFO16 |
| 243860/243D30 | Естественный размер через последовательность фрагментов |
| 301630 | Виртуальный SetSize(width,height), подтверждён vtable entry12 |
| 3006E0/300900 | SetMsgBoardSize и SetScrollable |
| 300720 | Обычный pooled wrapper передаёт formatted/allowClose параметры |
| 300570/3010E0 | Error wrapper и constructor используют plain0 |
| 095010/095040 | Defaults FONT_INFO16, scale1/style0/size0/colorFFFFFFFF |

SetMsg для ненулевой строки создаёт font с цветом **FFE3E0D9**, очищает панель
и выбирает plain либо formatted. Plain сохраняет буквальные теги. Null pointer
возвращает управление до изменения текста или размеров. Измерение идёт через
уже перенесённые GDI byte metrics/TextBoard, включая сложение ширин отдельных
фрагментов и особенности конечного newline.

Существенное отличие от0.7: **ResizeToText вызывается до чтения текущей ширины
и высоты для scrollable ветки**. Поэтому заданный заранее положительный размер
панели заменяется естественным размером. Числа300/250 ограничивают только
fallback при неположительном результате; обычные непустые длинные сообщения
могут превысить оба значения. Не заменять это привычным max-width/max-height.

При height<required добавляется scrollbar, затем задаётся его размер, затем
подключается observer панели. Сам SetMsg не удаляет существующий scrollbar.
Dialog minimum200×100; добавки к размерам панели30/30 без полосы и60/45 с ней,
плюс соответствующие scrollbar width/button height. Сохранён старый SetBound
как source bridge: типизированный modal.SetSize вызывает этот layout. В эталоне
301630 является именно SetSize, а не методом, принимающим RECT. Общий базовый
GUIObject.SetSize пока nonvirtual; его полная миграция остаётся отдельным gap.

В обычный `_GUIMessageBox` добавлены подтверждённые параметры formatted и
allowClose с defaultsFALSE/TRUE. Это передаёт boolean в реальный SetMsg; rich
ветка поэтому удерживается линкером естественно. Никаких /INCLUDE/force-link
или переосмысления общего plain InsertText не добавлялось. Source create-info
получил удобное поле bFormatted455; это адаптация исходников, не утверждение
об исходном455struct ABI. Все target wrapper variants/guards ещё не перенесены.

## Проверки и границы

Расширена full-object modal probe:12 групп для каждого Korea/Russia, реальные
обычные классы, NDLanguage, GDI HFONT и D3D9. Независимый GetTextExtentPoint32A
проверяет локализованную строку, длинную строку и ширины rich фрагментов.
Проверены min-size, замена requested size, natural width>300/height>250,
конечный newline, plain literal tags, explicit rich/base color, null no-op,
уже добавленный scrollbar, typed SetSize, forwarding rich/close из wrapper.

Пустая строка и markup без фрагментов: target243D30 читает неинициализированный
newline local, если список пуст. Source SetMsg явно отклоняет этот домен после
clear/insert. Это **не подтверждённая эквивалентность**; unknown/UB остаётся в
реестре. Неизвестные signed-overflow/invalid geometry/OOM/failure paths и
непроверенные ветки автоматического добавления полосы также не приняты.

Первые40 W оказались слишком узкими в русском шрифте для условия>300; тестовая
строка увеличена до80 W. Производственный алгоритм не менялся ради fixture.
Обе финальные пробы завершились естественно exit0. SHA-256 собственной probe
`1a1b30228f3f3e6a297a7b615e945ebf83b5dfa0c965aad4e0d2e203e092b2c5`,
entryE6B20. Проверены10 кадров640×480: normal/hover/disabled/rich/rich-wrapper
для обеих локализаций. Все просмотрены; наличие красных glyph pixels rich
ветки дополнительно проверяет checkpoint. Это не pixel parity всего GUI455.

## Сборка и следующий шаг

Production SHA-256
`c22502faf1a98ed229ed62d341f4609ab5ca55f31c33bd26cdc2b7bc5aa83340`,
x86/base400000/entry150290,2041856байт.182client/20kernel/28facade TU,
0 unresolved. Map содержит обычный SetMsg и реальные TextBoard formatted/extent
providers; маленький SetSize adapter inlined, SetBound provider сохранён.
Generator preparation idempotent:
`ef02c4a396988b2528d602e0143f06d8ab205347936c882eff0bb4936f8326da`.
R3Engine archive056 не менялся.

Точная новая PE прошла WinMain/TCP fixture/engine/D3D/Character/existingCreate1;
остановлена до игрового цикла. Это не аутентификация и не полный вход.
Firstchance40080201 через KernelBase остаётся неизвестным, как068; успешный
checkpoint не доказывает соответствие всех exception/failure domains.
Затронутые Tutorial-board/font/metrics/TextBoard/scrollbar/EX-Var/minimap/input
проверки прошли;9 scoped checkpoints PARTIAL. Неизменённые большие particle/
runtime suites не повторялись. Число проверок не мера полноты455.

Далее070: настоящий CGUIBriefingWindow, его rich text/ресурсы/события/состояния;
затем Avatar/world/Tutorial host и четыре stage. Учитывать оставшиеся другие
GUI layers/IME/base virtual size/wrapper и прочие client-acceptance gaps.

Доказательства: `inventory/client455-message-sizing-reference.json`,
`inventory/client455-message-sizing-checkpoint.json`, обновлённые modal-native,
normal/preparation/link и ui-startup manifests. Raw evidence в игнорируемом
artifacts/client455-tutorial/message-sizing-*069.json, собственные кадры work/m9.
