# M6 sprites048 — ресурсы интерфейса и следующая граница Create

Дополнение049: launcher уже перенесён передlanguage;новая проверяемая граница
после возврата существующего Create. Актуальный CLI `--after-create` заменяет
исторический `--before-launcher`. [Текущие доказательства](client455-launcher.md).

06.11.2026. Только клиент. Эталонные EXE не исполнялись, серверы не затрагивались.
Собственная сборка теперь загружает настоящие startup-спрайты455 и проходит
существующую инициализацию UI до чтения старых launcher-данных. Полный экран
входа и эквивалентность всей UI455 этим не доказаны.

## Эталон и уточнение очереди

Закреплённые x86 PE,imagebase0x400000:

- SHA256 `b1b5febf0d0394712e2322350e19dafe60742e8642697b93cfb89135bac1fd8b`;
- дополнительный `46528aac20499e3b3928d58658d7e0cefe26feba7cd193796d5cfbf7a2bbc558`.

IDA session64d5aa70 открывала work-копию IDB, закрыта/save=true.14диапазонов
одинаковы в обоих PE; точные RVA/длины/SHA находятся в
[client455-sprites-reference.json](../inventory/client455-sprites-reference.json).
Raw псевдокод и инструкции — ignored artifacts/client455-sprites/.

Проверка _CreateCharDataMgr уточнила очередь: target5E1920/RVA1E1920 лишь
выделяет180байт и вызывает ctor5FA190/Init5FA370. В этой точке нет tableIO.
Legacy создатель также только создаёт объект; LoadData вызывается позже при
входе. Поэтому предыдущая остановка «до readers» была слишком ранней. Игровые
таблицы не объявлены восстановленными и остаются обязательными позже.

Следующий реальный разрыв: CSpriteMgr использовал старые плоские пути и иной
набор IDs. Target7B0110/RVA3B0110 использует таблицу55×128bytes по
VABDB6A0/RVA7DB6A0, выбирает `./SpriteImage/<folder>/<filename>`, проверяет
`_access(path,0)` и при отсутствии возвращает `./SpriteImage/Common/<filename>`.
Существование Common повторно не проверяется. ID>=55 возвращает0.

Target IDs не равны legacy: loading2/login3/item8/unitparts19. Прямо совпадают
startup mouse0/common1; только эти два обычных UI consumer подключены сейчас.
Функция source выбора знает все55имён. Остальные legacy группы, номера,
раскладка и привязки остаются открытыми; произвольные aliases не добавлены.

## Реальный SPR и texture upload

Loader8CFB90/RVA4CFB90: float1.1,actions<16,DWORD frame count сохраняется вWORD,
24byte frame header {format,orgX,orgY,texX,texY,size}, затем rawpixels.
Native frame record20bytes. Layout/формат совпадают с существующим CSprite;
его parser пока legacy и не объявлен полностью сертифицированным455.

Четыре реальные файла разобраны и собраны обратно byte-identical:
Common/mouse50frames,Common/common522,ko-kr/common512,ru-ru/common512.
В каждом локальном common315frames используютDXT5. Старый texture helper
поддерживал толькоDXT1/ARGB32 на действующем пути и не годился для этих файлов.

Восстановлен GetDDSTexFromBuffer VA8F2E70/RVA4F2E70:

1. Проверка device и выбор размера дляDXT1,DXT5,ARGB32,R5G6B5,A1R5G5B5.
2. D3DXCreateTexture соднимуровнем/managed,LockRect,contiguous rawcopy.
3. ДляDXT1/DXT5 возврат сразу. Для несжатых — вторая managedtexture,два
   SurfaceLevel0,D3DXLoadSurfaceFromSurface/TRIANGLE и обратное копирование.
4. Проверка destinationPitch×height против опубликованногоразмера перед
   обратнойкопией,unlock/release временной texture.

Декомпилятор неверно отслеживает ESP после importedstdcall calls и смешивает
rawSrc/texture/surface variables. Порт основан на инструкциях: первая texture
в local+4,вторая+0,первые surface pointers+12/+8,LOCKRECTs+16/+24; после
второго CreateTexture дальнейшая коррекция stacklabels в псевдокоде неверна.
Compressed ветки проверены по CMP31545844/35545844 и переходам к return.
DXT3 проверяется в поздней ветке,но начальный selector его не принимает;
фиктивная поддержкаDXT3 не добавлена.

Source дополнительно проверяет first-copy размер и failedHRESULT,освобождает
ресурсы ошибок. Unsafe/OOM/error popup/allocation domains не объявлены
идентичными оригиналу. Contiguouscopy,а не новый pitch-aware алгоритм,сохранён
для подтверждённого valid-input пути.

