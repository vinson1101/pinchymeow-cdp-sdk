#!/usr/bin/env python3
"""
手动构建 swap，完全绕过 SmartAccount.swap()
"""

import asyncio
import sys
sys.path.insert(0, '.')

from cdp import CdpClient
from cdp.actions.evm.swap.create_swap_quote import create_swap_quote
from cdp.actions.evm.send_user_operation import send_user_operation
from cdp.evm_call_types import EncodedCall
from cdp.actions.evm.sign_and_wrap_typed_data_for_smart_account import (
    SignAndWrapTypedDataForSmartAccountOptions,
    sign_and_wrap_typed_data_for_smart_account,
)
from config import Config
from eth_utils import keccak

async def test_swap_manual():
    print("=" * 60)
    print("手动构建 Swap (完全绕过 SmartAccount.swap())")
    print("=" * 60)

    smart_addr = "0x5Bae0994344d22E0a3377e81204CC7c030c65e96"

    async with CdpClient(
        api_key_id=Config.CDP_API_KEY_ID,
        api_key_secret=Config.CDP_API_KEY_SECRET,
        wallet_secret=Config.CDP_WALLET_SECRET
    ) as client:
        # 步骤1: 获取 owner
        print("\n[步骤1] 获取 owner...")
        list_result = await client.evm.list_smart_accounts()

        owner_addr = None
        for acc in list_result.accounts:
            if acc.address == smart_addr:
                owner_addr = acc.owners[0]
                print(f"✅ Owner: {owner_addr}")
                break

        print("\n" + "=" * 60)

        # 步骤2: 获取 owner 账户对象
        print("\n[步骤2] 获取 Owner 账户对象...")
        owner_account = await client.evm.get_account(address=owner_addr)
        print(f"✅ Owner 类型: {type(owner_account).__name__}")

        print("\n" + "=" * 60)

        # 步骤3: 查询余额
        print("\n[步骤3] 查询余额...")
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

        # 步骤4: 创建 swap quote
        if has_usdc and usdc_bal >= 1.0:
            print("\n[步骤4] 创建 swap quote...")

            try:
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

                print(f"✅ Swap Quote 创建成功")
                print(f"  To: {swap_quote.to[:20]}...")
                print(f"  Requires Signature: {swap_quote.requires_signature}")

            except Exception as e:
                print(f"❌ Quote 失败: {e}")
                return

            print("\n" + "=" * 60)

            # 步骤5: 处理 Permit2 签名
            print("\n[步骤5] 处理 Permit2 签名...")

            if swap_quote.requires_signature and hasattr(swap_quote, 'permit2_data') and swap_quote.permit2_data:
                print("需要 Permit2 签名")

                # 创建简单的 SmartAccount 接口
                class SimpleSmartAccount:
                    def __init__(self, addr, owner):
                        self.address = addr
                        self.owners = [owner]

                simple_sa = SimpleSmartAccount(smart_addr, owner_account)

                try:
                    sign_result = await sign_and_wrap_typed_data_for_smart_account(
                        client.api_clients,
                        SignAndWrapTypedDataForSmartAccountOptions(
                            smart_account=simple_sa,
                            chain_id=8453,  # Base
                            typed_data=swap_quote.permit2_data.eip712,
                            owner_index=0
                        )
                    )

                    print(f"✅ Permit2 签名成功")
                    print(f"  Signature Length: {len(sign_result.signature)//2} bytes")

                    # 修改 tx_data，添加 Permit2 签名
                    sig_hex = sign_result.signature
                    if sig_hex.startswith("0x"):
                        sig_hex = sig_hex[2:]

                    sig_length = len(sig_hex) // 2
                    sig_length_hex = f"{sig_length:064x}"

                    new_tx_data = swap_quote.data + sig_length_hex + sig_hex

                    print(f"  Original Data Length: {len(swap_quote.data)//2}")
                    print(f"  New Data Length: {len(new_tx_data)//2}")

                except Exception as e:
                    print(f"❌ 签名失败: {e}")
                    return
            else:
                new_tx_data = swap_quote.data
                print("不需要 Permit2 签名")

            print("\n" + "=" * 60)

            # 步骤6: 创建 contract call
            print("\n[步骤6] 创建 contract call...")

            contract_call = EncodedCall(
                to=swap_quote.to,
                data=new_tx_data,
                value=int(swap_quote.value) if swap_quote.value else 0,
            )

            print(f"✅ Contract Call 创建成功")
            print(f"  To: {swap_quote.to[:20]}...")
            print(f"  Value: {swap_quote.value}")

            print("\n" + "=" * 60)

            # 步骤7: 发送 user operation
            print("\n[步骤7] 发送 user operation...")

            try:
                user_op = await send_user_operation(
                    api_clients=client.api_clients,
                    address=smart_addr,
                    owner=owner_account,  # 使用真实的 owner 账户
                    calls=[contract_call],
                    network='base',
                )

                print(f"\n✅ User Operation 提交成功！")
                print(f"User Op Hash: {user_op.user_op_hash}")
                print(f"状态: {user_op.status}")
                print(f"\n查看: https://basescan.org/tx/{user_op.user_op_hash}")

            except Exception as e:
                error_str = str(e)
                print(f"\n❌ User Operation 失败: {type(e).__name__}")

                if "TRANSFER_FROM_FAILED" in error_str:
                    print(f"原因: Permit2 transfer_from 失败")
                    print(f"  可能原因：")
                    print(f"  1. Smart Account 没有授权 Permit2")
                    print(f"  2. Permit2 签名格式不正确")
                    print(f"  3. 余额不足")
                elif "gas" in error_str.lower():
                    print(f"原因: Gas 相关")
                elif "signature" in error_str.lower():
                    print(f"原因: 签名问题")
                else:
                    print(f"原因: {error_str[:300]}")

                print(f"\n完整错误: {error_str}")

    print("\n" + "=" * 60)

if __name__ == "__main__":
    asyncio.run(test_swap_manual())
