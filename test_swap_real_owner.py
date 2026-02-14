#!/usr/bin/env python3
import asyncio
import sys
sys.path.insert(0, '.')

from cdp import CdpClient
from cdp.actions.evm.swap.types import SmartAccountSwapOptions
from config import Config

async def test_swap_real_owner():
    print("=" * 60)
    print("使用真实 Owner 对象进行 Swap")
    print("=" * 60)
    
    smart_addr = "0x125379C903a4E90529A6DCDe40554418fA200399"
    
    async with CdpClient(
        api_key_id=Config.CDP_API_KEY_ID,
        api_key_secret=Config.CDP_API_KEY_SECRET,
        wallet_secret=Config.CDP_WALLET_SECRET
    ) as client:
        print("\n步骤1: 获取Smart Account信息...")
        
        # 从list获取owner地址
        list_result = await client.evm.list_smart_accounts()
        owner_addr = None
        for acc in list_result.accounts:
            if acc.address == smart_addr:
                owner_addr = acc.owners[0]
                print(f"Smart Account: {acc.name}")
                print(f"Owner地址: {owner_addr}")
                break
        
        print("\n步骤2: 获取真实Owner对象...")
        
        # 获取owner账户对象
        owner_account = await client.evm.get_account(
            address=owner_addr
        )
        
        print(f"Owner类型: {type(owner_account).__name__}")
        print(f"Owner地址: {owner_account.address}")
        
        print("\n步骤3: 查询余额...")
        
        balances = await client.evm.list_token_balances(
            address=smart_addr,
            network='base'
        )
        
        eth_bal = 0
        for b in balances.balances:
            if b.token.symbol == 'ETH':
                eth_bal = float(b.amount.amount) / (10 ** b.amount.decimals)
        
        print(f"ETH余额: {eth_bal}")
        
        print("\n步骤4: 执行Swap...")
        
        from_amt = "1000000000000000"
        print(f"Swap: 0.001 ETH to USDC")
        
        try:
            # 获取smart account对象
            smart_account = await client.evm.get_smart_account(
                address=smart_addr
            )
            
            # 尝试swap
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
                print(f"这是SDK的已知bug")
            else:
                print(f"\n错误: {e}")
        
        except Exception as e:
            print(f"\nSwap失败: {type(e).__name__}: {e}")
            
            if "gasFee" in str(e):
                print(f"\nGas Fee验证错误（应该已修复）")
            elif "owner" in str(e).lower():
                print(f"\nOwner相关错误")

if __name__ == "__main__":
    asyncio.run(test_swap_real_owner())
