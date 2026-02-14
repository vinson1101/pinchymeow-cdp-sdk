#!/usr/bin/env python3
"""
使用 CDP SDK 检查 Permit2 授权
"""

import asyncio
import sys
sys.path.insert(0, '.')

from cdp import CdpClient
from config import Config

async def check_approval():
    print("=" * 60)
    print("检查 Permit2 授权状态")
    print("=" * 60)

    smart_addr = "0x5Bae0994344d22E0a3377e81204CC7c030c65e96"

    async with CdpClient(
        api_key_id=Config.CDP_API_KEY_ID,
        api_key_secret=Config.CDP_API_KEY_SECRET,
        wallet_secret=Config.CDP_WALLET_SECRET
    ) as client:
        # 使用 get_swap_price 获取详细信息
        print("\n[步骤1] 获取 swap 价格...")

        try:
            price = await client.evm.get_swap_price(
                from_token=Config.USDC_ADDRESS,
                to_token=Config.ETH_ADDRESS,
                from_amount="1000000",  # 1 USDC
                network='base',
                taker=smart_addr
            )

            print(f"✅ 价格获取成功")
            print(f"  From Amount: {price.from_amount}")
            print(f"  To Amount: {price.to_amount}")

            # 检查是否有 issues
            if hasattr(price, 'issues') and price.issues:
                print(f"\n⚠️  Issues detected:")
                print(f"  {price.issues}")

                if hasattr(price.issues, 'allowance'):
                    print(f"\nAllowance Issue:")
                    allowance = price.issues.allowance
                    print(f"  Has Allowance: {allowance.has_allowance if hasattr(allowance, 'has_allowance') else 'N/A'}")
                    print(f"  Spender: {allowance.spender if hasattr(allowance, 'spender') else 'N/A'}")

                if hasattr(price.issues, 'balance'):
                    print(f"\nBalance Issue:")
                    balance = price.issues.balance
                    print(f"  Has Balance: {balance.has_balance if hasattr(balance, 'has_balance') else 'N/A'}")

            else:
                print(f"\n✅ 没有 issues")

        except Exception as e:
            print(f"❌ 获取价格失败: {e}")

    print("\n" + "=" * 60)

if __name__ == "__main__":
    asyncio.run(check_approval())
