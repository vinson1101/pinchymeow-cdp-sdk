# PinchyMeow CDP SDK 工具包

**目的**: 为 PinchyMeow 和 F0x 提供完整的 CDP 钱包功能

**创建时间**: 2026-02-12 23:19 GMT+8  
**负责人**: PinchyMeow 🦞  
**Owner**: Vinson (sun1101)

---

## 📦 功能列表

### 1. 钱包管理
- ✅ 查询 ETH 余额
- ✅ 查询 USDC 余额
- ✅ 获取钱包地址
- ✅ 钱包信息显示

### 2. 转账功能
- ✅ ETH 转账
- ✅ USDC 转账
- ✅ 交易状态查询

### 3. 安全功能
- ✅ 私钥安全存储
- ✅ 环境变量配置
- ✅ 密钥不提交到 Git

---

## 🛠️ 项目结构

```
pinchymeow-cdp-sdk/
├── README.md                   # 本文件
├── package.json               # 项目配置
├── src/                       # 源代码
│   ├── wallet.js             # 钱包管理
│   ├── transfer-eth.js      # ETH 转账
│   ├── transfer-usdc.js     # USDC 转账
│   └── utils.js              # 工具函数
├── .env.example              # 环境变量示例
├── .gitignore                # Git 忽略文件
└── docs/                     # 文档
    ├── API.md                # CDP SDK 文档
    └── USAGE.md              # 使用说明
```

---

## 🔐 环境配置

复制 `.env.example` 到 `.env` 并配置：

```bash
# CDP API 密钥
CDP_API_KEY_ID=your-api-key-id
CDP_API_KEY_SECRET=your-api-key-secret
CDP_WALLET_SECRET=your-wallet-secret

# 网络
NETWORK=base

# USDC 合约地址（Base 链）
USDC_ADDRESS=0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913
```

---

## 📝 API 文档

### 查询余额

\`\`\`bash
node src/wallet.js balance
\`\`\`

**返回**: ETH 和 USDC 余额

---

### ETH 转账

\`\`\`bash
node src/transfer-eth.js <收货地址> <ETH 数量>
\`\`\`

**示例**:
\`\`\`bash
node src/transfer-eth.js 0xD75f990150D00EB02CfA22Ff49c659486C1AE4C6 0.001
\`\`\`

---

### USDC 转账

\`\`\`bash
node src/transfer-usdc.js <收货地址> <USDC 数量>
\`\`\`

**示例**:
\`\`\`bash
node src/transfer-usdc.js 0xD75f990150D00EB02CfA22Ff49c659486C1AE4C6 2
\`\`\`

---

## 🚀 快速开始

### 安装依赖

\`\`\`bash
npm install
\`\`\`

### 配置环境

\`\`\`bash
cp .env.example .env
# 编辑 .env 填入你的 CDP 密钥
\`\`\`

### 查询余额

\`\`\`bash
node src/wallet.js info
\`\`\`

---

## 📊 当前状态

**PinchyMeow 钱包**:
- **地址**: 0x145177cd8f0AD7aDE30de1CF65B13f5f45E19e91
- **网络**: Base Mainnet
- **ETH 余额**: 0 ETH
- **USDC 余额**: 3 USDC (转账 2 USDC 给 F0x 后剩余)

**F0x 钱包**:
- **地址**: 0xD75f990150D00EB02CfA22Ff49c659486C1AE4C6
- **资金**: 2 USDC

---

## 🔐 安全说明

**⚠️ 重要**:
- `.env` 文件包含敏感信息，**已添加到 .gitignore**
- **永远不提交** `.env` 文件到 Git
- `.env.example` 可以安全提交

**密钥管理**:
- CDP 私钥存储在 `/root/.openclaw/workspace/.env.cdp`
- 本项目使用独立 `.env`，从 `.env.cdp` 读取

---

## 📦 用途

### PinchyMeow 用途
- 管理 CDP 钱包（查询、转账）
- 为 F0x 提供资金支持
- 日常资金管理

### F0x 用途
- 接收 PinchyMeow 转账
- Base 链交易执行
- 策略资金分配（2 USDC）

---

## 🔄 版本历史

- **v1.0** (2026-02-12): 初始版本，基础 CDP 功能

---

*本项目由 PinchyMeow 为 Vinson 和 F0x 创建，用于管理 CDP 钱包和资金分配。* 🦞
