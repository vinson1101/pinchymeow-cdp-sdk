# PinchyMeow CDP SDK

**创建时间**: 2026-02-14
**负责人**: PinchyMeow 🦞
**版本**: 3.0.0 (Python 重构版)
**基于**: PinchyMeow-cdp-sdk v1.0.0 (Node.js)

---

## 项目说明

这是 PinchyMeow 的 Coinbase CDP SDK Python 重构版，为 OpenClaw Agent 提供链上交易功能。

### 核心功能

- ✅ **多账户支持** - 每个 Agent 控制自己的 CDP Account
- ✅ **前缀匹配权限** - Agent 只能使用前缀匹配的账户
- ✅ **链上交易** - 支持 USDC 转账、代币交换
- ✅ **余额查询** - ETH、USDC 余额查询
- ✅ **价格预言机** - 免费获取交换报价（不消耗 Gas）

---

## 目录结构

```
pinchymeow-cdp-sdk/
├── .env.python.example    # Python 环境变量示例
├── requirements.txt        # Python 依赖
├── config.py            # 配置管理（环境变量 + 常量）
├── wallet.py            # CDP 核心类
├── trader.py            # 交易核心类
└── README.md
```

---

## 环境变量

复制 `.env.python.example` 到 `.env.python` 并配置：

```bash
# CDP API Keys (从 https://portal.cdp.coinbase.com/ 获取)
CDP_API_KEY_ID=your-api-key-id
CDP_API_KEY_SECRET=your-api-key-secret

# 网络 (base-mainnet, base-sepolia)
NETWORK=base-mainnet
```

---

## 使用方法

### Python SDK 导入

```python
from wallet import CDPWallet
from config import Config

# 初始化钱包
wallet = CDPWallet()
await wallet.init()

# 查询余额
balance = await wallet.get_balance('usdc')
print(f"USDC 余额: {balance}")
```

### CLI 调用

```bash
# 查询余额
python wallet.py --account PinchyMeow-Main --balance usdc

# 发送 USDC
python wallet.py --account PinchyMeow-Main --send 0x... 1.0

# 代币交换
python trader.py --account PinchyMeow-Main --swap usdc eth 1.0
```

---

## 变更记录

### v3.0.0 (2026-02-14)

**从 Node.js 重构为 Python**

#### 新增
- ✅ Python SDK 实现
- ✅ 配置管理模块
- ✅ 钱包管理模块
- ✅ 交易执行模块

#### 移除
- ❌ Node.js 实现 (v1.0.0)
- ❌ 旧版钱包脚本

---

## 依赖

- `coinbase-cdp-sdk>=1.0.0`
- `web3>=6.15.0`
- `python-dotenv>=1.0.0`

---

**作者**: PinchyMeow 🦞
**项目**: OpenClaw CDP Trading Skill
