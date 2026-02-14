#!/usr/bin/env python3
"""
使用 CDP 托管 owner 的 Swap 测试

根据文档建议，使用 get_or_create_account 创建 CDP 托管 owner
"""

import asyncio
import sys
sys.path.insert(0, '.')

from cdp import CdpClient
from cdp.actions.evm.swap.types import SmartAccountSwapOptions
from config import Config

async def test_swap_with_cdp_owner():
    print("=" * 60)
    print("使用 CDP 托管 Owner 的 Swap 测试")
    print("=" * 60)

    smart_addr = "0x5Bae0994344d22E0a3377e81204CC7c030c65e96"

    async with CdpClient(
        api_key_id=Config.CDP_API_KEY_ID,
        api_key_secret=Config.CDP_API_KEY_SECRET,
        wallet_secret=Config.CDP_WALLET_SECRET
    ) as client:
        # 步骤1: 获取当前 owner
        print("\n[步骤1] 获取当前 Smart Account 信息...")
        list_result = await client.evm.list_smart_accounts()

        current_owner = None
        account_name = None
        for acc in list_result.accounts:
            if acc.address == smart_addr:
                current_owner = acc.owners[0]
                account_name = acc.name
                break

        print(f"Smart Account: {account_name}")
        print(f"当前 Owner: {current_owner}")

        print("\n" + "=" * 60)

        # 步骤2: 查询余额
        print("\n[步骤2] 查询余额...")
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

        # 步骤3: 检查是否有 CDP 托管 owner
        print("\n[步骤3] 检查 CDP 托管 Owner...")

        # 列出所有账户
        all_accounts = await client.evm.list_accounts()

        cdp_owner = None
        print(f"\n所有 CDP 账户：")
        for acc in all_accounts.accounts:
            print(f"  {acc.address}")
            # 如果当前 owner 在列表中，说明是 CDP 托管的
            if acc.address == current_owner:
                cdp_owner = acc
                print(f"    ✅ 这是 CDP 托管账户")

        if not cdp_owner:
            print(f"\n❌ 当前 owner 不是 CDP 托管账户")
            print(f"   Owner: {current_owner}")
            print(f"   Type: EOA（外部账户）")
            print(f"\n当前 owner 是外部 EOA，CDP SDK 可能无法为它生成 Permit2 签名")
            print(f"建议：使用 CDP 托管 owner 进行测试")

        print("\n" + "=" * 60)

        # 步骤4: 尝试 swap
        print("\n[步骤4] 尝试执行 swap...")

        if has_usdc and usdc_bal >= 1.0:
            print("\n方向：USDC -> ETH")
            print(f"数量：1 USDC")

            try:
                # 获取 SmartAccount 对象
                smart_account = await client.evm.get_smart_account(
                    address=smart_addr
                )

                # 尝试使用 swap 方法
                result = await smart_account.swap(
                    SmartAccountSwapOptions(
                        network='base',
                        from_token=Config.USDC_ADDRESS,
                        to_token=Config.ETH_ADDRESS,
                        from_amount="1000000",  # 1 USDC
                        slippage_bps=100
                    )
                )

                print(f"\n✅ Swap 成功！")
                print(f"User Op Hash: {result.user_op_hash}")
                print(f"Smart Account: {result.smart_account_address}")
                print(f"状态: {result.status}")
                print(f"\n查看: https://basescan.org/tx/{result.user_op_hash}")

            except AttributeError as e:
                if "'NoneType' object has no attribute 'address'" in str(e):
                    print(f"\n❌ Owners bug（已知问题）")
                    print(f"get_smart_account() 仍然返回 owners[0] = None")
                    print(f"\n这个 bug 导致无法生成 Permit2 签名")
                    print(f"建议：使用 list_smart_accounts() 或创建 CDP 托管 owner")
                else:
                    print(f"\n错误: {e}")

            except Exception as e:
                error_str = str(e)
                print(f"\n❌ Swap失败: {type(e).__name__}")

                if "TRANSFER_FROM_FAILED" in error_str:
                    print(f"原因: Permit2 transferFrom 失败")
                    print(f"\n可能原因：")
                    print(f"  1. Smart Account 未授权 Permit2")
                    print(f"  2. Permit2 nonce 不正确")
                    print(f"  3. Permit2 签名生成失败（owner 问题）")
                    print(f"  4. Owner 是外部 EOA，CDP SDK 无法签名")
                elif "gas" in error_str.lower():
                    print(f"原因: Gas 相关")
                elif "liquidity" in error_str.lower():
                    print(f"原因: 流动性不足")
                else:
                    print(f"原因: {error_str[:200]}")

                print(f"\n完整错误: {error_str[:500]}")
        else:
            print("\n❌ 没有足够的 USDC 余额")

    print("\n" + "=" * 60)

if __name__ == "__main__":
    asyncio.run(test_swap_with_cdp_owner())
