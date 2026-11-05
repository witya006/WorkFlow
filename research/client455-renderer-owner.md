# Владелец ресурсов Character455

2026-11-05. Восстановлены конструктор, привязка устройства и normal destruction
владельца Character, а также source adapters к существующим model/draw kernels.
Это зависимость совместного normal Character/D3D9 port; обычная сборка ещё
использует старые Character и D3D8. M6/M6F/M7/M9 остаются открытыми.

Эталон x86/base400000. SHA-256 основного455:
b1b5febf0d0394712e2322350e19dafe60742e8642697b93cfb89135bac1fd8b;
второго:46528aac20499e3b3928d58658d7e0cefe26feba7cd193796d5cfbf7a2bbc558.
11 диапазонов равны в обоих pins, размеры/SHA/RVA в renderer-owner-reference.json.
Главные: ctor5DFB70/RVA1DFB70, defaults91C8F0/RVA51C8F0,
device920590/RVA520590, dtor9228A0/RVA5228A0. IDA8ad1c657 закрыта/save.
Raw artifacts/client-character-interface/owner-*.json, полные инструкции
constructor/device/defaults/destructor с проверенными длинами страниц.

Новый тип RF455CharacterRenderer имеет подтверждённый размер33856(0x8440),
но не выдаётся за все методы/private ABI исходного C++ класса. Статические
проверки фиксируют embedded managers/pools/caps. Старый D3D8 объект не приводится
к новому и не дублируется shadow record. Opaque bytes сохраняют входное значение.

| Поле | Смещение |
|---|---:|
| Borrowed device, D3DLIGHT9, sprite | 0,8,112 |
| Bone/mesh managers, каждый4148bytes | 116,4264 |
| Texture manager, effect storage | 8424,8712 |
| Vertex64/Vertex36/Index16 pools | 8928,17128,25328 |
| Vertex mode, D3DCAPS9, specular flag | 33528,33532,33836 |
| Blend duration, не записывается этим ctor | 33844 |

Конструктор повторно использует восстановленные managers/pools, задаёт directional
light с diffuseRGB=.8 и ambientRGB=1, direction=(0,0,-1), mode2 и известные flags.
Неопределённые поля не обнуляются вслепую. Instruction-derived oracle содержит
32892 записанных байта и mask остальных; два начальных poison patterns проверены
одним сравнением каждого storage, без отдельного assertion на каждый байт.

Device binding заимствует device в owner/texture manager/трёх pools, не AddRef.
GetDeviceCaps HRESULT игнорируется, как в инструкциях. MaxVertexBlendMatrices2/4
меняет mode; остальные значения сохраняют прежний. MaxVertexBlendMatrixIndex
определяет indexedBlend, ShadeCaps bit9 — specular. Сохраняется256byte log-path
copy и точная debug warning string из455.

Общие shader manager/declarations отделены от экземпляра renderer. Bootstrap12
программ выполняется только при null shared shader device. Повторный bind не
перезагружает shader programs и не перепривязывает общие ресурсы даже при другом
device; это правило455, а не обещание поддержки произвольного device replacement.
При отрицательном bootstrap result предусмотрен diagnostic callback. Полный
original logger/errorUI и его return semantics без callback пока не восстановлены.

Destruction:20 effect resources→extra→sprite→IB pools→VB36→VB64→effect managers→
textures→mesh manager→bone manager. Sprite обнуляется; released effect/pool slots
сохраняются. Повторный destructor unsafe, как в reference. Общие shaders и
declarations освобождаются отдельно их владельцем. Constructor exception unwind,
device reset и сбои allocator остаются отдельными открытыми областями.

Проверены два constructor patterns, пять caps/gate случаев (включая неуспешный
GetDeviceCaps) и порядок Release с COM-ABI capture. На настоящем D3D9 HAL source
owner загрузил BELPHEGORHOLIDAY BN/MESH08, ANI и3textures, создал shader resources,
передал свои managers/pools в source load/draw contexts. Два разных кадра160/2160,
46geometry parts/92draws прошли отдельно и внутри полного client lab; BGRA SHA
совпали между запусками, previews просмотрены. Все свои allocations освобождены,
после очистки bindings device/D3D COM references0. В полном lab Dmalloc balance0,
игровые DLL отсутствуют. Это не original game frame parity; trig provider modernMT.

Gate inventory/client455-renderer-owner-checkpoint.json. Full lab197clientTUs,
5source APIs и их реальные PE targets проверены, linker E9 thunks учтены.
Normal293modernCOFF/MT/тот же engine archive; source owner APIs stripped.
Normal PE равен snapshot character455-frustum после исключения timestamps.
Immutable own runtime paths/SHA/RVA и кадры — renderer-owner-{gpu,client}.json.

Новых SDK/установок нет. Большие неизменённые model/ANI/texture/buffer suites
не повторялись. Оригинальные EXE не запускались; серверы не использовались.

Воспроизведение через scripts/Invoke-Python.ps1:
audit_client455_renderer_owner.py, build_client455_renderer_owner.py,
probe_client455_renderer_owner.py, prepare_client_build.py;
probe_client_character_build.ps1 [и -HelperLab];
probe_client455_renderer_owner.py --client, verify_client_coff.py,
audit_client455_normal_character_api.py, audit_client_executable.py --label НОВЫЙ_LABEL,
checkpoint_client455_renderer_owner.py. Native build/run используют обычную escalation.

Следом — реальный normal typed model/animation/ChInterface facade вместе с
движковым D3D9 device path. Для camera producer использовать уже готовый source
frustum031. Оставшиеся39 старых SDK functions/150field candidates перечислены в
normal interface inventory; владельца, loaders/pose/draw заново не восстанавливать.
