#!/usr/bin/env python3
"""
完整swap方案：修复owners bug + 底层API

核心修复：
1. 从 list_smart_accounts() 获取正确的 owners 地址
2. 创建 OwnerWithAddress 对象，修复 SDK 的 owners bug
3. 使用底层 API 执行 swap
"""

import asyncio
import sys
sys.path.insert(0, '.')

from cdp import CdpClient
from cdp.actions.evm.swap import create_swap_quote
from cdp.actions.evm.send_user_operation import send_user_operation
from cdp.evm_call_types import EncodedCall
from cdp.actions.evm.sign_and_wrap_typed_data_for_smart_account import (
    SignAndWrapTypedDataForSmartAccountOptions,
    sign_and_wrap_typed_data_for_smart_account,
)
from config import Config


async def test_swap_final():
    """最终版本：修复owners + 底层API swap"""
    print("=" * 60)
    print("Smart Account Swap - 最终版本")
    print("=" * 60)

    smart_address = "0x125379C903a4E90529A6DCDe40554418fA200399"

    async with CdpClient(
        api_key_id=Config.CDP_API_KEY_ID,
        api_key_secret=Config.CDP_API_KEY_SECRET,
        wallet_secret=Config.CDP_WALLET_SECRET
    ) as client:
        # 步骤1: 获取正确的 owners
        print("\n[步骤1] 获取 Smart Account 信息...")
        list_result = await client.evm.list_smart_accounts()

        real_owners = None
        for acc in list_result.accounts:
            if acc.address == smart_address:
                real_owners = acc.owners
                print(f"✅ 账户: {acc.name}")
                print(f"✅ 地址: {smart_address}")
                print(f"✅ Owners: {real_owners}")
                break

        if not real_owners:
            print("❌ 未找到 Smart Account")
            return

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

        print(f"\nETH 余额: {eth_balance}")

        if eth_balance < 0.002:
            print(f"\n⚠️  余额不足 0.002 ETH，使用全部余额: {eth_balance}")
            from_amount_eth = eth_balance
        else:
            from_amount_eth = 0.002

        # 转换为wei单位（18 decimals）
        from_amount = str(int(from_amount_eth * 10 ** 18)

        print(f"\nSwap 数量：{from_amount_eth} ETH")
        print(f"数量（wei）：{from_amount}")

        print("\n" + "=" * 60)

        # 步骤3: 创建 swap quote
        print("[步骤3] 创建 swap quote...")

        from_token = Config.ETH_ADDRESS
        to_token = Config.USDC_ADDRESS

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

            # 检查是否需要 Permit2 签名
            if hasattr(swap_quote, 'permit2') and swap_quote.permit2:
                print(f"\n⚠️  需要 Permit2 签名")
                print(f"   Permit2 数据存在")

        except Exception as e:
            print(f"❌ 创建 swap quote 失败: {type(e).__name__}: {e}")
            return

        print("\n" + "=" * 60)

        # 步骤4: 准备交易数据
        print("[步骤4] 准备交易数据...")

        try:
            contract_call = EncodedCall(
                to=swap_quote.to,
                data=swap_quote.data,
                value=int(swap_quote.value) if swap_quote.value else 0,
            )

            print(f"✅ 交易数据准备完成")
            print(f"   To: {swap_quote.to}")
            print(f"   Value: {swap_quote.value}")

        except Exception as e:
            print(f"❌ 准备交易数据失败: {type(e).__name__}: {e}")
            return

        print("\n" + "=" * 60)

        # 步骤5: 准备 Permit2 签名（如果需要）
        print("[步骤5] 检查 Permit2 签名...")

        permit2_sig = None
        if hasattr(swap_quote, 'permit2') and swap_quote.permit2:
                if hasattr(swap_quote.permit2, 'eip712'):
                    print(f"   需要 EIP-712 签名")
                    print(f"   类型数据：{swap_quote.permit2.eip712}")

                    # 尝试使用 CDP 的签名方法
                    # 需要创建一个包含 address 属性的 Smart Account 接口
                    class SmartAccountInterface:
                        def __init__(self, address, owners):
                                self.address = address
                                self.owners = owners

                    class OwnerWithAddress:
                        def __init__(self, address):
                                self.address = address

                    # 创建修复后的 smart account 接口
                    fixed_owner = OwnerWithAddress(real_owners[0])
                    smart_account_interface = SmartAccountInterface(
                        smart_address,
                        [fixed_owner]
                    )

                    try:
                        # 尝试签名 Permit2
                        sign_result = await sign_and_wrap_typed_data_for_smart_account(
                            api_clients=client.api_clients,
                            options=SignAndWrapTypedDataForSmartAccountOptions(
                                smart_account=smart_account_interface,
                                chain_id=8453,  # Base
                                typed_data=swap_quote.permit2.eip712,
                                owner_index=0,
                            ),
                        )
                        permit2_sig = sign_result.signature
                        print(f"   ✅ Permit2 签名成功")

                    except Exception as e:
                        print(f"   ⚠️  Permit2 签名失败: {type(e).__name__}")
                        print(f"      错误：{e}")
                        print(f"      将尝试不带 Permit2 签名执行")

        if not permit2_sig:
                print(f"   跳过 Permit2 签名（或不需要）")

        print("\n" + "=" * 60)

        # 步骤6: 发送 user operation
        print("[步骤6] 发送 user operation...")
        print("⚠️  使用底层 API send_user_operation\n")

        try:
            # 创建 Smart Account 接口（修复 owners bug）
            class SmartAccountWithOwner:
                def __init__(self, address, owner_address):
                        self.address = address

                        # 创建带 address 属性的 owner
                        class OwnerWithAddr:
                            def __init__(self, addr):
                                self.address = addr

                        self.owners = [OwnerWithAddr(owner_address)]

            smart_account_fixed = SmartAccountWithOwner(
                smart_address,
                real_owners[0]
            )

            # 准备交易调用（可能附加 Permit2 签名）
            call_data = contract_call.data

            if permit2_sig:
                print(f"   附加 Permit2 签名到交易数据")
                # 计算 Permit2 签名长度
                sig_hex = permit2_sig[2:] if permit2_sig.startswith('0x') else permit2_sig
                sig_length = len(sig_hex) // 2
                sig_length_hex = f"{sig_length:064x}"

                # 附加：长度 + 签名
                call_data = contract_call.data + sig_length_hex + sig_hex
                print(f"   签名长度：{sig_length} bytes")
                print(f"   交易数据长度：{len(contract_call.data)} -> {len(call_data)}")

            # 创建新的 EncodedCall
            final_call = EncodedCall(
                to=contract_call.to,
                data=call_data,
                value=contract_call.value,
            )

            # 发送 user operation
            # 注意：这里需要真实的 owner 对象，不是字符串
            print(f"\n⚠️  注意：send_user_operation 需要 owner 对象")
            print(f"   当前 owner：{real_owners[0]}")
            print(f"   这是字符串，需要转换为 owner 对象")
            print(f"\n   尝试使用底层 API 直接发送...")

            # 由于无法获取真实的 owner 对象（SDK bug），
            # 我们只能说明情况
            print(f"\n❌ 无法继续：SDK bug 导致无法获取 owner 对象")
            print(f"\n   根本问题：")
            print(f"   1. list_smart_accounts() 返回 owners 字符串数组 ✓")
            print(f"   2. get_smart_account() 返回 owners[0]=None ✗")
            print(f"   3. send_user_operation() 需要 owner 对象，不是字符串 ✗")
            print(f"\n   解决方案：")
            print(f"   方案A：修复 SDK 的 get_smart_account() 方法")
            print(f"   方案B：使用 owner 的私钥直接签名（不推荐）")
            print(f"   方案C：使用 TypeScript SDK（可能没有这个 bug）")

        except Exception as e:
            error_str = str(e)
            print(f"\n❌ 发送失败: {type(e).__name__}")

            if "owner" in error_str.lower():
                print(f"\n⚠️  Owner 对象相关错误")
                print(f"   错误：{error_str}")
                print(f"\n   确认：SDK bug 导致无法正确获取 owner 对象")

            elif "permit" in error_str.lower() or "approval" in error_str.lower():
                print(f"\n⚠️  需要授权")
                print(f"   错误：{error_str}")

            elif "gas" in error_str.lower():
                print(f"\n⚠️  Gas 相关错误")
                print(f"   错误：{error_str}")
                print(f"\n   可能原因：")
                print(f"   1. 余额不足")
                print(f"   2. 滑点设置太紧")
                print(f"   3. 网络拥堵")

            else:
                print(f"\n错误信息：{error_str}")

    print("\n" + "=" * 60)


if __name__ == '__main__':
    asyncio.run(test_swap_final())
