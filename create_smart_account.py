#!/usr/bin/env python3
"""
创建新的 CDP Wallet Smart Account

通过 CDP SDK 创建，这样才能用 account.swap()
"""

import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from cdp import CdpClient
from config import Config


async def create_smart_account():
    """创建 Smart Account"""
    print("=" * 60)
    print("创建 Smart Account")
    print("=" * 60)

    async with CdpClient(
        api_key_id=Config.CDP_API_KEY_ID,
        api_key_secret=Config.CDP_API_KEY_SECRET,
        wallet_secret=Config.CDP_WALLET_SECRET
    ) as cdp:
        try:
            # 创建 Smart Account（会自动部署到链上）
            smart_account = await cdp.evm.create_smart_account(
                name='f0x-smart-v2'
            )

            print(f"\n✅ Smart Account 创建成功!")
            print(f"地址: {smart_account.address}")
            print(f"类型: {type(smart_account).__name__}")

            # 检查是否有 swap 方法
            if hasattr(smart_account, 'swap'):
                print(f"✅ 账户有 swap() 方法")
            else:
                print(f"❌ 账户没有 swap() 方法")

            print(f"\n请向这个地址充值：")
            print(f"  地址: {smart_account.address}")
            print(f"  网络: Base mainnet")
            print(f"  金额: 0.01 ETH + $5-10 USDC")

            # 更新 Config
            print(f"\n需要更新 Config.py:")
            print(f"  'F0x': '{smart_account.address}',")

        except Exception as e:
            print(f"\n❌ 创建失败: {e}")
            import traceback
            traceback.print_exc()

    print("\n" + "=" * 60)


if __name__ == '__main__':
    asyncio.run(create_smart_account())
