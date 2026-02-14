#!/usr/bin/env python3
"""
使用 list_smart_accounts() + 伪造 owner 对象进行 swap

核心思路：
1. list_smart_accounts() 获取正确的 owners 字符串
2. 创建带 address 属性的 Owner 对象
3. 调用底层 API 进行 swap
"""

import asyncio
import sys
sys.path.insert(0, '.')

from cdp import CdpClient
from cdp.actions.evm.swap import create_swap_quote
from cdp.actions.evm.send_user_operation import send_user_operation
from cdp.evm_call_types import EncodedCall
from config import Config


async def test_swap_with_fake_owner():
    """使用伪造的owner对象进行swap"""
    print("=" * 60)
    print("Smart Account Swap - 伪造owner对象")
    print("=" * 60)

    smart_address = "0x125379C903a4E90529A6DCDe40554418fA200399"

    async with CdpClient(
        api_key_id=Config.CDP_API_KEY_ID,
        api_key_secret=Config.CDP_API_KEY_SECRET,
        wallet_secret=Config.CDP_WALLET_SECRET
    ) as client:
        # 步骤1: 获取owners地址
        print("\n[1] 获取owners...")
        list_result = await client.evm.list_smart_accounts()

        owner_address = None
        for acc in list_result.accounts:
            if acc.address == smart_address:
                owner_address = acc.owners[0]
                print(f"✅ Owner地址: {owner_address}")
                break

        if not owner_address:
            print("❌ 未找到owner")
            return

        # 步骤2: 查询余额
        print("\n[2] 查询余额...")
        balances = await client.evm.list_token_balances(
            address=smart_address,
            network='base'
        )

        eth_balance = 0
        for b in balances.balances:
            if b.token.symbol == 'ETH':
                eth_balance = float(b.amount.amount) / (10 ** b.amount.decimals)

        print(f"✅ ETH余额: {eth_balance}")

        swap_amount = min(0.002, eth_balance)
        from_amount = str(int(swap_amount * 10 ** 18)

        print(f"Swap数量: {swap_amount} ETH ({from_amount} wei)")

        # 步骤3: 创建swap quote
        print("\n[3] 创建swap quote...")
        try:
            swap_quote = await create_swap_quote(
                api_clients=client.api_clients,
                from_token=Config.ETH_ADDRESS,
                to_token=Config.USDC_ADDRESS,
                from_amount=from_amount,
                network='base',
                taker=smart_address,
                slippage_bps=100
            )

            print(f"✅ Quote创建成功")
            print(f"   预期: {swap_quote.to_amount} USDC")

        except Exception as e:
            print(f"❌ Quote创建失败: {e}")
            return

        # 步骤4: 创建伪造的owner对象
        print("\n[4] 创建owner对象...")

        # 方法A: 简单的Owner类
        class SimpleOwner:
            def __init__(self, address):
                self.address = address

        owner_obj = SimpleOwner(owner_address)
        print(f"✅ Owner对象创建: {owner_obj.address}")

        # 步骤5: 准备交易调用
        print("\n[5] 准备交易...")
        contract_call = EncodedCall(
            to=swap_quote.to,
            data=swap_quote.data,
            value=int(swap_quote.value) if swap_quote.value else 0,
        )

        print(f"✅ 交易数据准备完成")

        # 步骤6: 尝试发送user operation
        print("\n[6] 发送user operation...")

        try:
            # 尝试方法A：直接用owner对象
            print("尝试方法A: 使用owner对象...")

            user_op = await send_user_operation(
                api_clients=client.api_clients,
                address=smart_address,
                owner=owner_obj,
                calls=[contract_call],
                network='base',
            )

            print(f"\n✅ 成功！")
            print(f"User Op Hash: {user_op.user_op_hash}")
            print(f"状态: {user_op.status}")

        except Exception as e:
            print(f"\n❌ 方法A失败: {type(e).__name__}: {e}")

            # 尝试方法B: 获取真实的owner账户对象
            print("\n尝试方法B: 获取真实owner账户...")

            try:
                # 用owner地址获取账户对象
                owner_account = await client.evm.get_account(
                    address=owner_address
                )

                print(f"✅ Owner账户类型: {type(owner_account).__name__}")
                print(f"   地址: {owner_account.address}")

                # 再次尝试发送
                user_op = await send_user_operation(
                    api_clients=client.api_clients,
                    address=smart_address,
                    owner=owner_account,
                    calls=[contract_call],
                    network='base',
                )

                print(f"\n✅ 成功！")
                print(f"User Op Hash: {user_op.user_op_hash}")
                print(f"状态: {user_op.status}")

            except Exception as e2:
                print(f"\n❌ 方法B也失败: {type(e2).__name__}: {e2}")

    print("\n" + "=" * 60)


if __name__ == '__main__':
    asyncio.run(test_swap_with_fake_owner())
