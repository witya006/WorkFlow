# Продолжить146:подключить реальные обработчики

Контроллер13слотов икопирование обычного предмета уже реализованы ипройдены
на реальных ресурсах какPARTIAL_COMPONENT. Обычная145сборка неизменна.
Gate:inventory/client455-player-equipment-checkpoint.json;
research/client455-player-equipment.md. Не повторять уже закрытый32funcаудит.
Exact145before146 уже сохранён;не перезаписывать snapshot146.

Теперь:полные animation/effect/condition providers46DF10→46D2F0→46D730,
46D3D0,4411E0→441840/4418D0/441970/441AC0/442460;затемactualCPlayerProc/
CPlayer/Avatar/registered receiver иtyped GetNormalItem/upgrades. Ни один
probe-recorder callback не выдавать за готовую игровую реализацию.
Providerdiagnostics лежитвartifacts/client455-progress/player-equipment146-reference/providers-diagnostic.json;
441AC0 продолжитьсcursor100. ПолныеASM/CFG/equality этихproviders ещё нужны.
Послеинтеграции —настоящий animation/render loop ивидимые одетые персонажи.

4539BD/453A80 записываетownerpointer вequipment588,НЕ Player.SetPrevAction.
Kind братьmetadata88. CNormalItemClone ужеsource,не подменять полнымmemcpy200.
Текущийordinarygate остаётся equipment145;общаяоценка25%(20–35%)не меняется.
Ниже подробная основа145;исторические шагиsnapshot/разбораcontroller уже сделаны.

# Следующие шаги —10.11.2026

Текущий результат145 PARTIAL; inventory/client455-equipment-checkpoint.json.
Own1a355372…/x86/entry175F50/2299904bytes;182client/67engine/20modules/unresolved0.
Обычный WinMain→Title→Login: lobby/ожидание, кадр70/3235мс просмотрен.
Успешная авторизация, полная загрузка, внешний вид и выбор не приняты.
M6/M6F/M7/M9 OPEN; ориентир25%(20–35%),0/12полных областей.
См. progress-report.md, roadmap.md и research/client455-equipment.md.

## Следующий участок146: экипировка и внешний вид

1. Перед изменением runtime сохранить точную145базу:
   scripts/Invoke-Python.ps1 scripts/snapshot_client455_runtime.py 146 client455-equipment-checkpoint.
2. Разобрать полные инструкции/CFG контроллера CPlayerProc13слотов:
   PutOn453030,Create453760,remove453550,getters4536C0/453730,
   SetBone452FE0,rematch/weapon453280 иAvatar4198D0/4199D0.
   Адреса VA для x86/base400000; в отчётах указывать RVA и SHA бинарника.
   Diagnostic pcode есть в equipment145-reference/session.json; он не заменяет
   доказательства всех веток. Проверить реальные перегрузки4531E0/453100.
3. Восстановить создание/получение/снятие и типизированные игровые потребители,
   затем rematch/weapon/shield/fade/animation/draw. Не cast455rows вlegacyструктуры.
   Не считать наличие32загруженных моделей готовым внешним видом персонажа.
4. Проверить изменённый путь на настоящих Item/Resource/BN/MSH/ANI/texture входах,
   обычном обработчике списка персонажей и собственном кадре; обновить частичный gate.
   Не запускать неизменённые159kнаборы ради счётчика.

## До ближайшего принятого результата B

- Полный класс/умения и игровые потребители: часть143/144 только таблицы/индексы/
  имена; выделенные панели умений ещё не заполнены полной логикой455.
- Обычный внешний вид и UI выбора: полный контроллер экипировки, слои/состояния/
  анимация/отрисовка, данные всех3Avatar и правильные переходы/ошибки.
- Остаток bootstrap:Quest/EventShip/NDMsgMonster/ItemTimer/country slot296/
  NDMsgEvent/EventSound/SpecialStore/ItemCollection/Map/5default effects/
  Avatar finalization/registered request. Рольslot296 ещё неизвестна.
  ItemTimer/SpecialStore не подменять Exp/Combine. Не force success/не bypass.
- FullTitle/movie/factory4/explicitnext,10Loginwindows/systemsprite5/layout/
  focus/input остаются открыты. Legacyfactory3/modulo не считать455.

После B: C персонаж→карта→управление, затем D связанные игровые действия,
затем E все остальные требованияM6F/M7/M9. Обновлять оценку после B/C.
Проверка условий входа — клиентская задача; серверные проекты не изменять/не собирать.

## Текущие ограничения и данные

-145 подключает6typeddefaultslots; старые GetDefaultItem/UnsetDefaultItem/copy
 overload и полный private644ABI не восстановлены. Не заявлять fullappearance.
-1120 неразрешённых ссылок Resource141 — частичная опись, не1120доказанно
 обязательных отсутствующих файлов. В145 все33выбранные текстуры разрешены вRFT.
-Локальные подготовленные сетевые входы не равны настоящему успешному входу.
 ОбычныйLogin run отправил67байт, ответовRFпротокола не было.
-Engine137 неизменён;fullrefraction/particles/BBoShasi/INS/Empty/visibility/
 collision/device lifecycle ипрочие client-acceptance gaps сохранены.
-Exact144 сохранён before145; прежние snapshots не перезаписывать.
-Общие ресурсы новых стендов — через shared-runtime-inputs, только собственные
 копии. Оригиналы не hardlink. EXE/config/изменяемые fixtures частные.
-Старые150.95GiBlogical/42.29GiBunique не удалены; до очистки проверить
 содержимое дубликатов и достижимость доказательств. Не клонировать installedclient.
-IDA7dd394bb saved/closed;native jobs нет. Остальные правила — AGENTS.md.

Прежние детали очереди сохранены в research/next-steps-before-assessment-2026-11-10.md;
актуальный приоритет — этот файл и roadmap.md, не исторические «далее143/144».
