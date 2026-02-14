#!/usr/bin/env python3
"""
使用 CDP SDK 的 get_swap_quote
"""

import asyncio
import sys
sys.path.insert(0, '.')

from cdp import CdpClient
from config import Config

async def test_quote_full():
    print("=" * 60)
    print("测试 get_swap_quote")
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

        print(f"\nOwner: {owner_addr}")
        print("\n" + "=" * 60)

        # 使用 get_swap_quote
        print("\n[步骤1] 获取 swap quote...")

        try:
            quote = await client.evm.create_swap_quote(
                from_token=Config.USDC_ADDRESS,
                to_token=Config.ETH_ADDRESS,
                from_amount="1000000",  # 1 USDC
                network='base',
                taker=smart_addr
            )

            print(f"✅ Quote 获取成功")

            print(f"\nQuote 详情:")
            print(f"  To: {quote.to[:20]}...")
            print(f"  From Amount: {quote.from_amount}")
            print(f"  To Amount: {quote.to_amount}")
            print(f"  Min To Amount: {quote.min_to_amount}")
            print(f"  Value: {quote.value}")
            print(f"  Data Length: {len(quote.data) if quote.data else 0}")

            # 检查 Permit2
            print(f"\nPermit2:")
            print(f"  Requires Signature: {quote.requires_signature}")

            if hasattr(quote, 'permit2_data') and quote.permit2_data:
                print(f"  Has Permit2 Data: True")
                p2 = quote.permit2_data

                if hasattr(p2, 'eip712'):
                    print(f"  Has EIP712: True")
                    eip712 = p2.eip712

                    if isinstance(eip712, dict):
                        print(f"  EIP712 Type: dict")
                        print(f"  Keys: {list(eip712.keys())}")

                        # 打印 domain
                        if 'domain' in eip712:
                            print(f"  Domain: {eip712['domain']}")
                    else:
                        print(f"  EIP712 Type: {type(eip712).__name__}")
                else:
                    print(f"  Has EIP712: False")

                # 打印其他属性
                if hasattr(p2, 'hash'):
                    print(f"  Hash: {p2.hash}")
                if hasattr(p2, 'type'):
                    print(f"  Type: {p2.type}")

            else:
                print(f"  Has Permit2 Data: False")

            # 检查 issues
            if hasattr(quote, 'issues') and quote.issues:
                print(f"\nIssues:")
                print(f"  {quote.issues}")

        except Exception as e:
            print(f"❌ Quote 失败: {e}")

    print("\n" + "=" * 60)

if __name__ == "__main__":
    asyncio.run(test_quote_full())
