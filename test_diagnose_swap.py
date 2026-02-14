#!/usr/bin/env python3
import asyncio
import sys
sys.path.insert(0, '.')

from cdp import CdpClient
from config import Config

async def diagnose_swap():
    print("=" * 60)
    print("Swap 诊断 - 使用 quoteSwap()")
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
                print(f"Smart Account: {acc.name}")
                print(f"Owner: {owner_addr}")
                break
        
        print("\n" + "=" * 60)
        print("步骤1: 查询余额")
        print("=" * 60)
        
        balances = await client.evm.list_token_balances(address=smart, network='base')
        eth_bal = 0
        for b in balances.balances:
            if b.token.symbol == 'ETH':
                eth_bal = float(b.amount.amount) / (10 ** b.amount.decimals)
        
        print(f"ETH 余额: {eth_bal}")
        
        print("\n" + "=" * 60)
        print("步骤2: 创建 swap quote")
        print("=" * 60)
        
        from_amt = "1000000000000000"
        print(f"Swap: 0.001 ETH to USDC")
        print(f"Network: base")
        print(f"Slippage: 1%")
        
        try:
            # 使用 quoteSwap 获取诊断信息
            swap_quote = await client.evm.create_swap_quote(
                from_token=Config.ETH_ADDRESS,
                to_token=Config.USDC_ADDRESS,
                from_amount=from_amt,
                network='base',
                taker=smart,
                slippage_bps=100
            )
            
            print(f"\nLiquidity: {swap_quote.liquidity_available}")
            
            if hasattr(swap_quote, 'fees') and swap_quote.fees:
                print(f"\nGas Fee:")
                if hasattr(swap_quote.fees, 'gas_fee') and swap_quote.fees.gas_fee:
                    print(f"  Token: {swap_quote.fees.gas_fee.token}")
                    if hasattr(swap_quote.fees.gas_fee, 'amount'):
                        print(f"  Amount: {swap_quote.fees.gas_fee.amount}")
                else:
                    print(f"  None (gasless)")
            
            if hasattr(swap_quote, 'issues') and swap_quote.issues:
                print(f"\nIssues:")
                if hasattr(swap_quote.issues, 'balance') and swap_quote.issues.balance:
                    print(f"  Balance: {swap_quote.issues.balance}")
                if hasattr(swap_quote.issues, 'permit2') and swap_quote.issues.permit2:
                    print(f"  Permit2: {swap_quote.issues.permit2}")
            
            print(f"\nExpected Output: {swap_quote.to_amount} USDC")
            print(f"Min Output (1% slippage): {swap_quote.min_to_amount} USDC")
        
        except Exception as e:
            print(f"\nQuote failed: {type(e).__name__}: {e}")

if __name__ == "__main__":
    asyncio.run(diagnose_swap())
