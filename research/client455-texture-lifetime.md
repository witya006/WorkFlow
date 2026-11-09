# Текстуры118 — освобождение и обработчик предупреждений

2026-11-09. **PARTIAL, M6.** Подтверждены очистка управляемых текстур эффектов
и мира, общий счётчик R3T и происхождение20 предупреждений. Восстановлены два
отличия Warning: точная CP949 подпись «предупреждение» и возврат без окна при
отсутствующем обработчике. Освобождение текстур не переписано: оно уже следует
закреплённому455. Полный device/texture lifecycle и M9 остаются открытыми.

Gate: [client455-texture-lifetime-checkpoint.json](../inventory/client455-texture-lifetime-checkpoint.json).
Команда: `scripts/Invoke-Python.ps1 scripts/checkpoint_client455_texture_lifetime.py`.

## Эталон и статические доказательства

Оба эталона x86, image base0x400000. Основной SHA-256
b1b5febf0d0394712e2322350e19dafe60742e8642697b93cfb89135bac1fd8b;
второй46528aac20499e3b3928d58658d7e0cefe26feba7cd193796d5cfbf7a2bbc558.
18 полных функций/18 полных дизассемблирований/999 инструкций совпадают между
эталонами:17 новых/874 инструкции, release-cache125 инструкций повторно
использован из105 после проверки полноты и hashes. Отдельно закреплены
55 байт общего ReleaseSystemTexture tail8F2DE0 и литералы/начальные capacities.
Чтение полного CEntity::LoadEntity здесь не заявляется: сохранены только
дополнительные страницы его загрузочного участка, полная функция остаётся
частью ранее закреплённого map/resource scope.

| RVA | Роль |
|---|---|
| 0x4f2d10 | R3ReleaseTextureMem |
| 0x4e08f0 | CEntity::ReleaseTexMem,managed и independent flag8 ветви |
| 0x4e09a0 | CEntity::ReleaseEntity,loaded guard и уничтожение владельцев |
| 0x3e4bc0 | ReleaseEffectEntityList: cache order и вызовы освобождения |
| 0x4f2260 / 0x4f25d0 | Регистрация R3T и отдельной DDS,общий mSameCnt |
| 0x4f33b0 / 0x4f35b0 | R3T загрузка и отдельная загрузка изображения |
| 0x4f3560 / 0x4f2cc0 | ReleaseAllTextures и освобождение обеих таблиц |
| 0x4f1160 | Warning:ignore flag,callback,точные bytes,нет MessageBox fallback |
| 0x739258 | Семь байт подписи3c2db0e6b0ed00 |
| 0x7394c4 | Исходное предупреждение R3T,36 байт+NUL |

Raw: artifacts/client455-progress/texture118-reference.json и texture118-session.json.
Собственная IDA сессия99708884 сохранена/закрыта, итоговый список0.
Входные EXE не запускались; анализ проводился по копиям work/client-reference/.
Серверы не менялись и не собирались.

## Что делает455

Если texture table отсутствует,id=-1 или surface ужеNULL — release ничего
не делает. Поиск registry record использует startID и144-байтный stride.
При ненулевом mSameCnt счётчик уменьшается, surface сохраняется. Это общий
счётчик R3T, расходуемый каждым вызовом освобождения изображения. Его нельзя
молча превратить в отдельный «правильный» refcount для каждого пакета.

Когда счётчик0, для R3T выдаётся предупреждение, затем очищается первый байт
имени, вызывается COM Release и указатель surface обнуляется. Буквальный текст
сообщения не означает, что освобождение было пропущено. Эта особенность есть
в обоих закреплённых клиентах.

В Warning обработчик получает message+context+«<-경고» в CP949. Legacy код
добавлял «<-에러» и показывал MessageBox при отсутствии callback. В455 после
проверки No_warning копируются строки; без callback функция возвращается.
При установленном callback добавляется правильная шестибайтная подпись.
Обе ветви исправлены в scripts/native/client455_warning.inc. Error/FatalError
и остальные функции исходного jerror.cpp сохранены.

## Проверка реального владельца и COM

Сценарий повторно использует реальный registry lab: настоящий MainGame owner,
архивы Nuclear,live radar/launch/impact,локализованные сообщения,Miles и мир
neutralAS1. Обычные109 проверок прошли. Наблюдатели включены только в новом
texture-lifetime probe; обычный registry probe компилируется без них.

