# Material layout133 — семь runtime layers и46-byte wire prefix

2026-11-10. **PARTIAL M6**. Восстановлены runtime material526bytes,семь слоёв
по54bytes и два float поля specular flickering в конце каждого слоя. Binary R3M
по-прежнему читает46bytes на слой. Перенесены подтверждённые text writers и
2048 material count guard. Полный special-material shader pipeline ещё открыт.

Gate: `inventory/client455-material-layout-checkpoint.json`.
Проверка: `scripts/Invoke-Python.ps1 scripts/checkpoint_client455_material_layout.py`.
Runtime132 исторический,предыдущие static/math proofs сохранены. M6/M6F/M7/M9 OPEN.

## Основание в455

Primary SHA-256 `b1b5febf0d0394712e2322350e19dafe60742e8642697b93cfb89135bac1fd8b`;
secondary `46528aac20499e3b3928d58658d7e0cefe26feba7cd193796d5cfbf7a2bbc558`.
Оба x86/base400000. Пять full functions/1438 instructions/пять byte ranges
совпали между бинарниками. Полные CFG/pcode и все positive block starts проверены.
Дополнительно закреплён32-byte context2048 guard в main text parser;
full assembly этого отдельного parser здесь не заявляется.

| RVA | Роль |
|---|---|
| 0x509400 | MatInit memset526 и семь наборов layer defaults |
| 0x509500 | Text layer reader;extra floats,flags и runtime stride54 |
| 0x50a040 | Text material reader;семь surface defaults,flags shader/light |
| 0x50b1c0 | Binary R3M reader:allocation526,read46,stride54,version failure cleanup |
| 0x4c9230 | Special material shader consumer;PS18.zw читает новые float поля |

Семь слоёв теперь подтверждены initializer и семью surface writes,а не только
арифметикой526−148. Layer starts148+54*i. Extra fields находятся на layer+46/+50.
Text tokens именно `specular_flikering_scale` и `specular_flikering_speed`;
сохранена историческая орфография. Writers делают OR0x800001/0x800002 в layer flags.
Binary reader zeroes allocation и читает только prefix46,так что extra floats0.

Raw/session: `artifacts/client455-progress/material-layout133-*.json`.
Сессия24a6b8ee сохранена и закрыта;count0. Входные EXE не запускались.
В отдельном consumer8C9230 texture/UV параметры и новые поля идут в PS register18.
Его полный shader owner/draw pipeline ещё не перенесён. Восстановление хранения
и text metadata не считается завершением этого renderer contract.

## Исходники

Новый `client455_material_port.py` создаёт derived r3material455.h из неизменённого
legacy header. Guard и include order обеспечивают общий layout во всех engine/
client modules. Нет cast старого332-byte record к526:изменены реальные объявления,
capacity и вся компиляция потребителей. Static asserts проверяют526/54/46/50/148.

LoadIndependenceR3M читает46bytes вместо sizeof(runtime layer54). Исправлено
закрытие файла в ветке неверной версии по подтверждённому90B1C0. Сохранены
существующие base texture ID rebasing и NO_LOD/detail flag rules.

Text loader переносит specular extra fields,sky flags0x4/0x8/0x10/0x20,texture_splatting0x40,
shader_object и light_object. Последний сдвигает весь DWORD flags,прибавляет ID
и OR0x11000000. Это не отдельная masked byte вставка. Main text limit2048
вместо1024. Полный диапазон numeric/error/reload поведения ещё не принят.

## Проверки

Actual normal loaders,а не отдельная замена parser,прочитали:

- Два соседних binary records:семь46-byte layers и затем zero-layer sentinel.
  Все1052 runtime bytes совпали с независимым ожидаемым526/54 layout. Tail floats0,
  texture IDs rebased,соседний материал не перезаписан.
- Два соседних text records:слои0..6 со specular values,packed shader/light flags
  и zero-layer sentinel с семью default entries. Все1052 bytes совпали.
- Три malformed versions1.2 возвращаютNULL;process file handles245→245,
  три ожидаемых warning. Truncation/invalid layer indices/OOM остаются открытыми.

Native fixture: `work/m9/edb87690/material-layout-001`.
Generated inputs и оба binary dumps закреплены SHA-256. В CPU probe нет новых
изображений. Это подтверждает размещение и чтение семи слоёв,а не все7 GPU layers.

Изменён shared header:все182client/20kernel units пересобраны без ошибок.
Первая попытка link правильно отказала из-за старого ANI/BBX consumer report;
после свежей короткой проверки выполнен успешный link. Полную компиляцию
повторно не запускали. Последняя source правка version fclose затронула один
engine unit;headers после этого не менялись.

Engine67/21derived:42 payload changes,17 timestamp-only,8 byteequal132.
Engine SHA-256 `fa88420ddcc370d58758aea65431f530463f3ed855f957f3829e0dc580f2946c`.
RF_Online.bin x86/2256384bytes/base400000/entryRVA16CC90:
`b9002c4c0bc962af89c72bc7f6768f2b8610c8ffcc3ceed3d3ddbcced3a61e0a`.
Unresolved0;no CharacterMR/FORCE. Exact132 engine/PE/MAP/rsp/reports/shared headers
и исходный material header сохранены до изменений. Ignored не означает backup.

Свежие actual NeutralB owner77entries/2loads/20available lit entries,4BSPdraws;
72LitGrass directions/12FP modes,5328normals/8material states/3bump times;
world76queue/16clock,material60/36,fade90+27,lighting867/3/27Mie иweather90/5 PASS.
34 raw+PNG кадров побайтно равны просмотренным132;explicit review reuse,
новый просмотр изображений не заявляется. Unchanged240CPU math proof сохранён;
три точных math bodies перепроверены в новой PE. Собственная PE sound/window/
device/existingCreate1/contracts/providers PASS. Старые bulk suites не повторялись.

Следующий134:actual special-material shader dispatch/owner и consumer8C9230,
реальные shader_object/light_object inputs и GPU parameter binds. Далее caps/
failure/reset/OOM,все7GPU layers и оставшиеся material/world/CRT/UI/protocol/
Character/gameplay acceptance gaps. Серверы и оригиналы не изменялись,публикации нет.
