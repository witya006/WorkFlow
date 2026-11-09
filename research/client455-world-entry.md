# 139: реальный клиентский запрос/ответ входа455

2026-11-10. **PARTIAL M6**. Gate: `inventory/client455-world-entry-checkpoint.json`.
Команда: `scripts/Invoke-Python.ps1 scripts/checkpoint_client455_world_entry.py`.
Это перенос двух сообщений и их состояния, не приёмка авторизации или выбора персонажа.

## Подтверждённый455протокол

Primary x86/base400000 SHA256
`b1b5febf0d0394712e2322350e19dafe60742e8642697b93cfb89135bac1fd8b`;
secondary `46528aac20499e3b3928d58658d7e0cefe26feba7cd193796d5cfbf7a2bbc558`.
Восемь полных функций/1372инструкции/225положительных CFG-блоков, тела равны
между двумя pins. Все положительные блоки покрыты, внешних хвостов нет;
ASM страницы≤100. Raw: `artifacts/client455-progress/world-entry139-reference/session.json`.
Owned IDAe71a49ca saved/closed; idb_list count0. Входные EXE не выполнялись.

| Роль | RVA |
|---|---|
| Запрос входа | 16A840 |
| Ответ входа | 16A960 |
| Запись типа входа после callback | 16AAD0 |
| Преобразование ключей | 4ADAC0 |
| Getter/setter результата Login | 13EF80 / 13ED80 |
| Окончание ожидания ответа | 162AC0 |
| Полный основной диспетчер | 162F50 |

Исходящий group1/op1: **58байт**, вместо legacy21. AccountDWORD@0; четыре
преобразованных DWORD@4; fullscreenBYTE@20; clientVersionDWORD126455@21;
32символа signature и нуль@25. Signature — константа закреплённого бинарника,
не пользовательские учётные данные. Keymask=(k0+k2-k1-k3)*12AB34CC по модулю2^32,
затем каждый ключ XORmask. До SendNetMessage target пишет close-request flag435992=1.

Входящий group1/op2: **12байт**, вместо legacy2. ResultBYTE@0, gradeBYTE@1,
kindBYTE@2; три пары flagBYTE/indexWORD@3/4,6/7,9/10. Они выбирают варианты таблиц
cashShop/NPCShop/quest. Любой ненулевой flag включает unsigned16index, нулевой
задаёт-1. Результат, grade, responseSeen и индексы записываются также при ошибке.
Затем идёт ReceiveResponseMsg, **после него** запись kind436025. Getter результата
53EF80 читает435973; перенос связал его с existing normal Login getter.

## Изменение исходников и проверка

Добавлены читабельные inline packer/bounded decoder, типизированное состояние и
обычные методы CNetworkMgr. Реальный dispatcher проверяет размер до чтения1/2.
Own packed protocol declarations теперь58/12; исходные/server файлы не менялись.
Несоответствие остальных legacy packets не скрыто и не исправлялось перенумерацией
без переноса payload. Полные потребители bootstrap/error/UI ещё открыты.

Собственная PE
`eb84c16bd41447d4afb150d856108ea16915932cebbf4a496b49cb838c6370c8`,x86,
entryRVA16FC30,size2270208.182client/20kernels build/link0/unresolved0.
Engine137708c892e… не изменён. Header-зависимые normal objects пересобраны.

Full-object стенд использует настоящий SendNetMessage/LoadSendMsg, AES,
буферы, decode, main dispatcher и pending dialog. Ожидаемый62-byte plain frame
с искусственными account/keys сравнивается с фиксированным oracle. Проверены
fullscreenflag, длины0..11/null без мутации,24сочетания result/selector flags,
неполный пакет на границе кольца, полное продолжение, ошибка242 и успех0.
После ответа pending/dialog очищены, grade/kind/индексы сохранены. Это локальные
входные образцы; аутентифицированного peer или принятой игровой сессии не было.
Ранний отказ oracle был вызван standalone стендом: он пропускал WinMain и не
задавал g_bIsWindowed; исправлено состояние стенда, production правило не менялось.

Свежий обычный WinMain→Title→Login также проходит: `work/m9/eb84c16b/login-frame001`,
created1/loaded1,frame70/3204ms,640×500,Renderreturn/ownexit observed,no fatal.
PNGfe5073d2… просмотрен: lobby/окно ожидания, unopened panels отсутствуют.
Обычный запрос достиг loopback fixture: **67wirebytes вместо35** у138.
Fixture не отправлял RF-ответов; успешная авторизация этим не заявляется.
Component7assets иordinary43assets используют sharedpool,newpool0 в обоих.
Снимок138: `artifacts/client455-progress/before139/manifest.json`,47files.

## Следующий140

1. Перенести настоящий bootstrap5E7BE0, вызываемый53D0F0 при result0/state6,
   с правильными таблицами, локалью и тремя полученными selectors. Сейчас остаётся
   legacy consumer; успешная загрузка всех455данных не доказана.
2. Registered-character у455: request1/8 (56ADD0), reply1/9 (56AE40).
   В legacy request1/7/reply1/8. Восстановить payload, dispatcher и consumers
   вместе; не просто менять номера. Затем настоящий экран выбора персонажа.
3. Сохранить остальные требования: полная Title/movie/factory4, UI/input/focus,
   все сетевые потребители, world/gameplay/lifecycle и client-acceptance/M9.

Общая оценка остаётся около25% (20–35%); одна пара сообщений не закрывает систему
сети или весь Login. Серверная разработка не проводилась.
