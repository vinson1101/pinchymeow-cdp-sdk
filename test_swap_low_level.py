#!/usr/bin/env python3
"""
使用底层 API 直接调用 swap，传入正确的 owner 地址

绕过 SmartAccount.swap() 的 owners bug
"""

import asyncio
import sys
sys.path.insert(0, '.')

from cdp import CdpClient
from cdp.actions.evm.swap.send_swap_operation import (
    SendSwapOperationOptions,
    send_swap_operation,
)
from config import Config

class FixedSmartAccount:
    """修复后的 SmartAccount 包装类"""
    def __init__(self, real_account, owner_addr):
        self._real = real_account
        self.address = real_account.address
        self.owners = [type('Owner', (), {'address': owner_addr})()]

async def test_swap_low_level():
    print("=" * 60)
    print("使用底层 API + 修复后的 SmartAccount")
    print("=" * 60)

    smart_addr = "0x5Bae0994344d22E0a3377e81204CC7c030c65e96"

    async with CdpClient(
        api_key_id=Config.CDP_API_KEY_ID,
        api_key_secret=Config.CDP_API_KEY_SECRET,
        wallet_secret=Config.CDP_WALLET_SECRET
    ) as client:
        # 步骤1: 使用 list_smart_accounts() 获取正确的 owner
        print("\n[步骤1] 从 list_smart_accounts() 获取 owner...")
        list_result = await client.evm.list_smart_accounts()

        owner_addr = None
        for acc in list_result.accounts:
            if acc.address == smart_addr:
                owner_addr = acc.owners[0]
                print(f"✅ Owner 地址: {owner_addr}")
                break

        if not owner_addr:
            print("❌ 未找到账户")
            return

        print("\n" + "=" * 60)

        # 步骤2: 获取真实的 Smart Account 和 Owner 账户对象
        print("\n[步骤2] 获取 Smart Account 和 Owner 对象...")
        real_smart_account = await client.evm.get_smart_account(address=smart_addr)
        owner_account = await client.evm.get_account(address=owner_addr)

        print(f"✅ Smart Account 地址: {real_smart_account.address}")
        print(f"❌ Smart Account Owners (有 bug): {real_smart_account.owners}")
        print(f"✅ Owner 账户类型: {type(owner_account).__name__}")
        print(f"✅ Owner 地址: {owner_account.address}")

        # 创建修复后的 SmartAccount，使用真实的 owner 对象
        fixed_account = FixedSmartAccount(real_smart_account, owner_addr)
        # 替换为真实的 owner 对象（可以签名）
        fixed_account.owners = [owner_account]
        print(f"✅ Fixed Owners: {fixed_account.owners[0].address}")

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

        # 步骤4: 使用底层 API 执行 swap
        print("\n[步骤4] 使用底层 API 执行 swap...")

        if has_usdc and usdc_bal >= 1.0:
            print("\n方向：USDC -> ETH")
            print(f"数量：1 USDC")

            try:
                # 使用底层 API，传入修复后的 SmartAccount
                options = SendSwapOperationOptions(
                    smart_account=fixed_account,
                    network='base',
                    from_token=Config.USDC_ADDRESS,
                    to_token=Config.ETH_ADDRESS,
                    from_amount="1000000",  # 1 USDC
                    slippage_bps=100
                )

                result = await send_swap_operation(
                    api_clients=client.api_clients,
                    options=options
                )

                print(f"\n✅ 交易成功！")
                print(f"User Op Hash: {result.user_op_hash}")
                print(f"Smart Account: {result.smart_account_address}")
                print(f"状态: {result.status}")

            except AttributeError as e:
                if "'NoneType' object has no attribute 'address'" in str(e):
                    print(f"\n❌ 仍然有 owners bug")
                    print(f"错误: {e}")
                else:
                    print(f"\n❌ AttributeError: {e}")

            except Exception as e:
                error_str = str(e)
                print(f"\n❌ Swap失败: {type(e).__name__}")

                if "gas" in error_str.lower():
                    print(f"原因: Gas相关")
                elif "liquidity" in error_str.lower():
                    print(f"原因: 流动性")
                elif "owner" in error_str.lower() or "sign" in error_str.lower():
                    print(f"原因: Owner/签名")
                elif "reverted" in error_str.lower():
                    print(f"原因: 交易回执")
                else:
                    print(f"原因: {error_str[:300]}")

                print(f"\n完整错误: {error_str}")
        else:
            print("\n❌ 没有足够的 USDC 余额")

    print("\n" + "=" * 60)

if __name__ == "__main__":
    asyncio.run(test_swap_low_level())
