#!/usr/bin/env python3
import asyncio
import sys
sys.path.insert(0, '.')

from cdp import CdpClient
from cdp.actions.evm.swap import create_swap_quote
from cdp.actions.evm.send_user_operation import send_user_operation
from cdp.evm_call_types import EncodedCall
from config import Config

async def test_swap():
    print("=" * 60)
    print("Smart Account Swap - 简单版本")
    print("=" * 60)

    smart = "0x125379C903a4E90529A6DCDe40554418fA200399"

    async with CdpClient(
        api_key_id=Config.CDP_API_KEY_ID,
        api_key_secret=Config.CDP_API_KEY_SECRET,
        wallet_secret=Config.CDP_WALLET_SECRET
    ) as client:
        # Get owners from list
        list_result = await client.evm.list_smart_accounts()
        owner_addr = None
        for acc in list_result.accounts:
            if acc.address == smart:
                owner_addr = acc.owners[0]
                print(f"Owner: {owner_addr}")
                break

        if not owner_addr:
            print("Owner not found")
            return

        # Get balances
        balances = await client.evm.list_token_balances(address=smart, network='base')
        eth_bal = 0
        for b in balances.balances:
            if b.token.symbol == 'ETH':
                eth_bal = float(b.amount.amount) / (10 ** b.amount.decimals)

        amount = min(0.002, eth_bal)
        from_amt = str(int(amount * 10 ** 18)

        print(f"Swap: {amount} ETH")
        print(f"From (wei): {from_amt}")

        # Create swap quote
        print("\nCreating swap quote...")
        swap_quote = await create_swap_quote(
            api_clients=client.api_clients,
            from_token=Config.ETH_ADDRESS,
            to_token=Config.USDC_ADDRESS,
            from_amount=from_amt,
            network='base',
            taker=smart,
            slippage_bps=100
        )

        print(f"Expected: {swap_quote.to_amount} USDC")

        # Prepare call
        call = EncodedCall(
            to=swap_quote.to,
            data=swap_quote.data,
            value=int(swap_quote.value) if swap_quote.value else 0,
        )

        # Create fake owner object
        class FakeOwner:
            def __init__(self, addr):
                self.address = addr

        owner_obj = FakeOwner(owner_addr)

        print("\nSending user operation...")
        try:
            user_op = await send_user_operation(
                api_clients=client.api_clients,
                address=smart,
                owner=owner_obj,
                calls=[call],
                network='base',
            )
            print(f"Success! User Op Hash: {user_op.user_op_hash}")
            print(f"Status: {user_op.status}")

        except Exception as e:
            print(f"Failed: {type(e).__name__}: {e}")

    print("\n" + "=" * 60)

if __name__ == "__main__":
    asyncio.run(test_swap())
