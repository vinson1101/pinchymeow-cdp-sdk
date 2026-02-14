#!/usr/bin/env python3
"""
Price Sentinel Script

Lightweight price monitoring script (no LLM).
Checks ETH price every 60 seconds and triggers alert when threshold is crossed.

Usage:
    python sentinel.py               # Run once
    python sentinel.py --daemon      # Run as daemon (continuous)

Configuration (via environment variables):
    AGENT_NAME: Agent name (default: 'F0x')
    ACCOUNT_NAME: CDP account name (default: 'F0x-trading')
    ETH_THRESHOLD_USD: ETH price threshold in USD (default: 2000)
    CHECK_INTERVAL: Check interval in seconds (default: 60)

Author: Vinson <sun1101>
Created: 2026-02-14
Version: 1.0.0
"""

import os
import sys
import time
import json
import argparse
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from cdp_core import CDPTrader
from config import Config

class PriceSentinel:
    """Price sentinel for monitoring ETH price"""

    def __init__(self):
        """Initialize sentinel with configuration from environment"""
        self.agent_name = os.getenv('AGENT_NAME', 'F0x')
        self.account_name = os.getenv('ACCOUNT_NAME', 'F0x-trading')
        self.threshold_eth_price = float(os.getenv('ETH_THRESHOLD_USD', 2000))
        self.check_interval = int(os.getenv('CHECK_INTERVAL', 60))  # seconds

        # Files
        from config import Config
        self.log_file = os.path.join(Config.LOG_DIR, 'sentinel.log')
        self.trigger_file = os.path.join(Config.LOG_DIR, 'sentinel-trigger.json')

        # Core trading module
        self.core = None

    def log(self, message: str):
        """Log message to console and file"""
        timestamp = datetime.utcnow().isoformat()
        log_message = f"[{timestamp}] {message}\n"

        # Console output
        print(message)

        # File output
        try:
            os.makedirs(os.path.dirname(self.log_file), exist_ok=True)
            with open(self.log_file, 'a') as f:
                f.write(log_message)
        except Exception as e:
            print(f"❌ 日志写入失败: {e}")

    async def check_price_and_alert(self) -> bool:
        """
        Check ETH price and write trigger file if threshold crossed

        Returns:
            True if alert triggered, False otherwise
        """
        try:
            self.log('🔍 开始价格检查...')

            # Initialize core
            if self.core is None:
                self.core = CDPTrader()

            # Get quote for 1 ETH → USDC
            quote = await self.core.get_quote(
                from_token='eth',
                to_token='usdc',
                amount=1.0
            )

            # Calculate ETH price in USD
            from decimal import Decimal
            eth_price_usd = float(Decimal(quote['expected_amount']) / 10**6)

            self.log(f'📊 ETH 当前价格: ${eth_price_usd:.2f}')

            # Check threshold
            if eth_price_usd < self.threshold_eth_price:
                # Build alert object
                alert = {
                    'type': 'PRICE_ALERT',
                    'message': f'ETH 价格跌破 ${self.threshold_eth_price}: ${eth_price_usd:.2f}',
                    'agent': self.agent_name,
                    'account': self.account_name,
                    'action': 'evaluate_trade',
                    'from_token': 'eth',
                    'to_token': 'usdc',
                    'amount': 1.0,
                    'expected_usd': eth_price_usd,
                    'threshold': self.threshold_eth_price,
                    'timestamp': datetime.utcnow().isoformat()
                }

                self.log(f'🚨 触发价格警报！')
                self.log(f'   当前: ${eth_price_usd:.2f} < 阈值: ${self.threshold_eth_price}')

                # Write trigger file
                try:
                    os.makedirs(os.path.dirname(self.trigger_file), exist_ok=True)
                    with open(self.trigger_file, 'w') as f:
                        json.dump(alert, f, indent=2)

                    self.log(f'✅ 警报已写入: {self.trigger_file}')
                    return True

                except Exception as e:
                    self.log(f'❌ 警报写入失败: {e}')
                    return False

            else:
                self.log(f'✅ 价格正常，无需触发')
                return False

        except Exception as e:
            self.log(f'❌ 价格检查失败: {e}')
            return False

    async def run_once(self):
        """Run sentinel check once"""
        self.log('🚀 哨兵脚本启动 (单次运行)')
        self.log(f'   Agent: {self.agent_name}')
        self.log(f'   Account: {self.account_name}')
        self.log(f'   ETH 阈值: ${self.threshold_eth_price}')

        await self.check_price_and_alert()

    async def run_daemon(self):
        """Run sentinel as continuous daemon"""
        self.log('🚀 哨兵脚本启动 (守护进程)')
        self.log(f'   Agent: {self.agent_name}')
        self.log(f'   Account: {self.account_name}')
        self.log(f'   检查间隔: {self.check_interval} 秒')
        self.log(f'   ETH 阈值: ${self.threshold_eth_price}')

        while True:
            await self.check_price_and_alert()

            # Sleep until next check
            self.log(f'⏳ 等待 {self.check_interval} 秒...')
            await asyncio.sleep(self.check_interval)

def main():
    """Main entry point"""
    import asyncio

    # Parse arguments
    parser = argparse.ArgumentParser(description='Price Sentinel Script')
    parser.add_argument('--daemon', action='store_true', help='Run as continuous daemon')
    args = parser.parse_args()

    # Create sentinel
    sentinel = PriceSentinel()

    # Run
    if args.daemon:
        asyncio.run(sentinel.run_daemon())
    else:
        asyncio.run(sentinel.run_once())

if __name__ == '__main__':
    main()
