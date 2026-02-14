#!/usr/bin/env python3
"""
直接测试 Smart Account

1. 先查余额（不需要账户对象）
2. 然后测试 swap
"""

import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from cdp import CdpClient
from cdp.actions.evm import list_token_balances
from config import Config


async def test_smart_simple():
    """简单测试 Smart Account"""
    print("=" * 60)
    print("测试 Smart Account")
    print("=" * 60)

    smart_address = "0x125379C903a4E90529A6DCDe40554418fA200399"
    print(f"Smart Account: {smart_address}\n")

    async with CdpClient(
        api_key_id=Config.CDP_API_KEY_ID,
        api_key_secret=Config.CDP_API_KEY_SECRET,
        wallet_secret=Config.CDP_WALLET_SECRET
    ) as client:
        # 步骤1: 直接查余额（不需要账户对象）
        print("[步骤1] 查询余额...")
        try:
            balances = await list_token_balances(
                api_clients=client.api_clients,
                address=smart_address,
                network='base'
            )

            print(f"✅ 查询成功！")
            print(f"\n当前余额:")
            for b in balances.balances:
                amount = float(b.amount.amount) / (10 ** b.amount.decimals)
                print(f"  {b.token.symbol}: {amount}")

        except Exception as e:
            print(f"❌ 查询失败: {e}")
            return

        print("\n" + "=" * 60)

        # 步骤2: 测试 swap（尝试，即使没有 USDC）
        print("[步骤2] 测试 swap()...")
        print("注意：可能因为没有 USDC 而失败\n")

        try:
            # 尝试获取账户对象并调用 swap
            from cdp.actions.evm.swap.types import SmartAccountSwapOptions

            # 注意：这里仍然会失败，因为无法通过 SDK 获取账户对象
            # 但至少可以看到 swap 方法是否可用
            result = await client.evm.get_smart_account(smart_address)

            if result and hasattr(result, 'swap'):
                print("✅ Smart Account 对象获取成功")

                # 尝试小量交易
                swap_result = await result.swap(
                    SmartAccountSwapOptions(
                        network="base",
                        from_token=Config.USDC_ADDRESS,
                        to_token=Config.ETH_ADDRESS,
                        from_amount="100000",  # 0.10 USDC
                        slippage_bps=100
                    )
                )

                print(f"✅ 交易成功!")
                print(f"TX Hash: {swap_result.transaction_hash}")
            else:
                print("❌ Smart Account 对象获取失败")

        except Exception as e:
            print(f"❌ 失败: {type(e).__name__}: {e}")

    print("\n" + "=" * 60)


if __name__ == '__main__':
    asyncio.run(test_smart_simple())
