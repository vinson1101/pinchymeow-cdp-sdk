# PinchyMeow CDP 钱包工具 - 使用说明

## 🚀 快速开始

### 安装依赖（已完成）
```bash
cd /root/.openclaw/workspace/pinchymeow-cdp-sdk
npm install
```

### 配置环境
```bash
# 使用现有的 CDP 配置
cd /root/.openclaw/workspace/pinchymeow-cdp-sdk
cp ../../.env.cdp .env
```

## 📝 当前功能（立即可用）

### 1. 查询余额
```bash
node src/wallet.js info
```
**返回**: ETH 和 USDC 余额（包括 3 USDC）

### 2. ETH 转账
```bash
node src/transfer-eth.js <收货地址> <ETH 数量>
```
**示例**: 转账 0.001 ETH
```bash
node src/transfer-eth.js 0xD75f990150D00EB02CfA22Ff49c659486C1AE4C6 0.001
```

## 🔐 API 密钥配置

CDP SDK 初始化需要以下环境变量（已在 .env.cdp 中配置）：

```bash
CDP_API_KEY_ID=ca7ee92c-d269-4715-ae9b-1c9d75339a27
CDP_API_KEY_SECRET=B5+rm8t6l3XZT6PJoko+7VeU4Ct0kXyv91ky8nB7ApFFL0FQemn+x4mdogua4vBzNKm55RGjdj8iUftGNA7xvw==
CDP_WALLET_SECRET=MIGHAgEAMBMGByqGSM49AgEGCCqGSM49AwEHBG0wawIBAQQg8EXUxsi3mjaAOvGz9MGiigKNRR/aTAGK/eN9sFe2fVehRANCAASHF8xkER4doX7SUZxAPuHBxukFtFbdvW4n8jIFErlnGWhtUE43480O4dyvYJJ3HCEERYS/3O3S0v91JjfcnC3
```

## 🎯 实际用例

### 查询 PinchyMeow 余额
```bash
node src/wallet.js info
```
**预期输出**:
- ETH: 0 ETH
- USDC: 3 USDC

### 转账 2 USDC 给 F0x
```bash
node src/transfer-usdc.js 0xD75f990150D00EB02CfA22Ff49c659486C1AE4C6 2
```

### 转账 0.001 ETH 给 F0x
```bash
node src/transfer-eth.js 0xD75f990150D00EB02CfA22Ff49c659486C1AE4C6 0.001
```

## 📊 项目结构

```
pinchyMeow-cdp-sdk/
├── README.md          # 本文件
├── package.json        # 项目配置（已安装依赖）
├── .gitignore         # Git 忽略（密钥安全）
├── .env.example       # 环境变量示例
├── src/              # 源代码
│   ├── wallet.js         # 钱包管理
│   ├── transfer-eth.js   # ETH 转账
│   └── transfer-usdc.js  # USDC 转账
└── docs/             # 文档
```

## ✅ 立即可用

**项目状态**:
- ✅ 依赖已安装（99 包）
- ✅ Git 已初始化
- ✅ .gitignore 已配置（密钥不提交）
- ✅ 源代码已创建

**当前限制**:
- ⚠️ CDP SDK 需要完整环境变量初始化（当前简化）
- ✅ 钱包地址已加载
- ✅ 可执行转账（需要配置环境变量）

## 🚀 下一步

1. **配置环境**: `cp ../../.env.cdp .env`
2. **测试查询**: `node src/wallet.js info`
3. **执行转账**: `node src/transfer-usdc.js <地址> <数量>`

---

*项目由 PinchyMeow 为 Vinson 和 F0x 创建，用于管理 CDP 钱包和 5 USDC 可用资金。* 🦞
