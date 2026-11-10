# Продолжение M6 — практический вход и обычный персонаж

10.11.2026. Проверенная база154: own31d24ab9…/x86/entry17F430,
182 client / 67 engine / 20 kernels, build/link0. Контрольная точка:
inventory/client455-player-owner-checkpoint.json PARTIAL.
Оценка25%(20–35%), полных областей0/12. M6/M6F/M7/M9 OPEN.

## Что изменилось в обычном коде

Основной CPlayerProc владеет12типизированными объектами; подключены его
numeric PutOn/base PutOff, Animation/FrameMove, часть render/material/pose,
condition-host и Avatar→skill-board→SF→icon callback. Avatar PutOff возвращает
базовую одежду0..4; missing cloak/Siege specialskill возвращаетfalse уже после
снятия, как419BB0. Неперенесённые непустые specialskill/legacy paths явно отказаны.
Сборочная C2280 устранена отдельным копированием owned state, без двойного владельца.

В собственном полном объектном входе получен реальный собранный персонаж:
19draws,12657visiblepixels; снятие меняет3752pixels, replacement PNG равен
исходному. Камера/материал/свет контролируемые, позы не подменялись identity.
Это не принятый полный анимированный персонаж в игровом мире.

## Доступная практическая среда

- Пользователь запустил E:/RFOnlineTrash/rf455-v0.4.0. Подтверждены процессы
  именно из этой папки: TCP27830 game,27831 launcher,8080 website.
- E:/RFOnlineTrash/RFOnline/RF_Online.bin совпадает с primary SHA b1b5febf…;
  rflauncher.exe SHA38e32658… совпадает с комплектом сервера.
- Пользователь подтвердил реальный вход оригинальным клиентом до мира.
  Не выдавать это за собственный наблюдённый игровой проход.
- Own Taiwan WinMain реально подключается к127.0.0.1:27830 и проходит engine/Miles.
- Лаунчерный6C/03→6C/04 тестовый вход принят; получен16byte rf1:key.
  Самостоятельный RF game-auth пока не проверен. Пароль/ключ/идентификатор
  не сохранялись в файлах или Git; тестовые данные даны пользователем в чате.
- Не запускать входные EXE. Лаунчер анализируется как данные; для own runtime
  воспроизводится handoff93bytes. Не менять, строить или чинить сервер.
  GoMMO поведение отделять от спецификации pinned455.

## Следующее действие

1. Проверенная154 уже сохранена перед дальнейшими ordinary edits:
   artifacts/client455-progress/before155/manifest.json,52файла.
   Before154 — exact153,53файла; не перезаписывать.
2. Передать живой handoff собственному изолированному клиенту: ServerClient.Login,
   authreply identifier/serial, DecodeLoginKey rf1:, v4x Marshal93bytes.
   Секреты только во временной приватной памяти/передаче; не включать их в
   публичный манифест. Получить фактические сообщения/состояния own client.
3. По наблюдаемому первому расхождению довести world-entry/bootstrap/registered
   appearances. В registered_characters.inc ещё есть старый GetNormalItem/SetLevel;
   оружие/часть actions/effects также имеют legacy consumers. Не cast raw455
   в старые CNormalItem/ITEM_DATA и не принуждать успешный вход.
4. Довести девять оставшихся участков bootstrap, финализацию Avatar, обычную
   анимацию/материал/UI и экран выбора. Затем мир/камера/движение/коллизии,
   бой/умения/предметы/чат, остальные12областей и M6F/M7/M9.

## Не потерять ограничения и доказательства

- Target member copy404A40/4042D0 не вызывает rand/AddRef; queue527E70 вызывает.
  У копии сохраняются старые actor/currentProc pointers. Full Character clone
  lifecycle не принят: в probe очищались только fixture aliases трёх legacy
  owned pointers; payload refs компенсированы после наблюдения no-retain.
- Полные populated cloak/Siege specialskill unlink/board35/UI state/movement,
  activeUnit/Siege flags, profile17796/action-category614 producers открыты.
- Полный455CharInfo23fields/metrics/PremiumUI/SFwidget и его обычное population
  не завершены; нынешний callback использует реальное существующее окно.
- Particle registry всё ещё legacy1024/5clones вместо455vectors/6clones;
  ground wrapper, ненулевые particle draw и полные shadows также открыты.
- Taiwan Create/Login/account3Avatar PASS;Login195/3000ms просмотрен:
  lobby/ожидание/Beta0.738,7firstchance(6C++/1threadname),unhandled0.
  Шесть прежних renderPNG совпали153.
- Korea повторный запуск встретил настоящее правило одного экземпляра,
  когда пользователь держал оригинальный клиент. Taiwan использует собственную
  штатную country policy; unconditional bypass не добавлен.
- Первый неудачный собственный кадр ошибочно считал тёмную полосу фона
  видимым объектом. Проверка усилена и реальные финальные изображения просмотрены.
- Native final:work/m9/5544e512/player-owner-001; render6ebebfad/equipment-draw-001.
  Последняя полная storage-опись20:56:14:158.84logical/43.19uniqueGiB,
  не новый физический замер. Удалений0, новых полных копий клиента нет.
- Проверять затронутое; не повторять159k неизменённых проверок.
  Undefined/unsafe/CRT/FP/OOM/индекс12/lifecycle остаются явными M9 gaps.

См.research/client455-player-owner.md иresearch/client455-live-launcher.md.
