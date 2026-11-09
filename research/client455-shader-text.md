# Текстовый загрузчик шейдеров455 — участок136

2026-11-10. **PARTIAL M6**. Gate:
`inventory/client455-shader-text-checkpoint.json`.
Вместо временного отказа при отсутствии Init.r3o работает обычный Init.r3s fallback.
Полная приёмка455 остаётся открытой.

## Подтверждённые факты

Primary b1b5febf0d0394712e2322350e19dafe60742e8642697b93cfb89135bac1fd8b;
secondary46528aac20499e3b3928d58658d7e0cefe26feba7cd193796d5cfbf7a2bbc558.
x86/base400000. Семь полных функций/872инструкции/семь диапазонов совпали между
двумя455:904B60 text loader,904590 file compiler,903670 type lookup,
904080/9041E0 named bind VS/PS,903D40/903DC0 named constant tables.
Все ASM страницы<=100,unique/count/done/all positive CFG starts проверены.
RVA/SHA:inventory/client455-shader-text-reference.json.
Type tableBF8018/строки также закреплены в обеих версиях.

Raw184694chars:artifacts/client455-progress/shader-text136-reference.json;
session:shader-text136-session.json. Owned IDAe67d2585 saved/closed/list0.
Дополнительные decompile/xrefs по903E90/8CDE30/8CE0A0/8CEDC0 идругим соседям
сохранены,но не включены в число новых full ASM proofs.

## Восстановленное поведение

При отсутствии бинарного Init.r3o функция RF455_LoadSpecialShaderBinary вызывает
настоящий текстовый loader,подключённый к существующему RestoreDevice.
Не требуется отдельный вызов стенда вместо production callback.
Named bind/get-constant APIs восстановлены для следующего переноса реальных callers.

904B60 читает теги case-sensitive. `[path]` читает строку,но следующая итерация
с другим тегом снова ставит `.\\System\\Shader\\`:эта особенность сохранена.
`[fx_list]` читает толькоcount,положительного FX body в этой функции нет.
`[vs_list]`/`[ps_list]` компилируют ровно указанный файл безSHO decode/сменыextension.
Используется D3DXCompileShaderFromFileA(main,profile,flags0),затем реальный
CreateVertex/PixelShader. Успешные записи сохраняют исходное имя `.shr`.
Ошибочная программа не публикуется,последующие записи продолжают загружаться.
Полная семантика COM ownership на всех ошибках/предупреждениях не сертифицирована;
известные target quirks не исправлялись под видом эквивалентности.

`[sh_list]`:header4байта,10параметров по196,object stride1964. Если первыйID>=0,
пишутся два WORD;если отрицательный,второе число целиком становится DWORDheader.
Текстовый loader увеличивает published objectCount,в отличие от binary905220.
GetVS/GetPS сохраняют inclusive<=count иobject-indirect lookup.

Parameter record:name128/typeDWORD128/union64bytes132. Типы:
0=`n`,1=`b`,2=`i`,3=`f`,4=`v`,5=`m44`,6=`t`,7=`timer`,unknown=9.
Только1..5 читают значение иувеличивают cursor;0/6/7/9 занимают тот же slot
и не читают value. `strcpy` не очищает хвост имени,остаток предыдущего имени
сохранён и проверен. Cursor1175784 обнуляется послеobject,не отдельнымreset/init.

Сохранён исходный `while(!feof)` порядок:финальный `[sh_list]` без последующего
тега повторно обрабатывается,если после `}` есть whitespace. Новый пустойobject
получается при newline;безnewline EOF устанавливается уже при чтении последнего
токена иповтора нет. Нельзя заменять цикл на привычный `while(fscanf==1)` без
явного решения о несовместимом исправлении.

Named binding ищет exact case-sensitive name. Missing возвращает1 иоставляет
прежний shader;nullptr очищает stage ивозвращает0. Named constant table lookup
возвращает borrowed table/null. Автоматического GPU upload параметров объектов
в8C9230 нет;при восстановлении не добавлялся выдуманный upload.

