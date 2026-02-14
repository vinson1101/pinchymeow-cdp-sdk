#!/usr/bin/env python3
"""
检查账户的 ETH Gas 余额

EOA 账户必须持有 ETH 才能交易
"""

import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from src.cdp_core.cdp_trader import CDPTrader


async def check_gas_balance():
    """检查 ETH 余额"""
    print("=" * 60)
    print("检查 Gas 余额")
    print("=" * 60)

    # 初始化 trader
    trader = CDPTrader(
        account_name='F0X_TRADING',
        agent_name='F0x'
    )
    print(f"账户: {trader.account_name}")
    print(f"地址: {trader.account_address}\n")

    # 获取余额
    balance = await trader.get_balance()

    print("=" * 60)
    print("当前余额:")
    print("=" * 60)
    print(f"ETH:  {balance['eth_balance']:.6f} ETH")
    print(f"USDC: ${balance['usdc_balance']:.2f} USD")

    # 检查是否有足够的 ETH
    eth_balance = balance['eth_balance']
    min_gas = 0.0001  # 最小需要的 ETH (约 $0.3-$0.5)

    print("\n" + "=" * 60)
    if eth_balance >= min_gas:
        print(f"✅ ETH 余额充足 ({eth_balance:.6f} >= {min_gas:.6f})")
        print("✅ 可以进行交易")
    else:
        print(f"❌ ETH 余额不足 ({eth_balance:.6f} < {min_gas:.6f})")
        print(f"❌ 无法进行交易")
        print(f"\n需要:")
        print(f"  1. 向地址转入约 $1-$2 的 Base ETH")
        print(f"  2. 地址: {trader.account_address}")
        print(f"  3. 网络: Base mainnet")

    print("=" * 60)

    await trader.close()


if __name__ == '__main__':
    asyncio.run(check_gas_balance())
