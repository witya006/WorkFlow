# Universal Modder: установка и проверка

Установлено 04.11.2026 из https://github.com/rehan-remade/universal-modder,
ревизия `9811709d950979f1b5012dddf10b7ec122d7e95e`.

## Состав

Все 13 навыков установлены в `C:\Users\Admin\.codex\skills`:
asset-pipeline, blitz3d-decomp, fal-assets, game-automation, game-recon,
game-research-websearch, mashup-mods, mod-any-game, port-a-mod, publish-mod,
reverse-engineering, share-field-notes, showcase-video.

Основная точка входа: `$mod-any-game`. Для узких задач — `$game-recon` или
`$reverse-engineering`. Навыки доступны для выбора со следующего сообщения.

CLI: `C:\Users\Admin\.local\bin\um.exe`, версия 0.2.0; обнаруживается в PATH.
Установлен через uv tool install --editable с Python 3.11.16. Источник:
`local/universal-modder-install/universal-modder-9811709d950979f1b5012dddf10b7ec122d7e95e`.
Не удалять эту копию: CLI импортирует из неё код и находит локальную knowledge/.
Зависимости и хеши записаны в `inventory/universal-modder-installation.json`.

Использован штатный skill-installer с закреплённой ревизией. Полный плагин,
его хуки и fal MCP не устанавливались: пользователь запросил навыки.
CLI установлен как необходимый вспомогательный инструмент этих навыков.

## Исправление совместимости

В исходном game-recon описание содержало `<game>`, отвергаемый quick_validate.py.
Только в YAML description заменён этот placeholder на `this game`.
Все инструкции в теле сохранены. Остальные файлы побайтово сверены с источником.
Все 13 SKILL.md прошли официальный локальный валидатор Codex.

## Реальные проверки

- `um --version` и `um --help` — успешно; загружаются группы CLI и зависимости.
- `um kb search "RF Online" --json` и поиск `native` — база читается локально.
- `um scan "E:\RFOnlineTrash\RFOnline" --json` — 30 311 файлов, без запуска игры.
- Нативные вызовы IDA MCP отдельно подтвердили 669 функций и декомпиляцию.

Сканер не определил R3Engine по имени. Его unknown native engine не опровергает
наличие R3Engine в исходниках. Основной RF_Online.bin не вошёл в список его EXE.
Признаки GameGuard и ASI loader — автоматические результаты; наличие .asi может
относиться к аудио-библиотекам, поэтому мод-загрузчик таким отчётом не подтверждён.
Поиск по словам RF Online даёт и Red Faction — совпадение слов не доказательство.

Генерация ассетов через внешние сервисы, управление игрой, видео и 3D не проверялись.
fal/Sprixen/Voidless требуют отдельного подключения; ffmpeg и Blender не найдены
в проверенном PATH. Это не мешает чтению файлов, базе знаний и навыкам исследования.

Повторная локальная проверка:

```powershell
& 'C:\Users\Admin\AppData\Roaming\uv\tools\universal-modder\Scripts\python.exe' -X utf8 .\scripts\verify_universal_modder.py
```

Добавить `--scan`, чтобы заново выполнить сканирование RFOnline. Без него проверяются
установленные файлы, метаданные, запуск CLI, поиск базы знаний и сохранённый отчёт.

Результаты: inventory/universal-modder-installation.json, universal-modder-rf-scan.json,
universal-modder-kb-rf.json и universal-modder-kb-native.json. Полный сценарий создания
мода в игре не выполнялся и установочной проверкой не считается подтверждённым.
