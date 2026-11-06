# Unicode/GDI текст 455 в обычном UI — 046

Дополнение047: подтверждённая null-level ветка CLand перенесена; из актуального
font probe удалено специальное Land.Create. Оба прежних кадра и естественный
exit0 сохранены. Описанное ниже создание Land относится к исторической046
пробе. [Текущие доказательства](client455-lifecycle.md).

06.11.2026. M6, частичный результат. Восстановленный GDI/Unicode путь теперь
используется обычными R3LoadTextTexture/DrawR3Hangul. Настоящий CGUIText отрисовал
корейское «벨라토» и русское «Беллато» из NDLanguage; его кадры совпали с прямым
Unicode-вызовом того же backend. Метрики и alpha4 atlas отдельно сверены с
независимым Windows GDI. Полные UI/IME/FreeType/ANSI и M9 остаются открытыми.

## Источник и границы

Current SHA-256 `b1b5febf0d0394712e2322350e19dafe60742e8642697b93cfb89135bac1fd8b`,
backup `46528aac20499e3b3928d58658d7e0cefe26feba7cd193796d5cfbf7a2bbc558`;
оба x86/base400000.21тело/диапазон font/bootstrap/cache/draw совпали в обоих PE.
RVA/размеры/SHA — `inventory/client455-font-reference.json`. Raw IDA в
`artifacts/client455-font/`; sessiona9adfb47 закрыта/save=true. Граница функции
8C5C60..8C5F1A установлена по непрерывным инструкциям/ветвлениям и сохранена
только в собственной IDB. Входные EXE не исполнялись.

| Контракт | VA | RVA |
|---|---|---|
| Параметры страны/шрифта | 8C5A80 | 4C5A80 |
| Обычный GDI bootstrap трёх шрифтов | 8C5AE0 | 4C5AE0 |
| Отдельный configured FreeType bootstrap | 8C5C60 | 4C5C60 |
| Font name/charset | 9057F0/905810 | 5057F0/505810 |
| D3DX atlas creation | 905920 | 505920 |
| GDI/DIB/метрики | 9067E0 | 5067E0 |
| Unicode cache search | 905CF0 | 505CF0 |
| Выбор/вытеснение строки atlas | 906C10 | 506C10 |
| ExtTextOutW/alpha4 upload | 906DD0 | 506DD0 |
| UV/clipping/6vertices | 906F60 | 506F60 |
| Draw/shadow/outline/bold | 907710 | 507710 |

В455 недостаточно поменять имя старого CR3Font. Старый reader фиксировал6×12
пикселей на байт; новый Unicode кэш учитывает измеренную ширину и число WCHAR.
Оригинальный private font object2040bytes отличается от старого layout.
Source backend имеет собственные типы и не накладывает эти offsets на старый
CR3Font. Старый CR3Font.cpp сохранён в67unit engine, но обычный text bridge
больше не создаёт его глобальный экземпляр.

`8C5A80` копирует250байт в два256byte name globals и записывает points9,height12,
charset. Height12 здесь не основание для fixed glyph height: GDI использует
измеренную высоту. Locale bootstrap045 теперь применяет эти параметры перед
NDLanguage loading, как подтверждённый порядок7CFB10.

`905920`: D3DXCreateTexture(format26/A4R4G4B4,managed),GetCaps и два stateblock.
`9067E0`: DIB width=atlasWidth,height=-3×points; CreateFontA c выбранным charset,
quality0/pitch0; negative height=-MulDiv(points,DPI,72). Метрика `"w"` задаёт
cellWidth/Height; rows=atlasHeight/cellHeight,columns=atlasWidth/cellWidth.

Поиск кэша идёт по строкам/записям в прежнем порядке и сравнивает WCHAR bytes.
Новая запись должна вместиться и по pixels, и по числу WCHAR. При заполнении
вытесняется следующий row по кругу. Публикация записи предшествует LockRect,
поэтому failed upload не подменён удачным retry. ExtTextOutW с ETO_OPAQUE;
из младшего канала bitmap берутся bits4..7 и переводятся в alpha4|white RGB.

Рендер: FVF324,28byte stride,TRIANGLELIST; UV clipping меняет ширину/высоту
прямоугольника,vertices учитывают -0.5. Shadow даёт2прохода,outline8+1,bold2.
После draw ALPHABLEND выключен; linear filter по0x400 остаётся состоянием
устройства. Нормальный/16point/24point font выбирается по high flag bits.

Обычный bootstrap создаёт normal atlas512/1024 по порогам100/160million bytes,
16point1024×128 и24point1024×512; extra face Tahoma либоA010. System/010.TTF
добавляется/удаляется настоящими GDI APIs. У own labs удаляется только их копия,
в finally после controlled stop/ошибки; исходный font file не регистрируется и
не удаляется. Оригиналы, серверы и пользовательские учётные данные не менялись.

## Реализация и проверка