Native work/m9/5f3f4c71/texture-lifetime-001 завершился штатно,649 проверок
наблюдения. Собственные static symbols разрешаются из собственного MAP с
учётом его preferred base и фактического ASLR base. Равенство адреса функции
проверяется до чтения таблиц. Два первоначальных диагностических запуска
ошиблись в расчёте адреса и не приняты; их журналы сохранены. Это ошибка
наблюдателя, не доказательство дефекта production cache.

Зафиксированы21 cache owner,24 вызова release по изображениям,4 расходования
shared counter,20 освобождений effect surface и20 предупреждений. Независимый
Python oracle из закреплённой семантики предсказывает все конечные records,
surface pointers и счётчики; результат побайтно/по значениям совпадает.
Каждое предупреждение имеет полный правильный byte string,а stack содержит
ReleaseEffectEntityList→CEntity::ReleaseTexMem→R3ReleaseTextureMem.

Дополнительно на настоящем multi-image R3T проверены cache-hit increment,
уменьшение счётчика первым изображением и тем же счётчиком другим изображением.
После проверки исходное состояние восстановлено до ordinary cache teardown.

Число живых managed slots:152→132 после cache release→0 после world release.
У20 effect и132 world texture объектов временно удерживалась отдельная ссылка
стенда. Для каждого проверено уменьшение на одну ссылку движка, затем последняя
ссылка стенда вернула0. После мира обе таблицы отсутствуют,counts=1/1.
Учтённый Dmalloc23092316→20842680→785169→0 после завершения UI/audio/engine.
Это подтверждение данного пути и данного счётчика;оно не доказывает весь
CRT heap,все COM/GPU ресурсы или физическое использование видеопамяти драйвером.

Три Warning проверки проходят:точные callback bytes,ignore flag и возврат без
диалога при callbackNULL.20 настоящих R3T предупреждений сохранены;они не
подавлены и не заменены успешными заглушками. Формат и отсутствие fallback
проверены также по телу Warning обычного собственного RF_Online.bin.

## Изменение движка и регрессии

Engine67:
dce960bd12d8f82257edd760ebdbc73127b1f372b01a178141028cd397b4e656.
Код изменён только в jerror.obj.65 остальных COFF members совпали побайтно;
r3text.obj отличается только тремя байтами COFF timestamp по offsets4/5/6,
его код/данные/relocations/symbols совпадают. Проверка не маскирует произвольные
различия: разрешено только поле COFF TimeDateStamp. Производная common/jerror.cpp
создана из исходника заменой только Warning. Всего67 объектов,13 derived source.

Предыдущий engine67A546a7529… сохранён точными байтами в
artifacts/client455-progress/engine-before118.lib;старый обычный PEfd8b5070…
сохранён как normal-before118.bin. Baseline033 не менялся. Отсутствующий
исторический082 snapshot этим не восстановлен и остаётся отдельным gap.

Пересобраны ordinary consumer probe/link и текущие tests:

- Registry109 + texture observations649 и независимый target oracle.
- Пять GPU кадров просмотрены:flight/impact/countdown видны;после drain и
  destructor кадры пустые. Два пустых кадра равны116;для stochastic particle
  кадров полное byte equality между запусками не заявляется.
- Map2692/330 geometry cases и точный canonical output повторно проходят
  с текущим engine. Полный BSP load здесь обеспечивает registry scenario;
  map projection regression по-прежнему использует три скопированных node fixtures.
- Startup contracts,exact own PE ранний запуск и окно/device/existingCreate1 PASS.
  Полный bootstrap/auth/игровой сеанс не принят. Старые159k,world/audio/другиеGUI
  suites не повторялись. Старые runtime gates считаются историческими.

## Что остаётся

Independent flag8 release подтверждён статически,но ещё не отдельным runtime
сценарием. Не приняты device lost/reset/reentry/shutdown/failure/OOM/invalid-ID/
concurrency/private ABI,все shadow/render-target ресурсы и все writers/owners.
Не принят опасный Warning buffer/null-input domain или incidental return value.
Далее119 — настоящий world frame/camera quake/light/compositing и оставшиеся
texture/device пути. Полные map UI/layer consumers,клиентские стадии,протокол,
инвентарь и прежние client-acceptance gaps сохраняются. M6/M6F/M7/M9 OPEN.
