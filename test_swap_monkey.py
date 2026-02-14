#!/usr/bin/env python3
import asyncio
import sys
sys.path.insert(0, '.')

from cdp import CdpClient
from cdp.actions.evm.swap.types import SmartAccountSwapOptions
from config import Config

async def test_swap_monkey_patch():
    print("=" * 60)
    print("Monkey Patch 修复 Owners + Swap")
    print("=" * 60)
    
    smart_addr = "0x125379C903a4E90529A6DCDe40554418fA200399"
    
    async with CdpClient(
        api_key_id=Config.CDP_API_KEY_ID,
        api_key_secret=Config.CDP_API_KEY_SECRET,
        wallet_secret=Config.CDP_WALLET_SECRET
    ) as client:
        print("\n步骤1: 获取Owners地址...")
        
        list_result = await client.evm.list_smart_accounts()
        owner_addr = None
        for acc in list_result.accounts:
            if acc.address == smart_addr:
                owner_addr = acc.owners[0]
                print(f"Owner: {owner_addr}")
                break
        
        print("\n步骤2: 查询余额...")
        
        balances = await client.evm.list_token_balances(
            address=smart_addr,
            network='base'
        )
        
        eth_bal = 0
        for b in balances.balances:
            if b.token.symbol == 'ETH':
                eth_bal = float(b.amount.amount) / (10 ** b.amount.decimals)
        
        print(f"ETH余额: {eth_bal}")
        
        print("\n步骤3: 获取Smart Account...")
        
        smart_account = await client.evm.get_smart_account(
            address=smart_addr
        )
        
        print(f"Owners before patch: {smart_account.owners}")
        
        if not smart_account.owners or smart_account.owners[0] is None:
                print("\n检测到owners bug，执行monkey patch...")
                
                class OwnerWithAddress:
                    def __init__(self, addr):
                        self.address = addr
                
                fixed_owner = OwnerWithAddress(owner_addr)
                smart_account.owners = [fixed_owner]
                
                print(f"Owners after patch: {[(o.address if hasattr(o, 'address') else o for o in smart_account.owners]}")
        
        print("\n步骤4: 执行Swap...")
        
        from_amt = "1000000000000000"
        print(f"Swap: 0.001 ETH to USDC")
        
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
                print(f"\nOwners patch失败")
            else:
                print(f"\n错误: {e}")
        
        except Exception as e:
            error_str = str(e)
            print(f"\nSwap失败: {type(e).__name__}")
            
            if "gasFee" in error_str:
                print(f"Gas Fee错误（应该已修复）")
            elif "liquidity" in error_str.lower():
                print(f"流动性问题")
            elif "owner" in error_str.lower():
                print(f"Owner签名问题")
            else:
                print(f"错误: {error_str[:200]}")

if __name__ == "__main__":
    asyncio.run(test_swap_monkey_patch())
