#!/usr/bin/env python3
"""
测试 Smart Account swap() 方法

Smart Account 有 swap() 方法，可以直接交易！
"""

import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from cdp import CdpClient
from cdp.actions.evm.swap.types import SmartAccountSwapOptions


async def test_smart_swap():
    """测试 Smart Account swap() 方法"""
    print("=" * 60)
    print("测试 Smart Account swap() 方法")
    print("=" * 60)

    async with CdpClient(
        api_key_id=Config.CDP_API_KEY_ID,
        api_key_secret=Config.CDP_API_KEY_SECRET,
        wallet_secret=Config.CDP_WALLET_SECRET
    ) as client:
        smart_address = Config.AGENT_ACCOUNTS['F0x']['smart']
        print(f"Smart Account: {smart_address}\n")

        try:
            # Get Smart Account
            smart_account = await client.evm.get_smart_account(address=smart_address)
            print(f"✅ Name: {smart_account.name}")
            print(f"✅ Address: {smart_account.address}")
            
            # Check balance
            from cdp.actions.evm import list_token_balances
            balances = await list_token_balances(
                api_clients=client.api_clients,
                address=smart_account.address,
                network='base'
            )
            
            print(f"\n当前余额:")
            for token, balance in balances.balances.items():
                amount = float(balance.amount) / (10 ** balance.amount.decimals)
                print(f"  {token}: {amount}")
            
            # Test swap ($1.00 USDC → ETH)
            print(f"\n[测试] $1.00 USDC → ETH...")
            
            result = await smart_account.swap(
                SmartAccountSwapOptions(
                    network='base',
                    from_token='0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913',  # USDC
                    to_token='0x42000000000000000000000000000000000006',  # ETH
                    from_amount='1000000'  # 1 USDC (6 decimals)
                    slippage_bps=100
                )
            )
            
            print(f"✅ 交易成功!")
            print(f"  TX Hash: {result.transaction_hash}")
            print(f"\n查看: https://basescan.org/tx/{result.transaction_hash}")
            
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()

    print("\n" + "=" * 60)


if __name__ == '__main__':
    asyncio.run(test_smart_swap())
