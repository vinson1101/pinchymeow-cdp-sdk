#!/usr/bin/env python3
"""
测试 PinchyMeow-Smart 账户的 swap (修复owners bug)

账户：0x5Bae0994344d22E0a3377e81204CC7c030c65e96
"""

import asyncio
import sys
sys.path.insert(0, '.')

from cdp import CdpClient
from cdp.actions.evm.swap.types import SmartAccountSwapOptions
from config import Config

class FixedOwner:
    """修复后的Owner类，包含address属性"""
    def __init__(self, address: str):
        self.address = address

async def test_pinchy_swap_fixed():
    print("=" * 60)
    print("PinchyMeow-Smart Swap测试 (Owners修复版)")
    print("=" * 60)

    smart_addr = "0x5Bae0994344d22E0a3377e81204CC7c030c65e96"

    async with CdpClient(
        api_key_id=Config.CDP_API_KEY_ID,
        api_key_secret=Config.CDP_API_KEY_SECRET,
        wallet_secret=Config.CDP_WALLET_SECRET
    ) as client:
        # 步骤1: 获取owners
        print("\n[步骤1] 获取owners...")
        list_result = await client.evm.list_smart_accounts()

        owner_addr = None
        for acc in list_result.accounts:
            if acc.address == smart_addr:
                owner_addr = acc.owners[0]
                print(f"✅ Owners: {owner_addr}")
                break

        if not owner_addr:
            print("❌ 未找到账户")
            return

        print("\n" + "=" * 60)

        # 步骤2: 查询余额
        print("[步骤2] 查询余额...")
        balances = await client.evm.list_token_balances(
            address=smart_addr,
            network='base'
        )

        has_usdc = False
        has_eth = False
        usdc_bal = 0
        eth_bal = 0

        print(f"\n余额：")
        for b in balances.balances:
            amount = float(b.amount.amount) / (10 ** b.amount.decimals)
            print(f"  {b.token.symbol}: {amount}")

            if b.token.symbol == 'USDC':
                has_usdc = True
                usdc_bal = amount
            elif b.token.symbol == 'ETH':
                has_eth = True
                eth_bal = amount

        print(f"\n" + "=" * 60)

        # 步骤3: 执行swap
        print("\n[步骤3] 执行swap...")

        # 决定swap方向
        if has_usdc and usdc_bal >= 1.0:
            print("\n方向：USDC -> ETH")
            from_token = Config.USDC_ADDRESS
            to_token = Config.ETH_ADDRESS
            from_amount = "1000000"  # 1 USDC (6 decimals)
            print(f"数量：1 USDC")
        else:
            print("\n方向：ETH -> USDC")
            from_token = Config.ETH_ADDRESS
            to_token = Config.USDC_ADDRESS
            from_amount = "1000000000000000"  # 0.001 ETH (18 decimals)
            print(f"数量：0.001 ETH")

        try:
            print("\n[步骤4] 获取Smart Account对象...")
            smart_account = await client.evm.get_smart_account(
                address=smart_addr
            )

            # 检查并修复owners bug
            print(f"\n[步骤5] 检查owners bug...")
            print(f"Owners before: {smart_account.owners}")

            if not smart_account.owners or smart_account.owners[0] is None:
                print("⚠️  检测到owners bug，执行monkey patch...")
                fixed_owner = FixedOwner(owner_addr)
                smart_account.owners = [fixed_owner]
                print(f"✅ Owners已修复: {smart_account.owners[0].address}")

            print("\n[步骤6] 执行swap交易...")
            result = await smart_account.swap(
                SmartAccountSwapOptions(
                    network='base',
                    from_token=from_token,
                    to_token=to_token,
                    from_amount=from_amount,
                    slippage_bps=100
                )
            )

            print(f"\n✅ 交易成功！")
            print(f"TX Hash: {result.transaction_hash}")
            print(f"\n查看: https://basescan.org/tx/{result.transaction_hash}")

        except AttributeError as e:
            if "'NoneType' object has no attribute 'address'" in str(e):
                print(f"\n❌ Owners bug修复失败")
                print(f"错误: {e}")
            else:
                print(f"\n❌ AttributeError: {e}")

        except Exception as e:
            error_str = str(e)
            print(f"\n❌ Swap失败: {type(e).__name__}")

            # 分析错误
            if "gas" in error_str.lower():
                print(f"原因: Gas相关错误")
            elif "liquidity" in error_str.lower():
                print(f"原因: 流动性问题")
            elif "owner" in error_str.lower() or "sign" in error_str.lower():
                print(f"原因: Owner/签名问题")
            elif "reverted" in error_str.lower():
                print(f"原因: 交易回执")
            elif "amount" in error_str.lower():
                print(f"原因: 金额问题")
            else:
                print(f"原因: {error_str[:200]}")

            # 完整错误信息（开发用）
            print(f"\n完整错误: {error_str}")

    print("\n" + "=" * 60)

if __name__ == "__main__":
    asyncio.run(test_pinchy_swap_fixed())
