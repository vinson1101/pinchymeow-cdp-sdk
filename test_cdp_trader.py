#!/usr/bin/env python3
"""
Test script for CDPTrader class
"""

import asyncio
import sys
from decimal import Decimal

# Add parent directory to path
sys.path.insert(0, '/root/.openclaw/workspace/pinchymeow-cdp-sdk')

from src.cdp_core.cdp_trader import CDPTrader
from config import Config

async def test_cdp_trader():
    """Test CDPTrader class functionality"""

    print("=" * 60)
    print("CDPTrader Class Test")
    print("=" * 60)

    # Initialize trader
    print("\n[1/2] Initializing CDPTrader...")
    trader = CDPTrader()
    print(f"✅ CDPTrader initialized")

    # Test addresses
    addresses = {
        'PINCHYMEOW_MAIN': '0x145177cd8f0AD7aDE30de1CF65B13f5f45E19e91',
        'F0X_TRADING': '0x398f2eE522cF90DAA0710C37e97CabbFDded50bb'
    }

    # Query balances
    print("\n[2/2] Querying balances...")
    print("-" * 60)

    for name, address in addresses.items():
        print(f"\n📍 {name} ({address})")

        balance = await trader.get_balance(address)

        if 'error' in balance:
            print(f"   ❌ Error: {balance['error']}")
        else:
            print(f"   ETH: {balance['eth_balance']:.6f} ETH")
            print(f"   USDC: ${balance['usdc_balance']:.2f} USD")

            if balance['other_tokens']:
                print(f"   Other tokens:")
                for symbol, amount in balance['other_tokens'].items():
                    print(f"      {symbol}: {amount}")

    # Close connection
    await trader.close()

    print("\n" + "=" * 60)
    print("Test completed successfully")
    print("=" * 60)

if __name__ == '__main__':
    asyncio.run(test_cdp_trader())