## Проверка через обычного владельца

work/m9/66261fdd/shader-text-001:

- Init.r3o staging временно скрыт;обычные Invalidate/Restore выбирают Init.r3s.
  Все4программы компилируются из supplied decoded sources иGetFunction побайтно
  равен исходному binary-path результату. Это не синтетические substitute shaders.
- Проверены3смежных objects/5892bytes:10активных параметров первого объекта,
  sentinel следующего иnegative-ID header третьего;всего11значений. Все4inactive
  типа перезаписывают slot безadvance. Матрица/vector/integer/float/bool сохранены.
- Проверены named VS/PS bindings:positive/missing/case/null иполучение таблиц.
  Реальное устройство удерживает/очищает именно ожидаемые программы.
- EOF newline даёт2objects,безnewline1. Missing Init.r3s предупреждает доreset,
  сохраняя существующие таблицы. Mixed list с отсутствующим средним VS пропускает
  ошибку,загружает последующий shader ипубликует2validVS/2PS.
- Восстановлен исходный бинарный staging;обычный Restore снова даёт binary
  counts2/2/0. Handles439→439,Dmalloc623360→623360. Warnings2 — намеренные missing
  text иmissing shader;это не случайные startup diagnostics.

Тестовые SHR/Init.r3s/expected bytes сгенерированы только вwork/. Путь к ключу,
actual decoded source SHA иSHA всех fixtures закреплены. Generic native runner
получил optional prepare_run callback;по умолчанию поведение других сценариев
сохраняется. Серверы/исходная установленная игра не изменялись.

Свежая ordinary material regression:51BSPcases/layers1,2,7/seven distincttextures/
PS18/particle light/splat6DIP. Warnings0. Четыреraw+PNG побайтно равны ранее
просмотренному135;review переиспользован явно,нового просмотра не было.
135world-frame/полнаяBellato сцена остаются историческими,не fresh136.
НоваяPE:earlysound1/window/device/existingCreate1/contracts/providers PASS.

Engine5cf2c4bd34bdb13a47ceda24f093722207bd16543ee4512808a2be29893e8251.
PEd77ffe02b4d4fc6bf7a982dadeda9efb6bdbbef954ed6da7d66baa2575d274b7,
2267136bytes/entry16F0C0/WinMainB9900/afterCreateB9A74/unresolved0.
Из67engine units payload изменился толькоr3d3d8.obj. Private shader header
дополнен,но shared camera/material/particle/vertex headers неизменны;182/20
повторно не компилировались. Snapshot exact135 содержит51file:
artifacts/client455-progress/before136/manifest.json.

## Следующий137 и ограничения

Положительные writers VS12/VS13 найдены вFraction/refraction owners8CDE30/8CE0A0.
Первый копирует render target,выбирает vFraction.sho/pFraction.sho ипишет inverse-
view row4/viewport вVS12/13. Второй использует particle azirang fields иимеет
особые stack lanes,которые нельзя заменять придуманными defaults. Пока это
decompile-level исследование,не полный runtime перенос этих draw owners.
FXAA8CEDC0 использует named PS constant table дляWIDTH/HEIGHT;fullFXAA owner открыт.
903E90 меняет parameter table,имеет float→int→float quirk и не имеет прямых xrefs
в выбранном запросе;это не доказательство полного отсутствия внешних callers.

Приоритет137:полный настоящий Fraction/particle refraction pipeline иresource
capture lifecycle;затем отдельный per-BSP light owner/positive light_object.
Все retained PS6.w/unused lanes/positive binaryFX/caps/errors/OOM/overflow/CRT
parsing/badfiles/realReset/fullworld/stages/Login/auth/protocol/Character/gameplay
gaps остаются открыты. M6/M6F/M7/M9 OPEN;вся client-acceptance.md обязательна.
