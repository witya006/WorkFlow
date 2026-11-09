# Map entity owner132 — включение освещения из EBP

2026-11-10. **PARTIAL M6**. В обычном CBsp::LoadEntities восстановлен перенос
bit0x40 из записи карты в успешно загруженный CEntity. Раньше старые исходники
передавали только map-color и shader flags, поэтому новые fixed/LitGrass методы
не получали флаг освещения от этого настоящего игрового владельца.

Gate: `inventory/client455-entity-owner-checkpoint.json`.
Проверка: `scripts/Invoke-Python.ps1 scripts/checkpoint_client455_entity_owner.py`.
Runtime131 исторический; его точные math/source и static proofs сохраняются.
M6/M6F/M7/M9 OPEN. Полный клиент и все игровые writers не приняты.

## Источник поведения

Primary455 SHA-256 `b1b5febf0d0394712e2322350e19dafe60742e8642697b93cfb89135bac1fd8b`;
secondary455 `46528aac20499e3b3928d58658d7e0cefe26feba7cd193796d5cfbf7a2bbc558`.
Оба x86/base0x400000. Пять функций/1665 инструкций/пять byte ranges совпали.
Полные CFG, positive block starts и pcode проверены.1025 инструкций LoadEntity
повторно использованы из полного анализа130; неизменённая pagination не повторялась.
Новые640 инструкций покрывают следующие четыре функции и их связи:

| RVA | Роль |
|---|---|
| 0x4ff280 | EBP20 load и чтение EntityList |
| 0x4fde00 | Загрузка связанных placement/leaf streams и вызов LoadEntities |
| 0x4f94a0 | Создание real CEntity/CParticle, shader fallback и перенос bit40 |
| 0x4e08a0 | RestoreTexMem после успешной загрузки |
| 0x4e0a20 | LoadEntity присваивает исходный option; доказательство130 использовано повторно |

Запись EntityList имеет84bytes, Flag offset72, ShaderID74. CEntity flags —
offset104. Реальные инструкции VA8F9690 проверяют byte72 &0x40,
VA8F969D выполняет OR0x40 в entity+104. При отказе LoadEntity переход обходит OR.
Particle branch не получает эту операцию. При выключенных шейдерах ShaderID
обнуляется до выбора loader options. Остальные биты record.Flag не копируются.
Исходник вставлен перед RestoreTexMem в том же успешном nonparticle branch.

Raw/session: `artifacts/client455-progress/entity-owner132-*.json`.
Сессия3022d6f4 сохранена/закрыта, count0. Input EXE не запускался.
Статическая связь RenderOneEntityRender→CEntity fixed/shader methods подтверждена
участком130;132 проверяет её на автоматически загруженных объектах карты.

## Реальные входы и исполнение

Инвентаризация физических Map/**/*.ebp в переданном комплекте:93 файла,
3700 записей,1584 static rows с bit40,82 из них со ShaderID. Эти числа включают
дубликаты/альтернативные файлы и не означают уникальные модели,93 принятые карты
или1584 завершённых игровых сценария. SHA-256 каждого файла сохранён.

На настоящей neutralB таблица содержит77 entries,21 static lit record и15 lit
shader records. Один flagged объект — известный отсутствующий
e_neutralA/trade_bel/trade_bel.r3e. Он не подменялся. При каждом из двух обычных
CLand/CLevel loads загружено20 lit owners. Shader capability fixture1/0 проверяет
и сохранение source ShaderID, и его обнуление до выбора flags. Проверяются все77
runtime rows против независимого разбора исходного EBP, включая failed load.

Четыре GPU кадра:настоящие размещённые b_gate и b_tree04 при shader1/0.
Флаг CEntity вручную не задаётся. Native fixture задаёт камеру и её inverse view,
затем вызывает обычные FrameMove/DrawMapRender/DrawMapEntitiesRender для подготовки
видимости и alpha. После этого RenderOneEntityRender рисует выбранный экземпляр
в отдельный очищенный кадр. Подтверждены реальные indexed draws,stride36,
MODULATE4 и выбор fixed/LitGrass;300-byte shader dump равен исходному LitGrass1.vso.
Новая видимость и alpha queue не считаются полностью эквивалентными455 по этой
проверке:они использованы как существующая цепочка, полная приёмка остаётся открытой.

Native run: `work/m9/76a8740b/entity-owner-001`. Четыре кадра просмотрены.
Объекты различимы; дерево меняет освещение при выборе shader path. Сравнения
с пикселями работающего455 не было; исходный EXE не запускался.

Первый harness предполагал5 кадров; общий runner теперь принимает expected_frames
с прежним default5. Неверное ожидание21 loaded исправлено по реальному missing
input:21 исходная запись,20 успешных загрузок. Начальный direct render имелalpha0:
требовалась обычная visibility queue и inverse view от camera owner. Исправлена
именно подготовка native lab; production не менялся ради этих кадров.

## Текущая сборка

Engine67/21derived:один payload bsp.obj изменён,66 побайтно равны131.
Shared headers не менялись,182client/20kernel objects сохранены.
Engine SHA-256 `b710d6c802cc8ead4be3ce171e54789abc6d9f6ca80feb02d52aae4fec677974`.
RF_Online.bin x86/2255872bytes/base400000/entryRVA16C9C0:
`eed1a216cb7ee90fccad50d883b9e779fea1be46229a6ed5b63d5d72cb3cf227`.
Unresolved0; no CharacterMR/FORCE. Точные131 reports/engine/PE/MAP/rsp и shared
camera+vertex headers сохранены до изменений. Ignored не означает backup.

Свежие72 LitGrass directions,5328 normals,8material states,3bump times,
world76queue/16clock,sky material60/36,fade90+27,lighting867/3/27Mie иweather90/5
проходят.30 raw+PNG кадров побайтно равны131, использован подтверждённый просмотр.
Неизменённые240 CPU math cases явно сохранены как прежнее доказательство,
три точных math bodies перепроверены в новой PE. Старые bulk suites не повторялись.
ANI/BBX,own entry/providers,sound1,window/device,contracts и existing Create1 PASS.

Далее133: material runtime526/layer54/extra8/capacity vs source332/layer46/max4,
shader caps/failure/reset и unused registers. Другие flag40 writers, full visibility/
fade/alpha/camera/world,CRT matherr/errno/unmasked/status/NaN,INS/Planet/lensflare/
localfog/stages/auth/protocol/Character/gameplay и остальная acceptance matrix OPEN.
NeutralB thin geometry strips остаются неизвестным fidelity gap. Серверы и
оригиналы не изменялись, remote/publish отсутствуют. Текущий goal turn — progress.
