#!/usr/bin/env python3
"""
Test get_quote() implementation
"""

import asyncio
import sys
sys.path.insert(0, '/root/.openclaw/workspace/pinchymeow-cdp-sdk')

from src.cdp_core.cdp_trader import CDPTrader
from config import Config

async def test_get_quote():
    """Test get_quote for 1 ETH → USDC"""
    print("=" * 60)
    print("Testing CDPTrader.get_quote()")
    print("=" * 60)

    # Initialize trader (F0x account)
    trader = CDPTrader(
        account_name='F0X_TRADING',
        agent_name='F0x'
    )

    # Test get_quote: 1 ETH → USDC
    print("\n[1/2] Getting quote: 1 ETH → USDC...")
    quote = await trader.get_quote('eth', 'usdc', 1.0)

    print(f"\n📊 Quote Result:")
    print(f"   From: {quote['from_token']}")
    print(f"   To: {quote['to_token']}")
    print(f"   From Amount: {quote['from_amount']}")
    print(f"   Expected Amount: {quote['expected_amount']} wei")

    if 'price' in quote:
        print(f"   Price: {quote['price']}")

    if 'error' in quote:
        print(f"   Error: {quote['error']}")

    # Test get_quote: 100 USDC → ETH
    print("\n[2/2] Getting quote: 100 USDC → ETH...")
    quote2 = await trader.get_quote('usdc', 'eth', 100.0)

    print(f"\n📊 Quote Result:")
    print(f"   From: {quote2['from_token']}")
    print(f"   To: {quote2['to_token']}")
    print(f"   From Amount: {quote2['from_amount']}")
    print(f"   Expected Amount: {quote2['expected_amount']} wei")

    if 'price' in quote2:
        print(f"   Price: {quote2['price']}")

    if 'error' in quote2:
        print(f"   Error: {quote2['error']}")

    await trader.close()

    print("\n" + "=" * 60)
    print("Test completed")
    print("=" * 60)

if __name__ == '__main__':
    asyncio.run(test_get_quote())
