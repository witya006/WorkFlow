# Последовательность камер обучения455 — участок075

Восстановлена ветка вступительного ролика CGP_Tutorial: выбор CAM по расе,
порядок камер, границы затемнений, завершение, пропуск и сохранение счётчиков
при повторной загрузке. Она исполнена на трёх настоящих мирах через собственный
движок. Полный CGP_Tutorial и его подключение к фабрике этапов ещё открыты.

## Эталон и доказательства

455 x86, imagebase400000, SHA-256
`b1b5febf0d0394712e2322350e19dafe60742e8642697b93cfb89135bac1fd8b`;
backup `46528aac20499e3b3928d58658d7e0cefe26feba7cd193796d5cfbf7a2bbc558`.
15 полных диапазонов и три таблицы камер совпали между эталонами.
Сохранены четыре полных asm, декомпиляция helpers/setters и таблицы в ignored
artifacts/client455-progress/intro075.json; полный метод камеры и Load также
сохранены в материалах073. IDA b92074d1 сохранена и закрыта. Входные EXE не запускались.

| RVA | Контракт |
|---|---|
| 1594D0 | Load: raceBYTE/2, CAM, первый интервал, intro/input/UI/engine state |
| 1590B0 | Intro: play/matrix, end-70, ожидание fade, следующий ordinal, deferred skip/finish |
| 4B4A40 | IsFading: ненулевой fade time; это не проверка конечного alpha |
| 4B4AA0/4B4AD0 | FadeIn/FadeOut, time±epsilon, общий clock и density |
| 159420/13F690 | Camera count/текущие секунды |
| 159440 | Stage input-block field108 |
| 4CED70/4CE9D0/4D4CA0/4D4C30 | Engine state/camera controls; полные потребители ещё не перенесены |
| 4D2EB0 | Применение camera view |

Количество записей берётся из независимо прочитанных реальных CAM1.2:
Bellato9, Cora9, Accretia8. Сами интервалы берутся из бинарных таблиц по RVA
7D18C8/7D1938/7D19B0. audit_client455_tutorial_intro.py создаёт tables.h и
проверяет его происхождение перед normal preparation.

Существенные детали:

- Поле label в записи не выбирает камеру. Используется ordinal0..count-1;
  у Bellato/Accretia label и ordinal местами различаются. Это видно в asm.
- Порог — signed32(end-70), сравнённый с double(nowSeconds)*30; pending
  увеличивается один раз на камеру. Следующая камера ждёт IsFading==FALSE.
- FadeOut2, затем FadeIn3 перед следующей камерой. После последнего перехода
  ordinal==count ещё один tick остаётся active, завершение происходит следующим.
- Skip запоминается в конце intro-ветки как ordinalFFFF, очищает запрос и
  завершает ролик только следующим tick. Не является немедленным early return.
- Завершение: FadeOut0/FadeIn5, разрешение ввода, screen/mouse show, запрос
  запуска board script, сброс intro/engine state, follow-camera в том же tick.
- Init обнуляет pending/ordinal; Load этого не делает. Reload после skip сохраняет
  FFFF и снова завершает ролик следующим tick. Это отдельно проверено.

## Исходный код и границы интеграции

client455_tutorial_intro.cpp/h содержат восстановленную state machine.
client455_tutorial_intro_camera.cpp — переиспользуемый настоящий backend:
CAniCamera load/select/play, R3SetCameraMatrix, IsFading, SetFadeIn/Out и явный
ReleaseAniCamera. Обязательные stage/UI/QBI/new-engine consumer callbacks
абстрактны; успешных default/no-op реализаций нет.

Оба cpp собираются в обычной RFClient455Facade. В обычной фабрике владельца
CGP_Tutorial пока нет, поэтому linker удаляет неиспользуемые providers. Они не
force-retained и не объявлены работающим обычным обучением.

