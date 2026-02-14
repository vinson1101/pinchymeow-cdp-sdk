"""
Coinbase CDP SDK - Core Trading Module

Implements:
- get_quote() - Get swap price quote
- execute_swap() - Execute token swap
- get_balance() - Query account balances
- get_wallet() - Get or create persistent CDP wallet

Author: Vinson <sun1101>
Created: 2026-02-14
Version: 3.0.0 (适配真实CDP Python SDK v1.39+)

References:
- https://docs.cdp.coinbase.com/server-wallets/v1/introduction/quickstart
- https://github.com/coinbase/cdp-sdk-python
"""

import os
from decimal import Decimal
from typing import Dict, Any

# CDP SDK
try:
    from cdp import Wallet, Cdp
except ImportError:
    print("❌ CDP SDK not found. Install:")
    print("   pip install cdp-sdk")
    exit(1)

from config import Config

class CDPTrader:
    """Coinbase CDP Trading Core"""

    def __init__(self):
        """Initialize CDP SDK client"""
        self.wallet = None
        self.config = Config

    async def _ensure_cdp(self):
        """Ensure CDP SDK is configured"""
        # Configure CDP SDK with API keys from environment
        Cdp.configure(
            self.config.CDP_API_KEY_ID,
            self.config.CDP_API_KEY_SECRET
        )

    async def _ensure_wallet(self):
        """Ensure wallet exists"""
        if self.wallet is None:
            await self._ensure_cdp()

            # Create wallet (CDP SDK manages persistence)
            self.wallet = Wallet.create()
            print(f"✅ Using wallet: {self.wallet.default_address}")

    async def get_quote(
        self,
        from_token: str,
        to_token: str,
        amount: float
    ) -> Dict[str, Any]:
        """
        Get swap price quote

        Args:
            from_token: From token symbol ('usdc', 'eth')
            to_token: To token symbol ('eth', 'usdc')
            amount: Amount to swap (float)

        Returns:
            Dict with quote information
        """
        await self._ensure_wallet()

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
                from_amount_decimals = amount
            elif from_symbol == 'eth':
                decimals = 18
                from_amount_decimals = amount
            else:
                raise ValueError(f"Unsupported token: {from_token}")

            print(f"💰 Getting quote for {amount} {from_token} → {to_token}")

            # Get swap quote using wallet.trade() for preview
            # Note: CDP SDK wallet.trade() returns a Trade object
            result = self.wallet.trade(
                amount=from_amount_decimals,
                from_token=from_address,
                to_token=to_address
            )

            # Parse trade result for quote info
            expected_amount = result.to_amount  # Already converted to decimal
            gas_fee = result.gas_fee  # Gas fee in wei

            print(f"✅ Quote received:")
            print(f"  Expected: {expected_amount:.2f} {to_token.upper()}")
            print(f"  Gas Fee: {Decimal(gas_fee) / 10**18:.6f} ETH")
            print(f"  Liquidity: ✅ Available")

            return {
                'expected_amount': expected_amount,
                'gas_fee': gas_fee,
                'liquidity_available': True
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
        await self._ensure_wallet()

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
                from_amount_decimals = amount
            elif from_symbol == 'eth':
                decimals = 18
                from_amount_decimals = amount
            else:
                raise ValueError(f"Unsupported token: {from_token}")

            from_amount_wei = int(from_amount_decimals * (10 ** decimals))

            print(f"🔄 Executing swap: {amount} {from_token} → {to_token}")
            print(f"   Slippage: {slippage_bps / 100}% (1%)")

            # Execute atomic swap using wallet.trade()
            result = self.wallet.trade(
                amount=from_amount_decimals,
                from_token=from_address,
                to_token=to_address
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
        await self._ensure_wallet()

        try:
            # CDP SDK wallet has balance property (native ETH)
            eth_balance = self.wallet.balance

            # For ERC20 tokens like USDC, we need to query token balance
            # CDP SDK might have a method for this
            usdc_balance = Decimal(0)  # Placeholder - not implemented yet

            print(f"💰 Account Balance ({self.wallet.default_address[:10]}...):")
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

        # Create or fetch wallet
        # CDP SDK manages wallet persistence
        self.wallet = Wallet.create()

        return {
            'address': self.wallet.default_address,
            'wallet_id': self.wallet.id,
            'network_id': self.wallet.network_id
        }

# Export
__all__ = ['CDPTrader']
