# Продолжение M6 — освещение живого персонажа

Сейчас156,own68e02c3d…,gate inventory/client455-combat-transition-checkpoint.json.
Живой кадр выбора получен:364frames/8000ms,unhandled0. Пользователь подтвердил
анимацию и сообщил почти чёрного персонажа;это видно на сохранённом кадре.
Следующая задача157:проверить CResObject::SetLightColorFromMap,реальный цвет
изlobbyBSP,GetMatLightFromColor,материал иCharIF constants. Не обходить маршрут
постоянным белым материалом. Точная156 уже вbefore157,50файлов.
SetAction weapon/shield,typed Login reads/fade иCreateEffect/DestroyEffect
исправлены;ниже план155 исторический,не повторять уже исправленные участки.
GameBarStoreзапрос устранён и подтверждён пользователем:HKCUcapture/DVR0;
backup artifacts/environment/game-capture-20261110-232356-911.json.

# Исторический план после155

10.11.2026. Частичная контрольная точка155:
inventory/client455-live-login-checkpoint.json, own da42b501…,
x86/entry17F660/2347520bytes,182client/67engine/20kernels,build/link0.
Оценка25%(20–35%),полных областей0/12;M6/M6F/M7/M9 OPEN.

## Подтверждённый практический маршрут

- Пользователь запускает E:/RFOnlineTrash/rf455-v0.4.0.
  Game127.0.0.1:27830,launcher27831,website8080.
- Оригинал E:/RFOnlineTrash/RFOnline/RF_Online.bin совпадает с primary b1b5…;
  rflauncher.exe38e32658… совпал с комплектом. Пользователь вошёл до мира.
- Собственный клиент использует93-byte launcher handoff:auth6C/03→6C/04
  accepted,key16;затем game1/1 payload58→1/2 payload12,result0.
- Реальный ответ1/9 имеет178bytes для одного персонажа. Исправлен прежний
  ошибочный отказ по минимальной длине506. Активные записи проверяются
  по14+164*count,только отсутствующий неиспользуемый хвост дополняется нулями.
  Target16AE40 копирует506 избуфера ииспользует count;не утверждать,
  что unsafe overread или полная исходная длина wire уже воспроизведены.
- Registered handler использует GetNormalItem455/typed normal payload.
  Setter462170 пишет толькоBYTE113 без clamp/callback. Native границы,
  fragmented encrypted178 и3прежних assembled renderPNG PASS.
- Обычный Taiwan Login/кадр новой PE PASS. Живой вход НЕ завершён:
  после registered reply падает equipped action. Мир не достигнут.

## Следующее действие

1. До дальнейших обычных source edits сохранить точную155 вbefore156.
   Before155 уже содержит принятую154,52файла;не перезаписывать.
2. Воспроизведённый следующий вызов:
   CAvatar::SetCombatMode→CCharacter::SetCombatMode→CAvatar::SetAction
   →CPlayer::SetAction (ownRVA555FE)→CPlayerProc::GetEquipItem (ownRVA10B23).
   Это явный отказ оставшегося legacy consumer при непустом оружии.
3. Сверить соответствующий target combat-mode transition,перенести на
   typed equipment/SetItemAnimation455/реальный fade. Не вызывать унового
   объекта унаследованный legacy SetAnimation вместо recovered wrapper.
4. Для живого прогона запускать только собственный BIN. Тестовые данные
   есть в пользовательском сообщении;не записывать пароль,ключ,identifier
   или rawpackets. Временный handoff удаляется. Не выполнять входные EXE.
5. inventory/client455-live-resource-inputs.json хранит только нужные
   архивы/текстуры;новые зависимости добавлять через
   prepare_client455_live_resources.py --events <owned debug-events.jsonl>.
   Он сохраняет предыдущие зависимости;не копировать весь клиент.
   485missing изэтих логов отсутствуют ивисходной установке;пока не трактовать
   их все как блокирующие:пользовательский оригинальный проход работает.
6. После перехода вооружённого персонажа довести обычные анимации/материал,
   оставшиеся bootstrap/UI/selection. Затем управляемый персонаж вкарте,
   бой/умения/предметы/чат иостальные12областей. 1/21 payload1 наблюдён,
   его полное назначение/поведение ещё не принято.

## Границы доказательств

Full Character clone lifecycle,Siege/activeUnit,particle registry,UI metrics,
полные specialskill/linker callbacks ивсе docs/client-acceptance.md остаются.
Зелёная сборка,обычный Login,живой world-entry иisolated render не закрывают M9.
Последняя полная storageопись20:56:14:158.84logical/43.19uniqueGiB,не физический
новый замер. Удалений нет. Большие неизменённые проверки не повторять.
Подробности:research/client455-live-launcher.md,client455-player-owner.md.