- `client455_font_settings.h/.cpp`: country parameters и codepage для source bridge.
- `client455_font.h/.cpp`: source-owned GDI/Unicode owner/atlas/cache/draw.
- `client455_text_bridge.inc`: обычные engine public calls → этот backend.
- Производный engine заменяет только r3text.cpp в дополнение к двум исправлениям043;
 67units,033source/library сохранены. Новая library SHA
 `d0ef3b09bf260a5d513ceb7fad6468b5dcda5cfe5ed5108eaab445e746ee2b3a`.

182client/15facade/20canonical kernel objects,полный link0unresolved,без
CharacterMR и `/FORCE`. Own RF_Online.bin:

- SHA-256 `88942d085c1de3a349c337b51a91a3ca311e9522b112f824fc2105ebfa85289f`;
- x86/base400000,1 998 336bytes,entry RVA1485A0;
- WinMain B3D40,afterSound B3D89,afterD3D B3D9C,beforeCharData B3469.

Actual own PE под `work/m9/88942d08/`: Korean/Russian language/Miles прошли;
normal device/Create marker прошли, `RF455 Font:GDI:129:0` наблюдён вtrace.
Character device516afa0 равенapp device,ownerA2F3060. Остановка перед старыми
data readers,exitE0434200 наблюдён. Дополнительные first-chance C++ события
обработаны runtime;second-chance нет. Регистрация lab font удалена=true.

`probe_client455_font.py` линкует реальный normal client object set с собственным
console entry. Он вызывает CMainApp::InitR3D3D и actual CGUIText::Draw. Это
selected UI consumer внутри собственного entry,не полный production WinMain/UI.
Land member создаётся ровно его реальным Create перед выходом; типизированный
pointer-to-member получен компилятором через explicit instantiation,без guessed
offset/private-layout overlay/изменения класса. Полный CMainApp::Create с ещё
старыми table readers не вызывается.

Почему fixture создаёт Land: первый запуск нарисовал кадр, но завершился AV
при глобальном ~CLand. У старого CLand::Destroy безусловный UnloadLevel вызывает
null m_pLevel->ReleaseLevel до Create. Факт зафиксирован: own exception RVA7DD9C
вReleaseLevel,READ null+158h,raw work/m9/e73bb511/font-ko-kr001/exception.json.
Это известный разрыв early-abort/жизненного цикла; production guard не выдуман
ради теста. После реального создания Land оба процесса завершились сexit0.
Normal early-exit/shutdown всё ещё требует восстановления по455.

GUI frame равен прямому wide вызову; отдельный GDI oracle сравнил LOGFONT charset/
quality/pitch,метрику и каждый uploaded alpha4 texel. Проверены cache hits,
вытеснение rows,post-draw blend/filter. Видимых текстовых pixels внутри viewport
151(Korea)/179(Russia); счётчик исключает нижнюю полосу вне viewport. Actual
backbuffer640×500,viewport/configheight480 — это отдельный незакрытый sizing gap.
Preview BMP просмотрены: Hangul и кириллица читаемы. Последние пути/хеши кадров
хранятся в `inventory/client455-font-native.json`.

Короткие ANI/BBX/model/effect/shadow/clock/accounting регрессии прошли; прежние
цветные/effect/shadow кадры совпали,COM/Dmalloc0 в этих сценариях. Неизменённые
большие исторические suites не повторялись.13scoped checkpoints PASS/PARTIAL;
M6/M6F/M7/M9 открыты.

## Известные границы и продолжение

Source использует RAII rows и освобождает перезаписываемые initial stateblocks;
original allocation/leak/OOM/unsafe domains не объявлены эквивалентными.
Полный2040byte ABI,всеx87/floatingpoint modes,всеerror paths/стили/размеры не
приняты. Изображение glyph зависит от установленногоWindows font set/DPI/
fontlinking; GDI oracle не заменяет сравнение полного игрового кадра с455.

FreeType/configuredfont8C5C60,ANSI-specific cache,полный text API/IME/wordwrap
и UI layout остаются M6. Они не заменены фиктивным успешным FT provider.
Старый CGUIText::SetString всё ещё считает byteWidth6; selected Draw не доказывает
правильность размеров/clipping/указателякаретки всего455UI.

Следом047: восстановить early-abort/lifecycle CLand/CMainApp по эталону,затем
продолжить normal Create/data/UI/launcher. Сохранить обязательные FT/text/IME
gaps в очереди M6 перед M6F. Серверные компоненты не требуются и не разрабатываются.

Повтор: audit_client455_font.py;prepare/build normal;build_client455_engine_startup;
startup contracts;normal consumers/full link;probe_client455_font.py;own-entry/
startup audit и обычные startup/device/Create probes;checkpoint_client455_font.py.
Все Python через scripts/Invoke-Python.ps1. CPU/layout и целевые регрессии — по
изменениям; не повторять исторические большие наборы без риска.
