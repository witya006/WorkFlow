# Продолжение M6 — внешний вид, выбор и обычный игровой маршрут

Обновлено10.11.2026. Последняя проверенная обычная сборка150/0f671964…,
182client/67engine/20kernels,unresolved0.
Gate:inventory/client455-player-visual-checkpoint.json PARTIAL.
Оценка25%(20–35%);0/12полных областей. M6/M6F/M7/M9 открыты.

## Проверенная основа

- Обычные Create/Login/account3Avatar прошли;Login65/3016ms просмотрен,
  lobby/ожидание,Beta0.738. Авторизации/полного выбора/мира ещё нет.
- Render/default+matrix,fade/alpha,grade604 и очередь поз/владельцев149
  прошли свежую затронутую проверку150;шесть контролируемых кадров совпадают.
- В150 исправлен неверный вывод146:полные ctor/dtor создают12объектов.
  Index12 выходит за массив;собственный отказ не считается target failure parity.
- Race/helmet visibility и PRNG создания/копирования проверены отдельно.
  Полный контроллер пока не владеет обычными CPlayerProc/CPlayer/Avatar.

## Дальнейший порядок

1. Соединить12-slot controller иготовые object Render/pose/ANI/fade с обычными
   CPlayerProc/CPlayer/Avatar. Реальные owners/providers обязательны;recorders/
   no-op callbacks из probes не переносить как готовую production-реализацию.
   Ближайший видимый результат:правильно одетый персонаж в обычном клиенте.
2. Подключить FrameMove/Animation/dummy/effect/sound/condition/UI consumers.
   4513E0 — доказанно пустой processor FrameMove,не пропущенное тело.
   450BD0/451330 и equipment46D200/46D9B0 имеют отдельные реальные зависимости.
   Для flag442440 и bonusfloats24712 ещё не установлены owner/producers;
   не подменять их false/0 или догадками. Выбранный PRNG ctor/copy закрыт,
   но полная PRNG-последовательность/CRT/lifecycle остаётся непроверенной.
3. Перенести общий particle/entity registry:сейчас старыйg_Particle1024/5clones,
   target — vectors/6clones/one-attempt failure. Constructor/default capacity
   проверить;loader расширяет при count+1>3072,это не default2000 изRVP.
   Ненулевые эффекты экипировки ещё не приняты.
4. Довести bootstrap Quest/EventShip/NDMsgMonster/ItemTimer/NDMsgEvent/
   EventSound/SpecialStore/ItemCollection/Map,Avatar finalization иполный
   Title/Login/выбор455:input,ошибки,клиентские сообщения,переходы.
   Не обходить загрузку и не принуждать успешный вход. Сервер не разрабатывать.
5. Затем C:карта/камера/управление/коллизии;D:атака/умения/предметы/чат;
   E:остальные функции/классы/карты/устойчивость и полная M6F/M7/M9 приёмка.

## Сохранение и целевые проверки

- before150 — точная149runtime,52файла;before149 —148,также exact16sourceinputs;
  before148 —147,before146 —145. Существующие снимки не перезаписывать.
- **До следующих ordinary edits**:
  snapshot_client455_runtime.py151 client455-player-visual-checkpoint.
- Текущий runtime gate не заменять старыми146/149gate с историческими SHA.
  Старый13-slot вывод отменён;использовать новый player-visual auditor/runner.
- Полные selectedRender62functions/6959instructions/650CFG уже исследованы.
  Текущие11playerfunctions/684instructions/107CFG плюс полныйPRNG9instructions
  также доказаны на2pins;не повторять готовый поиск без новой зависимости.
- player-visual:work/m9/c6cec91b/player-visual-001;draw:work/m9/e2014ded/equipment-draw-001.
  Новых poolbytes0. Не повторять неизменённые огромные suites ради счётчика.
- Индекс12/queue writes за allocation,BYTEreference overflow иошибки CRT/FP/OOM
  явно остаются gaps;не выдавать управляемый отказ за полную target parity.
- IDA6a9e2ee9 сохранена/закрыта,list0,native jobs завершены.
  Оригиналы/сервер не менялись. Никакие старые стенды не удалены.

Оценка/остаток/готовность исходных данных:progress-report.md.
Текущие доказательства:research/client455-player-visual.md.
