import asyncio
import os
from bot import DiscordAnalyticsBot
from config.settings import BOT_TOKEN
from config.logging_config import setup_logging, BotLogger

async def main():
    """Main entry point for the Discord Analytics Bot."""
    
    # Setup logging first
    log_level = os.getenv('LOG_LEVEL', 'INFO')
    use_colors = os.getenv('LOG_COLORS', 'true').lower() == 'true'
    setup_logging(level=log_level, use_colors=use_colors)
    
    # Create main logger
    logger = BotLogger(__name__)
    
    try:
        logger.logger.info("🚀 Starting Discord Analytics Bot...")
        
        bot = DiscordAnalyticsBot()
        await bot.start(BOT_TOKEN)
        
    except KeyboardInterrupt:
        logger.logger.info("🛑 Bot shutdown requested by user")
    except Exception as e:
        logger.error("start bot", e)
        raise
    finally:
        if 'bot' in locals():
            logger.logger.info("🔄 Cleaning up and shutting down...")
            await bot.close()
        logger.logger.info("👋 Discord Analytics Bot stopped")

if __name__ == "__main__":
    asyncio.run(main())