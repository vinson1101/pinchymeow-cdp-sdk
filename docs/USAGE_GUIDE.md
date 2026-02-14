# PinchyMeow CDP SDK - 使用指南

**更新时间**: 2026-02-14

本指南帮助 **PinchyMeow** 和 **F0x** 两个 Agent 学会使用 CDP Trading 基础设施。

---

## 目录结构

```
pinchymeow-cdp-sdk/
├── config.py                          # 配置管理
├── requirements.txt                     # Python 依赖
├── src/
│   ├── cdp_core/
│   │   └── cdp_trader.py        # CDPTrader 核心类
│   ├── trader.py                     # SafeTrader 安全交易类
│   ├── transaction_logger.py         # TransactionLogger 日志类
│   ├── daily_report.py              # 每日报告生成器
│   └── sentinel.py                  # 价格哨兵脚本
├── data/                             # 数据目录（自动创建）
│   ├── transactions/                  # 交易日志（按账户隔离）
│   │   ├── f0x/                   # F0x 的日志
│   │   └── pinchymeow/             # PinchyMeow 的日志
│   └── reports/                       # 监控报告（自动创建）
│       ├── f0x-daily-*.md           # F0x 的报告
│       └── pinchymeow-daily-*.md    # PinchyMeow 的报告
└── tests/                             # 测试脚本
    └── integration_test.py            # 集成测试
```

---

## 快速开始

### 1. 安装依赖

```bash
cd /root/.openclaw/workspace/pinchymeow-cdp-sdk
pip3 install -r requirements.txt
```

### 2. 配置环境变量

确保 `/root/.openclaw/workspace/.env.cdp` 存在并包含正确的 API Keys：

```bash
CDP_API_KEY_ID=your_api_key_id
CDP_API_KEY_SECRET=your_api_key_secret
NETWORK=base
```

### 3. 验证配置

```bash
python3 -c "from config import Config; Config.validate()"
```

---

## PinchyMeow 使用指南

**角色**: 基础设施提供者（工具构建者）

### 1. 余额查询

```python
from src.cdp_core.cdp_trader import CDPTrader
import asyncio

async def check_balance():
    trader = CDPTrader(
        account_name='PINCHYMEOW_MAIN',
        agent_name='PinchyMeow'
    )
    balance = await trader.get_balance()
    print(f"ETH: {balance['eth_balance']:.6f}")
    print(f"USDC: ${balance['usdc_balance']:.2f}")
    await trader.close()

asyncio.run(check_balance())
```

**输出**:
```
ETH: 0.001000
USDC: 3.00
```

### 2. 价格查询（免费，无 Gas）

```python
from src.cdp_core.cdp_trader import CDPTrader
import asyncio

async def check_price():
    trader = CDPTrader(
        account_name='PINCHYMEOW_MAIN',
        agent_name='PinchyMeow'
    )
    quote = await trader.get_quote('eth', 'usdc', 1.0)
    print(f"1 ETH = ${quote['price']:.4f} USDC")
    await trader.close()

asyncio.run(check_price())
```

**输出**:
```
1 ETH = $2800.00 USDC
```

### 3. 生成每日报表

```bash
# 今日报告（所有 Agent）
python3 src/daily_report.py

# 指定日期
python3 src/daily_report.py 2026-02-13

# 指定 Agent
python3 src/daily_report.py --agent f0x
```

**输出示例**:
```
============================================================
每日交易报告 - 2026-02-14
============================================================

总览:
  总交易: 0
  成功: 0 | 失败: 0 | 待定: 0
  总交易额: $0.00 USD

按 Agent 分组:
============================================================
```

---

## F0x 使用指南

**角色**: 专业交易员（完全自主决策）

### 1. 价格监控（Sentinel）

```python
from src.sentinel import Sentinel
import asyncio

async def run_sentinel():
    sentinel = Sentinel(agent_name='F0x')
    await sentinel.run(daemon=False)  # 单次检查

asyncio.run(run_sentinel())
```

**工作原理**:
- 每 60 秒检查 ETH 价格
- 价格 < $2000 → 触发买入逻辑
- 价格 ≥ $2000 → 不操作
- 完全自主决策，不需要汇报

### 2. 安全交易

```python
from src.trader import SafeTrader
from src.transaction_logger import TransactionLogger
import asyncio

async def autonomous_trade():
    # 初始化
    logger = TransactionLogger('F0x')
    trader = SafeTrader(
        account_name='F0X_TRADING',
        agent_name='F0x',
        logger=logger
    )

    # 示例：小额交易（<$100，直接执行）
    result = await trader.swap_with_approval(
        from_token='usdc',
        to_token='eth',
        amount=0.50,  # $0.50 USDC
        agent_name='F0x'
    )

    if result['status'] == 'success':
        print(f"✅ 交易成功: {result['tx_hash']}")
    elif result['status'] == 'requires_approval':
        print(f"⚠️  大额交易需要人工确认")
        print(f"   价值: ${result['usd_value']:.2f} USD")

asyncio.run(autonomous_trade())
```

