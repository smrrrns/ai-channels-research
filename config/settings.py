import os
from dotenv import load_dotenv
from src.utils.validators import ConfigValidator

load_dotenv()

class Config:
    """Настройки из .env"""

    API_ID = os.getenv('API_ID')
    API_HASH = os.getenv('API_HASH')

    SESSION_NAME = os.getenv('SESSION_NAME')
    DEFAULT_POSTS_LIMIT = int(os.getenv('DEFAULT_POSTS_LIMIT'))
    REQUEST_DELAY = int(os.getenv('REQUEST_DELAY'))
    MAX_RETRIES = int(os.getenv('MAX_RETRIES'))
    LOG_LEVEL = os.getenv('LOG_LEVEL')

    TARGET_CHANNELS = []
    for i in range(1, 11):
        channel = os.getenv(f'CHANNEL_{i}')
        if channel and channel.strip():
            TARGET_CHANNELS.append(channel.strip())

    CUSTOM_REACTIONS_MAP = {
        'global': {},
        'by_channel': {
            'ict_moscow_ai': {
                '5217962652742996135': '❤️', # лампа
                '5289509472090220232': '❤️', # ICT
                '5445042860787252192': '❤️', # ICT

            },
            'd_code': {
                '5348351516182857544': '❤️', # аниме девочка
                '5350663853560581569': '❤️', # йода

            },
            'DSCSproAI': {
                '5436189026224728788': '🎉',
                '5438237047020088735': '🤖', # ai
                '5357314052072692864': '🤖', # ai
                '5235807206770750407': '😎', # кот в очках
                '5458801195814508191': '🤩', # кот с компьтером
                '5435931719028997627': '🩷',
                '5368748388885999718': '🩷', # top
                '4960832663062578456': '🩷', # сердечко
                '5307602562990492983': '🔥',
                '5472411062412254753': '🧑‍🎓',
                '5435968389459767071': '🔥',
                '5436383132976702162': '⭐',
                '5438544137181752811': '⚡',
                '4961156112754672853': '⚡',
                '5323772371830588991': '🫡',
                '5361918153934791430': '🩷', # снежинка
                '5424815192615706042': '🩷', # новогодние коты
                '5818845400840277279': '👀',
                '4961121357879313223': '🩷',
                '6032706485526465658': '🩷',
                '5235826817591420001': '👨‍💻',
                '5395732581780040886': '🤝',

            },
            'seeallochnaya': {
                '5355083340548419513': '🥹', # котик улыбается
                '5248951709367017473': '🚫', # парень перечеркнут красным крестом
            },
            'spbuniversity1724': {
                '5422748398518301870': '❤️', # спбгу
                '5420436396148027032': '❤️', # сердечко
                '5411468637577965032': '❤️', # спбгу
                '5307926626862909975': '❤️', # вау!
                '5388584785536904914': '❤️',
                '5388802501724092155': '❤️', # флаг россии
            },
            'naebnet': {
                '5235478122081560535': '👍',
            }
        }
    }

    @classmethod
    def get_reaction_name(cls, channel_username, reaction_id):
        """Имя реакции: сначала по каналу, потом глобальное, иначе unknown"""
        channel_map = cls.CUSTOM_REACTIONS_MAP['by_channel'].get(channel_username, {})
        if reaction_id in channel_map:
            return channel_map[reaction_id]

        if reaction_id in cls.CUSTOM_REACTIONS_MAP['global']:
            return cls.CUSTOM_REACTIONS_MAP['global'][reaction_id]

        return f"unknown_{reaction_id}"

    @classmethod
    def get_all_known_reactions(cls):
        """Все известные реакции из карты"""
        all_reactions = set(cls.CUSTOM_REACTIONS_MAP['global'].values())
        for channel_map in cls.CUSTOM_REACTIONS_MAP['by_channel'].values():
            all_reactions.update(channel_map.values())
        return sorted(list(all_reactions))

    @classmethod
    def validate(cls):
        errors = []

        if not cls.API_ID:
            errors.append("API_ID не найден в .env файле")
        elif not cls.API_ID.isdigit():
            errors.append("API_ID должен быть числом")

        if not cls.API_HASH:
            errors.append("API_HASH не найден в .env файле")
        elif len(cls.API_HASH) != 32:
            errors.append("API_HASH должен содержать 32 символа")

        if not cls.TARGET_CHANNELS:
            errors.append("Не указаны целевые каналы (CHANNEL_1, CHANNEL_2, ...)")

        if cls.DEFAULT_POSTS_LIMIT <= 0:
            errors.append("DEFAULT_POSTS_LIMIT должен быть положительным числом")

        if cls.REQUEST_DELAY < 0:
            errors.append("REQUEST_DELAY не может быть отрицательным")

        return errors

    @classmethod
    def print_summary(cls):
        print("Сводка конфигурации:")
        print(f"   Каналов: {len(cls.TARGET_CHANNELS)}")
        for i, channel in enumerate(cls.TARGET_CHANNELS, 1):
            print(f"     {i}. @{channel}")
        print(f"   Лимит постов: {cls.DEFAULT_POSTS_LIMIT}")
        print(f"   Задержка: {cls.REQUEST_DELAY} сек")

# конфиг проверяется при импорте
def initialize_config():
    errors = Config.validate()

    if errors:
        print("Ошибки конфигурации:")
        for error in errors:
            print(f"   {error}")
        print("Проверьте файл .env в корне проекта")
        return False
    else:
        Config.print_summary()

        if Config.API_ID and Config.API_ID.isdigit():
            Config.API_ID = int(Config.API_ID)

        return True

config = Config()
is_config_valid = initialize_config()