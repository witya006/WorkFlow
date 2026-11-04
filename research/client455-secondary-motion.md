# Вторичные движения Character455

2026-11-05, M6. Восстановлены состояние/таймер/матрицы вторичных движений;
точность старого CRT sine, actor defaults/producer кадров и normal renderer
ещё открыты. Это не готовый Character или M9. Gate:
inventory/client455-secondary-checkpoint.json.

## Первичные доказательства

CurrentSHA `b1b5febf0d0394712e2322350e19dafe60742e8642697b93cfb89135bac1fd8b`,
backupSHA `46528aac20499e3b3928d58658d7e0cefe26feba7cd193796d5cfbf7a2bbc558`,
x86/base400000. Body RVA51E270/80Ebytes, borrower3CD430/105bytes и staticCRT
__CIsin dispatcher473340/4Fbytes равны между PE. Хеши диапазонов и18 точных
double constants — inventory/client455-secondary-reference.json.
Raw584инструкции/stack expressions и xrefs:
artifacts/character-animation455/secondary-*.json,secondary-insn.txt.
Owned IDA8115e37c закрыта/save; входные EXE не запускались.

Secondary owner — borrowed84bytes: value5float,direction5signedint,minimum5float,
maximum5float,lastTickDWORD. Клиентский actor3CD430 передаёт свойthis+500 вmodel1184.
FrameMove очищает pointer1184 после работы, не освобождает состояние.
Это известная84байтная область внутри actor,не доказательство размера полного
исходного C++ класса или отдельной allocation. Source struct описывает эту область.
Другой найденный MOV offset4A0 в73428B относится к другому объекту, не использовать как
доказательство Character. Инициализация actor defaults ещё не установлена.

Декомпилятор путает stack после imported stdcall quaternion calls. Проверены
физические offsets: skirt trigger — quaternionW*Z<-.2, а не1.3*1.2; timers
используют сохранённый timeGetTime DWORD, а не quaternion bits. Direction=-1 —
integer FFFFFFFF, не NaN. Эти ошибки pseudocode в source не перенесены.

## Source и связка

scripts/native/client455_secondary.{h,cpp} входит вторым объектом в
RFClient455Pose.lib. RF455_ApplySecondaryMotion вызывается из UpdateCharacterPose
дляmesh5571. Контекст обязателен при непустом owner; отсутствующий backend
возвращает RF_POSE_SECONDARY. Нулевой owner корректно не вызывает время/матрицы.

Пять oscillator channels обновляются при unsignedDWORD(time-lastTick)>10.
Сохранены x87 operation order/m32 stores и различия double .3/float .3 widened,
double .005/float .005 widened. Состояние обычно обновляется на первом effect
данного прохода; последующие effects тоже читают время, но могут не обновлять
oscillator повторно. Принадлежащий actor84 и shared globals28 — разные lifetime.

Globals1189738..1189750: left/right timers, pony XYZ/timer/phase. Они общие для
персонажей; контекст должен сохранять один globals owner на renderer, не создавать
его заново для каждого effect. PonyL1 увеличивает phase на.001f widened,
отслеживает перемещение, строит Z/X rotations и нормализует quaternion/matrix,
сохраняет исходную translation. PonyL11 умножает local на parent.pose иXrotation.
R/Lskirt используют quaternion pose928/864, inverse1120/1056, axis(0,+/-.2,-1)
и связанные kicks/clamps. Bskirt вычисляет RotationY, затем применяет RotationZ;
неиспользуемый результат Y и quaternionMatrix(currentPose) вskirt сохранены.

Все D3DX calls идут вреальную pinnedD3DX9_36, SHA
`c12f0ab0338eb5031d3d04beaf7208ac848f7e037d21ff963d2af90221cbe935`.
Reference sine — static __CIsin с SSE/default dispatcher. Его реализация здесь
не восстановлена. Source требует sineFloat callback, тест явно использует
modern/MT sin(double)→float32. Это полноценное вычисление для выбранных входов,
но равенство старому CRT по всем битам/CPU/FPU условиям не доказано. Не скрывать
этот gap и не объявлять всю secondary ветку окончательно эквивалентной455.

## Проверка

- 36finite/nearestPC53 scalar scenarios, независимые Python state/global goldens:
  whole84/28 bytes, both limits, shrink/integration, unsigned clock wrap,
  delta10/11, pony motion detection, positive/negative skirt trigger иangles.
- Перехвачены и проверены kind/order/floatbits rotation-angle calls при
  выполнении настоящих D3DX методов. Проверены finite matrices и сохранениеpony
  translation. Это не независимое сравнение всех матриц с выполнением эталона.
- Настоящие Cora_Female.bn38parts со всеми5effects иCORFEMALE_ARMOR_061.bn35parts
  с3skirt effects загружены source legacy dispatcher. Шесть FrameMove updates
  вызывают эффекты, читают ожидаемое количество clock ticks, очищаютmodel1184
  и сохраняют borrowed state. Bone buffers/model lifetime освобождены, heap0.
- Fullclient ownentry повторил component результат. RF455_ApplySecondaryMotion
  имеет actual caller вsecondary TU и provider RFClient455Pose:secondary.obj.
  Всего6pose/secondary APIs, оба source objects x86/MT. Игровые DLL не загружаются,
  Dmalloc0. Устройство D3D/draw не создавались.
- Повторена только затронутая pose проверка:11pairs/132updates/2298skin matrices
  standalone/fullclient, результат прежний. Неизменённые большие IO/texture/GPU/
  manager suites не запускались; старые reports — исторические.
- Normal runtimebytes равны предыдущему snapshot за исключением timestamps;
  normal APIs покаunused/stripped. Lab189clientTUs,normal180. Полные PE identities
  вgate; normal snapshotcharacter455-secondary.

Reproduce через scripts/Invoke-Python.ps1: build_client455_pose.py →
probe_client455_pose.py →build_client455_secondary.py →probe_client455_secondary.py →
prepare_client_build.py →probe_client_character_build.ps1 [обычный/-HelperLab] →
probe_client455_secondary_client.py →probe_client455_pose_client.py →
checkpoint_client455_secondary.py. Reference audit уже закреплён.

Далее: originalCRT sine contract, actor state defaults/frame/transition producers,
AnimationManager/worker и связка source pose с455D3D9skin/draw/shaders/normal consumers.
Unchecked NaN/OOM/name/pointer/unwind, полный C++ ABI и поведение всех CPU/FPU
режимов остаются непроверенными. M6/M6F/M7/M9 открыты; серверы не затронуты.
