_English version: [README.md](README.md)_

# AI-Crawler-Blocklist

AI-Crawler-Blocklist публикует блок-листы ИИ-краулеров и готовые к развёртыванию сниппеты для файрволов из официальных источников, публикуемых операторами. Проект разделяет верифицированные IP-диапазоны, правила user-agent, механизмы контроля robots.txt и списки наблюдения, чтобы операторы сайтов могли выбрать подходящий уровень принудительного применения (enforcement), не смешивая сигналы разного качества.



<p align="center">
  <a href="https://github.com/ipanalytics/AI-Crawler-Blocklist/actions/workflows/update.yml"><img alt="Update" src="https://img.shields.io/github/actions/workflow/status/ipanalytics/AI-Crawler-Blocklist/update.yml?branch=main&label=update"></a>
  <a href="https://github.com/ipanalytics/AI-Crawler-Blocklist/actions/workflows/validate-pr.yml"><img alt="CI" src="https://img.shields.io/github/actions/workflow/status/ipanalytics/AI-Crawler-Blocklist/validate-pr.yml?branch=main&label=ci"></a>
  <a href="https://github.com/ipanalytics/AI-Crawler-Blocklist/releases"><img alt="Release" src="https://img.shields.io/github/v/release/ipanalytics/AI-Crawler-Blocklist?display_name=tag&sort=date"></a>
  <img alt="Dataset" src="https://img.shields.io/badge/dataset-generated%20dist-2f6fed">
  <img alt="Python" src="https://img.shields.io/badge/python-3.12-3776ab">
  <img alt="License" src="https://img.shields.io/badge/license-MIT-blue">
</p>

---

## Ссылки

| Ресурс | URL |
| --- | --- |
| Сгенерированные артефакты | [`dist/`](./dist) |
| Политика источников | [`docs/source-policy.md`](./docs/source-policy.md) |
| Заметки по развёртыванию файрволов | [`docs/firewalls.md`](./docs/firewalls.md) |
| Режимы работы | [`docs/modes.md`](./docs/modes.md) |
| Отчёт о состоянии источников | [`dist/sources-report.md`](./dist/sources-report.md) |
| Метаданные в машиночитаемом формате | [`dist/metadata.json`](./dist/metadata.json) |

## Обзор

AI-Crawler-Blocklist создан для издателей, операторов приложений, инфраструктурных команд и инженеров по безопасности, которым нужны воспроизводимые механизмы контроля для краулеров обучения ИИ, поисковых ботов ИИ, загрузчиков ассистентов (assistant fetchers) и связанных систем индексации.

Репозиторий берёт подготовленные определения источников из `config/sources.json`, проверяет политику источников, загружает официальные IP-фиды там, где они доступны, нормализует CIDR и формирует платформенно-специфичные выходные файлы в `dist/`. Сбои источников фиксируются в метаданных вместо падения всей сборки, что сохраняет работоспособность запланированных обновлений, обеспечивая при этом видимость состояния источников.

## Поведение системы

```text
config/sources.json
        |
        v
scripts/normalize_sources.py  -> confidence, enforcement, source policy
        |
        v
scripts/fetch_sources.py      -> official JSON/text/embedded JSON/static prefixes
        |
        v
scripts/build.py              -> deterministic dist artifacts
        |
        v
dist/metadata.json + firewall snippets + robots.txt + plain lists
```

Уровень принудительного применения определяется качеством источника:

| Класс | Качество источника | Поведение на выходе |
| --- | --- | --- |
| `verified-drop` | Официальный фид IP/CIDR конкретного краулера | Допускается жёсткий drop по IP |
| `ua-only` | Задокументированный user-agent без верифицированного IP-фида | Только правила блокировки по user-agent |
| `robots-only` | Токен robots, такой как `Google-Extended` | Только вывод в robots.txt |
| `static-watch` | Широкие статические диапазоны, CN/watch, диапазоны платформ, слабые сигналы | Наблюдение, challenge или rate-limit |

## Возможности

- Верифицированные списки IPv4/IPv6 по официальным IP-фидам ИИ-краулеров.
- Списки user-agent, списки regex, карты nginx, правила Apache SetEnvIf и выражения Cloudflare.
- Сниппеты robots.txt для opt-out от обучения, всех ИИ-ботов, ботов CN/watch и opt-out от ИИ, безопасного для поиска.
- Выходные конфигурации для iptables/ipset, nftables, pf/pfSense, Caddy, HAProxy и Traefik.
- Детерминированные сборки с поддержкой фиксированной метки времени через `CRAWLERSCOPE_GENERATED_AT`.
- Метаданные в машиночитаемом формате с количествами, состоянием источников, уровнем доверия (confidence), уровнем принудительного применения и источниками со сбоями.
- Запланированный workflow обновления в GitHub Actions и ежедневный workflow выпуска релизов.

