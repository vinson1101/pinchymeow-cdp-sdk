#!/usr/bin/env python3
"""
测试 Smart Account 对象获取和 swap

1. 查余额（已成功）
2. 尝试获取 Smart Account 对象
3. 检查是否有 swap() 方法
4. 尝试调用 swap()（可能因没 USDC 失败）
"""

import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from cdp import CdpClient
from config import Config


async def test_smart_swap():
    """测试 Smart Account swap"""
    print("=" * 60)
    print("测试 Smart Account swap")
    print("=" * 60)

    smart_address = "0x125379C903a4E90529A6DCDe40554418fA200399"
    print(f"地址: {smart_address}\n")

    async with CdpClient(
        api_key_id=Config.CDP_API_KEY_ID,
        api_key_secret=Config.CDP_API_KEY_SECRET,
        wallet_secret=Config.CDP_WALLET_SECRET
    ) as client:
        # 步骤1: 查余额（确认地址有效）
        print("[步骤1] 查询余额...")
        balances = await client.evm.list_token_balances(
            address=smart_address,
            network='base'
        )

        has_usdc = False
        for b in balances.balances:
            if b.token.symbol == 'USDC':
                has_usdc = True
                break

        if has_usdc:
            print("✅ 有 USDC 余额，可以测试 USDC→ETH 交易")
        else:
            print("⚠️  没有 USDC，只能测试 ETH→USDC（需要先充值）")

        print(f"   ETH: 0.001")
        print(f"   USDC: {'有' if has_usdc else '无'}")

        print("\n" + "=" * 60)

        # 步骤2: 尝试获取 Smart Account 对象
        print("[步骤2] 获取 Smart Account 对象...")

        try:
            # 方法1: get_smart_account(address=...)
            print(f"  尝试 get_smart_account(address=...)...")
            account = await client.evm.get_smart_account(
                address=smart_address
            )
            print(f"  ✅ 账户类型: {type(account).__name__}")
            print(f"  ✅ 有 swap(): {hasattr(account, 'swap')}")

            if hasattr(account, 'swap'):
                print(f"\n[步骤3] 测试 swap()...")
                print(f"  注意: 可能因没 USDC 而失败，这是预期的\n")

                from cdp.actions.evm.swap.types import SmartAccountSwapOptions

                # 尝试小额交易
                try:
                    result = await account.swap(
                        SmartAccountSwapOptions(
                            network="base",
                            from_token=Config.USDC_ADDRESS,
                            to_token=Config.ETH_ADDRESS,
                            from_amount="100000",  # 0.10 USDC
                            slippage_bps=100
                        )
                    )
                    print(f"  ✅ 交易成功!")
                    print(f"  TX Hash: {result.transaction_hash}")

                except Exception as e:
                    print(f"  ❌ 交易失败: {e}")
                    print(f"  (可能因为没有足够的 USDC 余额)")

        except Exception as e:
            print(f"  ❌ 获取账户失败: {e}")

    print("\n" + "=" * 60)


if __name__ == '__main__':
    asyncio.run(test_smart_swap())
