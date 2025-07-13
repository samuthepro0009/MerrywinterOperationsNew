
"""
Render-Specific Uptime Monitor for FROST AI
Optimized for Render hosting environment
"""

import asyncio
import aiohttp
import logging
import os
import time
from datetime import datetime, timezone

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class RenderUptimeMonitor:
    def __init__(self):
        self.check_interval = 120  # 2 minutes for Render
        self.max_failures = 2  # Lower threshold for faster response
        self.failure_count = 0
        self.last_successful_check = datetime.utcnow()
        self.restart_attempts = 0
        self.max_restart_attempts = 3
        self.restart_cooldown = 300  # 5 minutes
        self.last_restart_attempt = None
        
    async def check_bot_health(self):
        """Check if bot is responding on Render"""
        try:
            # Check the app's own health endpoint
            app_url = os.getenv('RENDER_EXTERNAL_URL', 'http://0.0.0.0:8080')
            
            async with aiohttp.ClientSession() as session:
                # Check keep-alive server
                async with session.get(f'{app_url}/health', timeout=15) as response:
                    if response.status == 200:
                        data = await response.json()
                        bot_ready = data.get('discord_bot', {}).get('ready', False)
                        
                        if bot_ready:
                            self.failure_count = 0
                            self.last_successful_check = datetime.utcnow()
                            logger.info("✅ Bot health check successful on Render")
                            return True
                        else:
                            logger.warning("⚠️ Bot server responding but Discord bot not ready")
                            return False
                    else:
                        logger.warning(f"⚠️ Health check returned status {response.status}")
                        return False
                        
        except asyncio.TimeoutError:
            logger.error("❌ Health check timed out")
            return False
        except Exception as e:
            logger.error(f"❌ Health check failed: {e}")
            return False
    
    async def send_webhook_ping(self):
        """Send external ping to keep Render service awake"""
        try:
            webhook_url = os.getenv('RENDER_WEBHOOK_URL')
            if webhook_url:
                async with aiohttp.ClientSession() as session:
                    async with session.get(webhook_url, timeout=10) as response:
                        if response.status == 200:
                            logger.info("✅ External webhook ping successful")
                        else:
                            logger.warning(f"⚠️ Webhook ping returned status {response.status}")
        except Exception as e:
            logger.warning(f"⚠️ Webhook ping failed: {e}")
    
    async def force_restart_check(self):
        """Check if we need to force a restart"""
        now = datetime.utcnow()
        
        # Check if we're in restart cooldown
        if self.last_restart_attempt:
            time_since_restart = (now - self.last_restart_attempt).total_seconds()
            if time_since_restart < self.restart_cooldown:
                logger.info(f"🔄 Restart cooldown active ({self.restart_cooldown - time_since_restart:.0f}s remaining)")
                return False
        
        # Check if we've exceeded max restart attempts
        if self.restart_attempts >= self.max_restart_attempts:
            logger.error("🚨 Maximum restart attempts reached - manual intervention required")
            return False
            
        return True
    
    async def attempt_service_restart(self):
        """Attempt to restart the service"""
        if not await self.force_restart_check():
            return
            
        logger.error("🚨 Attempting service restart...")
        self.restart_attempts += 1
        self.last_restart_attempt = datetime.utcnow()
        
        try:
            # For Render, we'll use the webhook approach or environment restart
            restart_webhook = os.getenv('RENDER_RESTART_WEBHOOK')
            if restart_webhook:
                async with aiohttp.ClientSession() as session:
                    async with session.post(restart_webhook, timeout=30) as response:
                        if response.status in [200, 202]:
                            logger.info("✅ Restart webhook triggered successfully")
                        else:
                            logger.error(f"❌ Restart webhook failed with status {response.status}")
            else:
                logger.warning("⚠️ No restart webhook configured")
                
        except Exception as e:
            logger.error(f"❌ Service restart failed: {e}")
    
    async def run_monitor(self):
        """Main monitoring loop optimized for Render"""
        logger.info("🚀 Starting FROST AI Render uptime monitor")
        
        while True:
            try:
                # Check bot health
                health_ok = await self.check_bot_health()
                
                if not health_ok:
                    self.failure_count += 1
                    logger.warning(f"Health check failed ({self.failure_count}/{self.max_failures})")
                    
                    # Send external ping to try to wake up the service
                    await self.send_webhook_ping()
                    
                    if self.failure_count >= self.max_failures:
                        await self.attempt_service_restart()
                        self.failure_count = 0  # Reset after restart attempt
                else:
                    # Reset restart attempts on successful health check
                    if self.restart_attempts > 0:
                        logger.info("🔄 Bot recovered - resetting restart attempts")
                        self.restart_attempts = 0
                
                # Sleep before next check
                await asyncio.sleep(self.check_interval)
                
            except KeyboardInterrupt:
                logger.info("Monitor stopped by user")
                break
            except Exception as e:
                logger.error(f"Monitor error: {e}")
                await asyncio.sleep(60)  # Wait before retrying

async def main():
    """Main function"""
    monitor = RenderUptimeMonitor()
    await monitor.run_monitor()

if __name__ == "__main__":
    asyncio.run(main())
