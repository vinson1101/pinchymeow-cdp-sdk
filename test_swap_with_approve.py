#!/usr/bin/env python3
import asyncio
import sys
sys.path.insert(0, '.')

from cdp import CdpClient
from cdp.actions.evm.swap import create_swap_quote
from cdp.actions.evm.send_user_operation import send_user_operation
from cdp.actions.evm.send_transaction import send_transaction
from cdp.evm_call_types import EncodedCall, TransactionRequest
from config import Config

async def test_swap_with_permit2():
    print("=" * 60)
    print("完整流程：Permit2授权 + Swap")
    print("=" * 60)

    smart = "0x125379C903a4E90529A6DCDe40554418fA200399"
    permit2 = "0x000000000022D473730EF32254ad802b0812a8278"

    async with CdpClient(
        api_key_id=Config.CDP_API_KEY_ID,
        api_key_secret=Config.CDP_API_KEY_SECRET,
        wallet_secret=Config.CDP_WALLET_SECRET
    ) as client:
        # 步骤1: 获取owners
        list_result = await client.evm.list_smart_accounts()
        owner_addr = None
        for acc in list_result.accounts:
            if acc.address == smart:
                owner_addr = acc.owners[0]
                print(f"Owner: {owner_addr}")
                break

        print("\n" + "=" * 60)
        print("步骤1: Permit2授权")
        print("=" * 60)

        # 准备approve交易
        print("\n准备approve交易...")

        # 方法签名：approve(address,uint256)
        approve_sig = owner_addr + "0000000000000000000000000000000000000000000000000000000002"  # func selector
        approve_sig += "0" + "0" * 63  # address padded
        approve_sig += "00000000000000000000000000000000000000000000000000000000000"  # amount (uint256 max)

        print(f"函数：approve(address,uint256)")
        print(f"spender: {smart}")
        print(f"token地址：{permit2}")

        # 创建TransactionRequest
        approve_req = TransactionRequest(
            to=Config.ETH_ADDRESS,
            data=approve_sig,
            value="0",
        )

        # Fake owner
        class FakeOwner:
            def __init__(self, addr):
                self.address = addr

        owner_obj = FakeOwner(owner_addr)

        # 发送approve
        print("\n发送approve交易...")
        try:
            approve_tx = await send_transaction(
                api_clients=client.api_clients,
                address=smart,
                owner=owner_obj,
                transaction=approve_req,
                network='base',
            )
            print(f"✅ Approve交易已发送！")
            print(f"TX Hash: {approve_tx.transaction_hash}")

        except Exception as e:
            print(f"❌ Approve失败：{type(e).__name__}: {e}")

            # 检查是否是签名问题
            if "sign" in str(e).lower():
                print("\n这是签名错误，说明:")
                print("1. FakeOwner对象无法用于签名")
                print("2. 需要真实的owner账户对象")
                print(f"\n当前owner地址：{owner_addr}")
                print(f"这个账户是通过CDP SDK创建的EOA账户")
                print(f"可以通过client.evm.get_account()获取对象")

                # 尝试获取真实owner对象
                print("\n尝试获取真实owner对象...")
                try:
                    real_owner = await client.evm.get_account(
                        address=owner_addr
                    )
                    print(f"✅ Owner对象类型：{type(real_owner).__name__}")
                    print(f"   地址：{real_owner.address}")

                    # 重新发送approve
                    print("\n使用真实owner对象重新发送...")
                    approve_tx2 = await send_transaction(
                        api_clients=client.api_clients,
                        address=smart,
                        owner=real_owner,
                        transaction=approve_req,
                        network='base',
                    )
                    print(f"✅ Approve交易已发送！")
                    print(f"TX Hash: {approve_tx2.transaction_hash}")

                except Exception as e2:
                    print(f"❌ 获取真实owner失败：{type(e2).__name__}: {e2}")

        print("\n" + "=" * 60)
        print("\n步骤2: Swap")
        print("=" * 60)

        # 等待approve确认
        print("\n等待approve确认...")
        await asyncio.sleep(5)

        # 创建swap quote
        from_amt = "1000000000000000"
        print(f"\nSwap: 0.001 ETH")

        try:
            swap_quote = await create_swap_quote(
                api_clients=client.api_clients,
                from_token=Config.ETH_ADDRESS,
                to_token=Config.USDC_ADDRESS,
                from_amount=from_amt,
                network='base',
                taker=smart,
                slippage_bps=100
            )

            print(f"✅ Quote创建成功")
            print(f"预期输出：{swap_quote.to_amount} USDC")

            # 准备swap调用
            call = EncodedCall(
                to=swap_quote.to,
                data=swap_quote.data,
                value=int(swap_quote.value) if swap_quote.value else 0,
            )

            print("\n发送swap交易...")
            user_op = await send_user_operation(
                    api_clients=client.api_clients,
                    address=smart,
                    owner=owner_obj,
                    calls=[call],
                    network='base',
                )
            print(f"✅ Swap成功！")
            print(f"User Op Hash：{user_op.user_op_hash}")
            print(f"状态：{user_op.status}")

        except Exception as e:
            print(f"❌ Swap失败：{type(e).__name__}: {e}")

    print("\n" + "=" * 60)

if __name__ == "__main__":
    asyncio.run(test_swap_with_permit2())
