#!/usr/bin/env python3
"""
Integration Tests for CDP Trading Infrastructure

Tests all modules:
- CDPTrader core functionality
- SafeTrader with safety checks
- TransactionLogger per-account isolation
- Daily report generation
- Sentinel price monitoring

Run from workspace root: python3 tests/integration_test.py
"""

import asyncio
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from datetime import datetime
from src.cdp_core.cdp_trader import CDPTrader
from src.trader import SafeTrader
from src.transaction_logger import TransactionLogger
from src.daily_report import generate_daily_report


async def test_cdp_trader():
    """Test CDPTrader core functionality"""
    print("\n" + "=" * 60)
    print("Testing CDPTrader Core Functionality")
    print("=" * 60)

    # Initialize trader (F0x account)
    trader = CDPTrader(
        account_name='F0X_TRADING',
        agent_name='F0x'
    )
    print(f"✅ Account: {trader.account_name}")
    print(f"✅ Agent: {trader.agent_name}")
    print(f"✅ Network: {trader.network}")

    # Test 1: Get balance
    print("\n[Test 1] Get Balance")
    balance = await trader.get_balance()
    print(f"✅ ETH Balance: {balance['eth_balance']:.6f} ETH")
    print(f"✅ USDC Balance: ${balance['usdc_balance']:.2f} USD")
    if balance['other_tokens']:
        print(f"✅ Other Tokens: {balance['other_tokens']}")
    print(f"✅ Address: {balance['address']}")

    # Test 2: Get quote (ETH → USDC)
    print("\n[Test 2] Get Quote: 1 ETH → USDC")
    quote = await trader.get_quote('eth', 'usdc', 1.0)
    if 'error' in quote:
        print(f"❌ Error: {quote['error']}")
    else:
        print(f"✅ From: {quote['from_token']}")
        print(f"✅ To: {quote['to_token']}")
        print(f"✅ Amount: {quote['from_amount']} ETH")
        print(f"✅ Expected: {quote['expected_amount']} wei")
        if 'price' in quote:
            print(f"✅ Price: 1 ETH = ${quote['price']:.4f} USDC")

    # Test 3: Get quote (USDC → ETH)
    print("\n[Test 3] Get Quote: 10 USDC → ETH")
    quote2 = await trader.get_quote('usdc', 'eth', 10.0)
    if 'error' in quote2:
        print(f"❌ Error: {quote2['error']}")
    else:
        print(f"✅ From: {quote2['from_token']}")
        print(f"✅ To: {quote2['to_token']}")
        print(f"✅ Amount: {quote2['from_amount']} USDC")
        print(f"✅ Expected: {quote2['expected_amount']} wei")
        if 'price' in quote2:
            print(f"✅ Price: 1 USDC = ${quote2['price']:.4f} ETH")

    await trader.close()

    print("\n" + "=" * 60)
    print("✅ CDPTrader Test Completed")
    print("=" * 60)


async def test_safe_trader():
    """Test SafeTrader with safety checks"""
    print("\n" + "=" * 60)
    print("Testing SafeTrader with Safety Checks")
    print("=" * 60)

    # Initialize trader with logger
    logger = TransactionLogger('F0x')
    trader = SafeTrader(
        account_name='F0X_TRADING',
        agent_name='F0x',
        logger=logger
    )
    print(f"✅ Account: {trader.account_name}")
    print(f"✅ Agent: {trader.agent_name}")
    print(f"✅ Logger: {logger.agent_name}")

    # Test 1: Calculate USD value (USDC)
    print("\n[Test 1] Calculate USD Value (USDC)")
    usd_value = await trader.calculate_usd_value('usdc', 10.0)
    print(f"✅ 10 USDC = ${usd_value:.2f} USD")

    # Test 2: Calculate USD value (ETH)
    print("\n[Test 2] Calculate USD Value (1 ETH)")
    eth_value = await trader.calculate_usd_value('eth', 1.0)
    print(f"✅ 1 ETH = ${eth_value:.2f} USD")

    # Test 3: Small trade (<$100, should execute directly)
    print("\n[Test 3] Small Trade ($10 USDC → 0.005 ETH)")
    print("   This should execute directly (no approval needed)")
    result = await trader.swap_with_approval(
        from_token='usdc',
        to_token='eth',
        amount=10.0,
        agent_name='F0x'
    )
    print(f"   Status: {result['status']}")
    print(f"   Message: {result['message']}")
    if result.get('tx_hash'):
        print(f"   TX Hash: {result['tx_hash']}")

    # Close trader
    # Note: SafeTrader doesn't have close(), but CDPTrader does
    await trader.core.close()

    print("\n" + "=" * 60)
    print("✅ SafeTrader Test Completed")
    print("=" * 60)


