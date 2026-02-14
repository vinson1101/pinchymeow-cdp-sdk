#!/usr/bin/env python3
"""
直接测试 Smart Account swap()

不管账户类型，直接获取对象并测试 swap
"""

import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from cdp import CdpClient
from config import Config


async def test_swap_directly():
    """直接测试 swap"""
    print("=" * 60)
    print("测试 Smart Account swap()")
    print("=" * 60)

    smart_account_address = "0x125379C903a4E90529A6DCDe40554418fA200399"
    print(f"Smart Account: {smart_account_address}\n")

    async with CdpClient(
        api_key_id=Config.CDP_API_KEY_ID,
        api_key_secret=Config.CDP_API_KEY_SECRET,
        wallet_secret=Config.CDP_WALLET_SECRET
    ) as cdp:
        # 直接用 get_account 获取（可能返回 EvmServerAccount）
        try:
            account = await cdp.evm.get_account(address=smart_account_address)
            print(f"✅ 获取到账户对象")
            print(f"账户类型: {type(account).__name__}")
            print(f"账户地址: {account.address}")

            # 检查是否有 swap 方法
            if hasattr(account, 'swap'):
                print(f"✅ 账户有 swap() 方法")

                # 检查余额
                balances = await cdp.evm.list_token_balances(
                    address=smart_account_address,
                    network='base'
                )

                print("\n当前余额:")
                for b in balances.balances:
                    amount = float(b.amount.amount) / (10 ** b.amount.decimals)
                    print(f"  {b.token.symbol}: {amount}")

                # 尝试小额交易（只是为了测试，即使失败也无所谓）
                print("\n[测试] 尝试 swap()...")
                from cdp.actions.evm.swap.types import AccountSwapOptions

                try:
                    # 注意：这里可能还是会失败，因为没有 USDC
                    result = await account.swap(
                        AccountSwapOptions(
                            network="base",
                            from_token=Config.USDC_ADDRESS,
                            to_token=Config.ETH_ADDRESS,
                            from_amount="1000000",  # $1.00
                            slippage_bps=100
                        )
                    )
                    print(f"✅ 交易成功!")
                    print(f"TX Hash: {result.transaction_hash}")
                except Exception as e:
                    print(f"❌ swap() 失败: {type(e).__name__}: {e}")

            else:
                print(f"❌ 账户没有 swap() 方法")
                print(f"可用方法: {[m for m in dir(account) if not m.startswith('_') and callable(getattr(account, m))][:10]}")

        except Exception as e:
            print(f"❌ 获取账户失败: {e}")
            import traceback
            traceback.print_exc()

    print("\n" + "=" * 60)


if __name__ == '__main__':
    asyncio.run(test_swap_directly())