## Быстрый старт

```bash
git clone https://github.com/ipanalytics/AI-Crawler-Blocklist.git
cd AI-Crawler-Blocklist
make install-dev
make build
make validate
make test
```

Для изолированных (sandboxed) сред, где `uv` должен хранить всё состояние внутри рабочего дерева (worktree):

```bash
UV_CACHE_DIR=.uv-cache UV_PYTHON_INSTALL_DIR=.uv-python \
  uv run --python 3.12 python scripts/build.py
```

## Установка

Сгенерированные файлы предназначены для непосредственного использования по raw-URL GitHub либо для встраивания (vendoring) в вашу собственную систему управления конфигурацией.

```bash
curl -fsSL https://raw.githubusercontent.com/ipanalytics/AI-Crawler-Blocklist/main/dist/metadata.json
```

Для контролируемого развёртывания в production рекомендуется фиксация на теге релиза:

```bash
curl -fsSL https://github.com/ipanalytics/AI-Crawler-Blocklist/releases/latest/download/ai-crawler-blocklist-dist.tar.gz \
  -o ai-crawler-blocklist-dist.tar.gz
```

## Примеры использования

### robots.txt

```bash
curl -fsSL https://raw.githubusercontent.com/ipanalytics/AI-Crawler-Blocklist/main/dist/robots-ai-all-block.txt \
  -o /var/www/html/robots.txt
```

### nginx

```bash
curl -fsSL https://raw.githubusercontent.com/ipanalytics/AI-Crawler-Blocklist/main/dist/nginx-ai-map.conf \
  -o /etc/nginx/snippets/nginx-ai-map.conf
```

```nginx
include /etc/nginx/snippets/nginx-ai-map.conf;

server {
    if ($ai_crawler) {
        return 403;
    }
}
```

```bash
nginx -t && systemctl reload nginx
```

### Apache

```bash
curl -fsSL https://raw.githubusercontent.com/ipanalytics/AI-Crawler-Blocklist/main/dist/apache-ai-setenvif.conf \
  -o /etc/apache2/conf-available/ai-crawlers.conf

a2enconf ai-crawlers
apachectl configtest && systemctl reload apache2
```

### Cloudflare WAF

```bash
curl -fsSL https://raw.githubusercontent.com/ipanalytics/AI-Crawler-Blocklist/main/dist/cloudflare-ai-expression.txt
```

Используйте выражение в пользовательском правиле WAF (WAF Custom Rule). Результат формируется на основе UA и предназначен для проверки перед развёртыванием.

### iptables

```bash
curl -fsSL https://raw.githubusercontent.com/ipanalytics/AI-Crawler-Blocklist/main/dist/iptables-ai.sh \
  -o /usr/local/sbin/update-ai-iptables.sh

chmod +x /usr/local/sbin/update-ai-iptables.sh
/usr/local/sbin/update-ai-iptables.sh
```

Сгенерированный скрипт использует `ipset` для сопоставления на основе множеств.

### nftables

```bash
curl -fsSL https://raw.githubusercontent.com/ipanalytics/AI-Crawler-Blocklist/main/dist/nftables-ai.nft \
  -o /etc/nftables.d/ai-crawlers.nft

nft -f /etc/nftables.d/ai-crawlers.nft
```

### Caddy

```bash
curl -fsSL https://raw.githubusercontent.com/ipanalytics/AI-Crawler-Blocklist/main/dist/caddy-ai-block.caddy \
  -o /etc/caddy/snippets/ai-crawlers.caddy

caddy validate --config /etc/caddy/Caddyfile && systemctl reload caddy
```

### HAProxy

```bash
curl -fsSL https://raw.githubusercontent.com/ipanalytics/AI-Crawler-Blocklist/main/dist/haproxy-ai-acl.cfg \
  -o /etc/haproxy/ai-crawlers.cfg

haproxy -c -f /etc/haproxy/haproxy.cfg && systemctl reload haproxy
```

## Результаты

| Артефакт | Назначение |
| --- | --- |
| `dist/ai-ips-verified-v4.txt` | Проверенные официальные CIDR IPv4 |
| `dist/ai-ips-verified-v6.txt` | Проверенные официальные CIDR IPv6 |
| `dist/ai-ips-verified-all.txt` | Объединённые проверенные CIDR |
| `dist/ai-ips-high-confidence-v4.txt` | Кандидаты IPv4 для challenge/ограничения частоты запросов |
| `dist/ai-ips-high-confidence-v6.txt` | Кандидаты IPv6 для challenge/ограничения частоты запросов |
| `dist/ai-user-agents.txt` | Простые UA-токены ИИ-краулеров |
| `dist/ai-user-agents-regex.txt` | Экранированные regex-токены UA |
| `dist/ai-cn-user-agents-watch.txt` | Список CN/watch UA |
| `dist/robots-ai-all-block.txt` | Правила robots.txt для ИИ-ботов и токенов только для robots |
| `dist/cloudflare-ai-expression.txt` | Выражение WAF Cloudflare |
| `dist/metadata.json` | Состояние источников и счётчики |
| `dist/sources-report.md` | Отчёт по источникам в человекочитаемом виде |

