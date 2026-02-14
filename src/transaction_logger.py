"""
Transaction Logger Module

Implements per-account transaction logging with daily rotation

Author: Vinson <sun1101>
Created: 2026-02-14
Version: 2.0.0 (per-account isolation)
"""

import os
import json
from datetime import datetime
from typing import Dict, Any
from config import Config


class TransactionLogger:
    """Transaction logger with per-account isolation"""

    def __init__(self, agent_name: str, log_dir: str = None):
        """
        Initialize transaction logger

        Args:
            agent_name: Agent name (e.g., 'F0x', 'PinchyMeow')
            log_dir: Base directory for logs (default: Config.LOG_DIR)
        """
        from config import Config

        self.agent_name = agent_name
        self.base_dir = log_dir or Config.LOG_DIR

        # Create per-account subdirectory
        self.log_dir = os.path.join(
            self.base_dir,
            'transactions',
            agent_name
        )

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
            transaction: Transaction details dict
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
            print(f"📝 Transaction logged: {log_file}")
        except Exception as e:
            print(f"❌ Log write failed: {e}")
            print(f"   File: {log_file}")

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
            print(f"❌ Log read failed: {e}")
            print(f"   File: {log_file}")

        return transactions

    def get_stats(self, date: str = None) -> Dict[str, Any]:
        """
        Get transaction statistics for a specific date

        Args:
            date: Date in YYYY-MM-DD format (default: today)

        Returns:
            Dict with statistics
        """
        transactions = self.get_transactions(date)

        stats = {
            'date': date,
            'total_tx': len(transactions),
            'success_tx': 0,
            'failed_tx': 0,
            'pending_tx': 0,
            'total_volume_usd': 0.0
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
            if isinstance(usd_value, (int, float)):
                stats['total_volume_usd'] += float(usd_value)

        return stats


__all__ = ['TransactionLogger']
