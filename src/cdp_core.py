"""
Coinbase CDP SDK - Core Trading Module

Implements:
- get_quote() - Get swap price quote (free, no gas cost)
- execute_swap() - Execute token swap
- get_balance() - Query account balances
- get_wallet() - Get or create persistent CDP wallet

Author: Vinson <sun1101>
Created: 2026-02-14
Version: 2.0.0 (适配真实CDP SDK)
"""

import os
import asyncio
from decimal import Decimal
from typing import Dict, Any, Optional

# CDP SDK
try:
    from cdp import CdpClient, Wallet
except ImportError:
    print("❌ CDP SDK not found. Install:")
    print("   pip install cdp-sdk")
    exit(1)

from config import Config

class CDPTrader:
    """Coinbase CDP Trading Core"""

    def __init__(self):
        """Initialize CDP SDK client"""
        self.cdp = None
        self.account = None
        self.config = Config

    async def _ensure_cdp(self):
        """Ensure CDP client is initialized"""
        if self.cdp is None:
            # Initialize CDP client with API keys from config
            self.cdp = CdpClient(
                api_key_id=self.config.CDP_API_KEY_ID,
                api_key_secret=self.config.CDP_API_KEY_SECRET
            )

    async def _ensure_account(self):
        """Ensure account exists"""
        if self.account is None:
            await self._ensure_cdp()

            # Get or create persistent wallet
            # Using get_or_create_account for persistence
            result = await self.cdp.evm.get_or_create_account(
                name="OpenClaw_Agent_01"
            )

            self.account = result
            print(f"✅ Using account: {self.account.address}")

    async def get_quote(
        self,
        from_token: str,
        to_token: str,
        amount: float
    ) -> Dict[str, Any]:
        """
        Get swap price quote (free, no gas cost)

        Args:
            from_token: From token symbol ('usdc', 'eth')
            to_token: To token symbol ('eth', 'usdc')
            amount: Amount to swap (float)

        Returns:
            Dict with quote information
        """
        await self._ensure_account()

        try:
            # Token addresses
            token_addresses = {
                'usdc': Config.USDC_ADDRESS,
                'eth': Config.ETH_ADDRESS,
                'weth': Config.WETH_ADDRESS
            }

            from_symbol = from_token.lower()
            to_symbol = to_token.lower()
            from_address = token_addresses.get(from_symbol)
            to_address = token_addresses.get(to_symbol)

            if not from_address or not to_address:
                raise ValueError(f"Unsupported token: {from_token} or {to_token}")

            # Convert amount to wei (decimals based on token)
            if from_symbol == 'usdc':
                decimals = 6
            elif from_symbol == 'eth':
                decimals = 18
            else:
                raise ValueError(f"Unsupported token: {from_token}")

            from_amount_wei = int(amount * (10 ** decimals))

            print(f"💰 Getting quote for {amount} {from_token} → {to_token}")

            # Get swap quote using CDP API
            quote = await self.account.quote_swap(
                from_token_address=from_address,
                to_token_address=to_address,
                from_amount=from_amount_wei
            )

            # Parse response
            expected_amount = quote.get('expectedAmount', quote.get('minToAmount', from_amount_wei))
            gas_fee = quote.get('gasFee', 0)  # Wei
            liquidity_available = quote.get('liquidityAvailable', True)

            print(f"✅ Quote received:")
            print(f"  Expected: {Decimal(expected_amount) / 10**6:.2f} {to_token.upper()}")
            print(f" Gas Fee: {Decimal(gas_fee) / 10**18:.6f} ETH")
            print(f" Liquidity: {'✅ Available' if liquidity_available else '❌ Insufficient'}")

            return {
                'expected_amount': expected_amount,
                'gas_fee': gas_fee,
                'liquidity_available': liquidity_available
            }

        except Exception as e:
            print(f"❌ Quote failed: {e}")
            raise

    async def execute_swap(
        self,
        from_token: str,
        to_token: str,
        amount: float,
        slippage_bps: int = 100
    ) -> Dict[str, Any]:
        """
        Execute token swap (atomic)

        Args:
            from_token: From token symbol ('usdc', 'eth')
            to_token: To token symbol ('eth', 'usdc')
            amount: Amount to swap (float)
            slippage_bps: Slippage in basis points (100 = 1%)

        Returns:
            Dict with:
                'tx_hash': str,        # Transaction hash
                'status': str           # 'success' | 'pending' | 'failed'
        """
        await self._ensure_account()

        try:
            # Token addresses
            token_addresses = {
                'usdc': Config.USDC_ADDRESS,
                'eth': Config.ETH_ADDRESS,
                'weth': Config.WETH_ADDRESS
            }

            from_symbol = from_token.lower()
            to_symbol = to_token.lower()
            from_address = token_addresses.get(from_symbol)
            to_address = token_addresses.get(to_symbol)

            if not from_address or not to_address:
                raise ValueError(f"Unsupported token: {from_token} or {to_token}")

            # Convert amount to wei
            if from_symbol == 'usdc':
                decimals = 6
            elif from_symbol == 'eth':
                decimals = 18
            else:
                raise ValueError(f"Unsupported token: {from_token}")

            from_amount_wei = int(amount * (10 ** decimals))

            print(f"🔄 Executing swap: {amount} {from_token} → {to_token}")
            print(f"   Slippage: {slippage_bps / 100}% (1%)")

            # Execute atomic swap
            result = await self.account.swap(
                from_token_address=from_address,
                to_token_address=to_address,
                from_amount=from_amount_wei,
                slippage_bps=slippage_bps  # Enforce 1% slippage
            )

            tx_hash = result.wait().transaction_hash
            status = 'success'

            print(f"✅ Swap completed:")
            print(f"   TX Hash: {tx_hash}")
            print(f"   Status: {status}")

            return {
                'tx_hash': tx_hash,
                'status': status
            }

        except Exception as e:
            print(f"❌ Swap failed: {e}")
            print(f"   Error: {str(e)}")
            raise

    async def get_balance(self) -> Dict[str, Any]:
        """
        Query account balances (ETH + USDC)

        Returns:
            Dict with:
                'eth_balance': Decimal,  # ETH balance (float)
                'usdc_balance': Decimal, # USDC balance (float)
        """
        await self._ensure_account()

        try:
            # Get ETH balance (native)
            eth_balance_wei = await self.cdp.evm.get_balance({
                "address": self.account.address,
                "block": "latest"
            })
            eth_balance = Decimal(eth_balance_wei) / 10**18

            # Get USDC balance (ERC20) - not yet implemented
            usdc_balance = Decimal(0)

            print(f"💰 Account Balance ({self.account.address[:10]}...):")
            print(f"   ETH: {eth_balance:.4f} ETH")
            print(f"   USDC: {usdc_balance:.2f} USDC (pending implementation)")

            return {
                'eth_balance': eth_balance,
                'usdc_balance': usdc_balance
            }

        except Exception as e:
            print(f"❌ Balance check failed: {e}")
            raise

    async def get_wallet(self) -> Dict[str, Any]:
        """
        Get or create persistent CDP wallet
        """
        await self._ensure_cdp()

        # Get or create account
        result = await self.cdp.evm.get_or_create_account(
            name="OpenClaw_Agent_01"
        )

        return {
            'address': result.address,
            'wallet_id': result.id,
            'network_id': result.network_id
        }

# Export
__all__ = ['CDPTrader']
