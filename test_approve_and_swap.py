#!/usr/bin/env python3
"""
完整流程：授权 + swap

步骤：
1. 使用 list_smart_accounts() 获取正确的 owners
2. 授权 Permit2（允许 Smart Account 花费 ETH）
3. 执行 swap
"""

import asyncio
import sys
sys.path.insert(0, '.')

from cdp import CdpClient
from cdp.actions.evm.swap import create_swap_quote
from config import Config


async def test_approve_and_swap():
    """授权 + swap 完整流程"""
    print("=" * 60)
    print("Smart Account 完整流程：授权 + Swap")
    print("=" * 60)

    smart_address = "0x125379C903a4E90529A6DCDe40554418fA200399"

    async with CdpClient(
        api_key_id=Config.CDP_API_KEY_ID,
        api_key_secret=Config.CDP_API_KEY_SECRET,
        wallet_secret=Config.CDP_WALLET_SECRET
    ) as client:
        # 步骤1: 使用 list 获取正确的 owners
        print("\n[步骤1] 获取 Smart Account 信息...")
        list_result = await client.evm.list_smart_accounts()

        real_owners = None
        account_name = None
        for acc in list_result.accounts:
            if acc.address == smart_address:
                real_owners = acc.owners
                account_name = acc.name
                break

        if not real_owners:
            print("❌ 未找到 Smart Account")
            return

        print(f"✅ 账户: {account_name}")
        print(f"✅ 地址: {smart_address}")
        print(f"✅ Owner: {real_owners[0]}")

        print("\n" + "=" * 60)

        # 步骤2: 查询余额
        print("[步骤2] 查询余额...")
        balances = await client.evm.list_token_balances(
            address=smart_address,
            network='base'
        )

        eth_balance = 0
        print(f"✅ 余额：")
        for b in balances.balances:
            amount = float(b.amount.amount) / (10 ** b.amount.decimals)
            print(f"  {b.token.symbol}: {amount}")

            if b.token.symbol == 'ETH':
                eth_balance = amount

        if eth_balance < 0.001:
            print(f"\n❌ ETH 余额不足（{eth_balance} < 0.001）")
            return

        print("\n" + "=" * 60)

        # 步骤3: 授权 Permit2
        print("[步骤3] 授权 Permit2...")
        print("⚠️  说明：Permit2 是标准授权合约")
        print("   允许合约地址操作你的 token")
        print("   对于 Smart Account swap 必不可少\n")

        # CDP SDK 可能提供授权方法
        # 方式1: 检查是否有 approve 方法
        smart_account = await client.evm.get_smart_account(address=smart_address)

        if hasattr(smart_account, 'create_user_operation'):
            print(f"✅ Smart Account 有 create_user_operation() 方法")

            # 方式2: 检查是否有 approve 相关方法
            if hasattr(client.evm, 'approve'):
                print(f"✅ client.evm 有 approve() 方法")
            else:
                print(f"⚠️  client.evm 没有 approve() 方法")

        # 尝试找到授权方法
        print("\n可用的授权方法：")
        evm_methods = [m for m in dir(client.evm) if not m.startswith('_') and callable(getattr(client.evm, m))]
        approve_methods = [m for m in evm_methods if 'approve' in m.lower() or 'permit' in m.lower() or 'auth' in m.lower()]

        if approve_methods:
            for method in approve_methods[:10]:
                print(f"  - {method}")
        else:
                print("  ❌ 未找到授权相关方法")

        print("\n" + "=" * 60)

        # 步骤4: 创建 swap quote
        print("[步骤4] 创建 swap quote...")

        from_token = Config.ETH_ADDRESS
        to_token = Config.USDC_ADDRESS
        from_amount = "2000000000000000"  # 0.002 ETH

        print(f"从: 0.002 ETH")
        print(f"到: USDC")
        print(f"网络: base")

        try:
            swap_quote = await create_swap_quote(
                api_clients=client.api_clients,
                from_token=from_token,
                to_token=to_token,
                from_amount=from_amount,
                network='base',
                taker=smart_address,
                slippage_bps=100
            )

            print(f"✅ Swap quote 创建成功")
            print(f"   预期输出: {swap_quote.to_amount} USDC")
            print(f"   最小输出: {swap_quote.min_to_amount} USDC")

        except Exception as e:
            print(f"❌ 创建 swap quote 失败: {type(e).__name__}: {e}")
            return

        print("\n" + "=" * 60)

        # 步骤5: 直接执行 swap（跳过授权，看是否会自动处理）
        print("[步骤5] 尝试执行 swap...")
        print("⚠️  如果需要授权，会返回具体错误信息\n")

        try:
            # 使用 get_smart_account 获取有 swap 方法的对象
            smart_account_for_swap = await client.evm.get_smart_account(
                address=smart_address
            )

            if hasattr(smart_account_for_swap, 'swap'):
                print(f"✅ Smart Account 有 swap() 方法")

                from cdp.actions.evm.swap.types import SmartAccountSwapOptions

                result = await smart_account_for_swap.swap(
                    SmartAccountSwapOptions(
                        network='base',
                        from_token=from_token,
                        to_token=to_token,
                        from_amount=from_amount,
                        slippage_bps=100
                    )
                )

                print(f"\n✅ Swap 成功！")
                print(f"TX Hash: {result.transaction_hash}")
                print(f"\n查看: https://basescan.org/tx/{result.transaction_hash}")

            else:
                print(f"❌ Smart Account 没有 swap() 方法")
                print(f"   类型: {type(smart_account_for_swap).__name__}")

        except AttributeError as e:
            if "'NoneType' object has no attribute 'address'" in str(e):
                print(f"\n❌ owners[0] 是 None（已知 bug）")
                print(f"   SDK 的 get_smart_account() 无法正确解析 owners")
                print(f"   建议：使用底层 API 直接执行")
            else:
                print(f"\n❌ {e}")

        except Exception as e:
            error_str = str(e)
            print(f"\n❌ Swap 失败: {type(e).__name__}")

            # 分析错误
            if "permit" in error_str.lower() or "approval" in error_str.lower():
                print(f"\n⚠️  需要授权！")
                print(f"   错误信息：{error_str}")
                print(f"\n   解决方案：")
                print(f"   1. 先执行 Permit2 授权交易")
                print(f"   2. 然后再执行 swap")

            elif "gas" in error_str.lower():
                print(f"\n⚠️  Gas 相关错误")
                print(f"   错误信息：{error_str}")
                print(f"\n   可能原因：")
                print(f"   1. 余额不足")
                print(f"   2. 滑点设置太紧")
                print(f"   3. 网络拥堵")

            elif "revert" in error_str.lower() or "failed" in error_str.lower():
                print(f"\n⚠️  交易回滚")
                print(f"   错误信息：{error_str}")
                print(f"\n   可能原因：")
                print(f"   1. 需要授权")
                print(f"   2. 交易数据错误")
                print(f"   3. 合约调用失败")

            else:
                print(f"\n错误信息：{error_str}")

    print("\n" + "=" * 60)


if __name__ == '__main__':
    asyncio.run(test_approve_and_swap())
