#!/usr/bin/env python3
import asyncio
import sys
sys.path.insert(0, '.')

from cdp import CdpClient
from cdp.actions.evm.swap.types import SmartAccountSwapOptions
from config import Config

async def test_swap():
    print("=" * 60)
    print("获取真实Owner对象 + Swap")
    print("=" * 60)
    
    smart_addr = "0x125379C903a4E90529A6DCDe40554418fA200399"
    
    async with CdpClient(
        api_key_id=Config.CDP_API_KEY_ID,
        api_key_secret=Config.CDP_API_KEY_SECRET,
        wallet_secret=Config.CDP_WALLET_SECRET
    ) as client:
        list_result = await client.evm.list_smart_accounts()
        owner_addr = None
        for acc in list_result.accounts:
            if acc.address == smart_addr:
                owner_addr = acc.owners[0]
                print(f"Owner地址: {owner_addr}")
                break
        
        balances = await client.evm.list_token_balances(
            address=smart_addr, network='base'
        )
        
        eth_bal = 0
        for b in balances.balances:
            if b.token.symbol == 'ETH':
                eth_bal = float(b.amount.amount) / (10 ** b.amount.decimals)
        
        print(f"ETH余额: {eth_bal}")
        
        print("\n获取真实Owner对象...")
        owner_account = await client.evm.get_account(
            address=owner_addr
        )
        
        print(f"Owner类型: {type(owner_account).__name__}")
        print(f"Owner地址: {owner_account.address}")
        print(f"有sign(): {hasattr(owner_account, 'sign')}")
        
        print("\n获取Smart Account对象...")
        smart_account = await client.evm.get_smart_account(
            address=smart_addr
        )
        
        print(f"Smart类型: {type(smart_account).__name__}")
        print(f"Smart地址: {smart_account.address}")
        print(f"Owners: {smart_account.owners}")
        
        print("\n执行Swap: 0.001 ETH to USDC")
        
        from_amt = "1000000000000000"
        
        try:
            result = await smart_account.swap(
                SmartAccountSwapOptions(
                    network='base',
                    from_token=Config.ETH_ADDRESS,
                    to_token=Config.USDC_ADDRESS,
                    from_amount=from_amt,
                    slippage_bps=100
                )
            )
            
            print(f"\n成功！")
            print(f"TX Hash: {result.transaction_hash}")
        
        except AttributeError as e:
            if "'NoneType' object has no attribute 'address'" in str(e):
                print(f"\nOwners bug: owners[0]是None")
                print(f"尝试使用底层API...")
                
                from cdp.actions.evm.swap import send_swap_operation
                from cdp.actions.evm.swap.send_swap_operation import SendSwapOperationOptions
                
                options = SendSwapOperationOptions(
                    smart_account=smart_account,
                    network='base',
                    from_token=Config.ETH_ADDRESS,
                    to_token=Config.USDC_ADDRESS,
                    from_amount=from_amt,
                    slippage_bps=100
                )
                
                result = await send_swap_operation(
                    api_clients=client.api_clients,
                    options=options
                )
                
                print(f"\n成功！")
                print(f"User Op Hash: {result.user_op_hash}")
            
            else:
                print(f"\n错误: {e}")
        
        except Exception as e:
            error_str = str(e)
            print(f"\nSwap失败: {type(e).__name__}")
            print(f"错误: {error_str[:300]}")

if __name__ == "__main__":
    asyncio.run(test_swap())
