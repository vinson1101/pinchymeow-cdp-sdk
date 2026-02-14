"""
CDP Core Trading Module

Implements core CDP trading functionality:
- Balance queries (ETH, USDC, and other tokens)
- Price quotes (get_quote)
- Token swaps (execute_swap)
- Wallet info retrieval

Author: Vinson <sun1101>
Created: 2026-02-14
Version: 1.0.0
"""

import asyncio
from decimal import Decimal
from typing import Dict, Any, Optional
from cdp import CdpClient
from config import Config


class CDPTrader:
    """Core CDP trading functionality"""

    def __init__(self, account_name, agent_name):
        """
        Initialize CDP trader with account and agent names

        Args:
            account_name: Account name (e.g., 'F0X_TRADING')
            agent_name: Agent name (e.g., 'F0x')
        """
        # Validate account access (prefix matching)
        from config import Config
        validate_account_access(agent_name, account_name)

        self.account_name = account_name
        self.agent_name = agent_name
        self.account_address = Config.AGENT_ACCOUNTS.get(agent_name)

        # Initialize CDP client
        self.client = CdpClient(
            api_key_id=Config.CDP_API_KEY_ID,
            api_key_secret=Config.CDP_API_KEY_SECRET
        )
        self.network = Config.NETWORK_ID


def validate_account_access(agent_name, account_name):
    """Validate agent can only access own account (prefix matching)"""
    from config import Config
    expected_prefix = Config.AGENT_ACCOUNT_PREFIX.get(agent_name)

    if not account_name.startswith(expected_prefix):
        raise ValueError(f"{agent_name} 无权访问 {account_name}")

    print(f"✅ Account access validated: {agent_name} → {account_name}")


__all__ = ['CDPTrader', 'validate_account_access']

    async def get_balance(
        self,
        address: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get token balances for an address

        Args:
            address: EVM address to query (defaults to Config main address)

        Returns:
            Dict with:
                'eth_balance': float       # ETH balance
                'usdc_balance': float      # USDC balance
                'other_tokens': dict      # Other token balances
                'address': str            # Queried address
        """
        # Use default address if not provided
        if address is None:
            from config import Config
            address = Config.F0X_TRADING

        result = {
            'address': address,
            'eth_balance': 0.0,
            'usdc_balance': 0.0,
            'other_tokens': {}
        }

        try:
            # List token balances
            balances = await self.client.evm.list_token_balances(
                address=address,
                network=self.network
            )

            # Parse balances
            for balance in balances.balances:
                token = balance.token
                amount = balance.amount

                # Convert to decimal
                decimal_amount = Decimal(amount.amount) / Decimal(10**amount.decimals)
                float_amount = float(decimal_amount)

                if token.symbol == 'ETH':
                    result['eth_balance'] = float_amount
                elif token.symbol == 'USDC':
                    result['usdc_balance'] = float_amount
                elif token.symbol:
                    result['other_tokens'][token.symbol] = float_amount

        except Exception as e:
            print(f"❌ Error getting balance: {e}")
            result['error'] = str(e)

        return result

    async def get_quote(
        self,
        from_token: str,
        to_token: str,
        amount: float
    ) -> Dict[str, Any]:
        """
        Get price quote for token swap

        Args:
            from_token: From token symbol ('eth', 'usdc')
            to_token: To token symbol ('usdc', 'eth')
            amount: Amount to swap (float)

        Returns:
            Dict with:
                'from_token': str
                'to_token': str
                'from_amount': float
                'expected_amount': int    # In smallest unit (wei)
                'price': float           # Exchange rate
                'network': str
        """
        from_token_lower = from_token.lower()
        to_token_lower = to_token.lower()

        # Get token addresses
        token_addresses = {
            'eth': Config.ETH_ADDRESS,
            'usdc': Config.USDC_ADDRESS
        }

        from_address = token_addresses.get(from_token_lower)
        to_address = token_addresses.get(to_token_lower)

        if not from_address or not to_address:
            raise ValueError(f"Unsupported token: {from_token} or {to_token}")

        # Calculate amount in smallest unit (wei)
        decimals = 18 if from_token_lower == 'eth' else 6
        from_amount_wei = int(amount * (10 ** decimals))

        result = {
            'from_token': from_token_lower,
            'to_token': to_token_lower,
            'from_amount': amount,
            'expected_amount': 0,
            'price': 0.0,
            'network': self.network
        }

        try:
            # Use CDP SDK get_swap_price (free, no gas)
            quote = await self.client.evm.get_swap_price(
                from_token=from_address,
                to_token=to_address,
                from_amount=from_amount_wei,
                network=self.network,
                taker=self.account_address  # Use account address as taker
            )

            # Parse result
            result['expected_amount'] = int(quote.expected_amount)
            result['price'] = float(quote.price) if quote.price else 0.0

        except Exception as e:
            print(f"❌ Error getting quote: {e}")
            result['error'] = str(e)

        return result

    async def execute_swap(
        self,
        from_token: str,
        to_token: str,
        amount: float,
        slippage_bps: int = 100
    ) -> Dict[str, Any]:
        """
        Execute token swap (NOT IMPLEMENTED - requires CDP Account)

        This method requires a CDP Account to send transactions.
        For external EOAs, use a different method or integrate with
        a wallet provider.

        Args:
            from_token: From token symbol
            to_token: To token symbol
            amount: Amount to swap
            slippage_bps: Slippage in basis points

        Returns:
            Dict with:
                'status': str           # 'success', 'failed'
                'tx_hash': str          # Transaction hash
                'message': str          # Status message
        """
        # NOTE: This requires a CDP Account (Smart Account or Server Account)
        # External EOAs cannot directly send swaps through CDP SDK
        return {
            'status': 'failed',
            'tx_hash': None,
            'message': 'execute_swap requires CDP Account (not implemented for external EOAs)'
        }

    async def get_wallet(
        self,
        address: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get wallet information

        Args:
            address: EVM address (optional)

        Returns:
            Dict with wallet info
        """
        balance = await self.get_balance(address)

        return {
            'address': balance['address'],
            'network': self.network,
            'balances': {
                'eth': balance['eth_balance'],
                'usdc': balance['usdc_balance'],
                'other': balance['other_tokens']
            }
        }

    async def close(self):
        """Close CDP client connection"""
        await self.client.close()


__all__ = ['CDPTrader']
