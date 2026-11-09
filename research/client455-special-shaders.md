# Специальные шейдеры материалов455 — участок134

2026-11-10. **PARTIAL M6**, не полная отрисовка специальных материалов.
Текущий gate: `inventory/client455-special-shaders-checkpoint.json`.
Предыдущий133 и точные бинарные результаты сохранены под
`artifacts/client455-progress/before134/`, manifest40файлов. Игнорирование Git не
считается резервным копированием; этот локальный snapshot отдельный.

## Подтверждённая цепочка

Две закреплённые455, x86/base400000:

- b1b5febf0d0394712e2322350e19dafe60742e8642697b93cfb89135bac1fd8b;
- 46528aac20499e3b3928d58658d7e0cefe26feba7cd193796d5cfbf7a2bbc558.

15полных функций/1592инструкции/20совпадающих диапазонов. Проверены все
положительные начала CFG, pagination<=100; отдельно19инструкций нижнего
несмежного cleanup8C8060–8C8093 у8C94A0. `disasm(8C8060)` возвращает начало
основной функции, поэтому этот chunk получен через диапазон `insn_query`.
Точные SHA/RVA в `inventory/client455-special-shaders-reference.json`.
Сырые результаты/сессия: `artifacts/client455-progress/special-shader134-*.json`.
Owned IDA88087e5c saved/closed/list0. InputEXE не исполнялся.

Основные VA (для RVA вычесть400000):

- 8C57C0:обычный RestoreDevice вызывает Release903870, затем Load905220.
- 8C43F0:InvalidateDevice освобождает registry через903870.
- 903B90:предупреждение при shader<1.1/textures<4/disabledVS, затем продолжение.
  Обнуляются три массива128×264 и объекты128×1964.
- 905220:binary Init.r3o loader;при отсутствии обращается к text904B60.
- 903A70:читает SHO и XOR137;ключ совпал с уже проверенным Character ключом.
- 904450:D3DXCompileShader(main,profile,flags0), затем CreateVertex/PixelShader.
  Это отдельная цепочка от Character combinedSHO/flags8008/PS3.0.
- 904730/9036D0:FX compiler/append;положительные FX не проверялись.
- 903730/9037D0:добавление отдельной VS/PS записи,limit128.
- 903C80:сырой object view;903FC0/904120:object-indirect getters с `index<=count`.
- 8C94A0:DrawOneMatGroup dispatcher, пока только исследован.

Реальный `System/Shader/init.r3o`,1424байта:256-byte path,0FX,
2VS(vFraction/vPlazma,vs_2_0),2PS(pFraction/pPlazma,ps_2_0),0objects.
Не считать неиспользуемые байты после NUL в path/name/profile текстом.
SHO — single-stage HLSL,а не Character секции `[vertex shader]`/`[pixel shader]`.

При binary objects reader намеренно читает DWORD вoffset0 иDWORD вoffset2,
потом count и196-byte параметры;runtime stride1964. Второй DWORD задевает первые
два байта parameters,если параметров0. Binary loader НЕ публикует objectcount
в1175780. После real init count0 и нулевая запись0 всё равно доступны по<=.
Это особенности455,их нельзя исправлять как очевидную ошибку.

## Реально восстановлено

`scripts/native/client455_special_shaders.inc/.h` подключены к производному
r3d3d8.cpp. Реальные Restore/Invalidate вызывают загрузку/освобождение registry.
В обычной PE подтверждены прямые CALL release(RVA110FF0),load(RVA111060) из
RestoreDevice(RVA10F400). Новый владелец удержан обычным linker.

Три registry таблицы:имя256,program COM pointer+256,constant table/pool+260.
Runtime allocation352768байт. Общие материал/vertex/camera/particle заголовки
не изменились;182/20 клиентских модулей повторно не компилировались.
Из67engine objects payload изменился толькоr3d3d8.obj.

