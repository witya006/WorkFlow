# Продвижение кадров: восстановлено в обычном клиенте

2026-11-05. Source455numeric kernel иCAnimation constructor подключены вобычный
RF_Online.bin черезреальные CResObject calls. Полный Character455/normal renderer
этим не восстановлен; M6/M6F/M7/M9 открыты.
Gate inventory/client455-animation-timing-checkpoint.json.

## Первичные данные

CurrentSHA `b1b5febf0d0394712e2322350e19dafe60742e8642697b93cfb89135bac1fd8b`,
backupSHA `46528aac20499e3b3928d58658d7e0cefe26feba7cd193796d5cfbf7a2bbc558`.
x86/base400000. Шесть bodyranges равны,размеры иSHA вreference report:

| RVA | Размер | Значение |
|---|---:|---|
| 3CD560 | 2AB | CResObject::CalculateCurrentAnimationFrame |
| 3CCC30 | 60 | CAnimation ctor100 |
| 51C490 | 76 | Инициализация84byte secondary region |
| 3CD1B0 | 1E | Wrapper ctorsecondary,вызываемый actor+500 |
| 4B3E30 | 7 | Getter elapsedfloat11550A0 |
| 048180 | 19 | Getter speedfloat animation+8 |

Owned77611a53/23cf5a01 закрыты/save. Raw decompile/инструкции:
artifacts/character-animation455/timing-*.json. Входные EXE не исполнялись.

## Изменение

Legacy CResObject source уже содержит тот жеосновной control flow: flags512stop,
256loop,2048interpolation; nullmodel return;oldFrame copy;current/max clamp;
carry сохраняется приstop и обнуляется приadvance; interpolation продвигает
своё время,а currentboneframe остаётся прежним до явной установки. Сохранены
существующие virtual IsEnable/IsDisable calls иbranches,а не rawoffset cast.

Новая sourceарифметика scripts/native/client455_animation_timing.cpp:
elapsedfloat→x87*1000double*5double+unsignedDWORDcarry→**double spill**,
затемspeedfloat multiply+unsignedDWORDcurrent. FISTP signed64 с временным
round-toward-zero и восстановлением controlword; результат —lowDWORD.
Это отличается от обычной современной float32 evaluation исходного выражения.
Например,current160/carry0/dt.03f/speed1: float32 expression округляется к310,
reference PC53-nearest sequence даёт309. Это сравнение форматов вычисления;
старый входной EXE для демонстрации не запускался.

Normalcresobject.cpp patch заменяет только двеnumeric expressions иCAnimation
ctor под RF_CLIENT_455_ANIMATION_TIMING. Legacy branches/Korean source bytes
сохранены,existingdraw455overlay сохранён. apply_client455_animation_timing.py
строит combined overlay изоригинала иdraw patch,отказывается отunknownchanges;
канонический hash вclient-behavior-patches.json. Воригиналы ничего не записывается.

Module компилируется вреальныйR3EngineMT,x86/MT. Flag defaultOFF,проверенный
драйвер включает его. Вnormal linked2APIs: AdvanceAnimationFrameValue и
InitializeAnimationControl. Вcresobject.obj подтверждены directE8REL32:2из
CalculateCurrentAnimationFrame и1изCAnimation ctor. Вlab также linked
InitializeSecondaryState; known84region теперь имеет восстановленные defaults:
value[.8,0,.4,0,0],direction1,min[0,0,-.2,0,0],max[1.3,.9,.7,1,.5],tick0.
Полная CResObject layout иподключение secondaryregion вnormal actor ещё открыты.

## Проверка

- 612finite/nonfinite/overflow/subnormal/carry/wrap cases на12maskedFPmodes.
  Независимый Fraction oracle моделирует двоичнуюточность24/53/64 и4roundingmodes,
  включаяdouble spill иsigned64truncate. Это не повторный вызовimplementation
  для golden. Проверено восстановление x87controlword.
- Whole100/84byte ctor outputs против pinnedinstruction-derived goldens.
  CAnimation size100 подтверждёнstatic_assert вреальном compiledclient.
- Полный собственный RF_Online.bin ownentry выполняет теже numericcases,а затем
  создаёт настоящий CResObject subclass ивызывает actualcompiledmethod:
  16сценариев — advance/explicitframe/stop/loop/clamp/interpolation done/incomplete/
  missingIP/disabledIP/zerospeed/carry/highDWORD/negativeelapsed/max0/nullbone.
  Провереныframe/old/carry/animating/IPstate иpublishingboneframe.
  LegacyCBone fixture — собственныйPODбеззагрузкиресурса,это не455modelABI proof.
- ActualcompiledCAnimation ctor сверяется по100bytes. HeapDmalloc0,
  gameDLLs не загружаются,frameClockInput восстанавливается. Ownentry не равен
  запуску normalWinMain илиприёмке реального игрового actor loop.
- Scopeddevice/Platform01 regression:2cases69checks,COM/Dmalloc0,previous frameSHA
  сохранён. Это прежнийD3D8renderer lab,не восстановленный455D3D9characterdraw.
  Неизменённые массовые IO/texture/Character suites не запускались.
- Normal180client+64engine+46JPEG=290modernCOFF/MT;lab190clientTUs. NormalPE
  **намеренно изменился** из-за реальных timing/ctor calls;никакого заявления
  оравенстве его runtimebytes предыдущейсборке нет. Snapshotcharacter455-animation-timing,
  всеPE identities вgate.

Открыты: upstreamelapsedclock smoothing/rate/CPU/FPU conditions,derivedactor
virtual flagbehavior,full actor lifecycle/normal455CBone/ChAnimationABI,
AnimationManager/worker,normal skin/draw/shaders иstaticCRT sine parity.
Unmaskedtraps/FPUexceptionflags/exceptionunwind не сертифицированы. Первый шаг
к normal integration не заменяет проверки функциональной полноты M6F/M9.

Воспроизведение черезscripts/Invoke-Python.ps1:
audit_client455_animation_timing.py →build_client455_animation_timing.py →
probe_client455_animation_timing.py →apply_client455_animation_timing.py →
prepare_client_build.py →probe_client_character_build.ps1 [обычный/-HelperLab] →
verify_client455_animation_timing.py [--lab] →probe_client455_animation_timing_client.py.
Послеscopedgraphics/COFF/snapshot:checkpoint_client455_animation_timing.py.
