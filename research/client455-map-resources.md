# Карты и реальные ресурсы погоды455

M5 остаётся в работе. Получены форматы контейнеров и воспроизводимый аудит данных;
обычный LoadLevel, GPU и полное поведение particle455 этим не проверены.
Клиентские исходники/сборки в этом цикле не менялись. Серверы не затрагивались.

## Бинарные доказательства

Оба закреплённых PE: x86, base0x400000. Current SHA-256
b1b5febf0d0394712e2322350e19dafe60742e8642697b93cfb89135bac1fd8b,
backup46528aac20499e3b3928d58658d7e0cefe26feba7cd193796d5cfbf7a2bbc558.
Все15 исследованных function bodies совпали между ними. SHA/размеры/VA/RVA и
конкретные инструкции: inventory/client455-map-resources.json. Raw decomp сохранён
в ignored artifacts/map455-analysis; owned IDA session295aeb19 закрыта с сохранением.

| Функция | VA / RVA | Подтверждённый контракт |
|---|---|---|
| RPK index | 0x8E6C50 /0x4E6C50 | float1.0, count,72*count bytes таблиц; payload base8+72*count |
| Path lookup | 0x8E6E70 /0x4E6E70 | дерево компонентов, directory offset=-1, file offset из отдельной таблицы |
| RPK fopen | 0x8E70D0 /0x4E70D0 | обычный FILE*, fseek(payloadBase+offset); размер файла не ограничивает чтение |
| Group lookup | 0x8E74B0 /0x4E74B0 | lowercases input, prefix length отсекается, поиск архивов по порядку группы |
| Wrapper | 0x8E7680 /0x4E7680 | активная группа сначала, loose fopen fallback; без группы сразу loose |
| BSP load | 0x8FDEA0 /0x4FDEA0 | header684bytes, DWORD version39, последовательное чтение, сумма35ReadSpare пропускается |
| EBP load | 0x8FF280 /0x4FF280 | header388bytes, DWORD version20 |
| Particle SPT | 0x8DB5B0 /0x4DB5B0 | archive-aware fopen; case-sensitive end до lowercase останавливает parsing |
| R3E geometry | 0x8E0A20 /0x4E0A20 | контейнер entity и дальнейший CPU/GPU путь; полный перенос не заявлен |
| R3T load | 0x8F33B0 /0x4F33B0 | version/count,128-byte names, size+embedded DDS для каждой текстуры |
| DDS mask | 0x8F1810 /0x4F1810 | XOR первых128bytes static mask0xBF7F00/RVA0x7F7F00; остальной payload не меняется |

RPK group scan0x8E71C0/RVA0x4E71C0 тоже изучен. Точный Windows enumeration order,
его skip-first/limit quirks, locale/path behavior и error/OOM domain пока не
воспроизведены. Нельзя заменить это сортировкой имён и объявить соответствие.

## RPK1.0

Header8bytes: float1.0, DWORD count. Далее count DWORD child indices, count signed
DWORD payload offsets и count64-byte nodes. Node: name[52], declaredSizeDWORD+52,
nameLengthWORD+56, childCountWORD+58, childStartDWORD+60. Offset-1 означает directory.
Повторяющиеся directory nodes с одинаковыми именами встречаются в реальных архивах.
Файлы открываются позиционированным FILE*, виртуальный EOF не устанавливается.

Tool scripts/rpk455.py сохранил bytes всех78MapEntity archives:3775file entries.
Проверены таблицы/дерево/компоненты/границы offsets. Repack заново формирует таблицы
и nodes, сохраняя opaque padding и payload.1067declaredSize не совпадают с extent
до следующего file offset/EOF. Частый наблюдаемый случай: uint32(-1-offset), когда
следующий node — directory. Это наблюдение о данных, причина генерации не доказана.
Игровой fopen не использует declaredSize; tooling сохраняет неверные поля и отдельно
использует inferred extent. Такой extent требует проверки собственного формата.
Tool не эмулирует небезопасные ошибки оригинального parser.

