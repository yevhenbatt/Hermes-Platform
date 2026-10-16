# SwarmClaw private adapter

Этот каталог содержит воспроизводимый overlay для отдельной исходной копии
SwarmClaw на VPS. Он не является пятым Git-репозиторием и не содержит OAuth-
токенов, service key или пользовательских данных.

## Назначение

- Добавляет закрытый маршрут `POST /api/internal/hermes/executions`.
- Принимает запросы только с `X-Hermes-Service-Key`.
- Создаёт задачу через стандартную очередь SwarmClaw.
- Создаёт отдельного технического агента для каждой пары `codex` +
  `providerConnectionId`.
- Изолирует профиль Codex в
  `HERMES_OAUTH_PROFILE_ROOT/codex/<providerConnectionId>`.

## Граница ответственности

Gateway до вызова маршрута проверяет JWT пользователя, организацию, workspace,
ACL и право использовать переданное подключение. SwarmClaw не получает OAuth-
токены и не реализует пользовательские ACL.

## Безопасность

- Идентификатор подключения должен быть UUID; он не может сформировать путь за
  пределами профиля OAuth.
- Нельзя использовать общий `CODEX_HOME` для Hermes-подключений.
- OAuth-вход выполняется отдельно для каждого подключения и никогда не
  передаётся через Gateway.
- Патч пока не применён на VPS. Его применение, сборка и перезапуск выполняются
  пользователем `batt` отдельной контролируемой процедурой.

## Состав patch-set

Patch-set добавляет:

1. Проверку service key с `timingSafeEqual`.
2. Безопасное вычисление профиля OAuth по `providerConnectionId`.
3. Внутренний маршрут создания, чтения и отмены выполнения.
4. Использование изолированного профиля в Codex CLI.
`0002-hermes-private-adapter-tests-and-stop-route.patch` добавляет unit-тесты
для проверки key и профиля, а также сохраняет совместимость с существующим
маршрутом отмены `/executions/:id/stop`.

`0003-install-codex-cli.patch` закрепляет CLI `@openai/codex@0.159.3` в
runtime-образе. Он нужен для OAuth-входа и запуска задач, но не добавляет
модельные API-ключи.

`0004-hermes-private-proxy-auth.patch` исправляет блокировку service key общим
`ACCESS_KEY` proxy. Только существующие execution-маршруты и методы используют
собственную проверку `HERMES_SWARMCLAW_SERVICE_KEY`; без ключа запрос отклоняется,
без настроенного ключа возвращается 503. Остальные API сохраняют прежнюю защиту.
Проверка ключа внутри обработчиков также остаётся включённой.

После применения четвёртого patch запустите тесты на исходниках SwarmClaw:

```bash
node --import tsx --test src/lib/server/hermes-private-auth.test.ts \
  src/lib/server/hermes-provider-profile.test.ts \
  src/lib/server/hermes-private-proxy.test.ts src/proxy.test.ts
```

Затем пересоберите и пересоздайте только контейнер SwarmClaw. Проверка из Gateway
с пустым телом запроса должна вернуть 401 без service key и 400 с верным ключом.

`0005-english-test-descriptions.patch` translates the six proxy regression test
names and the authentication comment into English. Apply it after `0004`.
It does not change runtime behavior or test assertions. Run the same test command
above after applying it.

`0006-codex-execution-failures.patch` removes the unsupported hardcoded model
from Hermes Codex agents. A private marker tells the CLI adapter to omit `-m`
and use the installed CLI/profile default. Existing Hermes agents with the old
`gpt-5.4-codex` default are migrated when a new execution is created. Explicit
model overrides are still passed to the CLI; this does not add a Desktop model
selector or a model catalog API.

The patch rejects CLI process failures and structured provider errors, and
prevents errored queue runs from passing completion validation. New private
executions have one attempt so a rejected model does not trigger automatic
repeated runs. Codex warning/error diagnostics are mirrored to Docker stderr
with configured secrets, bearer tokens and structured OAuth tokens redacted.
Existing file logging remains available.

Apply after patches 0001–0005. Run the existing tests plus:

```bash
node --import tsx --test src/lib/providers/codex-execution-policy.test.ts
```

Rebuild and recreate SwarmClaw once, then create a new Gateway smoke-test task.
The earlier task `65d7eb52-3496-412d-8431-95c7ed524427` remains a historical false
success; the patch does not rewrite its stored status. A successful OAuth login
or catalog entry does not prove access to a particular model: verify the actual
inference result.
