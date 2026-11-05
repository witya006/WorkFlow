# Отсечение объектов камерой 455

2026-11-05. Source extraction/normalization шести плоскостей, публикация
view×projection и AABB подключены к настоящим SetCharacterClipping и
CResObject::ProcessClipping обычного клиента. M6/M6F/M7/M9 остаются открытыми.
Gate: inventory/client455-frustum-checkpoint.json.

Эталон x86/base400000, SHA-256:

- Основной: b1b5febf0d0394712e2322350e19dafe60742e8642697b93cfb89135bac1fd8b.
- Второй: 46528aac20499e3b3928d58658d7e0cefe26feba7cd193796d5cfbf7a2bbc558.

Семь диапазонов равны между pins; размеры/SHA/RVA в frustum-reference.json.
8C2A90/RVA4C2A90 — producer, 8C2C90/RVA4C2C90 — AABB,
8C2DC0/RVA4C2DC0 — копирование96bytes. Все163 инструкции producer и65 AABB
сохранены; длины MCP страниц проверены. Raw artifacts/client-character-interface/
frustum-*.json. Owned IDA2a568200 закрыта/save.

clip = view×projection из pinned Microsoft D3DX9_36. Плоскости по порядку:
-(col0+col3), -(col3-col0), -(col3-col1), -(col1+col3), -(col2+col3),
-(col3-col2). Нормализация сохраняет x87 порядок y²+x²+z², отдельные float
spills суммы, корня, reciprocal и четырёх products. Старый SDK держал некоторые
промежуточные значения extended и не подменяет этот контракт.

__CIsqrt проверен до __load_CW и восстановления CW. На конечных неотрицательных
входах с masked exceptions сохраняется PC, выбирается nearest RC для FSQRT,
исходный CW возвращается перед caller float spill. Это явно реализовано source;
errno/matherr/unmasked exceptions/NaN payloads не сертифицированы.

AABB выбирает minimum для строго положительного normal, иначе maximum, включая
unordered. Dot = ((nx*x+ny*y)+nz*z)+d без float spills; строго положительный
результат отклоняет box. Касание остаётся видимым, unordered dot не отклоняет box.
x87 ветки проверены отдельно от decompiler.

Source: scripts/native/client455_frustum.{h,cpp}, client455_frustum_system.cpp.
Production adapter загружает D3DX9_36 из системного каталога, SHA установленной
x86 DLL закреплён. При отсутствии DLL/export возвращается failure, обычный caller
вызывает abort. Это отличается от original mandatory import failure до WinMain;
deployment failure policy остаётся открытой. Успешного пустого fallback нет.

Проверены только изменённый контракт и его зависимости:

- 72 матричных случая/12PC-RC modes: identity, translation, perspective, повёрнутая
  камера, ortho, shear. Oracle — Fraction/integer sqrt с float spills. Двоичные
  матричные произведения точны; signed zero при RC-down учтён явно.
- 204 AABB случая: шесть граней, касание/следующий float снаружи, большой/точечный
  box, cancellation, quiet NaN. MXCSR DAZ/FTZ не меняет x87 результат.
- Те же численные случаи прошли через actual SetCharacterClipping в полном
  client lab. Девять CResObject cases: inside/outside, scale, касание, отсутствие
  bounding box и сохранение прочих status bits. Последнее проверяет текущий
  caller, а не полный actor455 lifecycle. Dmalloc остаток0.
- Device/Platform01 scoped regression: прежние frame SHA, warnings/errors0,
  device/D3D COM references0 и прежний Dmalloc balance.

Normal RF_Online.bin:2451968bytes/entryRVA1BC610,
SHA198c2dd38f5f0c78bedbea8d70f6712981ef63b042a21cf4fa16db89bbbcc6b4,
snapshot artifacts/client-first-build/character455-frustum.180client+67engine+
46JPEG=293modern x86/MT objects. E8 calls и конечные source destinations проверены
в PE, в lab учтены реальные E9 linker thunks. Две старые SDK clipping references
отсутствуют в новых global/cresobject objects.

Lab196clientTUs; immutable runtime path/SHA/RVA в frustum-client.json. Собственный
тестовый вход не запускает normal WinMain/оригинальный455EXE. Normal renderer ещё
D3D8. Матричная DLL не означает полного D3D9 port; game camera/visibility,
Character wrappers, typed model/animation, device lifecycle остаются открытыми.

Через scripts/Invoke-Python.ps1: audit_client455_frustum.py,
build_client455_frustum.py, apply_client455_frustum.py, prepare_client_build.py;
затем probe_client_character_build.ps1 [и -HelperLab],
probe_client455_frustum_client.py, audit_client455_normal_character_api.py,
verify_client_coff.py, audit_client_executable.py --label НОВЫЙ_LABEL,
probe_client_graphics455.py --level Platform01 --output inventory/client455-frustum-graphics.json,
checkpoint_client455_frustum.py. Native build/run требуют обычную escalation.
Большие неизменённые model/ANI/texture/buffer suites не повторялись.
Серверные файлы и оригинальные установки не изменялись.
