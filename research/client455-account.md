# Account053: начальный обмен и пакеты входа клиента455

2026-11-06. Только клиент. M6/M6F/M7/M9 открыты.

Эталон x86, image base `0x400000`, SHA-256
`b1b5febf0d0394712e2322350e19dafe60742e8642697b93cfb89135bac1fd8b`.
Backup `46528aac20499e3b3928d58658d7e0cefe26feba7cd193796d5cfbf7a2bbc558`.
26 диапазонов функций, фрагмент ini setter и11 country selectors совпали в обоих
pins. Raw decompiler/evidence только в ignored artifacts/client455-account/.
Owned IDA `f2469475` закрыта с save=true. Входные EXE не исполнялись.

Подтверждённые контракты и восстановленные исходники:

| RVA | Клиентский контракт |
|---|---|
| `0x1627e0` | Accept endpoint0 вызывает запрос group21/op12; endpoint2 сохраняет отдельный MoveinZone путь |
| `0x169cd0` / `0x169d30` | Пустой запрос; ответ3байта: BYTE+1, LE16+3 с переполнением соответствующего типа |
| `0x162e80` | Каждый байт login: BYTE(byte+delta) XOR LOWBYTE(mask); global mode2 пропускает преобразование |
| `0x169d80` | Join84: ID51/PW33; успешная постановка в очередь очищает PW33 |
| `0x169ef0` | Login342: ID51/PW33/serverType1/ticket257; преобразовать весь буфер, затем перезаписать byte84 |
| `0x16a1a0` | Login reply50: result0, LE32 account1; PW33 сохранить только при result5 |
| `0x16a220` / `0x16a2c0` | WorldList request4zero; reply result1/dataSizeLE16/data; count и записи описаны ниже |
| `0x16a4f0` / `0x16a5a0` | SelectWorld LE16, сохранить выбранный индекс; reply24: result/IP/port/keys16/неиспользуемый byte23 |
| `0x16a640` / `0x16a780` | PushClose88: ID51/PW33/zero4; reply1байт; успешная отправка очищает PW33 |
| `0x162a20` / `0x162ac0` | Pending/tick и диалог F100: ND305, color B0FFFFFF, style5; условия зависят от active process0 и mode436232 |
| `0x1f0fe0` | Setter serverType436024; инструкции RVA1F0F93 читают MASTER_SERVER/SERVER_TYPE с default0 |

Начальный seed меняет преобразование login, **не AES keys**. Существующий sender
выключает AES для group21. Direct/ticket пакеты подключены к обычным методам
CNetworkMgr; normal AnalysisServerPacket передаёт размер decoded frame новому
bounded диспетчеру account op2/4/6/8/10/11/13. Малые методы MSVC встраивает в
AnalysisServerPacket/AcceptClientCheck; native probe сохраняет прямой dispatcher
из того же cnetworkmgr.obj. Прежние глобальные max_id_len/max_pw_len не изменены:
остальные сообщения ещё требуют собственного реверса.

Только nation8 country slot256 выбирает ticket branch. В нём ID/PW пустые,
ticket помещается в offset85 с capacity257. Нулевой ticket в оригинале оставляет
неинициализированный return; собственный код возвращает false. Источник ticket
и весь Taiwan loginUI пока не восстановлены. Нативная проверка меняет входной
nation в собственном компонентном fixture; это не запуск полного Taiwan профиля.

WorldList хранит300 записей со stride72: signed char wire value расширяется в
int32, затем name64/statusBYTE/padding3. В wire после count идут valueBYTE,
nameByteCount, name bytes, statusBYTE. Name копируется с capacity из пакета,
а не64: максимум N-1 символов, N bytes обнуляются; хвост прежнего имени остаётся.
Исходный count sign-extended и затем сравнивается unsigned. Собственный parser
принимает безопасный домен0..127, name spans1..64, data<=4097; до обновления
состояния проверяет все границы. Count128+, N0/N65+, обрезанные буферы не
воспроизводят исходные memory errors. Полные UI-смыслы value/status не доказаны;
старое имя m_bIsOpen сохранено как alias для legacy UI consumer.

Pending выставляется независимо от показа окна. Показ: active[0]!=2 OR mode==4.
Закрытие при ответе: active[0]!=2 OR mode!=-1. Mode initial=-1 подтверждён Init.
Восстановлены сами условия, но ещё не все writers mode. Параметры нового GUI API
и полный интерфейс455 не выданы за эквивалентность старому GUI.

Обычная собственная RF_Online.bin: SHA-256
`a12b10f729e561f075ba67ea36b575bee9f8110434449ec40b7d161f2ae10ad1`,
x86/base400000/entry14A980,2012672bytes. Собраны182client/20kernel/22facade,
неразрешённых символов0. Engine033 и производная startup library сохранены.
Сборочный отчёт теперь пишет UTF-8 явно, в том числе при ошибках русской MSVC.

Проверены реальные send/ring/receive/decode/dispatch методы на собственных
пакетах, перенос через конец буфера, фрагментация seed, wrap arithmetic,
ID50/PW32, ticket, очистка пароля, result/account/endpoint/key поля, signed world
value, повторная загрузка имён, count127/name64 и повреждённые границы. Настоящие
GUI окна ожидания открываются/закрываются; проверены и зональные predicates.
Процесс естественно завершился0. Fixture без listener и transport workers;
accepted flag задаётся только на границе компонентной проверки. Это не
доказательство реального сетевого accept или аутентификации.

Отдельные регрессии проверяют настоящий TCP на endpoint1/zero RF responses,
AES/кольца и собственный WinMain до D3D/существующего Create=1. Это остановка
перед игровым циклом. Russian argv по-прежнему останавливается до Connect;
endpoint0/1 gap не замаскирован. Большие прежние математические наборы не
повторялись для неизменённых алгоритмов.

Открыто: вызов MASTER_SERVER ini provider, runtime global mode2 и replay routing,
другие writers seed (в частности56BEA0),35handlers/country constructors,
настоящий вход, UI и notify11 localized/quit sideeffects (пока legacy с
проверкой2байт), прочий протокол, мир/игровые действия/IME/полный shutdown.
Никаких серверных изменений, реализации сервера или фиктивного входа нет.

Все20 текущих scoped checkpoint scripts завершились0/PARTIAL; PARTIAL сохраняет
открытые области, перечисленные выше. Это20групп доказательств, не процент
восстановления и не приёмка всего клиента.

Доказательства: inventory/client455-account-{reference,native,checkpoint}.json.
Воспроизведение: audit_client455_account.py, prepare/build normal,
probe_client455_normal_consumers.py, link_client455_normal.py,
audit_client455_own_entry.py, audit_client455_startup.py, собственные startup
пробы, probe_client455_account.py и checkpoint_client455_account.py через
scripts/Invoke-Python.ps1. После изменения binary повторять только затронутые
компоненты и короткие связанные регрессии.
