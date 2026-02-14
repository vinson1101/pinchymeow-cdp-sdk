#!/usr/bin/env python3
"""
测试 Smart Account 交易

Smart Account 不受 EOA 的 SDK bug 影响
"""

import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from cdp import CdpClient
from config import Config
from cdp.actions.evm.swap.types import SmartAccountSwapOptions


async def test_smart_account_trade():
    """测试 Smart Account 交易"""
    print("=" * 60)
    print("测试 Smart Account 交易")
    print("=" * 60)

    async with CdpClient(
        api_key_id=Config.CDP_API_KEY_ID,
        api_key_secret=Config.CDP_API_KEY_SECRET,
        wallet_secret=Config.CDP_WALLET_SECRET
    ) as cdp:
        # 获取 Smart Account 地址
        smart_account_address = Config.AGENT_ACCOUNTS.get('F0x')
        print(f"Smart Account: {smart_account_address}\n")

        # 使用 get_or_create 获取 Smart Account
        try:
            smart_account = await cdp.evm.get_or_create_smart_account(
                owner=None,  # Wallet secret 会作为 owner
                name='f0x-smart'
            )
            print(f"✅ Smart Account 地址: {smart_account.address}")
            print(f"账户类型: {type(smart_account).__name__}")
        except Exception as e:
            print(f"❌ 获取失败: {e}")
            import traceback
            traceback.print_exc()
            return

        # 检查余额
        balances = await cdp.evm.list_token_balances(
            address=smart_account_address,
            network='base'
        )

        print("\n当前余额:")
        for b in balances.balances:
            amount = float(b.amount.amount) / (10 ** b.amount.decimals)
            print(f"  {b.token.symbol}: {amount}")

        print("\n" + "=" * 60)
        print("[测试] $1.00 USDC → ETH")
        print("=" * 60)

        # 测试交易
        try:
            result = await smart_account.swap(
                SmartAccountSwapOptions(
                    network="base",
                    from_token=Config.USDC_ADDRESS,
                    to_token=Config.ETH_ADDRESS,
                    from_amount="1000000",  # $1.00 USDC
                    slippage_bps=100
                )
            )

            print(f"✅ 交易成功!")
            print(f"TX Hash: {result.transaction_hash}")
            print(f"查看: https://basescan.org/tx/{result.transaction_hash}")

        except Exception as e:
            print(f"❌ 交易失败: {e}")

        print("\n" + "=" * 60)


if __name__ == '__main__':
    asyncio.run(test_smart_account_trade())
