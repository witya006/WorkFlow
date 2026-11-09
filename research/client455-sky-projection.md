# Проекция неба обычного CLevel — участок123

2026-11-09. PARTIAL M6. Текущий gate:
inventory/client455-sky-projection-checkpoint.json.
Восстановлен обычный wrapper неба и соответствующее состояние проекции.
Это не полная приёмка CSkyBox/entity/fade,renderer или клиента.

## Подтверждённый target

PE32 x86,base400000. Primary SHA-256:
`b1b5febf0d0394712e2322350e19dafe60742e8642697b93cfb89135bac1fd8b`;
secondary:
`46528aac20499e3b3928d58658d7e0cefe26feba7cd193796d5cfbf7a2bbc558`.
6 полных тел/6 полных asm/1435 инструкций совпали между pins.
Все страницы<=100,проверены len/count/sum/total/unique и полные pcode.
Остальные поисковые тела в raw не объявлены полными доказательствами.

| RVA | Назначение |
| --- | --- |
| 4E7A10 | Ordinary CLevel sky projection wrapper |
| 4C3400 | InitCore;orthographic flag0/scale5 |
| 515660 | Loaded getter sky owner |
| 5157E0 | Настоящий sky render;исследован,полностью не перенесён |
| 4B5900 | Sky fade;его numeric parity ещё не принята |
| 4C2A90 | Frustum refresh |

Обычный constructor8E9F40 пишет B38494;vtable slot**17** указывает на8E7A10.
Первоначальная догадка slot15 была отвергнута проверкой байтов,исправлена до
принятия audit. Это обычный CLevel,не INS и не соседний метод.

Порядок8E7A10:perspective(FOV,aspect,near2,far)→SetTransform(PROJECTION),
loaded? DrawSkyBox(local view),DrawFadeSky,затем perspective(FOV,aspect,
configuredNear,far). Если orthographic flag ненулевой:identity,сохранённые
float height/scale и width/scale,OrthoLH(-5000,+5000),frustum refresh.
Последний SetTransform(PROJECTION) выполняется в обоих режимах.
Perspective ветка не вызывает новый frustum refresh.

InitCore явно устанавливает flag0 и scale5;referenced floatAAA450 проверен
по байтам обоих pins,как и все read-only float/double literals выбранных тел.
Получены15+15 прямых xrefs;ограниченный regexp-поиск stores в8B0000..940000
нашёл только init. Это не исчерпывающая классификация инструкций и не доказательство
отсутствия indirect/alias writes через state pointers. UI/console writers и
другие orthographic consumers остаются открытыми.

## Перенос

scripts/native/client455_sky_projection.inc заменяет настоящий
CLevel::DrawSkyBoxRender,удерживается обычной PE по MAP. Никакой фиктивной
проекции для прохождения теста не добавлено:source state хранит подтверждённые
BOOL mOrthographic иfloat mOrthographicScale,инициализирует0/5 в настоящем
InitCore. Source-owned core header расширен на8байт после mMatProj;это не
попытка наложить весь собственный state на target privateABI.

Отдельный owned skybox header добавляет реальный IsLoaded455 getter без
изменения layout CSkyBox. Единые headers включены в engine/normal/probes.
Пересобраны все67 engine TU,182client TU,20kernel и обычные facade consumers.
Base033 source/library и оригинальные installations не менялись.

Новый branch использует настоящий D3DX runtime и x86 float stores для размеров
ortho. Не заявляется fullFP/NaN/scale0/invalidNearFar/CRT/privateABI parity.
Остальные Character/ray/alpha consumers пока не используют все новые state
поля;это сохранённый gap,а не полная поддержка orthographic pipeline.

## Runtime доказательства

`work/m9/bae558a3/sky-projection-001`:12 конфигураций,24 настоящих D3D
projection binds при реальном unloaded CSkyBox. Два FOV/aspect/near/far/size
набора,два режима,scale .25/5/16. Проверены default0/5,temporary near2,
восстановление perspective/ortho,frustum unchanged/refreshed и побайтное равенство
финального source matrix реальному GetTransform устройства.
Независимый closed-form Python oracle:матрицы abs2e-6+rel2e-6;planes
abs.002+rel2e-6. Это сравнение с математическим контрактом,не запуск target455.

