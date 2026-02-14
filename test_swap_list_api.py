#!/usr/bin/env python3
"""
使用 list_smart_accounts() + 底层 API 实现 swap

方案：
1. 使用 list_smart_accounts() 获取正确的 owners 地址
2. 使用底层 API (create_swap_quote + send_user_operation) 执行 swap
3. 绕过 Smart Account 对象的 swap() 方法 bug

参考官方示例：
- https://github.com/coinbase/cdp-sdk/blob/main/examples/python/evm/swaps/account.swap.py
"""

import asyncio
import sys
sys.path.insert(0, '.')

from cdp import CdpClient
from cdp.actions.evm.swap import create_swap_quote
from cdp.actions.evm.send_user_operation import send_user_operation
from cdp.evm_call_types import EncodedCall
from config import Config


async def test_swap_with_list():
    """使用 list + 底层 API 实现 swap"""
    print("=" * 60)
    print("Smart Account Swap (list + 底层 API)")
    print("=" * 60)

    smart_address = "0x125379C903a4E90529A6DCDe40554418fA200399"

    async with CdpClient(
        api_key_id=Config.CDP_API_KEY_ID,
        api_key_secret=Config.CDP_API_KEY_SECRET,
        wallet_secret=Config.CDP_WALLET_SECRET
    ) as client:
        # 步骤1: 使用 list_smart_accounts() 获取正确的 owners
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

        print(f"✅ 账户名称: {account_name}")
        print(f"✅ 账户地址: {smart_address}")
        print(f"✅ Owners: {real_owners}")

        owner_address = real_owners[0]
        print(f"✅ Owner 地址: {owner_address}")

        print("\n" + "=" * 60)

        # 步骤2: 查询余额
        print("[步骤2] 查询余额...")
        balances = await client.evm.list_token_balances(
            address=smart_address,
            network='base'
        )

        has_usdc = False
        has_eth = False

        print(f"✅ 余额查询成功：")
        for b in balances.balances:
            amount = float(b.amount.amount) / (10 ** b.amount.decimals)
            print(f"  {b.token.symbol}: {amount}")

            if b.token.symbol == 'USDC':
                has_usdc = True
            elif b.token.symbol == 'ETH':
                has_eth = True

        print("\n" + "=" * 60)

        # 步骤3: 创建 swap quote
        print("[步骤3] 创建 swap quote...")

        # 根据余额决定交易方向
        if has_usdc:
            print("\n测试: USDC → ETH ($1.00)")
            from_token = Config.USDC_ADDRESS
            to_token = Config.ETH_ADDRESS
            from_amount = "1000000"  # $1.00 USDC (6 decimals)
        elif has_eth:
            print("\n测试: ETH → USDC (0.001 ETH)")
            from_token = Config.ETH_ADDRESS
            to_token = Config.USDC_ADDRESS
            from_amount = "1000000000000000"  # 0.001 ETH (18 decimals)
        else:
            print("\n❌ 没有足够余额")
            return

        try:
            # 使用底层 API 创建 swap quote
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

            # 检查 quote 状态
            if hasattr(swap_quote, 'liquidity_available') and not swap_quote.liquidity_available:
                print(f"❌ 流动性不足")
                return

            print(f"   预期输出: {swap_quote.to_amount}")
            print(f"   最小输出: {swap_quote.min_to_amount}")

        except Exception as e:
            print(f"❌ 创建 swap quote 失败: {type(e).__name__}: {e}")

            if "gasFee" in str(e):
                print("\n⚠️  这是 SDK 的 gasFee Bug")
                print("   API 返回 gasFee=None，但 SDK 模型不允许 None")
                print("   需要修复 CommonSwapResponseFees 模型")

            return

        print("\n" + "=" * 60)

        # 步骤4: 准备交易数据
        print("[步骤4] 准备交易数据...")

        try:
            # 创建 EncodedCall
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

        # 步骤5: 发送 user operation
        print("[步骤5] 发送 user operation...")

        try:
            # 需要获取 owner 的私钥来签名
            # 这里有个问题：我们需要 owner 的控制权才能签名
            print(f"⚠️  注意：需要 owner ({owner_address}) 的私钥来签名")
            print(f"   当前 Smart Account 的 owner 是外部账户")
            print(f"   无法通过 CDP SDK 自动签名")
            print(f"\n   需要使用 owner 的钱包来签名交易")

            # 尝试发送（会失败因为没有私钥）
            user_operation = await send_user_operation(
                api_clients=client.api_clients,
                address=smart_address,
                owner=None,  # ← 需要真实的 owner 对象
                calls=[contract_call],
                network='base',
            )

            print(f"\n✅ User operation 提交成功！")
            print(f"User Op Hash: {user_operation.user_op_hash}")
            print(f"状态: {user_operation.status}")

        except Exception as e:
            print(f"\n❌ 发送失败: {type(e).__name__}: {e}")

            if "owner" in str(e).lower() or "sign" in str(e).lower():
                print("\n⚠️  需要提供 owner 账户对象来签名")
                print(f"   Owner 地址: {owner_address}")
                print(f"   这个 owner 必须是通过 CDP SDK 创建的账户")
                print(f"   或者有私钥的外部账户")

    print("\n" + "=" * 60)


if __name__ == '__main__':
    asyncio.run(test_swap_with_list())
