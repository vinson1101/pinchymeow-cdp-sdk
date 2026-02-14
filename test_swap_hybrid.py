#!/usr/bin/env python3
"""
混合方案：使用 list 获取 owners，使用 get 获取 swap() 方法
"""

import asyncio
import sys
sys.path.insert(0, '.')

from cdp import CdpClient
from cdp.actions.evm.swap.types import SmartAccountSwapOptions
from config import Config


async def test_swap_hybrid():
    """混合方案测试"""
    print("=" * 60)
    print("Smart Account Swap (混合方案)")
    print("=" * 60)

    smart_address = "0x125379C903a4E90529A6DCDe40554418fA200399"

    async with CdpClient(
        api_key_id=Config.CDP_API_KEY_ID,
        api_key_secret=Config.CDP_API_KEY_SECRET,
        wallet_secret=Config.CDP_WALLET_SECRET
    ) as client:
        # 步骤1: 用 list 获取 owners 信息
        print("[步骤1] 获取 owners 信息...")
        list_result = await client.evm.list_smart_accounts()

        owners = None
        account_name = None
        for acc in list_result.accounts:
            if acc.address == smart_address:
                owners = acc.owners
                account_name = acc.name
                break

        if not owners:
            print("❌ 未找到 Smart Account")
            return

        print(f"✅ 账户名称: {account_name}")
        print(f"✅ Owners: {owners}")

        print("\n" + "=" * 60)

        # 步骤2: 用 get 获取有 swap() 方法的对象
        print("[步骤2] 获取 Smart Account 对象...")
        smart_account = await client.evm.get_smart_account(
            address=smart_address
        )

        print(f"✅ 账户地址: {smart_account.address}")
        print(f"✅ 有 swap(): {hasattr(smart_account, 'swap')}")

        print("\n" + "=" * 60)

        # 步骤3: 查询余额
        print("[步骤3] 查询余额...")
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

        # 步骤4: 测试 swap
        print("[步骤4] 测试 swap...")

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
                print(f"\n❌ owners[0] 是 None")
                print(f"  需要修复 owners 数组")
            else:
                print(f"\n❌ {e}")

        except Exception as e:
            print(f"\n❌ {type(e).__name__}: {e}")

            if "gasFee" in str(e):
                print("\n⚠️  SDK gasFee Bug")
                print("   需要修复 CommonSwapResponseFees 模型")

    print("\n" + "=" * 60)


if __name__ == '__main__':
    asyncio.run(test_swap_hybrid())