Сначала наблюдатель оставлял копию vtable собственного устройства на время
реального SetTransform и давал AV до завершения первого случая. Исправлен
только fixture:на время настоящего вызова возвращается original vptr,
GetTransform также вызывается без перехвата. После этого12 случаев проходят.
Внутренний механизм D3D,вызвавший AV при подменённом vptr,не исследован.
Неудачные native outputs сохранены подwork/m9;production workaround не добавлен.

`work/m9/001219e8/sky-world-001`:реальная Bellato,проверено IsLoaded455=true,
настоящее небо занимает307200pixels. Пять GPU кадров просмотрены:
base,translation+1000X,worldNear3000,orthographic restore,unloaded.
Первые4 кадра побайтно равны. После настоящего ReleaseSkyBox кадр полностью
соответствует clear control. Разница loaded/unloaded921600байт. Warnings0.
Неиспользуемый четвёртый байт backbuffer равен0:первоначальный oracle ошибочно
ожидалFF,исправлен после чтения фактического кадра. Повторён только verifier,
native успешно завершился ранее. Clear RGB302010 и uniform4byte pixel проверены.

`work/m9/9ca60b60/world-frame-001`:настоящая Bellato+архивныйFX,76queueops,
16OSclock±1,rayhit,16FX light frames,3ValidateDevice S_OK.5 GPU кадров просмотрены
и побайтно равны122;base==clear,magic151256/regular146637/FX646571bytes diff.
6 прежних texture warnings сохранены. Итого10 просмотренных GPU кадров123.
Кадры с реальным небом отделены от ground/light кадров:последние сами по себе
не были доказательством видимого sky.

Свежие map checks2692/330/110maps/canonical PASS,ANI2/BBX consumers PASS.
Точная новая PE прошла own entry/imports/startup sound1/contracts/window/device/
existingCreate1. Обработанные first-chance exceptions сохранены,включая
0x40080201,0xe06d7363,0x406d1388. Full bootstrap/auth/game не принят.
BSPleaf140/lightgeometry33/quake/explosion/texture/receiver/Character/159k и
прочие broad suites не повторялись и исторические.

## Сборки,сохранность,продолжение

Engine67/15derived SHA-256:
`e826ee1aaf9bb6b6f1f10a3470c411357f85eacf846b2436e9fa1aac1fe279cd`.
Из-за нового общего state42 COFF payload отличаются,17 timestamp-only,
8 byteequal. Это не заявление,что изменилось поведение42 функций/модулей.
Own PE SHA-256:
`182ecac65696d4ffdf3d8b7c7029aeb8befb54cf9c056912419e618449a3e26f`;
2227200bytes,x86/base400000,entry1679A0,WinMainB98B0/afterCreateB9A24,
182client/20kernel/unresolved0,безCharacterMR/FORCE.
Exact122 engine2fa70824…/PEb0b13a09… иreports сохранены под
artifacts/client455-progress/engine-before123.lib,normal-before123.bin,
*-before123.json. Baseline033 есть;старый082derivedsnapshot gap остаётся.
IDA5b615f3e saved/closed,list0. Raw sky-projection123-reference/session.json.
Original/server files не менялись;inputEXE не исполнялись;публикации нет.

Следующий124 — полный actual sky material/render-state flow9157E0 и связанный
fade8B5900:сравнить legacy CSkyBox/CEntity,проверить flags/animation/view restore,
перенести подтверждённые различия и проверить реальные sky assets.
Затем fullReadyBsp/local camera/world-frustum/cache/alpha/shadow/device reset
и остальные client-acceptance gaps. Wrapper123 не закрывает их.
M6/M6F/M7/M9 OPEN;M9 по-прежнему полная приёмка клиента455 без обновления графики.
