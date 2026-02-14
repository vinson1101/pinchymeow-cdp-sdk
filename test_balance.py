#!/usr/bin/env python3
"""
Test script for CDP balance query
Tests API key configuration and balance retrieval
"""

import asyncio
import os
import sys
from decimal import Decimal

# Add parent directory to path
sys.path.insert(0, '/root/.openclaw/workspace/pinchymeow-cdp-sdk')

from dotenv import load_dotenv
from cdp import CdpClient
from config import Config

# Load environment
load_dotenv('/root/.openclaw/workspace/.env.cdp')

async def test_balance_query():
    """Test balance query for PinchyMeow addresses"""

    print("=" * 60)
    print("CDP SDK Balance Query Test")
    print("=" * 60)

    # 1. Validate configuration
    print("\n[1/4] Validating configuration...")
    try:
        Config.validate()
    except ValueError as e:
        print(f"❌ Configuration error: {e}")
        return

    # 2. Initialize CDP client
    print("\n[2/4] Initializing CDP client...")
    try:
        client = CdpClient(
            api_key_id=Config.CDP_API_KEY_ID,
            api_key_secret=Config.CDP_API_KEY_SECRET
        )
        print(f"✅ CDP client initialized")
        print(f"   Network: {Config.NETWORK_ID}")
    except Exception as e:
        print(f"❌ Failed to initialize CDP client: {e}")
        return

    # 3. Define test addresses
    print("\n[3/4] Test addresses:")
    addresses = {
        'PINCHYMEOW_MAIN': '0x145177cd8f0AD7aDE30de1CF65B13f5f45E19e91',
        'F0X_TRADING': '0x398f2eE522cF90DAA0710C37e97CabbFDded50bb'
    }
    for name, addr in addresses.items():
        print(f"   {name}: {addr}")

    # 4. Query balances
    print("\n[4/4] Querying balances...")
    print("-" * 60)

    for name, address in addresses.items():
        print(f"\n📍 {name} ({address})")

        try:
            # List token balances
            result = await client.evm.list_token_balances(
                address=address,
                network=Config.NETWORK_ID
            )

            # Parse balances
            for balance in result.balances:
                token = balance.token
                amount = balance.amount

                # Convert to decimal
                if token.symbol:
                    decimal_amount = Decimal(amount.amount) / Decimal(10**amount.decimals)

                    if token.symbol == 'ETH':
                        print(f"   ETH: {decimal_amount:.6f} ETH")
                    elif token.symbol == 'USDC':
                        print(f"   USDC: ${decimal_amount:.2f} USD")
                    else:
                        print(f"   {token.symbol}: {decimal_amount}")

            if not result.balances:
                print(f"   (no balances found)")

        except Exception as e:
            print(f"   ❌ Error: {e}")

    print("\n" + "=" * 60)
    print("Test completed")
    print("=" * 60)

if __name__ == '__main__':
    asyncio.run(test_balance_query())
