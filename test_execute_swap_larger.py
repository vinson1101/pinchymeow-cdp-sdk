#!/usr/bin/env python3
"""
测试更大金额的交易

$0.50 可能太小导致流动性不足，尝试 $2.00
"""

import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from src.cdp_core.cdp_trader import CDPTrader


async def test_larger_trade():
    """测试更大金额的交易"""
    print("=" * 60)
    print("测试大额交易 ($2.00 USDC → ETH)")
    print("=" * 60)

    # 初始化 trader
    trader = CDPTrader(
        account_name='F0X_TRADING',
        agent_name='F0x'
    )
    print(f"账户: {trader.account_name}")
    print(f"地址: {trader.account_address}\n")

    # 先检查余额
    balance = await trader.get_balance()
    print(f"余额: ETH={balance['eth_balance']:.6f}, USDC=${balance['usdc_balance']:.2f}\n")

    # 测试 $2.00 交易
    print("[测试] $2.00 USDC → ETH...")
    try:
        result = await trader.execute_swap(
            from_token='usdc',
            to_token='eth',
            amount=2.00,  # $2.00 (全部 USDC)
            slippage_bps=100  # 1%
        )

        print(f"状态: {result['status']}")
        print(f"消息: {result.get('message', 'N/A')}")
        if result.get('tx_hash'):
            print(f"TX Hash: {result['tx_hash']}")
            print(f"\n✅ 交易成功！")
            print(f"查看: https://basescan.org/tx/{result['tx_hash']}")
        else:
            print(f"\n❌ 交易失败")
            if 'error' in result:
                print(f"错误详情: {result['error']}")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

    await trader.close()

    print("\n" + "=" * 60)


if __name__ == '__main__':
    asyncio.run(test_larger_trade())
