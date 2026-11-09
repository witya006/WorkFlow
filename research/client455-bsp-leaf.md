# BSP: обратные координаты и владельцы — участок122

2026-11-09. PARTIAL M6. Восстановлен реальный шаг world→local в
CBsp::GetLeafNum. Текущий gate: inventory/client455-bsp-leaf-checkpoint.json.
Это не полная приёмка BSP, ILevel, renderer или клиента.

## Подтверждённые факты

PE32 x86, preferred base400000. Primary SHA-256:
`b1b5febf0d0394712e2322350e19dafe60742e8642697b93cfb89135bac1fd8b`;
secondary:
`46528aac20499e3b3928d58658d7e0cefe26feba7cd193796d5cfbf7a2bbc558`.
13 полных тел/asm,971 инструкция совпадают:11 новых/742,2cached120/229.
Страницы<=100 инструкций проверены по len/count/sum/total/unique.
Полные выбранные pcode включают отдельный tail104-line INS loader.
Остальные поисковые pcode в raw могут быть частичными и полными не объявлены.

| RVA | Подтверждённая роль |
| --- | --- |
| 4FAF00 | GetLeafNum: inverse transform,search=-1,SearchNode1,return leaf |
| 4FAE20 | SearchNode;leaf0 не завершает поиск,нужен leaf>0 |
| 4C0980 | Affine XYZ transform без деления наW |
| 4EABF0 | CInstanceNode ctor,world/inverse изначально нулевые |
| 4EADC0 | Instance cell coords;world translation=cell×30000,inverse,bounds±15000 |
| 4EC850 | INS draw:27 nodes со stride276 |
| 4EB5E0 | INS metadata reader;все нормальные возвраты дают0 |
| 4ED220 | INS load:success block зависит от ненулевого4EB5E0 |
| 4ECFA0 | INS ctor;82 BSP records и27instance nodes |
| 510DD0 | CPlanetZoneNode ctor,отдельный тип |
| 512000 | CPlanetLevel ctor;27nodes со stride260 |
| 513800 | Planet draw:отдельные node callers |
| 3C8600 | CLand выбираетINS по расширению,иначеCLevel |

Настоящие vtables INS B3872C/load slot9→8ED220/draw slot18→8EC850 и
Planet B3A0BC/draw slot18→913800 совпадают между pins. RTTI COL/type descriptor
подтверждают имена CInstanceNode и CPlanetLevel,не по соседству функций.
Матрицы из121setter принадлежат отдельным instance/planet node owners.
Это не основание добавлять произвольный matrix writer в обычный CLevel.

В supplied Map tree не найдено файлов.ins/.wld. Более сильный факт — полный
4EB5E0:общий нормальный epilogue обнуляетEAX;поэтому его обычный ненулевой
success return в этом pin не подтверждается. Это не отменяет side effects,
ошибки/выходы,constructor/destructor/console/ILevel и не закрывает весьINS.
CLand исходника по-прежнему явно отказывает.ins;этот gap НЕ удалён.
Найденный caller Planet ctor находится в8E2500 с командами загрузки/capture;
полный console handler и достижимость из обычной игры не приняты.

## Перенос и проверка

Старый GetLeafNum копировал мировую точку напрямую в mTempCamera. Теперь он
вызывает существующий source455 affine helper с сохранённой inverse матрицей
CBsp,затем исходный SearchNode1. World matrix не инвертируется повторно.
Helper использует клиентскую реализацию x87 math;нового D3DX/projective
преобразования нет. Identity ordinary maps сохраняют поведение.

`work/m9/1e5a3366/bsp-leaf-001`:140 коротких воспроизводимых случаев.
Настоящий метод из полного собственного набора клиентских объектов проверен
для7 матриц(identity,translation,90°rotation,scale,reflection,shear,ненулевые
неиспользуемые homogeneous terms),4 BSP топологий и5 точек.
Все leaf IDs и1680 байт localXYZ точно совпали с независимым Python oracle.
Примеры сохраняют необычный target fallback после leaf0,negative initial
search и отсутствие W-divide. Второй CBsp сохраняет свою identity inverse.
World намеренно отличается от inverse,чтобы исключить скрытое её вычисление.
Это конечные affine примеры,не доказательство всех FP/CRT/NaN/unsafe domains.

Настоящая Bellato `work/m9/52d6745b/world-frame-001`:76queue operations,
16 OSclock samples±1,rayhit,16 archivedFX light frames,3ValidateDevice S_OK.
5 GPU кадров просмотрены и побайтно равны121. Base==clear;magic151256,
regular146637,FX646571 изменённых байт отclear.6 штатных warnings сохранены.
`work/m9/a3fb1290/map-data-001`:2692checks/330geometry/110maps/canonical PASS.
Точная новая PE проходит own entry/imports/startup sound1/contracts/device/
window/existingCreate1. Обработанные first-chance exceptions сохранены.

Новых GPU сравнений с запущенным455 нет:входныеEXE не запускались.
Старые geometry33/ANI-BBX/quake/explosion/texture/receiver/Character/159k
проверки не повторялись и считаются историческими.

## Сборка и воспроизведение

Engine67/14derived SHA-256:
`2fa70824eb20d19588c5043b438f12176f49e61065b31e68175da588e80bc1e4`.
Изменился только bsp.obj,66 members byteequal. Все shared overlays совпали
с121;182client/20kernel compile objects не менялись. НоваяPE связана с этим
engine,unresolved0,безCharacterMR/FORCE. SHA-256:
`b0b13a09b36ec625202244d3998c4581b702caa508c9cd38a329a0e9c5485af9`;
2226176bytes,x86/base400000,entry167600,WinMainb98b0/afterCreateb9a24.
Точные121 engine/PE/reports сохранены под artifacts/client455-progress/
engine-before122.lib,normal-before122.bin,*-before122.json.
Baseline033 сохранён;старый отсутствующий082derivedsnapshot остаётся gap.

Raw bsp-leaf122-reference/session.json сохранены в artifacts/client455-progress/.
IDA279e61eb saved/closed,list0. Source — scripts/native/client455_bsp_leaf.inc;
генератор — build_client455_engine_startup.py. Повтор gate:
scripts/Invoke-Python.ps1 scripts/checkpoint_client455_bsp_leaf.py.
Оригиналы и серверы не менялись;только локальный Git.

## Открыто и далее123

Полные ReadyBspRender/local-camera/visibility/world-frustum/alpha/entity caches
и их владельцы не восстановлены одним GetLeafNum. Не переносить affine
поправку повсюду без доказательства пространства каждого аргумента.

Следующий приоритет — обычный CLevel sky/projection:8E7A10 временно задаёт
near2 перед sky,вызывает fade и восстанавливает perspective либо orthographic
projection с frustum refresh. Legacy wrapper отличается. Перед новым state
проверить реальные writers orthographic flag/scale и существующие APIs.
Полный sky renderer/fade/device reset/Character/gameplay остаётся отдельной
приёмкой. INS/Planet/ILevel gaps сохранены,а не объявлены ненужными.
M6/M6F/M7/M9 OPEN;цельM9 не изменена.
