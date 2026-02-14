"""
Transaction Logger Module

Implements:
- JSONL format logging
- Daily rotation (YYYY-MM-DD.jsonl)
- Transaction fields: timestamp, type, agent, account, amounts, tx_hash, status
- Automatic directory creation

Author: Vinson <sun1101>
Created: 2026-02-14
Version: 1.0.0
"""

import os
import json
from datetime import datetime
from typing import Dict, Any

class TransactionLogger:
    """Transaction logger with daily JSONL rotation"""

    def __init__(self, log_dir: str = None):
        """
        Initialize transaction logger

        Args:
            log_dir: Directory for log files (default: Config.LOG_DIR/transactions)
        """
        from config import Config

        self.log_dir = log_dir or os.path.join(Config.LOG_DIR, 'transactions')
        self.ensure_dir()

    def ensure_dir(self):
        """Ensure log directory exists"""
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir, exist_ok=True)
            print(f"✅ Created log directory: {self.log_dir}")

    def log(self, transaction: Dict[str, Any]):
        """
        Log a transaction to daily JSONL file

        Args:
            transaction: Dict with transaction details
        """
        # Get current date in YYYY-MM-DD format
        date_str = datetime.utcnow().strftime('%Y-%m-%d')

        # Build log file path
        log_file = os.path.join(self.log_dir, f'{date_str}.jsonl')

        # Add timestamp if not present
        if 'timestamp' not in transaction:
            transaction['timestamp'] = datetime.utcnow().isoformat()

        # Append to log file
        try:
            with open(log_file, 'a') as f:
                f.write(json.dumps(transaction) + '\n')

            print(f"📝 交易已记录: {log_file}")

        except Exception as e:
            print(f"❌ 日志写入失败: {e}")
            print(f"   文件: {log_file}")

    def get_transactions(self, date: str = None) -> list:
        """
        Get all transactions for a specific date

        Args:
            date: Date in YYYY-MM-DD format (default: today)

        Returns:
            List of transaction dicts
        """
        if date is None:
            date = datetime.utcnow().strftime('%Y-%m-%d')

        log_file = os.path.join(self.log_dir, f'{date}.jsonl')

        if not os.path.exists(log_file):
            return []

        transactions = []
        try:
            with open(log_file, 'r') as f:
                for line in f:
                    if line.strip():
                        transactions.append(json.loads(line))

        except Exception as e:
            print(f"❌ 日志读取失败: {e}")

        return transactions

    def get_stats(self, date: str = None) -> Dict[str, Any]:
        """
        Get transaction statistics for a specific date

        Args:
            date: Date in YYYY-MM-DD format (default: today)

        Returns:
            Dict with statistics:
                - date: str
                - total_tx: int
                - success_tx: int
                - failed_tx: int
                - pending_tx: int
                - total_volume_usd: float
                - agents: dict (agent_name -> {count, volume})
        """
        transactions = self.get_transactions(date)

        stats = {
            'date': date or datetime.utcnow().strftime('%Y-%m-%d'),
            'total_tx': len(transactions),
            'success_tx': 0,
            'failed_tx': 0,
            'pending_tx': 0,
            'total_volume_usd': 0.0,
            'agents': {}
        }

        for tx in transactions:
            # Count by status
            status = tx.get('status', 'unknown')
            if status == 'success':
                stats['success_tx'] += 1
            elif status == 'failed':
                stats['failed_tx'] += 1
            elif status == 'pending' or status == 'requires_approval':
                stats['pending_tx'] += 1

            # Accumulate volume
            usd_value = tx.get('usd_value', 0.0)
            if isinstance(usd_value, (int, float, str)):
                stats['total_volume_usd'] += float(usd_value)

            # Group by agent
            agent = tx.get('agent', 'unknown')
            if agent not in stats['agents']:
                stats['agents'][agent] = {'count': 0, 'volume': 0.0}

            stats['agents'][agent]['count'] += 1
            stats['agents'][agent]['volume'] += float(usd_value)

        return stats

# Export
__all__ = ['TransactionLogger']
