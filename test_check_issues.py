#!/usr/bin/env python3
"""
检查 swap quote 的 issues 字段
"""

import asyncio
import sys
sys.path.insert(0, '.')

from cdp import CdpClient
from cdp.actions.evm.swap.create_swap_quote import create_swap_quote
from config import Config

async def check_issues():
    print("=" * 60)
    print("检查 Swap Quote Issues")
    print("=" * 60)

    smart_addr = "0x5Bae0994344d22E0a3377e81204CC7c030c65e96"

    async with CdpClient(
        api_key_id=Config.CDP_API_KEY_ID,
        api_key_secret=Config.CDP_API_KEY_SECRET,
        wallet_secret=Config.CDP_WALLET_SECRET
    ) as client:
        # 获取 owner
        list_result = await client.evm.list_smart_accounts()
        owner_addr = None
        for acc in list_result.accounts:
            if acc.address == smart_addr:
                owner_addr = acc.owners[0]
                break

        print(f"\nSmart Account: {smart_addr}")
        print(f"Owner: {owner_addr}")

        print("\n" + "=" * 60)

        # 创建 swap quote
        print("\n创建 swap quote...")

        swap_quote = await create_swap_quote(
            api_clients=client.api_clients,
            from_token=Config.USDC_ADDRESS,
            to_token=Config.ETH_ADDRESS,
            from_amount="1000000",  # 1 USDC
            network='base',
            taker=smart_addr,
            slippage_bps=100,
            signer_address=owner_addr
        )

        print(f"✅ Quote 创建成功")
        print(f"\n基本信息：")
        print(f"  Liquidity Available: {swap_quote.liquidity_available}")
        print(f"  Requires Signature: {swap_quote.requires_signature}")

        # 检查 issues
        if hasattr(swap_quote, 'issues') and swap_quote.issues:
            print(f"\n⚠️  Issues Detected:")
            print(f"  {swap_quote.issues}")

            # 详细检查 allowance
            if hasattr(swap_quote.issues, 'allowance'):
                allowance = swap_quote.issues.allowance
                print(f"\nAllowance Issue:")
                if hasattr(allowance, 'has_allowance'):
                    print(f"  Has Allowance: {allowance.has_allowance}")
                if hasattr(allowance, 'spender'):
                    print(f"  Spender: {allowance.spender}")

            # 详细检查 balance
            if hasattr(swap_quote.issues, 'balance'):
                balance = swap_quote.issues.balance
                print(f"\nBalance Issue:")
                if hasattr(balance, 'has_balance'):
                    print(f"  Has Balance: {balance.has_balance}")
        else:
            print(f"\n✅ 没有检测到 issues")

        print("\n" + "=" * 60)

        # 尝试执行 swap
        print("\n尝试执行 swap...")

        from cdp.actions.evm.swap.send_swap_operation import (
            SendSwapOperationOptions,
            send_swap_operation,
        )

        # 创建简单的 SmartAccount 接口
        class SimpleSmartAccount:
            def __init__(self, addr, owner):
                self.address = addr
                self.owners = [owner]

        # 获取真实的 owner 账户
        owner_account = await client.evm.get_account(address=owner_addr)

        simple_sa = SimpleSmartAccount(smart_addr, owner_account)

        options = SendSwapOperationOptions(
            smart_account=simple_sa,
            network='base',
            from_token=Config.USDC_ADDRESS,
            to_token=Config.ETH_ADDRESS,
            from_amount="1000000",
            taker=smart_addr,
            slippage_bps=100
        )

        result = await send_swap_operation(
            api_clients=client.api_clients,
            options=options
        )

        print(f"\n✅ Swap 成功！")
        print(f"User Op Hash: {result.user_op_hash}")
        print(f"Smart Account: {result.smart_account_address}")
        print(f"状态: {result.status}")

    print("\n" + "=" * 60)

if __name__ == "__main__":
    asyncio.run(check_issues())
