#!/usr/bin/env python3
"""
最简化的 swap 测试 - 直接使用 API
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

async def minimal_swap():
    print("=" * 60)
    print("最简化的 Swap 测试")
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

        # 步骤1: 创建 swap quote
        print("\n[步骤1] 创建 swap quote...")

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

        # 步骤2: 处理 Permit2 签名
        print("\n[步骤2] 处理 Permit2 签名...")

        if swap_quote.requires_signature and hasattr(swap_quote, 'permit2_data') and swap_quote.permit2_data:
            print("需要 Permit2 签名")

            # 获取真实的 owner 账户
            owner_account = await client.evm.get_account(address=owner_addr)

            # 创建简单的 SmartAccount 接口（用于 SDK 内部调用）
            class SimpleSmartAccount:
                def __init__(self, addr, owner):
                    self.address = addr
                    self.owners = [owner]

            simple_sa = SimpleSmartAccount(smart_addr, owner_account)

            try:
                # 调用 SDK 的签名函数
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
                print(f"  Signature: {sign_result.signature[:20]}...")

                # 构建完整的交易数据
                sig_hex = sign_result.signature
                if sig_hex.startswith("0x"):
                    sig_hex = sig_hex[2:]

                # 计算签名长度
                sig_length = len(sig_hex) // 2
                sig_length_hex = f"{sig_length:064x}"

                # 拼接：原始数据 + 长度 + 签名
                tx_data = swap_quote.data + sig_length_hex + sig_hex

                print(f"  原始数据长度: {len(swap_quote.data)//2}")
                print(f"  签名长度: {sig_length}")
                print(f"  新数据长度: {len(tx_data)//2}")

            except Exception as e:
                print(f"❌ 签名失败: {e}")
                return
        else:
            tx_data = swap_quote.data
            print("不需要 Permit2 签名")

        print("\n" + "=" * 60)

        # 步骤3: 创建 contract call
        print("\n[步骤3] 创建 contract call...")

        contract_call = EncodedCall(
            to=swap_quote.to,
            data=tx_data,
            value=int(swap_quote.value) if swap_quote.value else 0,
        )

        print(f"✅ Contract Call 创建成功")
        print(f"  To: {swap_quote.to[:20]}...")
        print(f"  Value: {swap_quote.value}")

        print("\n" + "=" * 60)

        # 步骤4: 发送 user operation
        print("\n[步骤4] 发送 user operation...")

        owner_account = await client.evm.get_account(address=owner_addr)

        try:
            user_op = await send_user_operation(
                api_clients=client.api_clients,
                address=smart_addr,
                owner=owner_account,
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
                print(f"原因: Permit2 transferFrom 失败")
                print(f"\n可能原因：")
                print(f"  1. Smart Account 未授权 Permit2")
                print(f"  2. Permit2 nonce 不正确")
                print(f"  3. Permit2 签名格式不正确")
                print(f"  4. 交易数据编码不正确")
            elif "execution reverted" in error_str:
                print(f"原因: 执行回退")
            else:
                print(f"原因: {error_str[:300]}")

            print(f"\n完整错误: {error_str[:500]}")

    print("\n" + "=" * 60)

if __name__ == "__main__":
    asyncio.run(minimal_swap())
