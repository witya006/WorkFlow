# Окно брифинга и экранный захват ввода — участок072

Уточнение073:guard45FBD0 оказался Screen singleton,а неуказателемэтапа.
Проверка перенесена вобычныйPostUIMessage. Остальныеграницы072 остаются.
[Текущее состояние](client455-avatar-stage.md).

Подтверждён исходный компонент CGUIBriefingWindow и его использование CTutorialBoard
в полной объектной сборке. Настоящий игровой этап Tutorial, Avatar и мир ещё не
подключены. M6/M6F/M7/M9 открыты; запуск оригинального EXE не проводился.

## Эталон и статические доказательства

455 x86, image base0x400000. SHA-256 текущего эталона:
`b1b5febf0d0394712e2322350e19dafe60742e8642697b93cfb89135bac1fd8b`.
Backup: `46528aac20499e3b3928d58658d7e0cefe26feba7cd193796d5cfbf7a2bbc558`.
32полных диапазона функций и primary vtable212bytes совпадают между эталонами.
19полных asm перечислены в reference manifest; дополнительно сохранены полные
asm setter633360 и проверки членства60C680. Raw decompile/asm хранится только в
ignored artifacts/client455-tutorial/briefing-window*072.json и briefing-core070.json.
IDA session18f99dcd сохранена и закрыта.

| RVA | Контракт |
|---|---|
| 332ED0 | Init462×207, typing462×143, margins25/15, gap5, keyframe140×207 |
| 333790/333920 | BYTEчисло страниц, интервал80ms, первая страница delay250, последующие0 |
| 333A50 | Продолжение: допечатать → следующая страница → Post1201/value1 |
| 333B30/333B80 | Подпись1059 во время печати,106 после завершения страницы |
| 333480 | Race=AvatarBYTE/2; roles0или2/3/15 → portrait action0/1/2 |
| 333CB0/333DE0 | Sprite31..33,128²cells,10fps;rand%5+10периодов idle,один период talk |
| 333F20 | Caps462/611,portrait134²/overlay128²,keyframe справа;typing смещается к portrait.right |
| 334210/334360 | Ленивое создание widget,два ряда,снятие/возврат без уничтожения |
| 2215A0 | Outline: base fill/children,затем четыре полосы границы |
| 233360 | Screen capture pointer;проверка main-list membership только при назначении |
| 230D30/231180 | Видимый capture получает InputProc/MsgProc вместо обычных окон |

Поле capture найдено поиском displacement bytes E0 80 04 00:16совпадений;
immediate search не находил displacement. Все обращения относятся к ctor,
InputProc,MsgProc,setter и visible predicate. Remove/Close его не обнуляют.
Проверка удаления выполнена только с живым объектом;освобождённый указатель
не разыменовывался. Перед уничтожением владелец обязан снять захват.
Base Close65C830 действительно отправляет1201/value0; запрос кнопки — value1.

## Реализация

scripts/native/client455_briefing_window.{h,cpp}: исходное владение элементами,
типизированные pages/typing/buttons/portrait/key/layout/outline. Это не private ABI
overlay. Существующие071controls и070typing используются напрямую. Портреты
получают настоящий race от будущего Avatar caller; фиктивный Avatar не добавлен.
Восстановленный RF455TutorialBriefingWindow преобразует serialized font12 в
TextInfo28,берёт ND445,включает keyframe,выравнивает окно по центру и bottom40,
открывает при необходимости и назначает/снимает настоящий screen capture.

Generator переносит source без изменения кодировки legacy inputs. В CGUIScreen
добавлено поле и API захвата; InputProc выдаёт capture ID независимо от результата
дочернего InputProc. MsgProc сначала обходит dialogs до потребления сообщения,
затем видимый capture либо видимые обычные окна. Очередь событий здесь не
опустошается: этого вызова нет в target631180. Остальная маршрутизация ещё не
считается полностью455. Новая facade31TU; обычные182client/20kernel TU сохранены.

В CTutorialBoard probe прежний View fixture удалён. Проверены настоящие title,
fragments,key widget,capture,closeBlocked,показ/скрытие и работа с модальными
окнами. Avatar/stage host всё ещё recording fixture — это прямо записано в отчёте.
Новые классы не притянуты искусственно в production PE: обычный этап Tutorial
пока не создаёт экземпляр. Source component доступен настоящему будущему owner.

## Проверка и границы

- Native Ko/Ru:3страницы,печатание по времени,первый delay250,переход delay0,
  повторное Open ненулевой страницы без перезапуска,autosize6lines.
- Настоящий MouseDev→Screen→GUI queue→Next/Close;обычные PostMessage сID38/value1.
  Начальный пробник не создал GUI queue;исправлен fixture,а не ослаблен контракт.
  Отдельно учтён lifecycle Close(value0). Первому typing tick требуется инициализировать
  previousTime — это подтверждённое правило070,не ускоренная печать.
- Capture:nonmember rejected,input returnFALSE всё равно даёт captureID,
  hidden fallback,удалённый живой объект и Close сохраняют указатель.
- Все три настоящих portrait sprites;role mapping,128cells,8idle/16talk frames,
  random threshold10,возврат после1600ms и реальный Update до cell2/UV0.5.
-22GPUкадра просмотрены через два hash-bound contact sheets. Видны страницы,
  клавиши,портреты и смена ячейки. Русский ND1059 выходит за45pxbutton;
  соответствие пикселей исходному455 этим не доказано и остаётся вопросом.
- Текущие gui-input/modal/minimap Ko/Ru regression passed. Старые font/text/
  scrollbar/typing/control отчёты не перезаписаны как свежие. Неизменённые большие
  Character/runtime suites не запускались. Новый production runtime изменился,
  поэтому сравнение071 «только timestamps» сюда не переносится.
- Обычный линк:0unresolved. Точная новая PE проходит собственный WinMain,
  TCP fixture,engine/sound/D3D/Character и existingCreate=1. SHA-256:
  `bd50df91f63d2e5a3e844cd6fafe9b960a8bcd3479f8f9c4c2c3b2bc3d5710f7`,
  x86/base400000/entry150350/2041856bytes. Проверка прекращается до игрового цикла.
  First-chance40080201 через KernelBase остаётся нерасследованным.
- Window probe SHA-256:
  `d0692d3d6c4e0857f7edbb284882f387cf549b737c472f2fc8b90525e6fcc745`,entryE7930.
  inventory/client455-briefing-window-checkpoint.json:PARTIAL.

## Открыто и следующий шаг

073: настоящий Avatar/world/frame/input/local-feedback host и Tutorial class,
затем четыре обычных этапа клиента,вход и переход в мир. Не регистрировать
Tutorial window в login stage для искусственного удержания кода.

На момент072 проверка Screen singleton45FBD0 ещё не была перенесена;073 её
закрыл. У окна ещё открыты полный base window lifecycle/
input/sound/docking,device-loss/reset и владение ресурсами21/31..33 в обычном
sprite manager,глобальная virtualSetSize,пиксельная приёмка против455,unsafe/OOM/
overflow/failure domains. Старые AnimatedImage callers,остальной GUI/IME/layers,
Character/renderer/gameplay gaps не закрыты. Компонентный PASS не означает
готовое обучение или полный клиент455.
