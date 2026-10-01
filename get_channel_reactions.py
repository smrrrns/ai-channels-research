import asyncio
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from config.settings import config, is_config_valid
from src.data_collection.telegram_client import TelegramClientManager
from src.data_collection.channel_collector import ChannelCollector

async def get_all_reactions():
    """Получение ВСЕХ доступных реакций каналов"""
    print("🔍 Получаем доступные реакции каналов...")

    if not is_config_valid:
        print("❌ Сначала настройте конфигурацию в .env")
        return

    try:
        async with TelegramClientManager(
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            session_name=config.SESSION_NAME
        ) as client:

            collector = ChannelCollector(client, config)
            all_reactions = {}

            for i, channel in enumerate(config.TARGET_CHANNELS, 1):
                print(f"\n🎯 [{i}/{len(config.TARGET_CHANNELS)}] Получаем реакции @{channel}")

                # Получаем ВСЕ доступные реакции канала
                reactions_map = await collector.get_available_reactions(channel)

                print(f"📊 Доступно реакций: {len(reactions_map)}")

                # Сохраняем для общего отчета
                all_reactions[channel] = reactions_map

                # Выводим детали
                emoji_count = sum(1 for r in reactions_map.values() if r['type'] == 'emoji')
                custom_count = sum(1 for r in reactions_map.values() if r['type'] == 'custom')

                print(f"   🔸 Эмодзи: {emoji_count}")
                print(f"   🔹 Кастомные: {custom_count}")

                # Сохраняем в файл
                filename = f"available_reactions_{channel}.txt"
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(f"ДОСТУПНЫЕ РЕАКЦИИ КАНАЛА: @{channel}\n")
                    f.write("=" * 50 + "\n\n")

                    for reaction_id, info in reactions_map.items():
                        if info['type'] == 'emoji':
                            f.write(f"ЭМОДЗИ: {reaction_id}\n")
                        else:
                            f.write(f"КАСТОМНАЯ: {reaction_id}\n")
                            if info.get('title'):
                                f.write(f"   Название: {info['title']}\n")
                            if info.get('premium'):
                                f.write(f"   ⭐ Premium\n")
                        f.write("-" * 30 + "\n")

                print(f"💾 Сохранено в {filename}")

            # Создаем общий отчет
            print(f"\n📈 ОБЩИЙ ОТЧЕТ:")
            total_emoji = 0
            total_custom = 0

            for channel, reactions in all_reactions.items():
                emoji = sum(1 for r in reactions.values() if r['type'] == 'emoji')
                custom = sum(1 for r in reactions.values() if r['type'] == 'custom')
                total_emoji += emoji
                total_custom += custom
                print(f"   @{channel}: {emoji} эмодзи, {custom} кастомных")

            print(f"   ВСЕГО: {total_emoji} эмодзи, {total_custom} кастомных")

    except Exception as e:
        print(f"❌ Ошибка: {e}")

def main():
    print("🎭 ПОЛУЧЕНИЕ ДОСТУПНЫХ РЕАКЦИЙ КАНАЛОВ")
    print("=" * 50)

    asyncio.run(get_all_reactions())

    print("\n" + "=" * 50)
    print("✅ Готово! Теперь у вас есть полный список ВСЕХ возможных реакций!")
    print("   Можно заполнять CUSTOM_REACTIONS_MAP в config/settings.py")

if __name__ == "__main__":
    main()
