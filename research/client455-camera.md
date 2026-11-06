# Camera056: загрузка и воспроизведение камер входа/обучения

2026-11-06. Только клиент. M6/M6F/M7/M9 открыты.

455 x86/base400000 SHA-256
`b1b5febf0d0394712e2322350e19dafe60742e8642697b93cfb89135bac1fd8b`;
backup `46528aac20499e3b3928d58658d7e0cefe26feba7cd193796d5cfbf7a2bbc558`.
12 function ranges совпали между pins. IDAc449e061 закрыта/save=true.
Input EXE не запускались; raw в ignored artifacts/client455-camera/.

| RVA | Восстановленный контракт |
|---|---|
| 4D2070 | CAM version>=1.2; при version>=float1.3 после camera header есть FOV count и20-byte keys |
| 4D1B00 | При первом вычислении матрицы установить storedFOV*float0.788 |
| 4D1DC0 | Forward/reverse/pause/loop/stop и момент обновления old/now frame |
| 4D1F20/4D1FC0 | FOV key interval и interpolation value0 при nowSeconds*30; отдельный updater |
| 4D1890 | Release hierarchy/tracks/dummies и обнуление owner |
| 159670/1590B0 | Race-selected Tutorial BSP/CAM и camera-cut потребитель; fullTutorial ещё открыт |

Target owner56байт, camera records88, animation nodes349. File header:
version/cameraCount, затем start/end при ненулевом count. Camera: name64,
fov/distance/hierarchyCount, а для1.3 FovCount/keys20; затем hierarchy nodes.
Node: matrix64/position12/quaternion16/PosCount/RotCount/keys16/keys20.
После камер идут DummyCount и name64/parent64 плюс тот же node payload.
Target игнорирует trailer. Parser сохраняет его для lossless roundtrip.

Реальные bellato/cora/accretia/lobby CAM оказались **1.2**:50камер,89camera
nodes и42dummy nodes. Отдельно создан1.3 fixture с FOV keys. Поддержка1.3
подтверждена кодом455 и synthetic runtime; real1.3 assets в этой проверке нет.
Все четыре реальные файла и synthetic прошли C++ decode→encode byte equality.
Python audit независимо обходит wire counts/границы и закрепляет SHA input.

Восстановленные loader/play подключены к обычному CAniCamera в производной
startup-engine. Engine033 source/library сохранены. Public source class остаётся
56байт; его собственные private camera records сохраняют old80байтовый тип.
Новые FOV данные хранятся в typed document registry. Все TUs используют один
и тот же header; нет mixed ABI definitions или overlay original88-byte records.
_ANI_OBJECT349 материализуется через настоящие typed members/combined tracks
и Dmalloc. Проверены все сериализованные поля/ключи и баланс Dmalloc после
повторного Release. Small registry container живёт до завершения процесса,
чтобы не зависеть от порядка глобальных CRT destructors; Release удаляет doc.
Оригинальный destructor пустой; explicit Release по-прежнему обязателен.

Forward завершение: frame>=end/30. Flag0 сбрасывает startTick, но записывает
**float(startFrame) как секунды**, без /30. Reverse завершается при frame<=0,
а не end/30; flag0 ставит end/30 и сбрасывает clock, flag!=0 ставит0. На границе
все варианты возвращают false. Эти особенности подтверждены инструкциями,
а не исправлены под ожидаемое поведение. Pause не читает clock, кроме loop
restart; обычный restart может прочитать clock дважды. Есть детерминированные
clock cases и проверки reverse/loop через настоящий CAniCamera::PlayAniCamera.

Файловые/32-bit allocation bounds проверяются до материализации; malformed
parse не меняет прежний документ. Target может release-first/overread/частично
изменить owner — такие unsafe domains не выданы за эквивалентность. OOM,
concurrency, всё пространство FP modes и malformed dummy cycles ещё открыты.

Нативная проверка с полным набором клиентских объектов создала настоящее
D3D9 device, загрузила4real+1synthetic CAM, проверила51камеру/90camera nodes/
42dummy nodes. Обычный Play выдал конечную матрицу и изменил реальную GPU
projection согласно FOV*0.788. Процесс естественно завершился0. Полной scene/
world/Tutorial приёмки эта проверка не означает.

Separate FOV interpolation API восстановлен и проверен, но target camera
consumer8D5FF0 ещё не перенесён. Не вставлять animatedFOV в каждый Play:
в455 это отдельный вызов, Tutorial использует собственный путь. Старые engine
GetAniMatrix/dummy hierarchy numeric domains также ещё не полностью сверены.

OwnPE SHA-256
`56905e68ce0746c5367db5e08cdda8ee948a26196091d11d4777c6c116a697cf`,
x86/base400000/entry14ACA0/2022912bytes;182client/20kernel/23facade,
0unresolved. Derived engine91bdf0c7.../67units/5overlays;baseline033 unchanged.
Exact own startup сохранил TCP→engine/Miles/D3D/Character/existingCreate=1,
затем controlled stop до цикла. Russian остаётся beforeConnect, без remap.
Короткие зависимые native probes обновлены для этой сборки. Все22 scoped
checkpoints завершились0/PARTIAL; это приёмка описанных участков, не полного455.

Доказательства: inventory/client455-camera-{reference,native,checkpoint}.json.
Reproduce через scripts/Invoke-Python.ps1: audit_client455_camera.py;
prepare_client455_normal.py; build_client455_engine_startup.py;
build_client455_normal.py; обычные consumers/link/entry/startup;
probe_client455_camera.py; checkpoint_client455_camera.py.

Далее057: реальная загрузка Tutorial scene/Avatar/UI/localhandlers и joint
fourstage factory. Camera-cut/FOV consumer и target matrix math остаются в
критериях. Не заменять обучение обычным MainGame и не выдавать эту зависимость
за полный режим обучения. Серверы не изменялись и не реализовывались.
