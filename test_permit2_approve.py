#!/usr/bin/env python3
"""
测试 Permit2 approve + swap
"""

import asyncio
import sys
sys.path.insert(0, '.')

from cdp import CdpClient
from cdp.actions.evm.swap.create_swap_quote import create_swap_quote
from cdp.actions.evm.send_user_operation import send_user_operation
from cdp.evm_call_types import EncodedCall
from config import Config

async def test_permit2_approve():
    print("=" * 60)
    print("测试 Permit2 Approve + Swap")
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

        # 步骤1: 先执行 Permit2 approve
        print("\n[步骤1] 执行 Permit2 Approve...")

        # Permit2 地址 (Base)
        PERMIT2_ADDRESS = "0x000000000022D473030f6c4fF0b9A0F4F26B36A4a6"

        try:
            # 获取 owner 账户
            owner_account = await client.evm.get_account(address=owner_addr)

            # 创建 USDC approve 调用
            # approve(address spender, uint256 amount)
            # ERC20 approve 函数签名：0x095ea7b2
            # approve(address,uint256)

            # 手动构建 calldata
            method_id = "0x095ea7b2"

            # spender 地址 (32 bytes)
            spender_padded = PERMIT2_ADDRESS.lower().replace('0x', '').rjust(64, '0')

            # amount = uint256 max (32 bytes)
            amount_hex = format(2**256 - 1, 'x')
            amount_padded = amount_hex.rjust(64, '0')

            approve_data = method_id + spender_padded + amount_padded

            print(f"Approve Calldata:")
            print(f"  Method ID: {method_id}")
            print(f"  Spender: {PERMIT2_ADDRESS}")
            print(f"  Amount: infinite")
            print(f"  Data Length: {len(approve_data)//2} bytes")

            approve_call = EncodedCall(
                to=Config.USDC_ADDRESS,
                data=approve_data,
                value=0
            )

            print(f"Approve USDC -> Permit2")
            print(f"  Spender: {PERMIT2_ADDRESS}")
            print(f"  Amount: infinite")

            # 创建简单的 SmartAccount 接口
            class SimpleSmartAccount:
                def __init__(self, addr, owner):
                    self.address = addr
                    self.owners = [owner]

            simple_sa = SimpleSmartAccount(smart_addr, owner_account)

            # 发送 user operation - 先 approve
            print(f"\n发送 approve user operation...")

            approve_result = await send_user_operation(
                api_clients=client.api_clients,
                address=smart_addr,
                owner=owner_account,
                calls=[approve_call],
                network='base'
            )

            print(f"✅ Approve 成功！")
            print(f"User Op Hash: {approve_result.user_op_hash}")

        except Exception as e:
            print(f"❌ Approve 失败: {e}")
            print(f"错误类型: {type(e).__name__}")

            # 如果 approve 失败，继续尝试 swap
            print(f"\n继续尝试 swap...")

        print("\n" + "=" * 60)

        # 步骤2: 创建 swap quote
        print("\n[步骤2] 创建 swap quote...")

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
        print(f"  Liquidity: {swap_quote.liquidity_available}")
        print(f"  Requires Signature: {swap_quote.requires_signature}")

        print("\n" + "=" * 60)

        # 步骤3: 执行 swap
        print("\n[步骤3] 执行 swap...")

        from cdp.actions.evm.swap.send_swap_operation import (
            SendSwapOperationOptions,
            send_swap_operation,
        )

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
    asyncio.run(test_permit2_approve())
