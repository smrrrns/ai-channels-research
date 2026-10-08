import asyncio
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from config.settings import config, is_config_valid
from src.data_collection.telegram_client import TelegramClientManager
from src.data_collection.channel_collector import ChannelCollector

async def get_all_reactions():
    """Сохраняет список доступных реакций каждого канала в txt"""
    if not is_config_valid:
        print("Сначала настройте конфигурацию в .env")
        return

    try:
        async with TelegramClientManager(
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            session_name=config.SESSION_NAME
        ) as client:

            collector = ChannelCollector(client, config)

            for i, channel in enumerate(config.TARGET_CHANNELS, 1):
                print(f"[{i}/{len(config.TARGET_CHANNELS)}] @{channel}")

                reactions_map = await collector.get_available_reactions(channel)

                emoji_count = sum(1 for r in reactions_map.values() if r['type'] == 'emoji')
                custom_count = sum(1 for r in reactions_map.values() if r['type'] == 'custom')
                print(f"   Эмодзи: {emoji_count}, кастомные: {custom_count}")

                filename = f"available_reactions_{channel}.txt"
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(f"Доступные реакции канала: @{channel}\n")
                    f.write("=" * 50 + "\n\n")

                    for reaction_id, info in reactions_map.items():
                        if info['type'] == 'emoji':
                            f.write(f"Эмодзи: {reaction_id}\n")
                        else:
                            f.write(f"Кастомная: {reaction_id}\n")
                            if info.get('title'):
                                f.write(f"   Название: {info['title']}\n")
                            if info.get('premium'):
                                f.write("   Premium\n")
                        f.write("-" * 30 + "\n")

    except Exception as e:
        print(f"Ошибка: {e}")

def main():
    asyncio.run(get_all_reactions())
    print("Готово, по спискам можно заполнять CUSTOM_REACTIONS_MAP в config/settings.py")

if __name__ == "__main__":
    main()
