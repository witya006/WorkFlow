# Блокировка предмета: зависимость игровых обработчиков, работа100

2026-11-07. В обычные CGUIItem/CBoardObject/CLinkBoard перенесён значок
блокировки по flag21. Это необходимая часть дальнейшего перетаскивания.
Полные обработчики использования/перестановки/удаления, hover manager и
финальная приёмка455 остаются открытыми.

Текущая проверка: `scripts/checkpoint_client455_item_lock.py`.
Отчёт: `inventory/client455-item-lock-checkpoint.json`, статус PARTIAL.
Предыдущая099 runtime-проверка теперь историческая; её статические доказательства
и просмотренные кадры сохраняются.

## Доказательства по455

Основной binary SHA-256:
`b1b5febf0d0394712e2322350e19dafe60742e8642697b93cfb89135bac1fd8b`.
Второй:
`46528aac20499e3b3928d58658d7e0cefe26feba7cd193796d5cfbf7a2bbc558`.
Оба x86, image base0x400000. Ниже указаны RVA.

17 полных функций/1610 инструкций и17 диапазонов совпадают в обоих binaries:

- `0x21d120` — raw BYTE visibility и позиция значка;
- `0x6bcf0/0x62d20` — wrapper refresh и чтение item flag21;
- `0x21aa10/0x21af30` — копирование и настройка ресурсов;
- `0x21b240/0x21b450` — различия SetPos и SetSize;
- `0x21b6b0/0x21b910` — обычная и clipped отрисовка;
- `0x21a3e0/0x21bb80` — конструктор и Empty;
- `0x226060/0x226140/0x226180/0x226230` — назначение sprite descriptor,
  автоматический размер и чтение исходных размеров;
- `0x4d1020/0x4d1080` — подтверждённые getter original width/height у CSprite.

Assembly/decompilation/canonical ranges сохранены в ignored
`artifacts/client455-progress/item-lock100-reference.json`. IDA session5eef459d
сохранена и закрыта; последующая проверка вернула sessions count0.

Реальный ресурс — target ID52, `SpriteImage/Common/ItemLock.spr`, action0/frame0.
Он содержит один DXT1 frame: original8×12, texture8×16. Файл разобран с проверкой
размеров и точным round trip; input SHA закреплён в reference manifest.
Оригинальные EXE не исполнялись; изменения только в собственных клиентских копиях.
Серверные исходники/оригинальные установки не менялись, новых установок нет.

## Реализация

CGUIItem содержит собственный CGUIObject для замка. Конструктор скрывает его.
ConfigureLock455 назначает реальный ресурс52. Legacy SetSpriteInfo только
копирует pointer/action/frame, а target дополнительно задаёт original dimensions
при включённом resize. Поэтому BindLock455 отдельно воспроизводит этот шаг;
глобальная legacy GUI-база этим переносом не заменялась.

SetLock455 принимает BYTE и сохраняет его raw visibility. Позиция всегда
пересчитывается: `x+iconWidth-glyphWidth-3,y+3`, в том числе при hidden значке.
SetPos обновляет её; SetSize сам по себе этого не делает. Для координат setter
используется определённая DWORD арифметика с wrap.

SetData копирует sprite descriptor и Show, получает размер из реального
ресурса, затем повторно применяет позицию destination. Empty и Remove сохраняют
состояние lock child, но пустая иконка больше не рисует его: ранний выход при
отсутствующем изображении остаётся. Полное копирование остальных GUIItem children
этим результатом не подтверждено.

В обеих ветвях Draw значок рисуется после таймера/его подписи. Clipped item
преднамеренно вызывает у замка обычный Draw, даже если image отвергнут своим
clip rectangle. Прежний ранний выход при неуспехе image Draw убран: он мешал
этому поведению455. IsShow и отсутствие image по-прежнему проверяются раньше.
Это восстановление поведения, а не исправление графики на другой дизайн.

