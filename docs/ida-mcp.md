# IDA MCP: рабочая конфигурация

Проверено 04.11.2026, Asia/Yakutsk. IDA Pro 9.2 + Hex-Rays 9.2.

## Установка

- Постоянный Python: `C:\Users\Admin\AppData\Roaming\uv\python\cpython-3.11.16-windows-x86_64-none`.
- IDAPython привязан через `idapyswitch --force-path` к `python311.dll` этого каталога.
- MCP venv: `E:\RFOnlineTrash\Source\WorkFlow\local\ida-mcp-venv`.
- Установлен `ida-pro-mcp` 2.0.0, ревизия `c133c3853faa111a9b00ee615c013b720d0c4acd`.
- Зависимости: `idapro` 0.0.12, `tomli-w` 1.2.0. Закреплены в `config/ida-mcp-requirements.txt`.
- Настройка idalib указывает на `C:\Program Files\IDA Professional 9.2`.
- GUI-плагин установлен в `%APPDATA%\Hex-Rays\IDA Pro\plugins\ida_mcp.py`
  и соседний каталог `ida_mcp`. Основной проверенный транспорт — headless stdio.
- Codex: `C:\Users\Admin\.codex\config.toml`, секция `[mcp_servers.ida_mcp]`.
- Прочие настройки Codex сохранены без изменений. Предыдущая конфигурация сохранена
  в игнорируемом `local/ida-mcp-install/before/`; не публиковать эти резервные файлы.

Новый официальный [Hex-Rays IDA MCP](https://github.com/HexRaysSA/ida-mcp) требует
IDA 9.4+. Для имеющейся 9.2 использован совместимый
[ida-pro-mcp](https://github.com/mrexodia/ida-pro-mcp/tree/c133c3853faa111a9b00ee615c013b720d0c4acd),
заявляющий поддержку IDA 8.3+. Совместимость 9.2 дополнительно подтверждена реальными вызовами.

## Как обращаться

Команда сервера из `config/ida-mcp.toml`:

```text
E:\RFOnlineTrash\Source\WorkFlow\local\ida-mcp-venv\Scripts\python.exe -m ida_pro_mcp.idalib_supervisor --stdio
```

1. Выполнить MCP initialize и получить tools/list, использовать актуальные схемы.
2. Вызвать idb_open с полным путём к рабочей копии и mode=force_headless.
3. Взять `session.session_id` из ответа. Это значение передавать как `database`.
4. Проверить server_health, затем вызвать list_funcs и decompile.
5. Закрыть свою сессию через idb_close; save=true сохраняет базу внутри work/.

Интеграционная проверка:

```powershell
.\scripts\Invoke-Python.ps1 scripts/probe_ida_mcp.py --configured
```

Она читает команду прямо из пользовательского Codex config, открывает копию старого
LoginServerSR.exe, получает полный список функций и декомпиляцию, сохраняет базу,
закрывает сессию. Игра и серверный EXE не запускаются.

В окружении с ограниченной песочницей потребуется запуск в контексте пользователя
Admin: IDA читает пользовательские настройки и данные установки. Это ограничение
исполнения отдельно от регистрации MCP.

## Доказательства

- `inventory/ida-runtime.json`: IDAPython и Hex-Rays в idat.
- `inventory/ida-mcp-tools.json`: 66 объявленных инструментов.
- `inventory/ida-mcp-verification.json`: проверка из зарегистрированной конфигурации,
  хеш входа, все 669 функций, готовность автоанализа/Hex-Rays и полный небольшой образец.
- Образец: `sub_401E60`, VA `0x401E60`, image base `0x400000`, RVA `0x1E60`.
- `work/ida-mcp-smoke/LoginServerSR.exe.i64`: сохранённая база, исключена из Git.

Пакет имеет версию 2.0.0, а MCP serverInfo объявляет 1.0.0; это разные поля,
оба сохранены как получены. 66 инструментов обнаружены; проверены только операции
открытия, готовности, перечисления функций, декомпиляции и закрытия.

После перезапуска Codex 04.11.2026 доступны 66 нативных инструментов IDA.
Прямыми вызовами из чата проверены открытие базы, server_health, все 669 функций,
декомпиляция sub_401E60 и закрытие сессии. Отчёт:
`inventory/ida-native-verification.json`. Дополнительный перезапуск для IDA не нужен.
[Документация настройки MCP](https://learn.chatgpt.com/docs/extend/mcp?surface=cli).

## Обслуживание

Не удалять venv и Python из uv, пока они используются этой конфигурацией.
Простая повторная проверка не требует переустановки. При обновлении закреплять
ревизию и повторять проверку функций и декомпиляции до изменения рабочего подключения.
Глобальный файл Codex содержит другие настройки: при отмене убрать только секцию
ida_mcp, а не заменять весь файл старой копией поверх последующих пользовательских изменений.
