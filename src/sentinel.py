#!/usr/bin/env python3
"""
Price Sentinel Script

Lightweight price monitoring script (no LLM)
Checks ETH price every 60 seconds and triggers alert when threshold is crossed.

Author: Vinson <sun1101>
Created: 2026-02-14
Version: 1.0.0
"""

import os
import sys
import argparse
import json
import asyncio
from decimal import Decimal
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from .cdp_core.cdp_trader import CDPTrader
from config import Config


class Sentinel:
    """Price sentinel for monitoring ETH price"""

    def __init__(self, agent_name='F0x'):
        """Initialize sentinel with configuration

        Args:
            agent_name: Agent name (e.g., 'F0x', 'PinchyMeow')
        """
        # Agent configuration
        self.agent_name = agent_name or os.getenv('AGENT_NAME', 'F0x')
        self.account_name = os.getenv('ACCOUNT_NAME', f'{self.agent_name.upper()}_TRADING')

        # Network configuration
        self.network = Config.NETWORK_ID

        # Trading limits (from Config)
        try:
            self.max_balance_usd = Config.TRADING_LIMITS[self.agent_name]['max_balance_usd']
            self.trade_amount_usd = Config.TRADING_LIMITS[self.agent_name]['max_single_trade_usd']
        except KeyError:
            print(f"⚠️ No trading limits defined for {self.agent_name}")
            self.max_balance_usd = 2.00
            self.trade_amount_usd = 0.50

        # Price monitoring configuration
        self.eth_threshold_usd = float(os.getenv('ETH_THRESHOLD_USD', '2000'))
        self.check_interval = int(os.getenv('CHECK_INTERVAL', '60'))  # seconds

        # Files
        self.log_file = os.path.join(Config.LOG_DIR, 'sentinel.log')
        self.trigger_file = os.path.join(Config.TRIGGER_DIR, 'sentinel-trigger.json')

        # Initialize CDP trader client
        self.client = CDPTrader(
            account_name=self.account_name,
            agent_name=self.agent_name
        )

    async def check_price(self) -> float:
        """
        Check current ETH price

        Returns:
            Current ETH price in USD
        """
        # Get quote for 1 ETH → USDC
        try:
            quote = await self.client.get_quote(
                from_token='eth',
                to_token='usdc',
                amount=1.0
            )

            # Calculate ETH price (USDC has 6 decimals)
            expected_usdc = Decimal(quote['expected_amount']) / Decimal(10**6)
            eth_price_usd = float(expected_usdc)

            return eth_price_usd

        except Exception as e:
            print(f"❌ Error getting price: {e}")
            return 0.0

    async def run_single(self) -> dict:
        """Run single price check and trigger alert if needed"""
        print(f"🔍 Checking price at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        # Check price
        eth_price_usd = await self.check_price()

        print(f"📊 ETH Price: ${eth_price_usd:.2f} USD")
        print(f"📊 Threshold: ${self.eth_threshold_usd:.2f} USD")

        if eth_price_usd < self.eth_threshold_usd:
            print(f"🚨 Price dropped below threshold! Triggering alert...")
            await self.trigger_alert(eth_price_usd)
            print(f"✅ Alert triggered successfully")
        else:
            print(f"✅ Price above threshold, no action needed")

        # Sleep before next check
        await asyncio.sleep(self.check_interval)

    async def trigger_alert(self, eth_price_usd: float) -> bool:
        """
        Trigger price alert by writing to trigger file

        Args:
            eth_price_usd: Current ETH price in USD

        Returns:
            True if alert written, False otherwise
        """
        alert = {
            'type': 'PRICE_ALERT',
            'message': f'ETH price dropped below ${self.eth_threshold_usd}: ${eth_price_usd:.2f}',
            'agent': self.agent_name,
            'account': self.account_name,
            'action': 'evaluate_trade',
            'from_token': 'eth',
            'to_token': 'usdc',
            'amount': self.trade_amount_usd,
            'eth_price_usd': eth_price_usd,
            'threshold_usd': self.eth_threshold_usd,
            'timestamp': datetime.now().isoformat()
        }

        # Write to trigger file
        with open(self.trigger_file, 'w') as f:
            json.dump(alert, f, indent=2)

        print(f"✅ Alert written to {self.trigger_file}")

        return True

    async def run_daemon(self):
        """Run sentinel in daemon mode (continuous monitoring)"""
        print(f"🔄 Starting daemon mode for {self.agent_name}")
        print(f"   Account: {self.account_name}")
        print(f"   Check Interval: {self.check_interval} seconds")
        print(f"   ETH Threshold: ${self.eth_threshold_usd:.2f}")

        while True:
            await self.run_single()

    async def close(self):
        """Close CDP client connection"""
        if self.client:
            await self.client.close()

    async def main(self):
        """Main entry point"""
        parser = argparse.ArgumentParser(
            description='Price Sentinel Script',
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog='[%(prog)s] [options]'
        )

        parser.add_argument(
            '--daemon',
            action='store_true',
            help='Run in daemon mode (continuous monitoring)'
        )

        args = parser.parse_args()

        print(f"🚀 Price Sentinel Starting")
        print(f"   Agent: {self.agent_name}")
        print(f"   Account: {self.account_name}")
        print(f"   Log File: {self.log_file}")
        print(f"   Trigger File: {self.trigger_file}")
        print(f"   Check Interval: {self.check_interval} seconds")
        print(f"   ETH Threshold: ${self.eth_threshold_usd:.2f}")

        try:
            if args.daemon:
                await self.run_daemon()
            else:
                await self.run_single()

        except KeyboardInterrupt:
            print("\n")
            print("🛑 Sentinel stopped")

        print(f"✅ Exiting normally")


async def main():
    """Wrapper for async execution"""
    try:
        await Sentinel().main()
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        import sys

    sys.exit(1)


if __name__ == '__main__':
    main()