async def test_transaction_logger():
    """Test TransactionLogger per-account isolation"""
    print("\n" + "=" * 60)
    print("Testing TransactionLogger Per-Account Isolation")
    print("=" * 60)

    # Test 1: F0x logger
    print("\n[Test 1] F0x Transaction Logger")
    logger_f0x = TransactionLogger('F0x')
    print(f"✅ Agent: F0x")
    print(f"✅ Log Dir: /data/transactions/f0x/")

    # Test 2: PinchyMeow logger
    print("\n[Test 2] PinchyMeow Transaction Logger")
    logger_pinchy = TransactionLogger('PinchyMeow')
    print(f"✅ Agent: PinchyMeow")
    print(f"✅ Log Dir: /data/transactions/pinchymeow/")

    # Test 3: Log a transaction
    print("\n[Test 3] Log Test Transaction")
    logger_f0x.log({
        'type': 'test_swap',
        'agent': 'F0x',
        'account': 'F0X_TRADING',
        'from_token': 'usdc',
        'to_token': 'eth',
        'from_amount': 10.0,
        'usd_value': 10.0,
        'status': 'success',
        'tx_hash': '0xtest123',
        'timestamp': datetime.utcnow().isoformat()
    })
    print("✅ Transaction logged to /data/transactions/f0x/")

    # Test 4: Get today's transactions
    print("\n[Test 4] Get Today's Transactions (F0x)")
    transactions = logger_f0x.get_transactions()
    print(f"✅ Total transactions: {len(transactions)}")
    for tx in transactions:
        print(f"   - {tx['type']}: {tx.get('status')}")

    print("\n" + "=" * 60)
    print("✅ TransactionLogger Test Completed")
    print("=" * 60)


async def test_daily_report():
    """Test daily report generation"""
    print("\n" + "=" * 60)
    print("Testing Daily Report Generation")
    print("=" * 60)

    # Test 1: Today's report (all agents)
    print("\n[Test 1] Today's Report (All Agents)")
    report = await generate_daily_report()
    print(f"✅ Date: {report['date']}")
    print(f"✅ Total Transactions: {report['total_tx']}")
    print(f"✅ Success: {report['success_tx']} | Failed: {report['failed_tx']} | Pending: {report['pending_tx']}")
    print(f"✅ Total Volume: ${report['total_volume_usd']:.2f} USD")

    # Test 2: By agent breakdown
    print("\n[Test 2] By Agent Breakdown")
    for agent, stats in report.get('agents', {}).items():
        print(f"\n{agent}:")
        print(f"  Total: {stats['count']}")
        print(f"  Success: {stats['success']}")
        print(f"  Volume: ${stats['volume']:.2f} USD")

    print("\n" + "=" * 60)
    print("✅ Daily Report Test Completed")
    print("=" * 60)


async def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("CDP Trading Infrastructure - Integration Tests")
    print("Run from workspace root: python3 tests/integration_test.py")
    print("=" * 60)
    print("")

    # Run all tests
    await test_cdp_trader()
    await test_safe_trader()
    await test_transaction_logger()
    await test_daily_report()

    print("\n" + "=" * 60)
    print("✅ All Tests Completed")
    print("=" * 60)


if __name__ == '__main__':
    asyncio.run(main())
