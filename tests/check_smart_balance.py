#!/usr/bin/env python3
"""
检查 Smart Account 余额

测试 USDC 和 ETH 余额
"""

import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from cdp import CdpClient


async def check_smart_balance():
    """检查 Smart Account 余额"""
    print("=" * 60)
    print("检查 Smart Account 余额")
    print("=" * 60)

    async with CdpClient(
        api_key_id='ca7ee92c-d269-4715-ae9b-1c9d75339a27',
        api_key_secret='B5+rm8t6l3XZT6PJoko+7VeU4Ct0kXyv91ky8nB7ApFFL0FQemn+x4mdogua4vBzNKm55RGjdj8iUftGNA7xvw=='
    ) as client:
        smart_address = Config.AGENT_ACCOUNTS.get('F0x').get('smart')
        print(f"Smart Account: {smart_address}\n")

        try:
            # Get Smart Account
            smart_account = await client.evm.get_smart_account(address=smart_address)
            print(f"✅ Name: {smart_account.name}")
            print(f"✅ Address: {smart_account.address}")
            print(f"✅ Type: {type(smart_account).__name__}")
            
            # Check balance
            from cdp.actions.evm import list_token_balances
            
            print(f"\n正在查询余额...")
            balances = await list_token_balances(
                api_clients=client.api_clients,
                address=smart_account.address,
                network='base'
            )
            
            print(f"✅ 余额查询完成！")
            
            print("\n当前余额:")
            for token, balance in balances.balances.items():
                amount = float(balance.amount) / (10 ** balance.amount.decimals)
                print(f"  {token}: {amount}")
            
            # Check specifically for ETH and USDC
            eth_balance = None
            usdc_balance = None
            
            for token, balance in balances.balances.items():
                if token.upper() == 'ETH' or 'ethereum' in token.lower():
                    eth_balance = float(balance.amount) / (10 ** balance.amount.decimals)
                elif token.upper() in ['USDC', 'USDC'] or 'usdc' in token.lower():
                    usdc_balance = float(balance.amount) / (10 ** balance.amount.decimals)
            
            print(f"\n代币余额:")
            if eth_balance:
                print(f"  ETH: {eth_balance:.6f}")
            else:
                print(f"  ETH: 0")
            if usdc_balance:
                print(f"  USDC: {usdc_balance:.2f}")
            else:
                print(f"  USDC: 0")
        
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
    
    await client.close()

    print("\n" + "=" * 60)


if __name__ == '__main__':
    asyncio.run(check_smart_balance())