CBoardObject.RefreshLock455 проверяет настоящий payload и icon, нормализует
ненулевой flag21 в1 и вызывает SetLock455. При null payload или icon состояние
не меняется. Обычный CLinkBoard.Add вызывает refresh после передачи своей иконки.
Прежний отказ для flag21 удалён после реализации; остальные три отказа
(live SF callback, live Animus callback, potion cache) сохранены.

## Проверка

Собственный native probe использует текущие ordinary client objects, настоящий
EDF payload, CGUIInventoryBoard, clone и CLinkBoard.Add/Remove/registry:

- 256 BYTE значений setter и256 значений wrapper flag21;
- 18 сочетаний позиции/размера, отдельное изменение Size и повторный setter;
- actual sprite binding, copy descriptor/raw Show, destination positioning;
- null payload, Empty, Remove и освобождение последнего shared owner;
- шесть просмотренных GPU кадров: off/on/partial clip/outside clip/empty/removed.

В кадрах действительно видны исходная иконка, её копия и owned Linker icon.
Замки рисуются в верхнем правом углу; clipped case сохраняет отдельный замок.
Локальные иконки явно показаны лабораторией. Это не запуск полного inventory
или normal game UI. Synthetic SF UI не принимается этой проверкой.

Восстановлены35 прежних raw кадров: ready6, timer6, window8, owners3, metadata3,
icon9. Они побайтно равны прежним просмотренным. Новый checkpoint связывает
current reports с сохранёнными099/098 review baselines; повторный просмотр
одинаковых пикселей не заявлен как новая работа. Дальние world/audio/159k/
atlas093/2013owner/SF1447/manual095 suites не повторялись.

Hotbar7 packets, storage3, account и точная новая PE/Create1 проходят. Сборка:
182 client/20 kernels/56 facade TU,0 unresolved. PE SHA-256
`49882fc3ef2ba826495dfbdff675a4ef30fa99dcced4557f50222d11fd306083`,
2140160 bytes,x86,base0x400000,entry0x157aa0,WinMain0xb7610,
afterCreate0xb777a. Create1 проверен с offline launcher fixture, до игрового
цикла; это не полная загрузка455 или authentication.

Derived engine остаётся
`546a7529b51139e856b1a108fcad7849c14b2d00563b7abbfdcc8db10026fa5a`.
Engine033/source сохранены. История замены082 derived library описана в099;
отдельного snapshot старой082lib по-прежнему нет.

## Следующая зависимость и ограничения

Перед actual UI drag нужно перенести CBoardManager hover ownership и CGUIScreen
catched item. Разведка сохранена в ignored
`artifacts/client455-progress/hover100-full-exploration.json` с180 инструкциями
SetHoverObject и дополнительными decomp bodies. Это ещё не полный pinned audit
всего менеджера и не реализация.

Assembly SetHoverObject RVA0xfe020 показывает hover pointer+244, backup+248 и
отдельный backup+252. Очистка hover сначала копирует его в первый backup,
затем очищает второй, освобождает hover и убирает экранную иконку. Это отличается
от одного legacy CBoardItem backup. Конкретные object lifetimes, cancel operation
для avatar states2/6/10, screen PickingObjectEvent и их зависимости ещё требуют
canonical assembly/pin и переноса; не заменять их успешными no-op.

Следом101: typed hover manager/screen, затем actual use/remove/swap/hover/MsgProc,
live inventory/equip/SF/Animus callbacks, Avatar potion cache, Macro35/Vending27,
fullCItemBoard.Add и normal table bootstrap. Lock child готов в выбранном
домене; generic animation, другие GUIItem children/shake, полные lifecycle/
deviceReset/privateABI/FPnumeric/unsafe/OOM/concurrency/shutdown не приняты.
Все прежние SF/Quest/36boards/Trunk/protocol/Tutorial/QBI/fourstage/Login/auth/
game gaps сохраняются. M6/M6F/M7/M9 OPEN, общей доли восстановления клиента нет.
