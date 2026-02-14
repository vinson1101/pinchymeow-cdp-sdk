#!/usr/bin/env python3
"""
使用 list_smart_accounts() 获取 owner 地址，直接执行 swap

完全绕过 get_smart_account() 的 owners bug
"""

import asyncio
import sys
sys.path.insert(0, '.')

from cdp import CdpClient
from cdp.actions.evm.swap.types import SmartAccountSwapOptions
from config import Config

async def test_swap_with_list_owner():
    print("=" * 60)
    print("使用 list_smart_accounts() + Owner 账户执行 Swap")
    print("=" * 60)

    smart_addr = "0x5Bae0994344d22E0a3377e81204CC7c030c65e96"

    async with CdpClient(
        api_key_id=Config.CDP_API_KEY_ID,
        api_key_secret=Config.CDP_API_KEY_SECRET,
        wallet_secret=Config.CDP_WALLET_SECRET
    ) as client:
        # 步骤1: 使用 list_smart_accounts() 获取正确的 owner
        print("\n[步骤1] 从 list_smart_accounts() 获取 owner...")
        list_result = await client.evm.list_smart_accounts()

        owner_addr = None
        for acc in list_result.accounts:
            if acc.address == smart_addr:
                owner_addr = acc.owners[0]
                print(f"✅ Smart Account: {acc.name}")
                print(f"✅ Owner 地址: {owner_addr}")
                break

        if not owner_addr:
            print("❌ 未找到账户")
            return

        print("\n" + "=" * 60)

        # 步骤2: 获取 owner 的账户对象（这个可以正确签名）
        print("\n[步骤2] 获取 Owner 账户对象...")
        owner_account = await client.evm.get_account(address=owner_addr)
        print(f"✅ Owner 账户类型: {type(owner_account).__name__}")
        print(f"✅ Owner 地址: {owner_account.address}")

        print("\n" + "=" * 60)

        # 步骤3: 查询 Smart Account 余额
        print("\n[步骤3] 查询 Smart Account 余额...")
        balances = await client.evm.list_token_balances(
            address=smart_addr,
            network='base'
        )

        has_usdc = False
        usdc_bal = 0

        print(f"\n余额：")
        for b in balances.balances:
            amount = float(b.amount.amount) / (10 ** b.amount.decimals)
            print(f"  {b.token.symbol}: {amount}")

            if b.token.symbol == 'USDC':
                has_usdc = True
                usdc_bal = amount

        print(f"\n" + "=" * 60)

        # 步骤4: 执行 swap
        print("\n[步骤4] 执行 swap...")

        if has_usdc and usdc_bal >= 1.0:
            print("\n方向：USDC -> ETH")
            print(f"数量：1 USDC")

            try:
                # 使用 owner 账户的 swap 方法，指定 Smart Account 作为 taker
                from cdp.actions.evm.swap.types import AccountSwapOptions

                result = await owner_account.swap(
                    AccountSwapOptions(
                        network='base',
                        from_token=Config.USDC_ADDRESS,
                        to_token=Config.ETH_ADDRESS,
                        from_amount="1000000",  # 1 USDC
                        slippage_bps=100
                    )
                )

                print(f"\n✅ 交易成功！")
                print(f"TX Hash: {result.transaction_hash}")
                print(f"\n查看: https://basescan.org/tx/{result.transaction_hash}")

            except Exception as e:
                error_str = str(e)
                print(f"\n❌ Swap失败: {type(e).__name__}")

                if "owner" in error_str.lower() or "sign" in error_str.lower():
                    print(f"原因: Owner/签名问题")
                elif "balance" in error_str.lower():
                    print(f"原因: 余额不足（注意：swap 需要 owner 的余额，不是 Smart Account 的）")
                elif "reverted" in error_str.lower():
                    print(f"原因: 交易回执")
                else:
                    print(f"原因: {error_str[:200]}")

                print(f"\n完整错误: {error_str}")
        else:
            print("\n❌ 没有足够的 USDC 余额")

    print("\n" + "=" * 60)

if __name__ == "__main__":
    asyncio.run(test_swap_with_list_owner())