<details>
<summary>Файлы для конкретных платформ</summary>

| Артефакт | Платформа |
| --- | --- |
| `dist/nginx-ai-map.conf` | nginx |
| `dist/nginx-ai-deny.conf` | nginx |
| `dist/apache-ai-setenvif.conf` | Apache |
| `dist/iptables-ai.sh` | iptables/ipset |
| `dist/nftables-ai.nft` | nftables |
| `dist/pf-ai-table.conf` | pf / pfSense |
| `dist/caddy-ai-block.caddy` | Caddy |
| `dist/haproxy-ai-acl.cfg` | HAProxy |
| `dist/traefik-ai-middleware.yml` | Traefik |

</details>

## Формат данных

Все сгенерированные текстовые файлы содержат заголовок с названием проекта, меткой времени генерации, исходным репозиторием, политикой и примечанием к проверке.

`dist/metadata.json` — операционный источник истины (source of truth) для текущего состояния сборки:

```json
{
  "generated_at": "2026-06-17T00:00:00Z",
  "project": "AI-Crawler-Blocklist",
  "policy": "official/operator-published sources only",
  "counts": {
    "verified_ipv4_prefixes": 2261,
    "verified_ipv6_prefixes": 1,
    "user_agent_patterns": 24,
    "robots_tokens": 26
  },
  "failed_sources": []
}
```

Определения источников находятся в `config/sources.json`. Нормализатор добавляет `confidence`, `enforcement`, `ipPolicy` и `includeInAiOutputs` во время сборки.

## Эксплуатационные замечания

- Используйте артефакты `verified-drop` для жёсткой блокировки по IP.
- Используйте файлы UA для средств контроля на уровне приложений, когда диапазоны IP недоступны.
- Используйте списки наблюдения для логирования, challenge-проверок, корректировки bot-score или ограничения частоты запросов.
- Рассматривайте `Google-Extended` и `Applebot-Extended` как средства контроля robots.txt.
- Проверяйте `dist/metadata.json` и `dist/sources-report.md` перед переносом изменений в производственную среду.

## Область охвата проекта

Проект охватывает ИИ-краулеры, ИИ-поисковых ботов, загрузчики контента ассистентов, боты для обучения/индексации и смежные с ИИ архивные источники, такие как CCBot. Универсальные поисковые краулеры, SEO-инструменты, мониторы доступности, краулеры проверки рекламы, боты социальных превью и сканеры безопасности не входят в сгенерированный набор ИИ-результатов, если только они явно не классифицированы политикой.

## Сценарии использования

- Средства управления ИИ-обходом для издателей.
- Генерация правил WAF для известных ИИ user agents.
- Списки IP для жёсткой блокировки на основе проверенных фидов официальных краулеров.
- Обогащение бот-аналитики данными из журналов доступа.
- Распространение политики в отношении краулеров в средства автоматизации инфраструктуры с контролем изменений.

## Ограничения

- Строки User-agent могут быть подделаны (spoofing).
- robots.txt зависит от того, соблюдают ли его краулеры.
- Некоторые загрузчики (fetchers) ассистентов запускаются пользователем и могут влиять на видимость продукта.
- Широкие диапазоны облачных платформ или платформ относятся к рабочим процессам observe/challenge, а не к жёсткому отбрасыванию (hard drop) по умолчанию.

## Структура каталогов

```text
.
├── config/                 # source definitions, policy, output manifest, schema
├── dist/                   # generated blocklists and platform artifacts
├── docs/                   # operator documentation
├── scripts/                # build, fetch, normalize, validate, render
├── templates/              # Jinja templates for generated configs
├── tests/                  # source policy, parsing, output, workflow tests
└── .github/workflows/      # update, PR validation, daily release
```

## Развёртывание

Рабочий процесс обновления пересобирает `dist/` каждые шесть часов и коммитит изменения, когда сгенерированные артефакты отличаются. Рабочий процесс релиза публикует ежедневный релиз, содержащий текущий архив `dist/`, а также метаданные и отчёт по источникам.

В производственных развёртываниях следует закрепляться на теге релиза или зеркалировать `dist/` через внутреннюю систему управления конфигурацией. Прямое использование raw URL подходит для простых хостов и лабораторных сред.

## Лицензия

MIT. См. [`LICENSE`](./LICENSE).

## Отказ от ответственности

Этот проект предоставляет данные для защитного контроля на сетевом и прикладном уровнях. Операторы несут ответственность за проверку влияния применения правил (enforcement) в собственной среде до блокировки трафика.
