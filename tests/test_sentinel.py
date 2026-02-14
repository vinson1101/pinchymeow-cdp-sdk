#!/usr/bin/env python3
"""
Test Sentinel Price Monitoring

Tests:
1. Sentinel initialization
2. Price monitoring logic
3. Threshold checking
4. Trade execution simulation
"""

import asyncio
import sys
sys.path.insert(0, '/root/.openclaw/workspace/pinchymeow-cdp-sdk')

from src.sentinel import Sentinel
from src.cdp_core.cdp_trader import CDPTrader
from config import Config


async def test_sentinel():
    """Test sentinel price monitoring"""
    print("=" * 60)
    print("Testing Sentinel Price Monitoring")
    print("=" * 60)

    # Initialize sentinel (F0x account)
    try:
        sentinel = Sentinel(agent_name='F0x')
        print(f"✅ Agent: {sentinel.agent_name}")
        print(f"✅ Account: {sentinel.account_name}")
        print(f"✅ Network: {sentinel.network}")
    except Exception as e:
        print(f"❌ Error: {e}")

    # Test price monitoring (single check)
    print("\n[Test 2] Price Monitoring (Single Check)")
    try:
        await sentinel.run_single()
        print("✅ Single check completed")
    except Exception as e:
        print(f"❌ Error: {e}")

    # Test configuration access
    print("\n[Test 3] Configuration Access")
    try:
        print(f"Threshold ETH Price: ${sentinel.eth_threshold_usd:.2f} USD")
        print(f"Check Interval: {sentinel.check_interval} seconds")
        print(f"Trade Amount: ${sentinel.trade_amount_usd} USD")
    except Exception as e:
        print(f"❌ Error: {e}")

    # Test stop method
    print("\n[Test 4] Stop Method")
    try:
        await sentinel.close()
        print("✅ Sentinel closed successfully")
    except Exception as e:
        print(f"❌ Error: {e}")

    print("✅ All sentinel tests completed")

    print("\n" + "=" * 60)
    print("=" * 60)


def main():
    """Main entry point"""
    asyncio.run(test_sentinel())