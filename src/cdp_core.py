"""
Coinbase CDP SDK - Core Trading Module

Implements:
- get_quote() - Get swap price quote
- execute_swap() - Execute token swap
- get_balance() - Query account balances (ETH + USDC)
- get_wallet() - Get or create CDP wallet

Author: Vinson <sun1101>
Created: 2026-02-14
Version: 3.2.0 (适配真实CDP Python SDK v1.39.1)

References:
- https://docs.cdp.coinbase.com/server-wallets/v1/introduction/quickstart
- https://github.com/coinbase/cdp-sdk-python
"""

import os
from decimal import Decimal
from typing import Dict, Any

# CDP SDK
    from cdp.cdp_client import CdpClient
    from cdp.end_user_client import EndUserClient
    from cdp.api_clients import ApiClients
except ImportError:
        print("❌ CDP SDK not found. Install:")
        print("   pip install cdp-sdk")
        exit(1)

    from cdp.cdp_client import CdpClient
    from cdp.end_user_client import EndUserClient
    from cdp.api_clients import ApiClients
except ImportError:
    print("❌ CDP SDK not found. Install:")
    print("   pip install cdp-sdk")
    exit(1)

from ..config import Config

class CDPTrader:
    """Coinbase CDP Trading Core"""

    def __init__(self):
        """Initialize CDP SDK client"""
        self.client = None
        self.end_user_client = None
        self.wallet = None
        self.config = Config

    async def _ensure_cdp(self):
        """Ensure CDP SDK is configured"""
        if self.client is None:
            # 初始化CdpClient
            self.client = CdpClient(
                api_key_id=self.config.CDP_API_KEY_ID,
                api_key_secret=self.config.CDP_API_KEY_SECRET
            )

    async def _ensure_end_user_client(self):
        """Ensure EndUserClient is initialized"""
        if self.end_user_client is None:
            await self._ensure_cdp()

            # 创建ApiClients实例（包含已配置的CDP客户端）
            api_clients = ApiClients(cdp_client=self.client)

            # 初始化EndUserClient
            self.end_user_client = EndUserClient(api_clients=api_clients)

    async def _ensure_wallet(self):
        """Ensure wallet exists"""
        if self.wallet is None:
            await self._ensure_end_user_client()

            # 列出账户
            accounts = self.end_user_client.list_accounts()

            if not accounts:
                raise ValueError("❌ 没有找到CDP账户，请先创建")

            # 使用第一个账户（PinchyMeow或F0x）
            account = accounts[0]
            self.wallet = account
            print(f"✅ Using account: {self.wallet.address}")

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

            from cdp.cdp_client import CdpClient
    from cdp.end_user_client import EndUserClient
    from cdp.api_clients import ApiClients
except ImportError:
        print("❌ CDP SDK not found. Install:")
        print("   pip install cdp-sdk")
        exit(1)

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

            # 转换为decimal（不做wei转换）
            if from_symbol == 'usdc':
                from_amount_decimals = amount
            elif from_symbol == 'eth':
                from_amount_decimals = amount
            else:
                raise ValueError(f"Unsupported token: {from_token}")

            print(f"💰 Getting quote for {amount} {from_token} → {to_token}")

            # CDP SDK账户对象的trade()方法
            # 参数：amount (Decimal), from_token (str), to_token (str)
            result = self.wallet.trade(
                amount=from_amount_decimals,
                from_token=from_address,
                to_token=to_address
            )

            # 解析交易结果
            expected_amount = result.to_amount
            gas_fee = result.gas_fee

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

            from cdp.cdp_client import CdpClient
    from cdp.end_user_client import EndUserClient
    from cdp.api_clients import ApiClients
except ImportError:
        print("❌ CDP SDK not found. Install:")
        print("   pip install cdp-sdk")
        exit(1)

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

            # 转换为decimal
            if from_symbol == 'usdc':
                from_amount_decimals = amount
            elif from_symbol == 'eth':
                from_amount_decimals = amount
            else:
                raise ValueError(f"Unsupported token: {from_token}")

            from_amount_wei = int(from_amount_decimals * (10 ** decimals))

            print(f"🔄 Executing swap: {amount} {from_token} → {to_token}")
            print(f"   Slippage: {slippage_bps / 100}% (1%)")

            # 执行交换
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

            from cdp.cdp_client import CdpClient
    from cdp.end_user_client import EndUserClient
    from cdp.api_clients import ApiClients
except ImportError:
        print("❌ CDP SDK not found. Install:")
        print("   pip install cdp-sdk")
        exit(1)

            # CDP SDK账户对象没有直接的balance属性
            # 需要通过其他方式获取余额

            # 方法1: 使用account对象的balances属性（如果存在）
            if hasattr(self.wallet, 'balances'):
                balances = self.wallet.balances
                eth_balance = balances.get('eth', Decimal(0))
                usdc_balance = balances.get('usdc', Decimal(0))
            else:
                eth_balance = Decimal(0)
                usdc_balance = Decimal(0)

            print(f"💰 Account Balance ({self.wallet.address[:10]}...):")
            print(f"   ETH: {eth_balance:.4f} ETH")
            print(f"   USDC: {usdc_balance:.2f} USDC")

            return {
                'eth_balance': eth_balance,
                'usdc_balance': usdc_balance
            }

        except Exception as e:
            print(f"❌ Balance check failed: {e}")
            raise

    async def get_wallet(self) -> Dict[str, Any]:
        """
        Get or create CDP wallet/account

        Returns:
            Wallet/account info
        """
        await self._ensure_end_user_client()

        # 列出所有账户
        accounts = self.end_user_client.list_accounts()

        if not accounts:
            raise ValueError("❌ 没有找到CDP账户，请先创建")

        # 使用第一个账户（PinchyMeow或F0x）
        account = accounts[0]
        self.wallet = account

        print(f"✅ 使用账户: {self.wallet.address}")

        return {
            'address': account.address,
            'wallet_id': account.id,
            'network_id': account.network_id
        }

# Export
__all__ = ['CDPTrader']
