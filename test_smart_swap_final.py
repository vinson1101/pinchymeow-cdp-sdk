#!/usr/bin/env python3
"""
使用 Smart Account 进行 swap

关键点：network='base-mainnet'
"""

import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from cdp import CdpClient
from cdp.actions.evm.swap.types import SmartAccountSwapOptions
from config import Config


async def test_smart_swap():
    """测试 Smart Account swap"""
    print("=" * 60)
    print("Smart Account Swap 测试")
    print("=" * 60)

    smart_address = "0x125379C903a4E90529A6DCDe40554418fA200399"
    print(f"Smart Account: {smart_address}\n")

    async with CdpClient(
        api_key_id=Config.CDP_API_KEY_ID,
        api_key_secret=Config.CDP_API_KEY_SECRET,
        wallet_secret=Config.CDP_WALLET_SECRET
    ) as client:
        # 步骤1: 查余额
        print("[步骤1] 查询余额...")
        balances = await client.evm.list_token_balances(
            address=smart_address,
            network='base'
        )

        print(f"✅ 查询成功！")
        print(f"\n当前余额:")
        for b in balances.balances:
            amount = float(b.amount.amount) / (10 ** b.amount.decimals)
            print(f"  {b.token.symbol}: {amount}")

        has_usdc = any(b.token.symbol == 'USDC' for b in balances.balances)

        print("\n" + "=" * 60)

        # 步骤2: 获取 Smart Account
        print("[步骤2] 获取 Smart Account 对象...")
        try:
            smart_account = await client.evm.get_smart_account(
                address=smart_address
            )
            print(f"✅ 账户类型: {type(smart_account).__name__}")
            print(f"   地址: {smart_account.address}")
            print(f"   有 swap(): {hasattr(smart_account, 'swap')}")
        except Exception as e:
            print(f"❌ 获取失败: {e}")
            return

        print("\n" + "=" * 60)

        # 步骤3: 测试 swap
        if has_usdc:
            print("[步骤3] 测试 USDC → ETH swap...")
        else:
            print("[步骤3] ⚠️  没有 USDC，测试 ETH → USDC swap...")

        try:
            # 注意：这里用 SmartAccountSwapOptions
            result = await smart_account.swap(
                SmartAccountSwapOptions(
                    network='base-mainnet',  # 关键！不是 'base'
                    from_token=Config.USDC_ADDRESS,
                    to_token=Config.ETH_ADDRESS,
                    from_amount="1000000",  # $1.00
                    slippage_bps=100
                )
            )

            print(f"✅ 交易成功!")
            print(f"TX Hash: {result.transaction_hash}")
            print(f"\n查看: https://basescan.org/tx/{result.transaction_hash}")

        except Exception as e:
            print(f"❌ 交易失败: {type(e).__name__}: {e}")

    print("\n" + "=" * 60)


if __name__ == '__main__':
    asyncio.run(test_smart_swap())
