#!/usr/bin/env python3
"""
最简单的测试：只查余额
"""

import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from cdp import CdpClient
from config import Config


async def test_balance_only():
    """只测试余额查询"""
    print("=" * 60)
    print("测试 Smart Account 余额")
    print("=" * 60)

    smart_address = "0x125379C903a4E90529A6DCDe40554418fA200399"
    print(f"地址: {smart_address}\n")

    async with CdpClient(
        api_key_id=Config.CDP_API_KEY_ID,
        api_key_secret=Config.CDP_API_KEY_SECRET,
        wallet_secret=Config.CDP_WALLET_SECRET
    ) as client:
        # 直接用 client.evm.list_token_balances()
        print("[查询余额]...")
        try:
            balances = await client.evm.list_token_balances(
                address=smart_address,
                network='base'
            )

            print(f"✅ 查询成功！")
            print(f"\n当前余额:")
            for b in balances.balances:
                amount = float(b.amount.amount) / (10 ** b.amount.decimals)
                print(f"  {b.token.symbol}: {amount}")

            print(f"\n总共: {len(balances.balances)} 种代币")

        except Exception as e:
            print(f"❌ 查询失败: {e}")
            import traceback
            traceback.print_exc()

    print("\n" + "=" * 60)


if __name__ == '__main__':
    asyncio.run(test_balance_only())
