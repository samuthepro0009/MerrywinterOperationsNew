
"""
External Uptime Monitor for FROST AI
Monitors bot health and restarts if necessary
"""

import asyncio
import aiohttp
import logging
import os
import sys
import subprocess
import time
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class UptimeMonitor:
    def __init__(self):
        self.check_interval = 300  # 5 minutes
        self.max_failures = 3
        self.failure_count = 0
        self.last_successful_check = datetime.utcnow()
        
    async def check_bot_health(self):
        """Check if bot is responding"""
        try:
            async with aiohttp.ClientSession() as session:
                # Check keep-alive server
                async with session.get('http://localhost:8080/health', timeout=10) as response:
                    if response.status == 200:
                        self.failure_count = 0
                        self.last_successful_check = datetime.utcnow()
                        logger.info("✅ Bot health check successful")
                        return True
                    else:
                        logger.warning(f"⚠️ Health check returned status {response.status}")
                        return False
        except Exception as e:
            logger.error(f"❌ Health check failed: {e}")
            return False
    
    async def restart_bot_if_needed(self):
        """Restart bot if health checks fail"""
        health_ok = await self.check_bot_health()
        
        if not health_ok:
            self.failure_count += 1
            logger.warning(f"Health check failed ({self.failure_count}/{self.max_failures})")
            
            if self.failure_count >= self.max_failures:
                logger.error("🚨 Maximum failures reached - attempting bot restart")
                try:
                    # Kill existing processes
                    subprocess.run(['pkill', '-f', 'main.py'], check=False)
                    subprocess.run(['pkill', '-f', 'keep_alive_server.py'], check=False)
                    
                    # Wait a moment
                    await asyncio.sleep(5)
                    
                    # Restart bot
                    subprocess.Popen([sys.executable, 'main.py'])
                    subprocess.Popen([sys.executable, 'keep_alive_server.py'])
                    
                    logger.info("🔄 Bot restart initiated")
                    self.failure_count = 0
                    
                except Exception as e:
                    logger.error(f"Failed to restart bot: {e}")
    
    async def run_monitor(self):
        """Main monitoring loop"""
        logger.info("🚀 Starting FROST AI uptime monitor")
        
        while True:
            try:
                await self.restart_bot_if_needed()
                await asyncio.sleep(self.check_interval)
                
            except KeyboardInterrupt:
                logger.info("Monitor stopped by user")
                break
            except Exception as e:
                logger.error(f"Monitor error: {e}")
                await asyncio.sleep(60)  # Wait before retrying

if __name__ == "__main__":
    monitor = UptimeMonitor()
    asyncio.run(monitor.run_monitor())
