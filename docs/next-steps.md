# Продолжение M6 — обычный персонаж и выбор

10.11.2026. Проверенная база153/3296a413…;182client/67engine/20kernels/link0.
Gate:inventory/client455-equipment-frame-checkpoint.json PARTIAL.
Оценка25%(20–35%);0/12полных областей. M6/M6F/M7/M9 открыты.

Сверка рабочих исходников:154 НЕ СОБИРАЕТСЯ, C2280 вcavatar.cpp:162.
Новый владелец экипировки делает старое Avatar::Clone некорректным.
Промежуточная линковка154 не была runtime-проверена и не является готовой базой.
Exact153 уже сохранена вbefore154/manifest.json (53файла);не перезаписывать.
Перед продолжением исправить копирование/владение по455,затем сборку и
проверку полного player-owner пути. Не возвращать shallow copy ownedpointer.

## Что готово для следующего соединения

- Typed controller12физических слотов,создание/clone/visibility и PRNG.
  Index12 выходит за настоящий массив;собственный отказ не равен target failure.
- Render/default+matrix,fade/alpha/grade/retained pose queue проверены отдельно.
  Шесть кадров153 совпадают150. Полный particle registry всё ещё старый.
- FrameMove/Animation/end transitions,однократные dummy,always state иevent
  magic follow восстановлены. Реальные cloak mode3(create_type10) имode4
  (Spine17),ANI иMiles проверены. Sound position берётся отequipment.
  Виртуальный kind2 false у CMesh/CEquip;не путать сbyte4 иground wrapper.
- Ordinary6default owners Avatar теперь производныеCEquip. Полное владение
  экипировкой икадр основного CPlayerProc всё ещё используют старую модель.
- Network Premium flag/Avatar benefits producer57/12 установлен;полные UI/
  condition refresh открыты. Stat setters14..18 и3basic rows перенесены;
  полные455metrics/23fieldlayout/41A8B0 refresh ещё нужны.

## Дальнейший порядок

1. Подключить12-slot controller к настоящим CPlayerProc/CPlayer/Avatar иего
   producers/consumers. Ближайший наблюдаемый результат — правильно одетый
   персонаж в обычной сборке,затем работающий выбор. Не кастоватьRF455payload
   илиmetadata в старыеCNormalItem/ITEM_DATA. Не оставлять успешные no-op hosts.
2. Соединить уже готовые frame/ANI/dummy/effect/pose/Render сlive actor view,
   текущим embedded processor иреальными condition/skill/UI owners.
   4513E0 реально пуст.450BD0/451330 имеют отдельные зависимости.
   Avatar virtual252→41A060→skillboard490EB0,typedSF accessor иinfo-window
   update463740 нужны для condition-host. Pcode26owners сохранены в
   artifacts/client455-progress/char-info152-reference/player-owner-diagnostics.json;
   это диагностика,не полный ASM proof. MountHeight читает текущий wornmount
   metadata mesh72,не tableindex и не произвольный detached object.
3. Общий particle/entity registry:старыйg_Particle1024/5clones,targetvectors/
   6clones/one-attempt failure. Default capacity неизвестна;не брать2000изRVP.
   Ненулевые частицы иground wrapper пока не приняты.
4. Довести bootstrap Quest/EventShip/NDMsgMonster/ItemTimer/NDMsgEvent/
   EventSound/SpecialStore/ItemCollection/Map,Avatar finalization иполные
   Title/Login/выбор455:ввод,ошибки,сообщения,переходы. Не обходить загрузку,
   не принуждать успешный вход;сервер не разрабатывать.
5. Затем C:карта/камера/управление/коллизии;D:атака/умения/предметы/чат;
   E:остальные функции/классы/карты/устойчивость иполнаяM6F/M7/M9 приёмка.

## Сохранение и проверки

- Перед154 ordinary edits exact153 уже сохранена:
  artifacts/client455-progress/before154/manifest.json,53файла.
  Следующий snapshot только после проверенной154;старый не перезаписывать.
  before153 — exact152,52файла;старые снимки не перезаписывать.
- Новый frame auditor/runner/gate используют current sources. Старые146/150/
  152gates состарымиSHA — исторические,не свежие проверки текущей PE.
- Final frame:work/m9/55c69791/equipment-frame-001;render:
  work/m9/07878f1a/equipment-draw-001. Контролируемыеkind9/46 — branch fixture,
  не проверенные настоящиеSiege visuals. Callback host не productionCPlayerProc.
- Fresh Create/Login/account3Avatar пройдены;Login65/3015ms просмотрен,
  ожидание/Beta0.738/безauth.9прежнихfirst-chance,unhandled0.
- Тестировать затронутое. Не повторять неизменённые159k/bulk suites.
  Индекс12/queue заallocation/byteoverflow/неинициализированные позиции иCRT/
  FP/OOM домены остаются gaps. Управляемый отказ не принимается как targetparity.
- Последняя полная опись20:56:14,158.84GiB logical/43.19GiB unique files,
  не точный filesystem allocation. Final staging pool0;ничего не удалено.

Подробности:research/client455-equipment-frame.md;оценка:docs/progress-report.md.
