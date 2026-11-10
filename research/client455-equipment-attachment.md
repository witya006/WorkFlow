# Привязка эффектов146 к частям персонажа

Статус PARTIAL_COMPONENT. Обычная PE145 не менялась. Новые обработчики ещё
не подключены к обычному CPlayerProc; внешний вид и выбор персонажа не приняты.

## Доказательства эталона

x86/image base0x400000. Основной SHA-256
b1b5febf0d0394712e2322350e19dafe60742e8642697b93cfb89135bac1fd8b;
второй46528aac20499e3b3928d58658d7e0cefe26feba7cd193796d5cfbf7a2bbc558.
23 полные функции/1953 инструкции/223 положительных CFG-блока совпадают в обоих.
Из них21 выгружена сейчас,две7E0D10/7E22F0 переиспользованы из проверенного
equipment-effects146. Таблица переходов7E1134/68байт проверена отдельно.

RVA:3E0720 binding-name matcher,3E07B0 player part,3E09B0 NPC,
3E0B90 общий named lookup,3E0D10 тип позиции,3E22F0 запуск magic,
3DCA10 damage point,3DCCF0 actor point,3DD140 weapon point,
3F2D60 dummy initialization,6DAD0/6DB00 dummy get/set,3CDFC0 bounding box.
Подробные регионы/хеши:inventory/client455-equipment-attachment-reference.json.
Raw:artifacts/client455-progress/equipment-attachment146-reference/session.json.

## Восстановленное поведение

scripts/native/client455_effect_positions.h реализует подтверждённые providers.
Игрок/Avatar(type0/15) ищет кость по equip0..9. Сравниваются имена parent/blend
bindings части,затем используется матрица из настоящего actor part cache.
Возвращаемый индекс blend-name matcher не выбирает другую матрицу cache.
NPC поддержанных типов использует имена и матрицы собственного mesh.

Типы3/4 —руки,8/9 —Foot,а не старые Toe0. Тип17 сначала Spine,затем Spine1.
Тип18 отсутствует вswitch и оставляет позицию владельца,как0/10/прочиеdefault.
Тип1 берёт world bbox maxY. Тип7 и bbox-fallback дополнительно умножают уже
масштабированную высоту bbox на actor scale;это особенность455,не исправление.
Weapon points сохраняют mapping0/2/1/3/4/5/6/7 и fallback66%. Damage fallback72%,
а у рас0/1/3 при двух найденныхSpine/Spine1 берётся середина.

Dummy cache изначально нулевой;инициализация7F2D60 заполняет255,ищет effect1/2,
fire1..4 по первым19байтам имени с приведением регистра,last match wins.
Обновление этого cache в обычном equipment frame producer ещё не подключено.

7E22F0 сначала создаёт настоящий magic runtime,затем заменяет только translation
его матрицы. Он отличается от более широкого CAllEffectInfo attachment path.

## Проверка

Native full-object стенд использует текущие настоящие клиентские объекты/менеджеры,
25моделей тела пяти вариантов персонажа,их реальные binding pointers и actor pose
caches. Руки/ноги/позвоночник дают25определённых позиций. Для аккретия применена
настоящая ANI1090849056 изRFS. На всех пяти вариантах реальный cloak script
50006004/create_type17 создаёт magic с рассчитанной translation.

Отдельные28проверок координат сверяют заранее выбранные результаты:масштаб,
yaw90,world bounds,двойное масштабирование высоты,Spine1fallback,damage midpoint,
weapon markers,ошибки/default и различия NPC/player. Это не счётчик готовности.
Native завершился0/PASS. Стенд1694asset paths/197618821logicalbytes,
новых файлов ресурсов вsharedpool0;EXE/config/логи частные. Полный клиент не копирован.

## Открытые ограничения

При отсутствии некоторых bone/weapon/bbox данных эталон копирует неинициализированные
локальные координаты. В собственной source API это явно отмечается defined=false;
magic wrapper отклоняет такую translation. Полное соответствие этих ошибок не принято.
Переполнение binding count,некорректные указатели и ресурсные ошибки также не закрыты.
Все выбранные creation-types используют actor dummy8 илиweapon0..7.
Полный target actor dummy массив13элементов ещё не перенесён в старыйCCharacter;
его прочие пользователи не считаются принятыми этим компонентом.

Не выполнены ordinaryCPlayerProc/Avatar/registered/frame/render integration,
typed4411E0conditions,полная загрузочная цепочка/внешний вид/выбор/мир/M9.
Следующая работа —typedconditions,затем соединение providers в обычном клиенте.
Не повторять полный23function аудит без изменения доказательств.

Gate:inventory/client455-equipment-attachment-checkpoint.json.
Воспроизведение черезscripts/Invoke-Python.ps1:
audit_client455_equipment_attachment.py →probe_client455_equipment_attachment.py
→checkpoint_client455_equipment_attachment.py.
IDA5c1cdbca saved/closed/list0;native jobs завершены. InputEXE/server не тронуты.
