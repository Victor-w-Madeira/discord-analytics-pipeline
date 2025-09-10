import asyncio
import logging
from bot import DiscordAnalyticsBot
from config.settings import BOT_TOKEN

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

async def main():
    """Main entry point for the Discord Analytics Bot."""
    try:
        bot = DiscordAnalyticsBot()
        await bot.start(BOT_TOKEN)
    except KeyboardInterrupt:
        logger.info("Bot shutdown requested by user")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
    finally:
        await bot.close()

if __name__ == "__main__":
    asyncio.run(main())