# Следующая работа — связанный экран выбора персонажа

Обновлено10.11.2026. M6/M6F/M7/M9 OPEN. Около25%(20–35%),0/12полных областей.
Текущая обычная сборка145:1a355372…;182client/67engine/20modules/unresolved0.
Gate:inventory/client455-equipment-checkpoint.json. Login показывает ожидание;
вход →выбор →мир ещё не пройден.

## Уже проверено в146

- Контроллер13слотов/normal clone:inventory/client455-player-equipment-checkpoint.json.
- Реальные ANI/pose/fallback/fade/height:inventory/client455-equipment-providers-checkpoint.json.
  69случаев/52ANI/16моделей;высота использует meshID@72 через416940,не table index.
- Magic/sound ownership/cleanup/loop tracking:inventory/client455-equipment-effects-checkpoint.json.
  Реальные RPK/MagicSpt/Miles.
- Создание в рассчитанной точке:inventory/client455-equipment-attachment-checkpoint.json.
  25реальных моделей/25namedpositions/5cloakmagic;targetfailureundefined остаётсяopen.
- Обычная145PE неизменна. Ни один из этих отдельных компонентов не закрывает
  полный внешний вид и выбор персонажа.

## Очередь до ближайшего рубежаB

1. Typed4411E0 conditions и потребители:4412A0/441840/4418D0/441970/441AC0/442460.
   Их полная ASM уже в24function provider proof;не собирать заново без причины.
2. Подключить actualCPlayerProc/CPlayer/Avatar/registered typed upgrades,
   ordinary frame/render/default substitution. Не кастовать455Item rows
   к старому CEquipItem/CNormalItem и не выдавать probe recorders за providers.
   Позиции7E0D10/7E22F0 и23helperfunctions ужеsource/nativeverified;
   теперь подключитьк actual effectbackend. Dummycache заполнять внастоящемframeproducer,
   а не при каждом lookup. Тип17=Spine→Spine1,18=default. Полные CAllEffectInfo
   attachment иundefined/errorfidelity сохраняются вM9backlog.
3. Закончить загрузчики Quest/EventShip/NDMsgMonster/ItemTimer/NDMsgEvent/
   EventSound/SpecialStore/ItemCollection/Map и Avatar finalization.
4. Принять обычный список/внешний вид/выбор, UI/input и клиентские переходы/ошибки.
   Полные Title/Login455 рубежаA также остаются открыты.
   Не обходить загрузку, не принуждать успешный вход, сервер не разрабатывать.

ПослеB:персонаж в карте/управление(C) →связанные действия(D) →остальная полнота(E).
Переоценить объём послеB/C;пока нет основания обещать датуM9.

## Практические ограничения

- Snapshot before146 уже сохранён50files;не перезаписывать.
- ANI maximum0 допустим;exporterbasename выделять на байтах до ASCIIdecode.
- Полные данные ASM:IDA basic_blocks+independent count →decode_client455_cfg.py.
  Compactanalyze_batch preview не принимать за полную ASM.
- Targeted checks для изменённых частей;не повторять неизменённые159k suites.
- Shared staging только собственных копий. При пределе900ссылок используется
  следующая собственная реплика пула;в реальном1024link failure повторныйrun
  прошёл с280новыми байтами. Старые стенды ещё не очищены.
- Свежая дисковая опись154,86GiBlogical/42,85GiBunique;точнаяallocationне измерена.
- IDA5c1cdbca saved/closed/list0;native jobs завершены.
- Полные renderer/physics/lifecycle/CRT-FP/ошибки сохраняются вM9backlog.
  Локальный сетевой приёмник не отвечал RFпротоколом:успешная авторизация не доказана.

Полная оценка:docs/progress-report.md;план:docs/roadmap.md.
Предыдущие подробности сохранены вresearch/next-steps-before-effects146.md.
