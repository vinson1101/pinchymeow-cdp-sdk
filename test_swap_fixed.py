#!/usr/bin/env python3
"""
修复 owners 字段后进行 swap
"""

import asyncio
import sys
sys.path.insert(0, '.')

from cdp import CdpClient
from cdp.actions.evm.swap.types import SmartAccountSwapOptions
from config import Config


async def test_swap_fixed():
    """修复 owners 后测试 swap"""
    print("=" * 60)
    print("Smart Account Swap (修复 owners)")
    print("=" * 60)

    smart_address = "0x125379C903a4E90529A6DCDe40554418fA200399"

    async with CdpClient(
        api_key_id=Config.CDP_API_KEY_ID,
        api_key_secret=Config.CDP_API_KEY_SECRET,
        wallet_secret=Config.CDP_WALLET_SECRET
    ) as client:
        # 步骤1: 用 list 获取正确的 owners
        print("[步骤1] 获取正确的 owners...")
        list_result = await client.evm.list_smart_accounts()

        real_owners = None
        for acc in list_result.accounts:
            if acc.address == smart_address:
                real_owners = acc.owners
                print(f"✅ Owners from list: {real_owners}")
                break

        if not real_owners:
            print("❌ 未找到 Smart Account")
            return

        print("\n" + "=" * 60)

        # 步骤2: 用 get 获取有 swap() 方法的对象
        print("[步骤2] 获取 Smart Account 对象...")
        smart_account = await client.evm.get_smart_account(
            address=smart_address
        )

        print(f"✅ 账户地址: {smart_account.address}")
        print(f"✅ Owners before fix: {smart_account.owners}")

        # 步骤3: 修复 owners 字段
        print("\n[步骤3] 修复 owners 字段...")

        # 创建带 address 属性的 owner 对象
        class OwnerWithAddress:
            def __init__(self, address):
                self.address = address

        # 创建新的 owners 列表
        fixed_owners = [
            OwnerWithAddress(owner) if isinstance(owner, str) else owner
            for owner in real_owners
        ]

        # 尝试修改 smart_account.owners
        try:
            smart_account.owners = fixed_owners
            print(f"✅ Owners after fix: {[(o.address if hasattr(o, 'address') else o) for o in smart_account.owners]}")
        except AttributeError as e:
            print(f"❌ 无法修改 owners (只读属性): {e}")
            print("  需要使用其他方案")
            return

        print("\n" + "=" * 60)

        # 步骤4: 查询余额
        print("[步骤4] 查询余额...")
        balances = await client.evm.list_token_balances(
            address=smart_account.address,
            network='base'
        )

        has_usdc = False
        has_eth = False

        print(f"✅ 余额查询成功：")
        for b in balances.balances:
            amount = float(b.amount.amount) / (10 ** b.amount.decimals)
            print(f"  {b.token.symbol}: {amount}")

            if b.token.symbol == 'USDC':
                has_usdc = True
            elif b.token.symbol == 'ETH':
                has_eth = True

        print("\n" + "=" * 60)

        # 步骤5: 测试 swap
        print("[步骤5] 测试 swap...")

        # 根据余额决定交易方向
        if has_usdc:
            print("\n测试: USDC → ETH ($1.00)")
            from_token = Config.USDC_ADDRESS
            to_token = Config.ETH_ADDRESS
            from_amount = "1000000"  # $1.00 USDC
        elif has_eth:
            print("\n测试: ETH → USDC (0.001 ETH)")
            from_token = Config.ETH_ADDRESS
            to_token = Config.USDC_ADDRESS
            from_amount = "1000000000000000"  # 0.001 ETH
        else:
            print("\n❌ 没有足够余额")
            return

        try:
            swap_result = await smart_account.swap(
                SmartAccountSwapOptions(
                    network='base',
                    from_token=from_token,
                    to_token=to_token,
                    from_amount=from_amount,
                    slippage_bps=100
                )
            )

            print(f"\n✅ 交易成功！")
            print(f"TX Hash: {swap_result.transaction_hash}")
            print(f"\n查看: https://basescan.org/tx/{swap_result.transaction_hash}")

        except AttributeError as e:
            if "'NoneType' object has no attribute 'address'" in str(e):
                print(f"\n❌ owners[0] 仍然是 None")
                print(f"  owners 修复未生效")
            else:
                print(f"\n❌ {e}")

        except Exception as e:
            print(f"\n❌ {type(e).__name__}: {e}")

            if "gasFee" in str(e):
                print("\n⚠️  SDK gasFee Bug")
                print("   需要修复 CommonSwapResponseFees 模型")

    print("\n" + "=" * 60)


if __name__ == '__main__':
    asyncio.run(test_swap_fixed())
