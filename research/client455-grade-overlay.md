# 148A: материалы свечения и дополнительный проход экипировки

10.11.2026. PARTIAL, M6/M6F/M7/M9 открыты.
Gate:inventory/client455-grade-overlay-checkpoint.json.
RF_Online.bin03637d6a6630c52aa6a966c777b5690679c10b2c2a6d6acf9888e16ed1761d91,
x86/entry1771C0,182client/67engine/20kernels/unresolved0.
Engine4c6652a59c7172ad8f852d599c9a42183a5658d728ebd32959f65e1668b002b5.

## Перенесено

- Четыре526-byte материала с54-byte слоями: Bgrade,Agrade,Cgrade,Dgrade;
  настоящие DDS,полный набор выбранных командами217-line parser свойств.
- Grade0 не трогает GPU;grade>4 выбирает последний. Шейдер9 для UV,
  10 для environment;матрица идёт в VS c92,НЕ D3D texture-transform.
- Begin устанавливает настоящие текстуры/смешивание/свет/ZWrite;
  End восстанавливает конкретный набор состояний,не произвольный state-block.
- 92E140/92FBE0:вторичная геометрия сохраняет shader/textures вызывающего,
  использует реальные palettes/VBO/CPU/batch providers иочищает shader в конце.
  У времени отдельные overlay globals;основной render не заменён этим маршрутом.
- Archive mode setter/getter8E75D0/8E75E0 иgatedOpen/Exists8E7680/8E75F0.
  Flag сохраняет исходное целое,в том числе17;выключение не удаляет RPKgroup.
  Собственный API SetResourceGroup публикует иактивирует группу.
  Привязки всех исходных455producer-вызовов ещё не приняты.
- Вобычные CreateEffect/DestroyEffect добавлены grade load/release на целевых
  местах. Их фактические CALL в own PE проверены. Исполнение этих мест при
  Login не заявляется. Общий mesh-object Render иCPlayerProc ещё не подключены.

Статика:19новых полных функций2677инструкций/229CFG плюс2переиспользованные
Begin/End из предшествующего исследования:21/2863/239.5dataregions:
порядок имён MST ичетыре строки. SHA-256,x86,RVA обоих эталонов сохранены
в inventory/client455-grade-overlay-reference.json. Raw/ASM:
artifacts/client455-progress/grade-overlay148-reference/session.json.
Исходные EXE не выполнялись. Серверные файлы не менялись.

## Проверено исполнением

Реальные4MST/4GPUтекстуры;все2104байта материалов сверены с независимыми
замороженными значениями. Дополнительный личный fixture проверяет слой6 и
команды,которых нет в штатных4файлах;3malformed cases даютограниченный отказ.
Исходные MST в probe копируются отдельно,меняются только личные копии,
после теста исходные байты восстановлены. Shared оригиналы не меняются.

Нормальный проход иследующий overlay рисуют реальную Bellatoдеталь брони
вконтролируемой позе/камере.7настоящих GPU submissions и2659изменённых RGBpixels.
Это доказательство работы данного backend,не внешнего вида полного персонажа.
Первый одиночный проход был пуст:fixture не подготовил SetState/основной draw.
После исправления последовательности результат проверяется пикселями,
ане одним счётчиком calls. Неиспользуемая чёрная полоса viewport исключена
из счётчика видимой модели.

Archive/loose fallback иExists проверены на маленьком собственном RPK:
flag1/0/17 меняет реальный источник,приэтом группа остаётся загруженной.
UV-функция читает все7слоёв54-byte ABI;подозрение о старом46-byte ABI
не подтвердилось. Переделки этого backend не потребовалось.

Create/Login изатронутый account/registered receiver3Avatar собственной PE
прошли. Login66/3031ms просмотрен:lobby/ожидание ипрежняя Betaметка;
успешный вход/выбор/мир не проверены. Девять first-chance как147,unhandled0.

Сами вторичные geometry functions обычный linker пока удаляет:
они вызываются full-object probe,не обычным player renderer. Это явно
сохранено в gate как secondary_geometry_retained_in_normal_PE=false.
Не выдавать данный участок за готовый full equipment илиM9.

## Остаток

CMeshObject/CEquipObject Render overloads,эффектная очередь/RenderWithShadow,
producer overlay604,обычные CPlayerProc/Avatar/frame/animation/conditions,
bootstrap/selection/world/gameplay/lifecycle. Неинициализированные поля,
все archive-mode producers,malformed/OOM/EOF/repeated-load иCRT/FP также открыты.
Диагностические queue/ctor pcode сохранены отдельно;это ещё не полное ASM-доказательство.
IDA c6eeef7e saved/closed/list0. Новых установок не нужно.
Финальный staging166840076logicalbytes:новых poolbytes0;полной копии клиента нет.
