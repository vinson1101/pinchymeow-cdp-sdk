#!/usr/bin/env python3
"""
诊断 Permit2 和 swap quote
"""

import asyncio
import sys
sys.path.insert(0, '.')

from cdp import CdpClient
from cdp.actions.evm.swap.create_swap_quote import create_swap_quote
from config import Config

async def diagnose_permit2():
    print("=" * 60)
    print("诊断 Permit2 和 Swap Quote")
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

        # 步骤2: 创建 swap quote
        print("\n[步骤2] 创建 swap quote...")

        try:
            swap_quote = await create_swap_quote(
                api_clients=client.api_clients,
                from_token=Config.USDC_ADDRESS,
                to_token=Config.ETH_ADDRESS,
                from_amount="1000000",  # 1 USDC
                network='base',
                taker=smart_addr,
                slippage_bps=100,
                signer_address=owner_addr  # 传入正确的 owner 地址
            )

            print(f"\n✅ Swap Quote 创建成功！")
            print(f"\n详细信息：")
            print(f"  To: {swap_quote.to}")
            print(f"  From Amount: {swap_quote.from_amount}")
            print(f"  To Amount: {swap_quote.to_amount}")
            print(f"  Min To Amount: {swap_quote.min_to_amount}")
            print(f"  Value: {swap_quote.value}")
            print(f"  Data Length: {len(swap_quote.data) if swap_quote.data else 0}")

            # 检查 Permit2 相关字段
            print(f"\nPermit2 信息：")
            print(f"  Requires Signature: {swap_quote.requires_signature}")
            print(f"  Has Permit2 Data: {hasattr(swap_quote, 'permit2_data')}")

            if hasattr(swap_quote, 'permit2_data') and swap_quote.permit2_data:
                print(f"\n  Permit2 Data:")
                p2 = swap_quote.permit2_data
                print(f"    Type: {type(p2).__name__}")
                print(f"    Has EIP712: {hasattr(p2, 'eip712')}")

                if hasattr(p2, 'eip712'):
                    eip712 = p2.eip712
                    print(f"    EIP712 Type: {type(eip712).__name__}")
                            # 打印 EIP712 的字段
                    if hasattr(eip712, 'model_fields'):
                        print(f"    EIP712 Fields: {list(eip712.model_fields.keys())}")
            else:
                print(f"  ❌ 没有 Permit2 数据")

            # 检查 issues
            if hasattr(swap_quote, 'issues') and swap_quote.issues:
                print(f"\nIssues: {swap_quote.issues}")

        except Exception as e:
            print(f"\n❌ 创建 quote 失败: {type(e).__name__}")
            print(f"错误: {str(e)[:500]}")

    print("\n" + "=" * 60)

if __name__ == "__main__":
    asyncio.run(diagnose_permit2())