Engine SHA256 ec4fcca5accbaa898e86053d441007e375f3503caa45bb9bd1ee7bded0d5f24c.
RF_Online.bin SHA256 5c3e6bdb0215578dedde6411d4d1700b7657889a5afb79f78a92ce6c8ad6cad7,
2260480байт,entry16D9A0,WinMainB98B0,afterCreateB9A24,unresolved0.

Ресурсы закреплены через `prepare_client455_special_shaders.py`;runtime staging
включает binary list и4encryptedSHO при обычном device startup и full-object labs.
Исходная установленная игра не изменена.

## Проверки

`work/m9/f9254290/special-shaders-001`:настоящий device init создал4GPU programs
и их constant tables. Дамп GetFunction/reflection подтверждает shader model2.0.
Три вызова настоящего Invalidate/Restore:
registry полностью исчезает/перечитывается,bytecode всех4побайтно совпадает,
удержанная внешняя COM reference остаётся валидна. Dmalloc623360→623360,
process handles440→440,shader warnings0;финальный обычный teardown освобождает
registry. Отдельная staged fixture с2objects подтверждает196-byte параметры,
перекрытие DWORD и сохранение неопубликованного count0. Оригинал staging восстановлен.
Это циклы ресурсных callbacks на том же живом устройстве. Настоящие D3D9 Reset,
потеря устройства и смена режима этим стендом не проверены.

4малых теста bounded Python inventory parser:настоящий список,обрезанные границы,
capacity/NUL/trailing data,196-byte parameter row. Это не доказательство native
поведения на повреждённых файлах;native reader сохраняет исходные unsafe границы.

Свежая world-frame regression:76queue operations/16clock samples±1/5GPU frames.
Все5raw иPNG побайтно равны ранее просмотренному133. Просмотр переиспользован
явно;нового визуального просмотра не было. R3T warnings6 прежние,не shader failure.
Ранний звук1/окно/device/existingCreate1/контракты/providers проходят на новой PE.
Большие неизменённые suites159k не повторялись. Остальные29кадров133 — исторические,
не свежая проверка134.

## Следующая работа135 и ограничения

Приоритет — настоящий material draw dispatcher8C94A0 иconsumer8C9230,не отдельный
рисующий helper. `shader_object` выбирает index=wholeDWORDflag-01000001;
`light_object`:BYTE(flag>>8)-1 и сохраняемый BYTE(flag). Dispatcher извлекает
WORD из object,а getter снова индексирует objects:двойная индирекция подтверждена
кодом,но фактическая ветка DrawOneMatGroup ещё не перенесена.

Lightmap помещается вslot=layerCount;material textures в0..count-1. После draw
текстуры0..count-1/VS/PS очищаются,lightmap slot остаётся. Fixed multilayer branch
пропускается дляshaderflag01000000;flag40splat отдельный postpass не терять.

8C9230 уже полностью подтверждён133:projection c0..3/view c4..7/world c8..11;
VS/PS15=global1158038,float4;light owner1154E90/Get0 или fallbackVS18;
PS18.xy=scrollSHORT/256,PS18.z/w=новые floats при ANY-bit masks800001/800002;
PS17=GetBumpFactor,последняя компонента R3GetTime. Fog отключается без local restore.
Нужно проследить matrix/camera/light storage owners,не предполагать transpose или
значение четвёртой компоненты. vFraction используетVS13Divider,который этот
consumer не устанавливает:не добавлять production default без доказанного writer.

Text Init.r3s fallback904B60 только частично декомпилирован;в текущем коде его
отсутствие обозначено явной диагностикой,полная loader equivalence не заявляется.
Нужны полный fallback/904590 file compiler,positive FX иошибки/caps/OOM/overflow/
malformed input,все7GPUlayers,light owner иunused register lanes. Известные
resource quirks target на ошибках сохранены,но не сертифицированы тестами.
Вся матрица docs/client-acceptance.md остаётся действующей. M6/M6F/M7/M9 OPEN.