## Сборка и настоящие потребители

Baseline033source/library сохранены. Derivedengine теперь67units/4CPP overlays,
добавлен r3d3dtex.cpp. SHA256 библиотеки:
`879f9b754d229f3570913d9256327e3ddf0231881efc793e68480d1067814cec`.
Normal182client/20kernel/16facade;0unresolved,без CharacterMR и /FORCE.
RF_Online.bin SHA256:
`d431094dfee0ceb2ba854c8dc71f2eaacdaf08909c0d57f1cffc1b8103b1fa47`,
x86/base400000,entryRVA148390,1999360bytes.

`probe_client455_sprites.py` линкует полныйnormal object set с собственным entry.
Настоящие члены g_MainApp SpriteMgr/Screen опубликованы через compiler-typed
member pointers; реальные LoadData/UnloadData вызваны через typed method
pointers. Без guessedoffset/изменения класса/дубликатов методов. Это настройка
lab,не full CMainApp.Create/WinMain.

В двух отдельных Korean/Russian labs обычный LoadData выбрал Common/mouse и
свой локальный common. Проверены все55binary-derived filenames и границы.
Повторные LoadData/LoadSprite сохранили кэш. У562frames вкаждом lab измерены
метаданные,реальные GPU texture descriptors и payload каждого texel/block
черезLockRect;байты совпали сSPR для4реально встреченныхформатов. Это проверки
автоматического nativeкода,не отдельные обращениякИИ.

Настоящий CGUIMouse::Draw и обычный CSprite commonbutton дали567изменённых
пикселей вviewport; BMP просмотрен: курсор и кнопка видимы. Это фрагмент UI,
не изображение полного экрана входа455. Остались640×500backbuffer vs480viewport.
UnloadData удалил sprites; device references вернулись кbaseline. Оба процесса
естественно exit0 после globaldestructors. Labs work/m9/315bb2d7;
[отчёт/кадры](../inventory/client455-sprites-native.json).

## Продвижение production Create

Точная новая fullPE запущена отдельно из ownlab с реальными shader/font/sprite
inputs. Она прошла Character/data-manager allocation,UI initialization,
LoadData и выделение старого title progress до чтения launcher-данных.

GetDataFromLauncher инлайнится MSVC; отсутствующий MAPsymbol не заменён
угаданным offset. `audit_client455_own_entry.py` находит uniqueownliteral
DefaultSet.tmp,декодированный PUSHадреса иследующий реальный CreateFileA IATcall.
Граница ownRVA B354A,CALL B354F. Это точка до открытия/чтения файла.
Own debugger ставит временный breakpoint,восстанавливает byte,фиксирует
Character owner/device,затем TerminateProcessE0434200. Не подменяет EAX/ветви.

Latest ui-startup002: ready1/windowed1/render32,device51DBF60 совпал сCharacter
device,ownerA614720;граница достигнута,exit наблюдён. Только first-chance
обработанные D3DX/CRT события,second-chance нет. Регистрация labfont очищена.
DefaultSet.tmp не предоставлялся и не читался. Этот остановленный запуск
нельзя выдавать за естественный exit/full455Create или законченныйlogin.
[UI startup отчёт](../inventory/client455-ui-startup-native.json).

Прежние ранние/Character/Korean/Russian/font/lifecycle сценарии,короткие
ANI/BBX/effects/shadow/clock/accounting и предыдущие кадры прошли.
15scoped checkpoints PASS/PARTIAL;большие исторические suites не повторялись.

## Продолжение

Следом049: восстановить target455launcher/bootstrap order7D04E0 и контракты
входных данных/ошибок,затем полный Create/вход. Старый GetDataFromLauncher не
проверяет CreateFile/ReadFile и читает старую schema;не исполнятьего с
отсутствующим input и не подменять auth успехом. В455 порядок nation→launcher→
language→FG_CB→clientnetwork→engine/BGM ещё требует переноса. Только offline
own fixtures дляначальных проверок;серверная разработка не нужна.

FullUI/прочиеtargetmanagers/video,resource reload/error/allSPRAPI,FT/ANSI/IME/
layout,ILevel/world,игровые таблицы,клиентская сеть и shutdown остаются открыты.
M6/M6F/M7/M9 не закрыты.

Повтор: audit_client455_sprites;prepare/build normal;buildstartupengine;
startupcontracts;normalconsumers/link;probe_client455_sprites;ownentry/startup
audit;startup/device/--create/--before-launcher;font/lifecycle;shortdependent
probes;scopedcheckpoints. ВсеPython через scripts/Invoke-Python.ps1.
