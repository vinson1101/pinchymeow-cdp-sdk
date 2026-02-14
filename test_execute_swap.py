#!/usr/bin/env python3
"""
测试 EOA 交易功能

测试 execute_swap() 方法是否能正常工作
"""

import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from src.cdp_core.cdp_trader import CDPTrader


async def test_execute_swap():
    """测试 execute_swap"""
    print("=" * 60)
    print("测试 EOA 交易功能")
    print("=" * 60)

    # 初始化 trader
    print("\n[1] 初始化 Trader...")
    trader = CDPTrader(
        account_name='F0X_TRADING',
        agent_name='F0x'
    )
    print(f"✅ Account: {trader.account_name}")
    print(f"✅ Address: {trader.account_address}")

    # 测试小额交易（USDC → ETH）
    print("\n[2] 测试小额交易 ($0.50 USDC → ETH)...")
    try:
        result = await trader.execute_swap(
            from_token='usdc',
            to_token='eth',
            amount=0.50,  # $0.50
            slippage_bps=100  # 1%
        )

        print(f"Status: {result['status']}")
        print(f"Message: {result.get('message', 'N/A')}")
        if result.get('tx_hash'):
            print(f"TX Hash: {result['tx_hash']}")
            print(f"\n✅ 交易成功！")
            print(f"查看: https://basescan.org/tx/{result['tx_hash']}")
        else:
            print(f"\n❌ 交易失败")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

    await trader.close()

    print("\n" + "=" * 60)


if __name__ == '__main__':
    asyncio.run(test_execute_swap())
