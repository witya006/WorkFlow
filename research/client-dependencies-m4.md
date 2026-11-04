# M4: восстановление зависимостей и проверка CRT

2026-11-04. Оригиналы, серверные исходники и установки не изменялись. Клиент не запускался.

## JPEG закрыт как сборочная зависимость

Официальный IJG JPEG 6b: https://www.ijg.org/files/jpegsrc.v6b.tar.gz.
SHA-256 архива: 75c3ec241e9996504fe02a9ed4d12f16b74ade713972f3db9e65ce95cd27e35d.
Он закреплён в scripts/build_jpeg6b.py. Никакие upstream C-файлы не изменены;
штатный jconfig.vc скопирован в generated jconfig.h. README с лицензией сохранён.

Собран настоящий JpegLibMT.lib, 46 C-файлов, MSVC x86 /MT. Собственная native проверка
сравнила 28 значений ABI с локальными старыми заголовками (version 62, размеры типов/
структур и offsets). Два штатных JPEG — baseline testorig.jpg и progressive testprog.jpg —
декодированы самостоятельно собранным djpeg с integer DCT. Оба результата побайтово
совпали с testimg.ppm из того же архива. Это проверка зависимости, не поведения 455.
Манифест inventory/jpeg6b-build.json, исходники/бинарники ignored work/client-dependencies/jpeg6b.

## Miles и недостижимый старый dispatch

Существующая рабочая mss32.lib подключена как зависимость R3EngineClientMT. Заглушки
звука не включались. У поставленного 455 Snd/mss32.dll статически проверены x86 и все
26 фактически требуемых r3sound.obj импортов, включая stdcall stack decoration.
SHA-256 DLL/архива и RVA функций в inventory/miles-link-audit.json. DLL не загружалась;
качество/поведение звука и полная ABI совместимость не установлены.

В cnetworkmgr.cpp исходная ветка _NEW_UI_ уже передавала item_msg в NMP_ITEM и
безусловно делала break. Старый switch после #endif был недостижим, но /Od оставлял
ссылки на отсутствующие старые методы. #endif заменён на #else, закрытие перенесено
после старого switch. Живая маршрутизация не менялась, без _NEW_UI_ старый блок сохранён.
Байтовый патч и хеши входят в ledger (теперь 11 файлов).

Повтор применения идентичных патчей теперь сохраняет timestamps: проверены все
11 файлов. Генераторы CMake/Character/shim также не переписывают неизменный текст.
Это предотвращает ненужные полные перекомпиляции.

## Полная диагностика линковки

Чтобы увидеть реальные undefined symbols, отдельная diagnostic конфигурация явно
линкует неизменённый CharacterMR.lib под его настоящим именем. Только в ней отложены
default libraries CharacterR.lib, ziplibm.lib, ZipArchive_STL_M.lib, libci.lib через
адресные /NODEFAULTLIB. Это не /FORCE и не подавление unresolved errors. CheckFiles
остаётся настоящим отсутствующим символом; проверка целостности не отключалась.
В основной конфигурации такие настройки запрещены без diagnostic shim.

Остались 13 уникальных undefined symbols: три конструктора Character; шесть inline/
коротких API; std::_Xlen/_Xran; CheckFiles и SendLog. Точный список в
inventory/client-character-diagnostic.json. Старые missing audio references оказались
реальными __imp__AIL_* из mss32.lib, а не отсутствующими C++ реализациями звука.
Парсер исправлен и проверен тремя тестами, чтобы не путать unresolved symbol с
именем вызывающей функции в сообщении LNK2019.

## Подтверждённая несовместимость прямого FILE доступа

Character member_03.obj SHA-256:
d939f5e90d6ce4428cd4635c9d2e57b3253c8fbdb17a31d0cefaad45e0d729f2.
В LoadEffectFileList@EffectList инструкции +0x31 (8A 46 0C) и +0x38 (A8 10)
читают FILE+12 и проверяют EOF mask 0x10. Это COFF offsets, не runtime RVA.

scripts/probe_vc6_stdio.py собрал собственную x86 /MT программу с однобайтовой собственной
fixture. Modern feof вернул true, flags по старому смещению были 8265 (0x2049),
старый тест дал false. После ошибки записи в read-only stream flags=8273 (0x2051):
старый EOF mask совпадает с современным error bit. Исходная fixture не изменилась.

Та же проверка через системный classic msvcrt.dll вернула EOF flags=25 (0x19),
старый EOF test совпал с feof. Native DLL metadata сверены с x86 файлом SysWOW64,
а не с x64 System32, видимым 64-битному Python. Результаты и точные хеши:
inventory/vc6-stdio-probe.json. Запускались только собственные проверки; игровые
EXE/DLL не исполнялись.

Это доказывает конкретный дефект прямого использования CharacterMR с UCRT. Один
успешный classic EOF тест не доказывает общую совместимость CRT/STL. Даже будущая
успешная линковка без исправления этого дефекта не закрывает M4.

## Следующий шаг

Изолировать восемь stream API старой Character (fopen/fclose/fgets/fread/fwrite/
fscanf/fseek/ftell) и проверить их на собственных fixtures с classic FILE, либо
восстановить соответствующие загрузчики исходным кодом. Не смешивать FILE двух CRT.
Затем реальные конструкторы/inline и std helpers с проверками; CheckFiles/SendLog
восстанавливать по клиентским доказательствам, без отключения вызовов.
Не считать диагностический CharacterMR заменой готового Character SDK.

Все 180+58+46 = 284 современных объекта проверены как COFF x86 /MT;
inventory/client-mt-variant.json. M4 не завершён, M5 не начат.
