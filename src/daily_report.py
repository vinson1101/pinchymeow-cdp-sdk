#!/usr/bin/env python3
"""
Daily Report Generator

Generates daily trading reports from transaction logs

Author: Vinson <sun1101>
Created: 2026-02-14
Version: 1.0.0
"""

import os
import sys
from datetime import datetime
from typing import Dict, Any, List

# Add parent directory to path
sys.path.insert(0, '/root/.openclaw/workspace/pinchymeow-cdp-sdk')

from src.transaction_logger import TransactionLogger
from config import Config


async def generate_daily_report(
    date: str = None,
    agent_name: str = None
) -> Dict[str, Any]:
    """
    Generate daily trading report

    Args:
        date: Date in YYYY-MM-DD format (default: today)
        agent_name: Filter by agent name (optional)

    Returns:
        Dict with:
            date: str
            total_tx: int
            success_tx: int
            failed_tx: int
            pending_tx: int
            total_volume_usd: float
            agents: dict (agent_name -> stats)
    """
    # Get date string
    if date is None:
        date = datetime.utcnow().strftime('%Y-%m-%d')

    # Get all agents
    agents = agent_name if agent_name else None

    if agents:
        agents_list = [agents]
    else:
        agents_list = Config.AGENT_ACCOUNT_PREFIX.keys()

    # Initialize stats
    stats = {
        'date': date,
        'total_tx': 0,
        'success_tx': 0,
        'failed_tx': 0,
        'pending_tx': 0,
        'total_volume_usd': 0.0,
        'agents': {
            agent: {
                'count': 0,
                'volume': 0.0,
                'success': 0,
                'failed': 0,
                'pending': 0
            }
            for agent in agents_list
        }
    }

    # Read transactions for each agent
    for agent in agents_list:
        logger = TransactionLogger(agent_name=agent)
        transactions = logger.get_transactions(date)

        for tx in transactions:
            # Count by status
            status = tx.get('status', 'unknown')
            if status == 'success':
                stats['agents'][agent]['success'] += 1
                stats['success_tx'] += 1
            elif status == 'failed':
                stats['agents'][agent]['failed'] += 1
                stats['failed_tx'] += 1
            elif status == 'pending' or status == 'requires_approval':
                stats['agents'][agent]['pending'] += 1
                stats['pending_tx'] += 1

            stats['agents'][agent]['count'] += 1

            # Accumulate volume
            usd_value = tx.get('usd_value', 0.0)
            if isinstance(usd_value, (int, float)):
                stats['total_volume_usd'] += float(usd_value)
                stats['agents'][agent]['volume'] += float(usd_value)

        stats['total_tx'] += stats['agents'][agent]['count']

    # Print report
    print("\n" + "=" * 60)
    print(f"每日交易报告 - {date}")
    print("=" * 60)

    # Summary
    print("\n总览:")
    print(f"  总交易: {stats['total_tx']}")
    print(f"  成功: {stats['success_tx']} | 失败: {stats['failed_tx']} | 待定: {stats['pending_tx']}")
    print(f"  总交易额: ${stats['total_volume_usd']:.2f} USD")

    # By agent
    print("\n按 Agent 分组:")
    for agent, data in stats['agents'].items():
        if data['count'] > 0:
            print(f"\n  {agent}:")
            print(f"    交易: {data['count']}")
            print(f"    成功: {data['success']} | 失败: {data['failed']} | 待定: {data['pending']}")
            print(f"    交易额: ${data['volume']:.2f} USD")

    print("\n" + "=" * 60)


async def main():
    """Main entry point"""
    # Parse arguments
    if len(sys.argv) > 1:
        arg = sys.argv[1]
        if arg == '--agent':
            # Filter by agent
            if len(sys.argv) > 2:
                agent_name = sys.argv[2]
                await generate_daily_report(agent_name=agent_name)
            else:
                print("Usage: python daily_report.py --agent <agent_name>")
                print("Example: python daily_report.py --agent f0x")
        else:
            # Specific date
            await generate_daily_report(date=arg)
    else:
        # Today's report
        await generate_daily_report()


if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
