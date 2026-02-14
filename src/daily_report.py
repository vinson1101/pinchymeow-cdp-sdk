#!/usr/bin/env python3
"""
Daily Report Generator

Generates daily trading statistics report from transaction logs.

Usage:
    python daily_report.py              # Today's report
    python daily_report.py 2026-02-14   # Specific date report

Author: Vinson <sun1101>
Created: 2026-02-14
Version: 1.0.0
"""

import sys
import os
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from transaction_logger import TransactionLogger

def print_report(stats: dict):
    """Print formatted report to console"""
    print(f"\n📊 每日交易报告 - {stats['date']}")
    print(f"{'='*60}")

    # Total transactions
    print(f"\n   总交易: {stats['total_tx']} 笔")
    print(f"   成功: {stats['success_tx']} | 失败: {stats['failed_tx']} | 待定: {stats['pending_tx']}")

    # Total volume
    print(f"\n   总交易额: ${stats['total_volume_usd']:.2f} USD")

    # Per-agent breakdown
    if stats['agents']:
        print(f"\n   按 Agent 分组:")
        for agent_name, agent_stats in sorted(stats['agents'].items()):
            print(f"   {agent_name}: {agent_stats['count']} 笔, ${agent_stats['volume']:.2f} USD")
    else:
        print(f"\n   无 Agent 数据")

    print(f"{'='*60}\n")

def main():
    """Main entry point"""
    # Parse date argument
    date_arg = sys.argv[1] if len(sys.argv) > 1 else None

    # Validate date format if provided
    if date_arg:
        try:
            datetime.strptime(date_arg, '%Y-%m-%d')
        except ValueError:
            print(f"❌ 无效日期格式: {date_arg}")
            print(f"   正确格式: YYYY-MM-DD (例如: 2026-02-14)")
            sys.exit(1)

    # Initialize logger
    logger = TransactionLogger()

    # Get statistics
    stats = logger.get_stats(date_arg)

    # Print report
    print_report(stats)

    # Exit with appropriate code
    if stats['total_tx'] == 0:
        print(f"ℹ️  无交易记录")
        sys.exit(0)
    elif stats['failed_tx'] > 0:
        print(f"⚠️  存在 {stats['failed_tx']} 笔失败交易")
        sys.exit(1)
    else:
        print(f"✅ 所有交易正常")
        sys.exit(0)

if __name__ == '__main__':
    main()