**工作原理**:
- 额度检查：不超过 $2 USD
- 滑点固定：100 bps (1%)
- > $100 需要人工确认（PinchyMeow 批准）
- ≤ $100 直接执行
- 自动记录交易日志

### 3. 查询交易日志

```python
from src.transaction_logger import TransactionLogger
import asyncio

async def check_logs():
    logger = TransactionLogger('F0x')

    # 获取今日所有交易
    transactions = logger.get_transactions()
    print(f"总交易: {len(transactions)}")

    for tx in transactions:
        print(f"- {tx['timestamp']}: {tx['type']}")
        print(f"  From: {tx['from_token']} → {tx['to_token']}")
        print(f"  Value: ${tx.get('usd_value', 0):.2f} USD")
        print(f"  Status: {tx['status']}")

asyncio.run(check_logs())
```

### 4. 查看账户信息

```python
from src.cdp_core.cdp_trader import CDPTrader
import asyncio

async def get_wallet_info():
    trader = CDPTrader(
        account_name='F0X_TRADING',
        agent_name='F0x'
    )
    wallet = await trader.get_wallet()
    print(f"Address: {wallet['address']}")
    print(f"Network: {wallet['network']}")
    print(f"ETH: {wallet['balances']['eth']:.6f}")
    print(f"USDC: ${wallet['balances']['usdc']:.2f}")

asyncio.run(get_wallet_info())
```

---

## 集成测试

运行所有测试：

```bash
cd /root/.openclaw/workspace/pinchymeow-cdp-sdk
python3 tests/integration_test.py
```

**测试覆盖**:
- ✅ CDPTrader 核心功能（余额、报价）
- ✅ SafeTrader 安全检查（额度、滑点、大额确认）
- ✅ TransactionLogger 按账户隔离
- ✅ Daily report 生成

---

## 交易流程图

```
PinchyMeow (基础设施提供者)           F0x (专业交易员)
                                     │
                                     │
                                     ▼
                          ┌────────────────────────────┴─────────┐
                          │                             │              │
    构建工具                       │              │
    (SafeTrader,                  │              │
     TransactionLogger,             │              │
      daily_report)              │              │
                                     │              │
                                     ▼
                                     │
                          ┌────────────────────────────┴─────────┐
                          │                             │              │
    价格监控                     │              │
    (sentinel.py)                 │              │
                          │              │              │
    自主决策                     │              │
    余额查询                     │              │
    交易执行                     │              │
    日志记录                     │              │
                                     ▼
                                     │
                          ┌────────────────────────────┴─────────┐
                          │   CDPTrader.get_balance()        │              │
                          │   CDPTrader.get_quote()           │              │
                          │   SafeTrader.swap_with_approval()    │              │
                          │   TransactionLogger.log()            │              │
                                     ▼
```

---

## 常见问题

### Q: 如何修改交易额度？

**A**: 编辑 `config.py`：

```python
TRADING_LIMITS = {
    'F0x': {
        'max_balance_usd': 5.00,  # 从 $2 改为 $5
        'allowed_pairs': ['usdc-eth', 'eth-usdc'],
        'max_single_trade_usd': 1.00,  # 从 $0.50 改为 $1
        'max_daily_trades': 20
    }
}
```

### Q: 如何修改价格阈值？

**A**: 编辑 `config.py`:

```python
SENTINEL_CONFIG = {
    'agent_name': 'F0x',
    'account_name': 'F0X_TRADING',
    'from_token': 'eth',
    'to_token': 'usdc',
    'amount': 1,  # 1 ETH
    'threshold_eth_price': 1900,  # 从 $2000 改为 $1900
    'check_interval': 60  # 秒
}
```

### Q: 如何查看 F0x 的交易历史？

**A**:

```bash
# 方式 1：使用 daily_report.py
python3 src/daily_report.py --agent f0x

# 方式 2：直接查看日志文件
cat /root/.openclaw/workspace/pinchymeow-cdp-sdk/data/transactions/f0x/2026-02-14.jsonl
```

### Q: 如何查看 PinchyMeow 的交易历史？

**A**:

```bash
# PinchyMeow 的日志
python3 src/daily_report.py --agent pinchymeow

# 或直接查看
cat /root/.openclaw/workspace/pinchymeow-cdp-sdk/data/transactions/pinchymeow/2026-02-14.jsonl
```

---

## 进阶使用

### 多代币支持

当前支持：ETH、USDC

如需其他代币（如 WBTC），在 `config.py` 中添加：

```python
TOKEN_ADDRESSES = {
    'eth': '0x4200000000000000000000000000006',
    'usdc': '0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913',
    'wbtc': '0x...'  # WBTC 合约地址
}
```

### DEX 套利（未来）

当前使用 CDP Trade API，自动路由到最佳 DEX。

套利机会检测（未来功能）：
- 跨 DEX 价格差异
- 自动执行套利交易
- MEV 保护

---

**作者**: Vinson <sun1101>
**维护者**: PinchyMeow 🦞
**文档版本**: 1.0.0