Legacy client/R3Engine не содержат RPK/group/fopen реализации. Кроме того, старый
LoadParticleSPT читает до EOF и игнорирует end. Просто заменить fopen на архивный
будет недостаточно: parser начнёт читать следующие записи архива.455 проверяет
end до [Particle] и в основном цикле до strlwr (0x8DB650 и0x8DB741). Это следующий
исходниковый перенос; сейчас эти два пробела только описаны, не закрыты.

## BSP39 / EBP20

Существующие684/388-byte header layouts legacy совпадают по размеру и версиям с455.
scripts/map455.py проверил70BSP+93EBP: границы непустых lumps, делимость известных
record sizes, lossless header/table round trip с неизменённым payload. Node24,
Leaf25, Object88, ReadMatGroup42; EBP EntityList84, MapEntitiesList38. Полная семантика
геометрии/индексов/анимации/коллизий этим не сертифицирована.

У Dungeon00/dungeon00.bsp сохранённые offset поля устарели: FVertex offset427104
перекрывает Track401374..442550, другие offsets тоже расходятся.455 читает известные
секции последовательно, а не seek по каждому offset. Сумма последовательных чтений
и skip равна точному размеру файла2936270. Файл не исправлялся; anomaly явно в отчёте.
У остальных162контейнеров ненулевые offsets совпали с последовательным порядком;
после выбранного последовательного набора у всех163нет лишнего хвоста. Это проверка
контейнера, а не доказательство правильного исполнения LoadBsp на GPU.

## Погодные зависимости

65loose R3X содержат6уникальных активных weather paths (25slot uses). Пять SPT найдены
в MapEntity13/20/26/28.rpk: snow, cora_cir_light, fe,fe2,magmadust. Для каждого найдены
реальные R3E113/R3M/R3T модели: всего20unmodified assets сохранены под
work/map-resource-audit/selected, с SHA/архивным offset/node/declaredSize/extent.
Модели/текстуры не запускались; geometry headers проверены отдельно.

| Weather | Particle count из файла | Модель | DDS |
|---|---:|---|---|
| fe |15| e_pf/fsmk2/smk |128x128 DXT1,8mips,masked |
| fe2 |500| e_pf/spkl_y/spkl_b |64x64 DXT3,7mips,masked |
| snow |800| e_resources/snow/snow |64x64 DXT1,5mips,plain |
| cora_cir_light |40| e_cora/cir_light/cir_light |256x256 DXT5,9mips,masked |
| magmadust |150| e_cauldron01/magmadust/magmadust |128x128 DXT3,6mips,masked |

Проверены R3T1.1/1.2 framing,128-byte mask (равен в обоих PE), DDS magic/header,
dimensions/FourCC/mips и точный размер DXT blocks всех пяти текстур. GPU decode,
sampling/material/blending, реальный emission/curve/collision не выполнялись.
Числа particle count в таблице — данные scripts, а не native runtime result.

Не найден .\map\Entity\e_cauldron_boss_tower\spt\magmadust.spt, используемый тремя
R3X Cauldron_TowerA/B/C. Точного directory component нет во всех162RPK indexes
установленного клиента (таблицы отдельно хешированы), loose path отсутствует.
Не подменять его похожим e_cauldron01 ресурсом. Поведение отсутствующего входа и
возможное происхождение комплекта остаются вопросами; это не блокирует другие карты.

## Повтор проверки и следующий шаг

scripts/Invoke-Python.ps1 scripts/test_map455.py —8tests: rebuild, неверные версии,
truncation/count, tree cycle/ranges/names/duplicates, offsets, strides, явный overlap,
plain/masked DDS и malformed lengths. Все прошли. Затем
scripts/Invoke-Python.ps1 scripts/audit_client_map_resources455.py воспроизводит аудит,
сверяет оба PE и hashes, сохраняет20assets только под work/ и отказывается затереть
изменённый snapshot. Обычный и lab EXE не менялись, прежние native suites не повторялись.

Далее восстановить source RPK/group/fopen и end boundaries particle parser, проверить
их собственным native code на найденных assets/fixtures. Затем реальные entity/particle
load и обычный LoadLevel/FPU/GPU; clock/time caller идёт после необходимого resource path.
Не закрывать M5 по этому статическому аудиту; критерии M9 прежние.
