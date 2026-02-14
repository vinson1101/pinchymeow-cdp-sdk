#!/usr/bin/env python3
"""
检查 Permit2 授权状态
"""

import asyncio
import sys
sys.path.insert(0, '.')

from cdp import CdpClient
from web3 import Web3
from config import Config

# Permit2 Contract ABI (只包含我们需要的函数)
PERMIT2_ABI = [
    {
        "constant": False,
        "inputs": [
            {"internalType": "address", "name": "owner", "type": "address"},
            {"internalType": "address", "name": "token", "type": "address"},
            {"internalType": "address", "name": "spender", "type": "address"},
            {"internalType": "uint256", "name": "amount", "type": "uint256"},
            {"internalType": "uint256", "name": "expiration", "type": "uint256"}
        ],
        "name": "allowance",
        "outputs": [
            {"internalType": "uint160", "name": "", "type": "uint160"},
            {"internalType": "uint256", "name": "", "type": "uint256"},
            {"internalType": "uint256", "name": "", "type": "uint256"}
        ],
        "payable": False,
        "stateMutability": "view",
        "type": "function"
    }
]

# USDC ABI (只包含 approve)
USDC_ABI = [
    {
        "inputs": [
            {"name": "spender", "type": "address"},
            {"name": "amount", "type": "uint256"}
        ],
        "name": "approve",
        "outputs": [{"name": "", "type": "bool"}],
        "type": "function"
    },
    {
        "inputs": [
            {"name": "owner", "type": "address"},
            {"name": "spender", "type": "address"}
        ],
        "name": "allowance",
        "outputs": [{"name": "", "type": "uint256"}],
        "type": "function"
    }
]

async def check_permit2():
    print("=" * 60)
    print("检查 Permit2 授权状态")
    print("=" * 60)

    smart_addr = "0x5Bae0994344d22E0a3377e81204CC7c030c65e96"

    # Permit2 地址 (Base)
    PERMIT2_ADDRESS = "0x000000000022D473030f6c4fF0b9A0F4F26B36A4a6"

    # 1inch Swap Router 地址 (从 swap quote 获取)
    SWAP_ROUTER = "0xdc5d8200a030798bc6227240f68b4dd9542686ef"

    w3 = Web3(Web3.HTTPProvider('https://mainnet.base.org'))

    # 步骤1: 检查 USDC 对 Permit2 的授权
    print("\n[步骤1] 检查 USDC -> Permit2 授权...")

    usdc_contract = w3.eth.contract(
        address=Config.USDC_ADDRESS,
        abi=USDC_ABI
    )

    # 检查 Smart Account 对 Permit2 的授权额度
    # Permit2 地址已经是正确的格式
    allowance = usdc_contract.functions.allowance(
        smart_addr,
        PERMIT2_ADDRESS
    ).call()

    print(f"USDC Allowance (Smart Account -> Permit2): {allowance}")
    print(f"  已授权: {allowance > 0}")

    print("\n" + "=" * 60)

    # 步骤2: 检查 Permit2 的 allowance
    print("\n[步骤2] 检查 Permit2 -> Swap Router 授权...")

    permit2_contract = w3.eth.contract(
        address=PERMIT2_ADDRESS,
        abi=PERMIT2_ABI
    )

    # 检查 Permit2 对 Swap Router 的授权
    try:
        permit2_allowance = permit2_contract.functions.allowance(
            smart_addr,
            Config.USDC_ADDRESS,
            SWAP_ROUTER,
            2**256 - 1,  # infinite expiration
        ).call()

        print(f"Permit2 Allowance:")
        print(f"  Amount: {permit2_allowance[0]}")
        print(f"  Expiration: {permit2_allowance[1]}")
        print(f"  Nonce: {permit2_allowance[2]}")
    except Exception as e:
        print(f"❌ 查询失败: {e}")

    print("\n" + "=" * 60)

    # 步骤3: 结论
    print("\n[步骤3] 结论...")

    if allowance == 0:
        print("❌ Smart Account 没有授权 Permit2")
        print("\n需要先执行 approve：")
        print(f"  USDC.approve({PERMIT2_ADDRESS}, type(uint256).max)")
    else:
        print("✅ 已经授权 Permit2")
        print("\n但 swap 还是失败了，可能是：")
        print("  1. Permit2 nonce 问题")
        print("  2. Permit2 签名格式不正确")
        print("  3. Swap Router 的具体问题")

    print("\n" + "=" * 60)

if __name__ == "__main__":
    asyncio.run(check_permit2())
