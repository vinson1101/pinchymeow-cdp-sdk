#!/usr/bin/env python3
"""
使用 list_smart_accounts() 进行 swap

PinchyMeow 已验证 list_smart_accounts() 可用
"""

import asyncio
import sys
sys.path.insert(0, '.')

from cdp import CdpClient
from cdp.actions.evm.swap.types import SmartAccountSwapOptions
from config import Config


async def test_swap_with_list():
    """使用 list_smart_accounts() 获取账户并测试 swap"""
    print("=" * 60)
    print("Smart Account Swap (使用 list_smart_accounts)")
    print("=" * 60)

    async with CdpClient(
        api_key_id=Config.CDP_API_KEY_ID,
        api_key_secret=Config.CDP_API_KEY_SECRET,
        wallet_secret=Config.CDP_WALLET_SECRET
    ) as client:
        # 使用 list_smart_accounts() 获取账户
        print("\n[步骤1] 获取 Smart Account...")
        list_result = await client.evm.list_smart_accounts()

        # 找到 F0x-Smart 账户
        smart_account = None
        for acc in list_result.accounts:
            if 'F0x' in acc.name:
                smart_account = acc
                break

        if not smart_account:
            print("❌ 未找到 F0x-Smart 账户")
            return

        print(f"✅ 账户名称: {smart_account.name}")
        print(f"✅ 账户地址: {smart_account.address}")
        print(f"✅ Owners: {smart_account.owners}")
        print(f"✅ 有 swap(): {hasattr(smart_account, 'swap')}")

        print("\n" + "=" * 60)

        # 查询余额
        print("[步骤2] 查询余额...")
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

        # 测试 swap
        print("[步骤3] 测试 swap...")

        # 根据余额决定交易方向
        if has_usdc:
            print("\n测试: USDC → ETH ($1.00)")
            from_token = Config.USDC_ADDRESS
            to_token = Config.ETH_ADDRESS
            from_amount = "1000000"  # $1.00 USDC (6 decimals)
        elif has_eth:
            print("\n测试: ETH → USDC (0.001 ETH)")
            from_token = Config.ETH_ADDRESS
            to_token = Config.USDC_ADDRESS
            from_amount = "1000000000000000"  # 0.001 ETH (18 decimals)
        else:
            print("\n❌ 没有足够余额进行交易")
            return

        try:
            swap_result = await smart_account.swap(
                SmartAccountSwapOptions(
                    network='base',  # PinchyMeow确认: 必须用 'base'
                    from_token=from_token,
                    to_token=to_token,
                    from_amount=from_amount,
                    slippage_bps=100
                )
            )

            print(f"\n✅ 交易成功！")
            print(f"TX Hash: {swap_result.transaction_hash}")
            print(f"\n查看交易: https://basescan.org/tx/{swap_result.transaction_hash}")

        except Exception as e:
            print(f"\n❌ 交易失败: {type(e).__name__}: {e}")

            if "gasFee" in str(e):
                print("\n⚠️  这是 SDK 的 gasFee Bug")
                print("   API 返回 gasFee=None，但 SDK 模型不允许 None")
                print("   解决方案：需要修复 SDK 的 CommonSwapResponseFees 模型")

    print("\n" + "=" * 60)


if __name__ == '__main__':
    asyncio.run(test_swap_with_list())
