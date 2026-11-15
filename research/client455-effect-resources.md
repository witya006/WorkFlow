# Штатный владелец ресурсов эффектов — работа 105

Частичный перенос продолжает [работу104](client455-magic.md). Таблица эффектов
теперь сама владеет индексами архивов `Effect`, а обычные StartMagicEffect и
первичная загрузка entity/particle выбирают эту группу. Ручная установка группы
больше не нужна для обычного запуска прицела. Полный мировой runtime эффекта и
ядерный контроллер ещё не восстановлены; M6/M6F/M7/M9 открыты.

## Подтверждение на 455

Установленный native IDA MCP: сессия `e536890b` сохранена/закрыта, после неё list0.
14 полных функций, 1315 инструкций, 14 равных диапазонов двух закреплённых x86
бинарников с base `0x400000`; отдельно равны 41 байт статического инициализатора.
SHA-256 основной 455:
`b1b5febf0d0394712e2322350e19dafe60742e8642697b93cfb89135bac1fd8b`;
второй:
`46528aac20499e3b3928d58658d7e0cefe26feba7cd193796d5cfbf7a2bbc558`.

| RVA | Контракт |
| --- | --- |
| `0x3e4390` / `0x3e4590` | Lazy entity / particle template и clone |
| `0x3e4840` / `0x3e4bc0` | Чтение таблицы / освобождение |
| `0x3e4060` / `0x3d8970` | Getter группы / выбор группы при запуске |
| `0x4e7150` / `0x4e71c0` / `0x4e7440` | Ctor268 / каталог архивов / Release |
| `0x4e75d0` / `0x4e76c0` / `0x6a01b0` | Setter группы / destructor thunk / atexit |
| `0x3d85d0` / `0x3d85a0` | Getter/setter particle flags на offset1224 |
| `0x689590` | Статический initializer, 41 байт |

Полные SHA-256 диапазонов и 24 настоящих файла замыкания прицела закреплены в
`inventory/client455-effect-resources-reference.json`; сырой IDA вывод —
`artifacts/client455-progress/effect105-reference.json`.

## Перенос в обычные клиентские исходники

В текущем RES-01 список и его RPK публикуются вместе, а прежний кэш
сценариев очищается только после успешной замены. Подробности в
[контракте загрузчика](client455-resource-cache.md#замена-effectentitylist-и-индексов-rpk).

`client455_magic_port.py` дополняет клиентские effectentitylist.h/.cpp и
effectcore.cpp. Глобальный владелец содержит уже восстановленную группу268;
его статический destructor освобождает индексы. LoadEffectEntityList сначала
открывает loose table, освобождает прежнюю table allocation, выделяет768×100,
затем Release/LoadDirectory `.\effect\`. Само чтение таблицы активную группу
не меняет. Release освобождает индексы перед проверкой пустого списка.

StartMagicEffect выбирает effect group перед существованием ресурса/парсером.
Lazy entity и первый particle template выбирают её перед Load. Cache hits группы
не переключают. Активный указатель после Release остаётся на безопасном пустом
статическом owner, как у target. Обычные методы retained из effectentitylist.obj /
effectcore.obj, engine library не менялась.

Также исправлен подтверждённый particle branch: NO_LOOP/END очищаются только
для конечной эмиссии перед установкой NO_LOOP; always-live/emission-time ветка
сохраняет flags. В fixture104 исправлено сохранение прежней группы: setter
возвращает новую, поэтому предыдущую нужно отдельно читать через getter.
Выявленный target quirk повторной загрузки таблицы с уже закэшированными
entity остаётся gap: target освобождает только таблицу, а не её object owners.

## Реальная проверка и обнаруженные ограничения

66 native checks проходят в `work/m9/6a9a43cc/effect-resources-001`:
обычный table bootstrap, повторная загрузка ещё пустой таблицы без утечки,
архивный cue на6 tracks, настоящий R3E model и5 particle recipes,10 clones с
раздельными element allocations и общими entity, матрица/обнуление translation,
START flags, сохранение активной группы при cache hit. Из настоящего архива59
загружаются все6 R3E/R3M/R3T, их текстуры создаются на реальном D3D9 device.

Первая проверка `work/m9/4e90af58/effect-resources-001` не прошла слишком широкое
условие возврата памяти: после уничтожения эффекта остались9728 байт. Проверка
показала, что это две начальные process-owned таблицы текстур:64×144 и64×8.
Все6 GPU handles уже равны null. Стенд отдельно вызывает публичный
R3ReleasePreTextures и получает Dmalloc270592→270592. Этот вызов относится к
владельцу общего текстурного manager; он не добавлен в production effect destroy.
Это не полная приёмка глобального shutdown.

При освобождении наблюдаются6 legacy R3T warnings. Они не скрыты: target warning
parity ещё не проверена. GPU handles освобождаются, но текущее подтверждение
не распространяется на все texture APIs/reset/shutdown. Новый эффект не рисовался
в GPU сцене и не обновлялся через полный игровой FrameMove. Проверены реальные
базовые recipes прицела; владение shared curve/control pointers у остальных
видов particle clones остаётся открытым.

Новая собственная PE SHA-256
`015a25c2b580ea606652fdfd82cf17d5b0b0de8e25920203b7722b64ea2750db`,
2154496 байт, x86/base400000, entry RVA15a320, WinMainb85a0, afterCreateb8714.
182 client /20 kernel /59 facade objects, unresolved0. Точная PE прошла прежний
offline Create→1 до game loop и сохранила настоящий Fast2D ready:7969.
Повторены magic36/status58/audio157/account/hotbar7/storage3. Шесть свежих hover
кадров просмотрены и побайтно равны104; другие32 кадра и большие неизменённые
world/audio/159k suites не повторялись. Engine546a7529… неизменён. Gate104
исторический. Originals/server не менялись; входные EXE не исполнялись.

Воспроизведение: `scripts/Invoke-Python.ps1 scripts/checkpoint_client455_effect_resources.py`.
Итог: `inventory/client455-effect-resources-checkpoint.json`.

## Следующий шаг

Работа106: проверить target texture release warnings и реальные EffectList /
FrameMove/matrices/render contracts, затем включить полный шестидорожечный
прицел. После этого — nuclear pending/position/frame/cancel, tagged sound и C1A.
True predicate hover пока явно отказывает до изменения предмета. Все прежние
gaps client-acceptance остаются обязательными для M9.
