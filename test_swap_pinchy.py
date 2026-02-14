#!/usr/bin/env python3
"""
测试 PinchyMeow-Smart 账户的 swap

账户：0x5Bae0994344d22E0a3377e81204CC7c030c65e96
"""

import asyncio
import sys
sys.path.insert(0, '.')

from cdp import CdpClient
from cdp.actions.evm.swap.types import SmartAccountSwapOptions
from config import Config

async def test_pinchy_swap():
    print("=" * 60)
    print("PinchyMeow-Smart Swap测试")
    print("=" * 60)

    smart_addr = "0x5Bae0994344d22E0a3377e81204CC7c030c65e96"

    async with CdpClient(
        api_key_id=Config.CDP_API_KEY_ID,
        api_key_secret=Config.CDP_API_KEY_SECRET,
        wallet_secret=Config.CDP_WALLET_SECRET
    ) as client:
        # 步骤1: 获取owners
        print("\n[步骤1] 获取owners...")
        list_result = await client.evm.list_smart_accounts()

        owner_addr = None
        for acc in list_result.accounts:
            if acc.address == smart_addr:
                owner_addr = acc.owners[0]
                print(f"✅ Owners: {owner_addr}")
                break

        if not owner_addr:
            print("❌ 未找到账户")
            return

        print("\n" + "=" * 60)

        # 步骤2: 查询余额
        print("[步骤2] 查询余额...")
        balances = await client.evm.list_token_balances(
            address=smart_addr,
            network='base'
        )

        has_usdc = False
        has_eth = False

        print(f"\n余额：")
        for b in balances.balances:
            amount = float(b.amount.amount) / (10 ** b.amount.decimals)
            print(f"  {b.token.symbol}: {amount}")

            if b.token.symbol == 'USDC':
                has_usdc = True
            elif b.token.symbol == 'ETH':
                has_eth = True

        print(f"\n" + "=" * 60)

        # 步骤3: 执行swap
        print("\n[步骤3] 执行swap...")

        # 决定swap方向
        if has_usdc:
            print("\n方向：USDC -> ETH")
            from_token = Config.USDC_ADDRESS
            to_token = Config.ETH_ADDRESS
            from_amount = "100000"  # 1 USDC (6 decimals)
        else:
            print("\n方向：ETH -> USDC")
            from_token = Config.ETH_ADDRESS
            to_token = Config.USDC_ADDRESS
            from_amount = "1000000000000000"  # 0.001 ETH (18 decimals)

        try:
            smart_account = await client.evm.get_smart_account(
                address=smart_addr
            )

            result = await smart_account.swap(
                SmartAccountSwapOptions(
                    network='base',
                    from_token=from_token,
                    to_token=to_token,
                    from_amount=from_amount,
                    slippage_bps=100
                )
            )

            print(f"\n成功！")
            print(f"TX Hash: {result.transaction_hash}")
            print(f"\n查看: https://basescan.org/tx/{result.transaction_hash}")

        except AttributeError as e:
            if "'NoneType' object has no attribute 'address'" in str(e):
                print(f"\n❌ Owners bug（已知问题）")
            else:
                print(f"\n错误: {type(e).__name__}: {e}")

        except Exception as e:
            print(f"\nSwap失败: {type(e).__name__}")
            print(f"错误: {str(e)[:300]}")

    print("\n" + "=" * 60)

if __name__ == "__main__":
    asyncio.run(test_pinchy_swap())
