# AI Channels Research

Исследование вовлеченности аудитории в русскоязычных Telegram-каналах про AI/IT: сбор постов через Telegram API, очистка данных и анализ факторов, влияющих на просмотры, репосты и реакции.

Это первая часть истории — сбор и подготовка данных. Итоговый датасет (`data/final/ai_publics_dataset.csv`) дальше используется в соседнем проекте `ai_channels_feature_engineering`, где строятся признаки текста, векторные представления и кластеризация постов по темам.

## Что внутри

- **Сборщик данных** (`src/data_collection/`) — на [Telethon](https://docs.telethon.dev/), собирает по каждому каналу посты со всеми метаданными: текст, просмотры, репосты, реакции (включая кастомные Telegram-эмодзи), опросы, ссылки, медиа.
- **Пайплайн обработки** (`notebooks/`) — объединение сырых выгрузок, очистка, приведение кастомных реакций к обычным эмодзи, разбиение на raw → interim → processed → final.
- **Итоговый датасет** (`data/final/ai_publics_dataset.csv`) — 10 479 постов из 10 каналов, 83 признака. Схема описана в [`docs/dataset_specification.md`](docs/dataset_specification.md).
- **Анализ** (`notebooks/analysis.ipynb`) — описательная статистика, динамика публикаций, корреляции метрик вовлеченности, графики в `notebooks/figures/`.

## Каналы

| Канал | Название | Подписчики | Постов |
|---|---|---:|---:|
| `d_code` | Код Дурова | 369 381 | 3 222 |
| `naebnet` | NN | 2 362 717 | 2 491 |
| `spbuniversity1724` | Что там в СПбГУ | 17 632 | 962 |
| `skoltech_daily` | Сколтех | 10 655 | 868 |
| `seeallochnaya` | Сиолошная | 69 276 | 805 |
| `ict_moscow_ai` | База знаний AI | 8 495 | 693 |
| `AI_point_of_view` | Точка машинного зрения | 2 597 | 393 |
| `DSCSproAI` | DSCS.pro | 765 | 367 |
| `Education_Yandex` | Яндекс Образование | 36 000 | 365 |
| `tbank_education` | Т-Образование | 115 068 | 313 |

Период: декабрь 2024 — декабрь 2025 (~364 дня). Подробная статистика — в [`docs/dataset_statistics.csv`](docs/dataset_statistics.csv) и [`docs/analysis_report.csv`](docs/analysis_report.csv).

## Структура проекта

```
ai_channels_research/
├── config/                # конфигурация (.env → settings.py) и карта кастомных реакций
├── src/
│   ├── data_collection/   # подключение к Telegram, сбор постов и реакций
│   ├── data_processing/   # список постов → DataFrame/CSV
│   ├── models/            # dataclasses для структур данных (ChannelInfo, PostData, ...)
│   └── utils/             # валидация конфига и очистка текста
├── data/
│   ├── channels_data/
│   │   ├── raw/           # сырая выгрузка по каждому каналу
│   │   ├── interim/       # после нормализации реакций
│   │   └── processed/     # после очистки по каналу
│   └── final/              # объединенный и очищенный датасет для анализа
├── notebooks/
│   ├── 01_data_cleaning.ipynb  # объединение + очистка → data/final/
│   ├── refactor.ipynb          # пересчет статистики по датасету
│   ├── analysis.ipynb          # итоговый анализ и графики
│   └── figures/                 # графики из analysis.ipynb
├── docs/                   # спецификация датасета, статистика, структура признаков
├── test/                   # тестовый прогон сборщика на одном канале
├── run.py                  # сбор данных по всем каналам из .env
└── get_channel_reactions.py # сбор карты доступных реакций по каналам
```

## Установка

```bash
pip install -r requirements.txt
```

Создайте файл `.env` в корне проекта по образцу:

```env
API_ID=...
API_HASH=...
SESSION_NAME=ai_research

DEFAULT_POSTS_LIMIT=500
REQUEST_DELAY=1
MAX_RETRIES=3

CHANNEL_1=channel_username_1
CHANNEL_2=channel_username_2
...

LOG_LEVEL=INFO
DATA_FOLDER=data
```

`API_ID`/`API_HASH` получаются на [my.telegram.org](https://my.telegram.org). При первом запуске Telethon попросит авторизоваться в Telegram (номер телефона + код) и сохранит сессию в файл `<SESSION_NAME>.session` — держите его вне git, это фактически ключ доступа к аккаунту.

## Использование

```bash
# Сбор постов по всем каналам из .env → data/channels_data/row/
python run.py

# Сбор карты доступных реакций по каналам → available_reactions_<channel>.txt
python get_channel_reactions.py

# Тестовый прогон на одном канале → test/data/
python test/test_telegram_client.py
```

Дальше данные проходят через ноутбуки в `notebooks/` в порядке: `01_data_cleaning.ipynb` → `refactor.ipynb` → `analysis.ipynb`.