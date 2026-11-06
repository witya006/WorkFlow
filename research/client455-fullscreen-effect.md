# Fullscreen-проход455 и реальные intro callbacks — участок076

Восстановлена обычная motion-ветка FullScreenEffect в производном исходном
движке. Intro mode/density callbacks больше не являются recording callbacks:
они вызывают реальный движок. Полный CGP_Tutorial/factory/QBI пока не создан.

## Подтверждённый контракт

Эталоны: x86/base400000,
SHA-256 `b1b5febf0d0394712e2322350e19dafe60742e8642697b93cfb89135bac1fd8b`,
backup `46528aac20499e3b3928d58658d7e0cefe26feba7cd193796d5cfbf7a2bbc558`.
11 полных диапазонов и default float совпали между pins. Четыре полных asm,
helpers/init/end и xrefs сохранены в ignored
artifacts/client455-progress/fullscreen076.json. IDA f1ac7cc2 сохранена и закрыта.

| RVA | Контракт |
|---|---|
| 4CE9D0 | Store density float без нормализации |
| 7F7850 | Начальное значение0.25; intro ставит0.15 и затем0.25 |
| 4CED70/4CED90 | Полный modeDWORD; только mode0 сбрасывает previous-mode cache |
| 4CD9F0 | Основные effect textures512, независимо от старого video-memory level |
| 4CDB80 | R3BeginScene возвращает результат настоящего texture Begin;unloaded даёт0 |
| 4CE9F0 | End main→Begin blur→motion passes→restore framebuffer/depth/viewport→quad |
| 4DA470/4DA4C0/4DA510 | Texture Clear/End/Begin |

Старая база уже содержит SetStateFullScreenEffect/R3BeginScene/FullScreenEffect
и два нужных CTextureRender. Их наличие само по себе не означает совпадения455.
Начальное предположение о накоплении истории было уточнено по asm:

1. При смене режима455 рисует main opaque и очищает **текущий blur target**.
2. Каждый motion frame рисует main с alpha=trunc(density*255), очищает текущий
   blur target и снова рисует main opaque.
3. Затем blur-текстура выводится в настоящий framebuffer, ZENABLE сноваTRUE.

Окончательный opaque pass сохраняется, даже если название _FSE_MOTION_BLUR
предполагает другое. На одноцветных последовательных сценах след предыдущего
цвета не должен оставаться. Подмена на привычное накопительное смешивание
изменила бы поведение455. В legacy было только постоянное alpha0x3f и не было
двух подтверждённых очисток/финального opaque pass.

В новом overlay r3d3d8.cpp также исправлен возврат ошибки R3BeginScene при
выгруженном effect target и texture size512 для старого low-memory режима.
Density setter сохраняет float как есть; область проверки отрисовки — конечные
значения0..1. Out-of-range/NaN/OOM/прочие failure domains не приняты.

## Исходники и обычный клиент

client455_fullscreen_motion.inc задаёт motion branch; density API объявлен в
client455_fullscreen_effect.h и реализован в производном r3d3d8.cpp.
build_client455_engine_startup.py создаёт седьмой byte-preserving overlay,
не меняя baseline033 sources/library. В движке по-прежнему67 TU.

Обычный MainGame renderer уже вызывает FullScreenEffect, поэтому новый код
естественно присутствует в RF_Online.bin: provider R3Engine455Startup:r3d3d8.obj
проверен в .map. Force-retention не используется. Source camera backend теперь
реализует setEngineRenderFlag через SetStateFullScreenEffect и
setEngineFloat8CE9D0 через настоящий density setter. Сам ordinary Tutorial owner
ещё не подключён к фабрике; mode/density provider исполнен в full-object probes.

## Проверки

Отдельный GPU probe выполнил18 кадров через реальные R3BeginScene→
FullScreenEffect→R3EndScene. Проверены:

- Density0/0.15/0.25/1, последовательности red→blue→green, default0.25 и хранение
  полного modeDWORD, включая0x80000005. Центр кадра равен текущему цвету.
- Отключение эффекта/повторное включение, post-composite UI marker в framebuffer.
- Тот же фактический render target и depth surface, viewport640×480,
  screen dimensions640×480 и восстановление ZENABLE.
- Два legacy video-memory level0/2: реальные main/blur textures512×512.
- Release→неуспешный R3BeginScene→Init→новый успешный проход.

Пять сохранённых GPU pattern frames просмотрены. Это проверка своего кода и
статических контрактов455, не pixel comparison с работающим эталонным EXE.

Все три настоящих учебных мира повторно прошли intro через настоящий fullscreen
pipeline. Сохранились9/9/8 камер,357/325/258 ticks,343/310/244 matrix applications,
skip/reload/counter retention и Dmalloc270592 до/после. Предупреждений0, exit0.
Все29 новых world GPU views просмотрены. Stage input/QBI/follow/camera-control
callbacks в этих probes всё ещё recording callbacks; Avatar используется для
race/stage, полноценный actor/render/gameplay не выдан за готовый.

Resources остаются work-копиями; SHA входов после world runs неизменны. Run
EXE/map/result/trace/frames сохранены отдельно. Raw assets/analysis не в Git.
Ни один входной EXE не запускался, серверные файлы не изменялись.

## Сборка и пределы результата

Новая RF_Online.bin:
`4553f4016e40d2803bee9a91661961206ef00b59f2ac395c564dcd311dc6f204`,
x86/base400000/entry150860/2043904bytes,182client/20kernel/34facade TU,
0unresolved. Derived engine67TU/7overlays/library SHA
`2df1e50eafb559452c4c610815e3c9534cc6eb0d1f5186e0c876cd7ab3576592`.

Точная новая PE прошла WinMain/TCP fixture/engine/sound/D3D/Character/Create1;
обновлён startup contracts probe. First-chance40080201 через KernelBase остаётся
неизвестным. Runtime изменился: timestamp-only reuse075 к этой сборке неприменим.
Old GUI/kernel/world075 gates оставлены историческими, не переписаны как fresh.
Текущий gate — inventory/client455-fullscreen-effect-checkpoint.json, PARTIAL.

Полный postprocessing не принят: water/bloom/дополнительные455targets,
полный Init/restore/reset/COM/GPU lifecycle и старый shadow allocation остаются
явными разрывами. Это не модернизация графики и не завершение M6F/M9.

Далее077: продолжить настоящий CGP_Tutorial owner. Остаётся camera-control
8D4C30 и его реальные потребители, затем Load/Create/Frame/Input/Destroy,
realAvatar/QBI/localfeedback/board и fourstage/nextDWORD/Login совместно.
Не заменять оставшиеся callbacks no-op. Использовать уже проверенные BSP,
intro, fullscreen и briefing providers. Legacy2->3 bridge убрать только вместе
с настоящими Tutorial2/MainGame3. Дополнительно прочитаны5588C0 и5488F0:
первый содержит Tutorial stats99 и inventory handling, второй — обычное создание
Avatar из сетевых данных; их нельзя взаимозаменять без проверки call sites.
Все прежние ILevel/Empty/INS/Character/render/auth/gameplay/IME/failures gaps остаются.
