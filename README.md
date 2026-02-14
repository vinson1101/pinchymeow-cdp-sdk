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
├── config.py                    # 配置管理（环境变量 + 常量）
├── requirements.txt             # Python 依赖
├── README.md                    # 项目说明
└── src/                         # Python 源代码
    ├── __init__.py              # 包初始化
    ├── cdp_core.py              # CDP 核心类（交易、余额、钱包）
    ├── trader.py                # 增强交易模块（安全检查）
    ├── transaction_logger.py    # 交易日志记录器
    ├── daily_report.py          # 每日报告生成器
    └── sentinel.py              # 价格哨兵脚本
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
from src import CDPTrader, SafeTrader, TransactionLogger
from config import Config

# 初始化交易核心
core = CDPTrader()

# 查询余额
balance = await core.get_balance()
print(f"ETH: {balance['eth_balance']}, USDC: {balance['usdc_balance']}")

# 获取价格报价（免费，无 Gas）
quote = await core.get_quote(from_token='eth', to_token='usdc', amount=1.0)
print(f"预期收到: {quote['expected_amount']} USDC")
```

### 安全交易（推荐）

```python
from src import SafeTrader, TransactionLogger

# 初始化安全交易器
logger = TransactionLogger()
trader = SafeTrader(logger=logger)

# 安全交换（自动检查大额交易）
result = await trader.swap_with_approval(
    from_token='usdc',
    to_token='eth',
    amount=10.0,
    agent_name='F0x'
)

if result['status'] == 'requires_approval':
    print(f"⚠️  大额交易需要确认: ${result['usd_value']:.2f}")
elif result['status'] == 'success':
    print(f"✅ 交易成功: {result['tx_hash']}")
```

### CLI 调用

```bash
# 查询余额
python src/daily_report.py              # 今日交易报告
python src/daily_report.py 2026-02-14   # 指定日期报告

# 价格哨兵（单次检查）
python src/sentinel.py

# 价格哨兵（守护进程）
python src/sentinel.py --daemon
```

---

## 变更记录

### v3.0.0 (2026-02-14)

**从 Node.js 重构为 Python**

#### 新增
- ✅ Python SDK 实现
- ✅ 配置管理模块 (`config.py`)
- ✅ CDP 核心交易模块 (`cdp_core.py`)
- ✅ 增强交易模块 (`trader.py`) - 安全检查、滑点限制、大额确认
- ✅ 交易日志记录器 (`transaction_logger.py`) - JSONL 格式、按日轮转
- ✅ 每日报告生成器 (`daily_report.py`) - 交易统计、Agent 分组
- ✅ 价格哨兵脚本 (`sentinel.py`) - 轻量级监控、自动触发

#### 核心特性
- 🔒 固定滑点 1%（防止 LLM 自行决定导致大额损失）
- 🛡️ 大额交易人工确认机制（阈值 $100 USD）
- 📊 免费价格预言机（高频监控，无 Gas 消耗）
- 📝 完整交易日志记录（JSONL 格式）
- 📈 每日交易报告生成
- 🚨 价格哨兵自动触发（ETH < $2000）

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
