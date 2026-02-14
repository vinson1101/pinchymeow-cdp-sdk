"""
Enhanced Trading Module with Safety Checks

Implements:
- Hardcoded slippage limit (1%)
- Human-in-the-Loop for large trades (> $100 USD)
- USD value calculation
- Safe swap method with approval threshold
- Transaction logging

Author: Vinson <sun1101>
Created: 2026-02-14
Version: 1.0.0
"""

import os
from decimal import Decimal
from typing import Dict, Any, Optional
from datetime import datetime

from cdp_core import CDPTrader
from config import Config

class SafeTrader:
    """Enhanced trading with safety checks"""

    # Constants
    HARDCODED_SLIPPAGE_BPS = 100  # 1% slippage (hardcoded, non-configurable)
    APPROVAL_THRESHOLD_USD = 100  # $100 USD threshold for human approval

    def __init__(self, logger=None):
        """
        Initialize safe trader

        Args:
            logger: Optional TransactionLogger instance
        """
        self.core = CDPTrader()
        self.logger = logger
    """Enhanced trading with safety checks"""

    # Constants
    HARDCODED_SLIPPAGE_BPS = 100  # 1% slippage (hardcoded, non-configurable)
    APPROVAL_THRESHOLD_USD = 100  # $100 USD threshold for human approval

    def __init__(self, logger=None):
        """
        Initialize safe trader

        Args:
            logger: Optional TransactionLogger instance
        """
        self.core = CDPTrader()
        self.logger = logger

    async def calculate_usd_value(
        self,
        token_symbol: str,
        amount: float
    ) -> float:
        """
        Calculate USD value of token amount

        Args:
            token_symbol: Token symbol ('usdc', 'eth')
            amount: Amount in token units (not wei)

        Returns:
            USD value as float
        """
        symbol = token_symbol.lower()

        if symbol == 'usdc':
            # USDC has stable value: 1 USDC = $1 USD
            return float(amount)

        elif symbol == 'eth':
            # Get current ETH price via quote
            try:
                # Quote 1 ETH → USDC
                quote = await self.core.get_quote(
                    from_token='eth',
                    to_token='usdc',
                    amount=1.0
                )

                # Calculate USD value
                # expected_amount is in wei (6 decimals for USDC)
                expected_usdc = Decimal(quote['expected_amount']) / 10**6
                eth_price_usd = float(expected_usdc)

                # Calculate USD value of amount
                usd_value = float(amount) * eth_price_usd
                return usd_value

            except Exception as e:
                print(f"⚠️  Failed to get ETH price: {e}")
                return 0.0

        else:
            raise ValueError(f"Unsupported token: {token_symbol}")

    async def swap_with_approval(
        self,
        from_token: str,
        to_token: str,
        amount: float,
        agent_name: str = 'unknown',
        slippage_bps: int = None
    ) -> Dict[str, Any]:
        """
        Execute swap with safety checks and human approval for large trades

        Args:
            from_token: From token symbol ('usdc', 'eth')
            to_token: To token symbol ('eth', 'usdc')
            amount: Amount to swap (float)
            agent_name: Agent name for logging
            slippage_bps: Slippage in basis points (MUST be 100, ignored if set)

        Returns:
            Dict with:
                'status': str           # 'success', 'requires_approval', 'failed'
                'usd_value': float      # USD value of trade
                'message': str          # Status message
                'tx_hash': str          # Transaction hash (if executed)
                'quote': dict           # Price quote details
        """
        from_symbol = from_token.lower()

        # 1. Enforce hardcoded slippage
        if slippage_bps is not None and slippage_bps != self.HARDCODED_SLIPPAGE_BPS:
            print(f"⚠️  滑点必须是 {self.HARDCODED_SLIPPAGE_BPS} bps (1%)")
            print(f"⚠️  忽略传入的 slippage_bps={slippage_bps}")
            print(f"⚠️  使用固定滑点防止 LLM 自行决定导致大额损失")

        actual_slippage_bps = self.HARDCODED_SLIPPAGE_BPS

        # 2. Calculate USD value
        try:
            usd_value = await self.calculate_usd_value(from_token, amount)
        except Exception as e:
            return {
                'status': 'failed',
                'usd_value': 0.0,
                'message': f'Failed to calculate USD value: {e}',
                'tx_hash': None,
                'quote': None
            }

        # 3. Get price quote
        try:
            quote = await self.core.get_quote(from_token, to_token, amount)
        except Exception as e:
            return {
                'status': 'failed',
                'usd_value': usd_value,
                'message': f'Failed to get quote: {e}',
                'tx_hash': None,
                'quote': None
            }

        # 4. Check if human approval is required
        if usd_value > self.APPROVAL_THRESHOLD_USD:
            print(f"⚠️  大额交易检测: ${usd_value:.2f} USD")
            print(f"⚠️  需要人工确认才能执行")
            print(f"⚠️  请通过 OpenClaw 控制台确认交易")

            # Log pending transaction
            if self.logger:
                self.logger.log({
                    'type': 'swap_pending_approval',
                    'agent': agent_name,
                    'account': 'unknown',  # Will be filled by caller
                    'from_token': from_token,
                    'to_token': to_token,
                    'from_amount': amount,
                    'usd_value': usd_value,
                    'slippage_bps': actual_slippage_bps,
                    'status': 'requires_approval',
                    'message': f'大额交易 (${usd_value:.2f}) 需要人工确认',
                    'timestamp': datetime.utcnow().isoformat()
                })

            return {
                'status': 'requires_approval',
                'usd_value': usd_value,
                'from_token': from_token,
                'to_token': to_token,
                'amount': amount,
                'agent_name': agent_name,
                'message': f'大额交易 (${usd_value:.2f}) 需要人工确认。请通过 OpenClaw 控制台确认。',
                'tx_hash': None,
                'quote': quote,
                'timestamp': datetime.utcnow().isoformat()
            }

        # 5. Small trade: execute directly
        print(f"✅ 小额交易: ${usd_value:.2f} USD (阈值: ${self.APPROVAL_THRESHOLD_USD})")
        print(f"🔄 直接执行交换...")

        try:
            result = await self.core.execute_swap(
                from_token=from_token,
                to_token=to_token,
                amount=amount,
                slippage_bps=actual_slippage_bps
            )

            # Log successful transaction
            if self.logger:
                self.logger.log({
                    'type': 'swap',
                    'agent': agent_name,
                    'account': 'unknown',  # Will be filled by caller
                    'from_token': from_token,
                    'to_token': to_token,
                    'from_amount': amount,
                    'expected_amount': Decimal(quote['expected_amount']) / 10**6,
                    'usd_value': usd_value,
                    'slippage_bps': actual_slippage_bps,
                    'tx_hash': result.get('tx_hash'),
                    'status': result.get('status'),
                    'timestamp': datetime.utcnow().isoformat()
                })

            return {
                'status': result.get('status'),
                'usd_value': usd_value,
                'message': f'交换成功 (${usd_value:.2f} USD)',
                'tx_hash': result.get('tx_hash'),
                'quote': quote
            }

        except Exception as e:
            # Log failed transaction
            if self.logger:
                self.logger.log({
                    'type': 'swap',
                    'agent': agent_name,
                    'account': 'unknown',
                    'from_token': from_token,
                    'to_token': to_token,
                    'from_amount': amount,
                    'usd_value': usd_value,
                    'slippage_bps': actual_slippage_bps,
                    'tx_hash': None,
                    'status': 'failed',
                    'error': str(e),
                    'timestamp': datetime.utcnow().isoformat()
                })

            return {
                'status': 'failed',
                'usd_value': usd_value,
                'message': f'交换失败: {e}',
                'tx_hash': None,
                'quote': quote
            }

    async def get_balance(self) -> Dict[str, Any]:
        """Get account balances (ETH + USDC)"""
        return await self.core.get_balance()

    async def get_wallet(self) -> Dict[str, Any]:
        """Get wallet info"""
        return await self.core.get_wallet()

# Export
__all__ = ['SafeTrader']
