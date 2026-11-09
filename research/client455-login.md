# 138: обычный Login и регистрация окон

2026-11-10. **PARTIAL M6**, не полная приёмка Login или клиента455.
Проверка: `scripts/Invoke-Python.ps1 scripts/checkpoint_client455_login.py`.
Текущий gate: `inventory/client455-login-checkpoint.json`.

## Изменение обычного клиента

Обычный WinMain собственной сборки прошёл Title, создание/загрузку Login и
отрисовку реальной lobby. Два первоначальных падения были вызваны отсутствующими
спрайтами по старым плоским путям. Перенесён выбор локализованного/Common файла:
legacy mouse0→target0, common1→1, loading8→2, login7→3, belt3→main4.
Сохранён legacy namespace вызывающих функций; это мост имён файлов, а не полная
миграция номеров групп, кадров или всех455окон.

После этого стали видны сразу все панели. В455 CGUIScreen::Add использует
AlwaysTop для выбора вставки в начало/конец главного списка, устанавливает
родителя и **всегда вызывает Show(FALSE)**. Generic Container::Add наследует
видимость родителя, поэтому отсутствие последнего шага в legacy root открывало
зарегистрированные окна. Исправлен общий метод Add; список скрываемых панелей
по именам не добавлялся. Сохранены null/no-op и SetParent/Hide при повторной
регистрации уже присутствующего объекта. Другие root/layer/window операции ещё
не полностью перенесены.

## Статическое доказательство

Primary x86/base400000 SHA256:
`b1b5febf0d0394712e2322350e19dafe60742e8642697b93cfb89135bac1fd8b`.
Secondary:
`46528aac20499e3b3928d58658d7e0cefe26feba7cd193796d5cfbf7a2bbc558`.

CGUIScreen RTTI: TD VA BD5D1C, COL B808B4, primary vtable ADAD8C.
Slot208→Add VA630A60/RVA230A60; slot40→Draw VA632430.
Полные пять функций: Add230A60, AlwaysTop getter230AD0, Container Add20BFA0,
AddFront20C040, Login UI_LoadSprite140350. Собраны221инструкция и21положительный
блок CFG, хвостов вне проверенных тел нет. Пять диапазонов идентичны двум pins.
Нормальный target Login запрашивает группы0,1,3,2,4,5; system5 и полные consumers
ещё открыты. Raw: `artifacts/client455-progress/login138-reference/registration-full.json`.
IDA5a0405db saved/closed; последующая diagnostic5818692d также saved/closed,
idb_list count0. Входные EXE не выполнялись.

## Обычный запуск и визуальная проверка

Собственная PE SHA256:
`ba23dd6de02e9b050f3651fd522e69f7ed8e2ab3acd977f4aa801bcfe2c7793b`,
x86/base400000, entryRVA16F640,2269184bytes.182client/20kernels, link0/unresolved0.
Engine137 SHA708c892e60c3bf7457389b40ac24b9a466958c9d232d9efaf497d1ac3232b870
не изменён. Пересобран изменённый guiscreen.cpp; старые крупные suites не повторены.
Свежие normal-consumer ANI/BBX, provider/WinMain/Miles и обычный кадр проходят.

Последний run: `work/m9/ba23dd6d/login-frame002`, created1/loaded1, без fatal,
возврат из Render после захвата и завершение своего процесса наблюдались.
Захват: frame70,3203ms,640×500,result0. PNG SHA:
`0bf6ec516f28045e235ea6353811c02aa9d24f1d4fef9ef8c6e378ddc822ca7c`.
Просмотрены реальные lobby и окно ожидания; прежние перекрывающиеся панели
создания/расы/атрибутов/перехода исчезли. Это смысловое наблюдение, не сравнение
пикселей с запущенным reference455. Legacy version label не менялся косметически.

Захват включается только opt-in env собственного диагностического запуска;
дополнительной отрисовки нет. Данные читаются после обычного EndScene. Названия
checkpoint/report теперь прямо говорят о возврате после захвата, не о frame1;
старые first_* поля оставлены как помеченные compatibility aliases.

Run использует55inputs/43shared assets,44,211,245linked bytes, **new pool bytes0**.
Оригиналы не hardlinked и не изменялись. Нет новой копии всех ресурсов клиента.
Предыдущее состояние9adc8d0d сохранено13files/4,663,664bytes в
`artifacts/client455-progress/login138-before-window-registration/manifest.json`;
exact137snapshot47files сохранён отдельно. До/после image reports не подменялись.

## Следующая связанная работа

Diagnostic pcode: `artifacts/client455-progress/login138-reference/flow-diagnostic.json`.
Не полное ASM/CFG/equality доказательство этих функций. Target init5401D0
устанавливает Login state6 при обычном входе,7 при request-logout. Input53F100
проверяет результаты через53D0F0; ветка результата0 приstate6 вызывает загрузку
клиентских данных5E7BE0. Getter53EF80 читает NetworkMgr BYTE435973. Это следующий
реальный стык response→bootstrap→selection, не основание принудительно открыть
окно пароля или объявить вход успешным. Country slot284 false во всех11 pins
профилях: не включать legacy reconnect безусловно.

Create53BB20 пока имеет разбитые границы в IDB/JUMPOUT и неверную CRT-аннотацию;
при переносе использовать инструкции/реальные границы. Полные четыре stages,
Title/movie, все10окон/ввод/фокус/слои, авторизация/выбор персонажа, world/gameplay
и прежние client-acceptance gaps остаются открытыми. Этап M9 не достигнут.
