#!/usr/bin/env python3
"""
测试 Smart Account swap - 不使用 owners

直接用 smart_account.address 作为 signer_address
"""

import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from cdp import CdpClient
from config import Config


async def test_swap_without_owners():
    """测试不用 owners 的 swap"""
    print("=" * 60)
    print("测试 Smart Account swap (不用 owners)")
    print("=" * 60)

    smart_address = "0x125379C903a4E90529A6DCDe40554418fA200399"
    print(f"Smart Account: {smart_address}\n")

    async with CdpClient(
        api_key_id=Config.CDP_API_KEY_ID,
        api_key_secret=Config.CDP_API_KEY_SECRET,
        wallet_secret=Config.CDP_WALLET_SECRET
    ) as client:
        # 查询余额
        print("[查询余额]...")
        balances = await client.evm.list_token_balances(
            address=smart_address,
            network='base'
        )

        print(f"✅ 查询成功！")
        for b in balances.balances:
            amount = float(b.amount.amount) / (10 ** b.amount.decimals)
            print(f"  {b.token.symbol}: {amount}")

        print("\n" + "=" * 60)

        # 获取 Smart Account
        print("[获取 Smart Account]...")
        try:
            smart_account = await client.evm.get_smart_account(
                address=smart_address
            )
            print(f"✅ 账户地址: {smart_account.address}")
            print(f"  owners 长度: {len(smart_account.owners)}")

            if smart_account.owners and smart_account.owners[0]:
                print(f"  owners[0] 类型: {type(smart_account.owners[0])}")
                print(f"  owners[0] 有 address: {hasattr(smart_account.owners[0], 'address')}")

        except Exception as e:
            print(f"❌ 获取失败: {e}")
            import traceback
            traceback.print_exc()
            return

        print("\n" + "=" * 60)

        # 尝试手动调用 swap
        print("[尝试手动调用 swap]...")
        try:
            from cdp.actions.evm.swap import send_swap_operation
            from cdp.actions.evm.swap.types import SmartAccountSwapOptions

            # 手动构造参数
            options = SmartAccountSwapOptions(
                network='base-mainnet',
                from_token=Config.USDC_ADDRESS,
                to_token=Config.ETH_ADDRESS,
                from_amount="1000000",
                slippage_bps=100
            )

            print(f"✅ SwapOptions 创建成功")
            print(f"  from_token: {options.from_token}")
            print(f"  to_token: {options.to_token}")
            print(f"  from_amount: {options.from_amount}")

            # 手动指定 signer_address
            signer_address = smart_account.address

            print(f"\n[手动指定参数]")
            print(f"  smart_account: {smart_account.address}")
            print(f"  signer_address: {signer_address}")

            # 调用 send_swap_operation
            result = await send_swap_operation(
                api_clients=client.api_clients,
                smart_account=smart_account,
                options=options
            )

            print(f"\n✅ 交易成功！")
            print(f"TX Hash: {result.transaction_hash}")

        except Exception as e:
            print(f"❌ 失败: {e}")
            import traceback
            traceback.print_exc()

    print("\n" + "=" * 60)


if __name__ == '__main__':
    asyncio.run(test_swap_without_owners())
