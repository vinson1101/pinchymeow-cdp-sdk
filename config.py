"""
Configuration Management for PinchyMeow CDP SDK

Handles:
- Environment variable loading
- Trading constants (slippage, limits, thresholds)
- Network configuration
- Token address mapping
"""

import os
from decimal import Decimal
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/root/.openclaw/workspace/.env.cdp')

class Config:
    """CDP Configuration"""

    # API Keys (from environment)
    CDP_API_KEY_ID = os.getenv("CDP_API_KEY_ID")
    CDP_API_KEY_SECRET = os.getenv("CDP_API_KEY_SECRET")

    # Network (for list_token_balances API)
    NETWORK_ID = "base"

    # Token Addresses (Base)
    USDC_ADDRESS = "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913"
    ETH_ADDRESS = "0x4200000000000000000000000000000000006"  # WETH
    WETH_ADDRESS = "0x4200000000000000000000000000000000000006"

    # Trading Constants
    SLIPPAGE_BPS = 100  # 1% slippage
    MAX_TRADE_USD = 5000  # $5000 max per trade
    MIN_ETH_GAS = Decimal("0.001")  # Min ETH to keep (for gas)

    # Strategy Thresholds
    COW_SWAP_THRESHOLD = 1000  # >$1000 use CowSwap

    # Sentinel Configuration
    SENTINEL_CHECK_INTERVAL = 60  # seconds
    ETH_PRICE_THRESHOLD = 2000  # $2000

    # Logging
    LOG_DIR = "/root/.openclaw/workspace/data"
    TRIGGER_DIR = "/root/.openclaw/workspace/triggers"

    @staticmethod
    def validate():
        """Validate required configuration"""
        if not Config.CDP_API_KEY_ID:
            raise ValueError("CDP_API_KEY_ID not set")
        if not Config.CDP_API_KEY_SECRET:
            raise ValueError("CDP_API_KEY_SECRET not set")

        print("✅ Configuration validated")
        print(f"   Network: {Config.NETWORK_ID}")
        print(f"   USDC: {Config.USDC_ADDRESS}")
        print(f"   ETH: {Config.ETH_ADDRESS}")
