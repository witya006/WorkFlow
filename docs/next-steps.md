# Продолжение M6 — полный персонаж и выбор

Обновлено10.11.2026. Последняя проверенная обычная сборка149/f4e62e48…,
182client/67engine/20kernels,unresolved0.
Gate:inventory/client455-equipment-draw-checkpoint.json.
Оценка25%(20–35%);0/12полных областей,M6/M6F/M7/M9 открыты.

## Достигнуто

- Перенесены Render(default/matrix), fade/alpha и источник overlay604:
  slots6/7 читают metadata152, остальные пишут0; numeric effect grade — payload113.
- Настоящий предмет рисуется новым object Render; видимое свечение и разные
  matrix/default проходы проверены. Это предмет в контролируемой позе, не actor.
- Очередь хранит позы и payload owners, сохраняет target4-matrix aliases,
  предел256 и Start. Обычные Clear/Render вызывают новые entrypoints.
- Вторичная геометрия теперь удержана обычной PE, но полный player caller отсутствует.
- Обычные Create/Login и затронутый receiver3Avatar прошли; Login65/3016ms
  просмотрен, ожидание/Beta0.738. Авторизации и полного выбора ещё нет.

## Следующие действия

1. Подключить готовый13-slot controller146 и новый Render к обычным
   CPlayerProc/CPlayer/Avatar. Перенести реальные slot guards450810 и
   pose restore43CDE0, setters позиции/масштаба и Render(default/matrix).
   450330/450710 и источник overlay уже полностью исследованы; не повторять.
2. Соединить реальные Animation/FrameMove, ANI/fade/height, effect/sound/
   attachment/condition providers146 и их UI consumers. Требуемый результат:
   правильно одетый персонаж в обычном клиентском маршруте.
   В полном ctor/clone учесть rand()/100→612 из46BE60: нынешний wrapper/queue-copy
   ещё не воспроизводит потребление PRNG; это известный gap, не принятый lifecycle.
3. Перенести общий particle/entity registry. Сейчас adapter использует старый
   g_Particle1024/5clones; target — динамические vectors/6clones и одноразовая
   попытка загрузки. Проверить constructor/default capacity и loader/release.
   7BE640/7BF060 расширяют при count+1>3072; не подставлять2000 из RVP.
   Диагностика сохранена; ненулевые эффекты149 ещё НЕ проверены.
4. Довести bootstrap Quest/EventShip/NDMsgMonster/ItemTimer/NDMsgEvent/
   EventSound/SpecialStore/ItemCollection/Map, Avatar finalization и UI выбора/
   ошибки/переходы. Не обходить загрузку и не принуждать успешный вход.
5. После выбора — карта/управление, связанный игровой цикл и полная приёмка
   по docs/roadmap.md и docs/client-acceptance.md. Сервер не разрабатывать.

## Сохранение и проверки

- before149/manifest.json содержит148; before148 —147; before146 —145.
  Дополнительно exact148 source hashes сохранены в before149/recovered-source/.
- До следующих ordinary edits сохранить149:
  snapshot_client455_runtime.py150 client455-equipment-draw-checkpoint.
  Существующие снимки не перезаписывать.
- Новый audit использует16новых+27render/19backend148 полных функций;
  уникально62/6959instructions/650CFG. Не повторять готовое исследование.
- Последняя nativeпроверка:work/m9/0fdac5c0/equipment-draw-001;
  underlying model/frame fixtures неизменны. Новых poolbytes0.
- Кадры base/overlay совпадают с сохранённым backend148. Полный character
  appearance/selection этим не доказан. Registry/nonzero particles открыты.
- Ошибка первых fixture-run: SetPosition(0,0,0) выбрал overload сNULLVector3f;
  исправлено float-аргументами. Это не исправление production-клиента.
- Проверять затронутое; неизменённые большие suites не повторять.
- Queue byte-reference overflow и writes за allocation не считать безопасными
  принятыми сценариями. Известные расхождения хранить в списке приёмки.
- IDA0a6749ce saved/closed/list0, jobs завершены. Оригиналы/сервер не менялись.
