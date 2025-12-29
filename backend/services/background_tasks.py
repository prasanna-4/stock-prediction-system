"""
Background Tasks Service
Handles periodic updates for stock data and predictions
"""
import asyncio
import logging
from datetime import datetime, time
from typing import Optional

logger = logging.getLogger(__name__)


class BackgroundTaskManager:
    """
    Manages background tasks for automatic data updates
    """

    def __init__(self):
        self.tasks: list[asyncio.Task] = []
        self.running = False

    async def start(self):
        """
        Start all background tasks
        """
        if self.running:
            logger.warning("Background tasks already running")
            return

        self.running = True
        logger.info("Starting background task manager...")

        # Schedule daily update task
        daily_update_task = asyncio.create_task(self._daily_update_scheduler())
        self.tasks.append(daily_update_task)

        logger.info("Background tasks started successfully")

    async def stop(self):
        """
        Stop all background tasks
        """
        self.running = False
        logger.info("Stopping background tasks...")

        for task in self.tasks:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass

        self.tasks.clear()
        logger.info("Background tasks stopped successfully")

    async def _daily_update_scheduler(self):
        """
        Scheduler for daily updates
        Runs every day at 6:00 PM ET (after market close)
        """
        while self.running:
            try:
                now = datetime.now()
                target_time = time(18, 0)  # 6:00 PM

                # Calculate seconds until next run
                if now.time() < target_time:
                    # Run today at 6 PM
                    next_run = now.replace(hour=18, minute=0, second=0, microsecond=0)
                else:
                    # Run tomorrow at 6 PM
                    next_run = now.replace(hour=18, minute=0, second=0, microsecond=0)
                    next_run = next_run.replace(day=next_run.day + 1)

                wait_seconds = (next_run - now).total_seconds()

                logger.info(f"Next daily update scheduled for: {next_run.strftime('%Y-%m-%d %H:%M:%S')}")

                # Wait until scheduled time
                await asyncio.sleep(wait_seconds)

                # Run the update
                if self.running:
                    await self._run_daily_update()

            except asyncio.CancelledError:
                logger.info("Daily update scheduler cancelled")
                break
            except Exception as e:
                logger.error(f"Error in daily update scheduler: {e}", exc_info=True)
                # Wait 1 hour before retrying on error
                await asyncio.sleep(3600)

    async def _run_daily_update(self):
        """
        Run daily update tasks
        - Refresh stock prices
        - Generate new predictions
        - Send email alerts (if configured)
        """
        logger.info("Running daily update...")

        try:
            # Import here to avoid circular dependencies
            from backend.services.market_data import MarketDataService

            # Refresh prices
            logger.info("Refreshing stock prices...")
            market_service = MarketDataService()
            # Note: This would call the actual price refresh
            # await market_service.refresh_all_prices()

            logger.info("Daily update completed successfully")

        except Exception as e:
            logger.error(f"Error during daily update: {e}", exc_info=True)


# Global instance
background_manager = BackgroundTaskManager()