Native full-object probe использует этот же provider, настоящие CLand/CLevel,
CAniCamera/R3SetCameraMatrix, GPU/fade, CGUIScreen/CGUIMouse и CAvatar для race/stage.
Он не создаёт/не рисует полноценного Avatar actor. Stage input flag, запуск QBI,
follow-camera и новые engine-control consumers представлены явными recording
callbacks. full_stage_QBI_engine_controls=false записан во все результаты.

Первая попытка дала пустой кадр: новый backend был собран без conditional
RF_CLIENT_455_WEATHER и читал _R3ENGINE_STATE с неверным layout. Исправлены
compile definitions **только этой TU**: полный ENGINE_DEFINITIONS согласован с
движком/клиентом. Это проверяется в checkpoint; actual compiler tlog содержит
нужные definitions. Старые engine033/074 library и оригинальные sources не менялись.
После исправления каждая входная и применённая матрица сравнивается в нулевом
rotation домене probe; реальные кадры присутствуют. Ранние неуспешные запуски сохранены
в ignored work/, не выданы за PASS.

## Наблюдения

| Мир | Камеры | Tick/250ms | Применено matrix | FadeOut2 | Dmalloc до/после |
|---|---:|---:|---:|---:|---:|
| Bellato |9|357|343|9|270592/270592|
| Cora |9|325|310|9|270592/270592|
| Accretia |8|258|244|8|270592/270592|

Все три процесса завершились0, предупреждений0. R3SetTime/R3SetLoopTime
управляют собственным движковым clock: полного реального ожидания роликов не
было. На каждом tick идут реальная матрица, world frame/GPU и DrawFadeScreen.
Сохранены 26 кадров отдельных камер и три начальных кадра; все29 просмотрены
на трёх contact sheets. Затемнения видны, но эталонный runtime не запускался:
пиксельный паритет, полный fade renderer и численная идентичность матриц455 не
объявлены принятыми. Dmalloc balance не доказывает все COM/GPU/heap lifetimes.

У всех трёх сценариев отдельно прошли skip с deferred completion, повторная
загрузка с сохранёнными счётчиками и явный Init. Проверены порядок callbacks
завершения, один FadeOut2 на камеру и сохранение посторонних camera-control bits.
Actual trace.jsonl подтверждает переход через ordinal==count перед завершением.

Resources — копии под work/world455-inputs; runs используют hardlinks только к
этим work-копиям. SHA всех фактических входов после исполнения не изменились.
Каждый run хранит собственные EXE/map/console/trace/results/frames; raw assets
не добавлены в Git. Evidence — inventory/client455-tutorial-intro-*.json.

## Сборка и дальнейшая работа

RF_Online.bin `516664365726f782f256c87337ba0d14f349ee2e7556fa48205a53619220a44c`,
x86/base400000/entry150790/2043392bytes,182client/20kernel/34facade TU,
0unresolved. Runtime bytes равны074 c72e3d7 после маскирования двух DWORD
link timestamps по offsets304/1874448; layout/size совпали, больше различий нет.
Это ожидаемо: новый provider ещё не подключён к обычной фабрике.

Точная новая PE прошла WinMain/TCP fixture/engine/sound/D3D/Character/Create1;
остановка до обычной игры. First-chance40080201 через KernelBase остаётся
неизвестным. Неизменённые большие GUI/kernel suites не повторялись; старые
отчёты сохранены историческими. Gate PARTIAL; M6/M6F/M7/M9 открыты.

Далее076 — настоящий CGP_Tutorial owner: Create/Destroy/Load/Unload/Frame/Input,
реальные engine-state consumers8CED70/8CE9D0/8D4C30, Avatar/QBI/localfeedback/
board и fourstage factory/nextDWORD совместно. Использовать уже проверенные
BSP и intro providers. Не подменять required callbacks заглушками. Legacy2->3
bridge убирать только вместе с настоящими Tutorial2/MainGame3 и переходами Login.
Остаются все ранее учтённые ILevel/Empty/INS/Character/render/auth/игровые/IME/
lifecycle/failure gaps; текущий результат не закрывает полноту455.
