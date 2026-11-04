# Поза Character455: ключи и основные FrameMove phases

2026-11-05. M6, клиент. Source готов для описанного участка; полные FrameMove,
Character, renderer и M9 не закрыты. Исходные установки/серверы не менялись,
входные EXE не исполнялись. Текущий gate: inventory/client455-pose-checkpoint.json.

## Основание

Два x86/base400000 PE: currentSHA
`b1b5febf0d0394712e2322350e19dafe60742e8642697b93cfb89135bac1fd8b`, backupSHA
`46528aac20499e3b3928d58658d7e0cefe26feba7cd193796d5cfbf7a2bbc558`.
9bodyranges, размеры иSHA вinventory/client455-pose-reference.json; оба PE равны
наэтих участках. Owned IDA66b26ca4 закрыта/save в предыдущем исследовании.
Новых IDA sessions этот source unit не открывал: использованы сохранённые инструкции.

| RVA | Контракт |
|---|---|
| 51DE80/51DF90/51E160 | Scale/rotation/translation, каналы2/0/1 |
| 534FC0/534D60 | Дополнительный axis scale и D3DX multiply wrapper |
| 523A40 | Основной FrameMove pose/transition/ramp/parent/bone flow |
| 51E270 | Secondary pony/skirt motion, пока reference only |
| 533430/533490 | Profiling begin/end, пока reference only |

Cached decompiler неверно определяет stdcall signatures и локальные массивы
D3DXQuaternionSlerp/MatrixRotationQuaternion. Инструкции доказывают4/2аргумента;
правильные pointer/stack expressions нельзя брать из pseudocode без проверки.
Raw: artifacts/character-animation455/{key-*-insn,framemove-*,pose-*,scale-axis}.json.

## Реализация

scripts/native/client455_pose.{h,cpp}, RFClient455Pose.lib, x86/MT/O2/Gy/W4/WX.
Пять C APIs: SelectPoseKeys,ApplyPoseScale/Rotation/Translation,UpdateCharacterPose.
Новый RF_CLIENT_455_POSE defaultOFF, драйвер включает после source proof.
Normal consumers пока legacy, новая библиотека там unused/stripped.

Key time — signedDWORD comparison, count — lowWORD. Scale ищет линейно,
rotation/translation бинарно; диапазон до первого/после последнего extrapolate.
Вычитание timestamp сохраняет DWORD wrap, numerator интерпретируется signed32,
denominator unsigned32 через x87 FILD+2^32 correction. Ratio сохраняется float32.
Count1 всё равно читает соседний key: source допускает это внутри полного owner
span, а не придумывает постоянный key. Выход за owner — bounded failure.

Scale меняет diagonal3, затем умножает наaxis mesh5483; при отсутствии ключей
используется mesh4766. Rotation — реальный pinnedD3DX slerp, x87 FCHS quaternionW,
RotationQuaternion и multiply. Fallback берётmesh5022 с inverse parent5022,
обнуляетtranslation. Translation — интерполяция3, fallback mesh4750.
Все матричные операции использовали установленную D3DX9_36 сSHA
`c12f0ab0338eb5031d3d04beaf7208ac848f7e037d21ff963d2af90221cbe935`.

UpdatePose вызывает source Character loader, затем рассчитывает current/previous
с разными frame672/684. Проверены modifier5499/5503 с сохранениемtranslation,
transition692/duration, clamp/release previous и resets680/684/688, ramp704/708/
712/716, порядок snapshot4894/localbaseline4958 и parent.pose4830. Frame672 эта
функция не продвигает. Special slots1–3 копируют inverse/pose вmodel1188.
Последние две фазы вычисляют skin646=mesh4574*bone4638*bone.pose4830 с сохранением
порядка и физических offsets. Бounded policies для invalid pointers/counts/matrix
failures не воспроизводят unchecked reference failures.

## Проверка и пределы доказательства

- 132выбранных real-key cases: before/middle/after для первого animated канала
  каждого типа в22ANI. Independent Python interval/golden float32 для finite
  monotone keys; actual quaternion inputs/ratio/W-sign перехвачены и проверены
  при вызовах настоящей D3DX, provider не заменён scripted math.
- 8аналитических сцен на12maskedFPmodes: parent chain, current/previous transition,
  negative/completed transition, ramp, modifier, diagnostic null current,
  secondary-required failure и specialslot3. Дополнительно lowWORDcount,
  count1+owner boundary, duplicate times, signed/unsigned wrap, empty/null/missing model.
- Для родительского ramp аналитическая expected childtranslation имеет допуск1e-4
  из-за наблюдаемого отклонения D3DX inverse от идеальной математики. Остальные
  аналитические scalar assertions точные. Reciprocal approximation как причина
  отклонения — гипотеза; отдельного instruction proof DLL этого unit не делал.
- 11настоящих BN→MESH08 пар,22ANI:132updates корня/потомка,2298skin matrices.
  Проверены finite poses, whole64byte skin identity и inactive parent closure,
  оба ANI owners живут до освобождения meshes. Это structural consistency
  source pipeline, не независимое выполнение полного FrameMove эталона.
- Полный own-entry RF_Online.bin повторил результат component;5C APIs имеют
  реальные UNDEF callers вnative TU и provider RFClient455Pose:pose.obj в map.
  Heap/Dmalloc0, игровые DLL не загружаются. D3D device/draw для этой CPU проверки
  не создавались; загруженные CPU matrices не являются отрисованной анимацией.
- Normal180client/289modernCOFF/MT,lab188clientTUs. Normal runtimebytes равны
  предыдущему ANI snapshot после исключения timestamps. Snapshot финальной
  normal сборки:character455-pose-final. Идентичности всех PE — current gate.
- Прежние large runtime suites не запускались. Старые ANI/legacy/manager/graphics
  reports остаются историческими с собственными PE pins. Новая проверка не
  заявляет, что эти suites были повторены на текущем lab.

Непроверенные области: произвольные matrices/NaN/unmaskedFP/full exception unwind,
private global scratch/profiling ABI, arbitrary traversal/overlap31+bone pointers,
все input/allocator/OOM failure domains, exact deprecated unsafe owner routes.
Нормальный WinMain не запускался и не переключён на455typed Character consumers.

Secondary91E270 с непустым owner1184 ещё не реализован: если этот путь требуется,
UpdatePose возвращает RF_POSE_SECONDARY после уже выполненных операций, а не успех.
Нельзя использовать эту partial API как готовую замену всей455FrameMove.
Далее восстановить secondary owner/timeGetTime/pony-skirt math и producer frame/
transition state; затем full manager/worker и связать pose с455D3D9skin/draw/shaders.

Воспроизведение через scripts/Invoke-Python.ps1:
prepare_client455_pose_inputs.py →build_client455_pose.py →probe_client455_pose.py →
prepare_client_build.py →probe_client_character_build.ps1 [обычный/-HelperLab] →
probe_client455_pose_client.py →checkpoint_client455_pose.py.
Reference audit уже закреплён; не повторять без изменения исходных PE/analysis.
