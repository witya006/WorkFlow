# Ресурсы кадра455 — участок137

2026-11-10. **PARTIAL M6**. Обычные InitFullScreenEffect/ReleaseFullScreenEffect
теперь владеют всеми пятью render targets:screen-sized сdepth,512²сdepth,
512²безdepth,ещё512²сdepth,256²безdepth. Добавлен PerbMap load/release и
capture-current helper. Full Fraction/particle/BBoShasi draw/routing не перенесён.

Текущий checkpoint:inventory/client455-scene-capture-checkpoint.json.
Повторить scripts/Invoke-Python.ps1 scripts/checkpoint_client455_scene_capture.py.

## Доказательства и обычная сборка

Два x86/base400000эталона:primary
b1b5febf0d0394712e2322350e19dafe60742e8642697b93cfb89135bac1fd8b;
secondary46528aac20499e3b3928d58658d7e0cefe26feba7cd193796d5cfbf7a2bbc558.
12полных selected functions,1855instructions включая8инструкций нижнего
chunk8CD830;13ranges одинаковы между pins. Все положительные CFG starts
покрыты,пагинация<=100. Это также включает ещё не перенесённые refraction
owners:сбор доказательств не означает готовую реализацию этих render owners.
Raw:artifacts/client455-progress/refraction137-reference.json;
IDA b4737bcb saved/closed/list0. InitRVA4CD9F0/Release4CDAD0/capture4CE020.

Exact136snapshot47files:artifacts/client455-progress/before137/manifest.json.
Новая engine708c892e60c3bf7457389b40ac24b9a466958c9d232d9efaf497d1ac3232b870;
из67payloads изменён толькоr3d3d8.obj. Shared camera/particle/vertex/material
headers не менялись,182client/20kernels повторно не компилировались.
PE42213f081aceb9f1630add0c9d4a77deab330f1ca43936a85fee4c97c5c7cf89,
2267648bytes,entry16F1C0,unresolved0. Fresh own WinMain/Miles1/window/D3D/
existingCreate1/contracts/providers проходят;это не Title/Login/gameplay.

## Реальная проверка

work/m9/21083b2f/fullscreen-effect-001:5actual GPUresources,8configurations,
3resize cases,positive synthetic32x16PerbMap DDS load/release иmissing-file path.
2capture cases:полный actual framebuffer скопирован точно с сохранением source;
при активномfullscreen выбираетсяmain texture.18прежних fullscreen frames
сохраняют framebuffer/depth/viewport/UI.5GPUviews просмотрены:RGB,cyan,magenta
с белым UI marker. Warnings0. Это ownGPU contract checks,не reference runtime
pixel equivalence. Capture helper ещё не подключён к ordinary game producer.

Первый target в текущем wrapper создаётся640x500 до публикации viewport640x480.
Для exact-copy case lab явно выбирает размер фактической поверхности. Полный
wrapper/real device Reset/lost-device/failure domains остаются открытыми.

8CE020 игнорирует HRESULTs и удерживает GetSurfaceLevel reference. Поведение
воспроизведено в историческом прогоне. В текущем коде форка обе временные
ссылки освобождаются. Изменение подтверждено на x86 с подставными COM-объектами
и описано в [RES-01](client455-resource-cache.md).
Loose PerbMap.dds в455отсутствует;
positive test использует явную synthetic fixture,не подмену455asset.
8CE2A0 — Fraction,неPlazma. У8CE0A0 остаются unowned stack lanes;defaults не
выдуманы. Все прежние fullstage/Character/protocol/gameplay/M9gaps сохраняются.

## Место и следующий функциональный рубеж

Общие immutable assets теперь через scripts/client455_asset_staging.py.
Pool подwork/shared-runtime-inputs принимает проверенные ownedcopies;originals
не hardlinked,configs/executables остаются независимыми. Реальный startup:
8assets/2.0MiB linked,208896newpool bytes;existingCreate36assets/9.0MiB linked,
newpool0;fullscreen11assets/newpool0.5file identity/boundary cases PASS.
Старые каталоги не удалялись. Storage scan150.95GiBlogical/42.29GiBunique —
снимок до этих небольших изменений,не новый полный scan.

Следующий приоритет A–E изdocs/roadmap.md:ordinaryTitle/Login→selection→world→
gameplay→fullM6F/M7/M9. Не расширять137 новыми микроконтрактами вместо этого.
