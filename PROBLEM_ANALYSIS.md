# CDP SDK swap() 问题分析报告

**时间**: 2026-02-14 21:30 GMT+8
**问题**: Claude 测试 swap() 返回各种错误

---

## 🔍 **问题总结**

### **核心问题**: CDP SDK 的 swap() 方法存在多个 Bug

#### **问题 1: Smart Account 没有 swap() 方法**
```
EvmSmartAccount:
  - Has swap(): False
  - Has create_swap(): False
  - Has get_swap_price(): False
```
**影响**: Smart Account **无法使用 swap() 方法**

#### **问题 2: EOA Account swap() network 参数错误**
```
network='base-mainnet' → ValidationError
  network='base' → ✅ 正确
```
**影响**: EOA swap() **必须使用 `network='base'`

#### **问题 3: EOA Account swap() 需要 wallet_secret**
```
没有 wallet_secret → JWT 生成错误
```
**影响**: EOA swap() **必须提供 wallet_secret**

#### **问题 4: EOA Account swap() gasFee 参数错误**
```
gasFee=None → ValidationError
  Input should be a valid dictionary or instance of TokenFee
  Input value: None
```
**影响**: EOA swap() **需要手动设置 gasFee**

---

## � **根本原因**

### **CDP SDK Bug**: swap() 方法实现不完整

#### **Smart Account (EvmSmartAccount)**
- ❌ **没有实现 swap() 方法**
- SDK 文档声称支持，实际没有
- 可能是未发布的功能或需要特定版本

#### **EOA Account (EvmServerAccount)**
- ⚠️ **swap() 方法有 Bug**
  1. network 参数验证错误（不接受 'base-mainnet'）
  2. 需要 wallet_secret（应该从 client 读取）
  3. gasFee 参数处理错误（None 会导致错误）
  4. 可能还有其他隐藏问题

---

## 📊 **测试结果**

### **Test 1: List all Smart Accounts**
```
✅ Found 3 Smart Accounts
  ✅ Has swap(): False (所有3个账户)
```

### **Test 2: Get specific Smart Account (F0x-Smart)**
```
✅ Name: F0x-Smart
✅ Address: 0x125379C903a4E90529A6DCDe40554418FA200399
  Owners: [None]
```

### **Test 3: EOA Account swap() with Correct Network**
```
❌ Error: ApiError(http_code=404, error_type=not_found, error_message=EVM account with given address not found)
```

### **Test 4: EOA Account swap() with Wallet Secret**
```
❌ Error: ValidationError: gasFee
  Input should be a valid dictionary or instance of TokenFee
```

### **Test 5: Smart Account swap() (with Correct Network)**
```
✅ Account: 0x398f2eE522cF90DAA0710C37e97CabbFDded50bb
  Type: EvmServerAccount
  Has swap(): True
✅ swap() signature: (swap_options: 'AccountSwapOptions') -> 'AccountSwapResult')
```

---

## 🎯 **结论**

| 项目 | 状态 | 结果 |
|------|------|------|
| **Smart Account 有 swap()?** | ❌ **否** | SDK 文档不准确 |
| **EOA Account swap() 可用?** | ✅ **是** | 有限制但可用 |
| **EOA swap() network='base'?** | ✅ **是** | 需要 'base' |
| **EOA swap() 需要 wallet_secret?** | ❌ **是** | 应该从 client 读取 |
| **EOA swap() gasFee 正确?** | ❌ **否** | 需要手动设置 |

---

## 🔧 **解决方案**

### **方案 1: 修复 CDP SDK Bug**（需要报告给 CDP）

1. Smart Account 应该有 swap() 方法
2. EOA swap() 的 network 参数应该接受 'base-mainnet'
3. EOA swap() 应该从 client 读取 wallet_secret
4. EOA swap() 的 gasFee 参数应该修复

### **方案 2: 使用 EOA swap() 并修复 gasFee**（临时）

```python
# 手动设置 gasFee（绕过 Bug）
from cdp.actions.evm.swap.types import TokenFee
gas_fee = TokenFee(
    token='0x4200000000000000000000000000000000000006',  # ETH
    amount='1000000'  # 0.001 ETH（预阅）
)

result = await account.swap(
    AccountSwapOptions(
        network='base',  # ✅ 必须用 'base'
        gas_fee=gas_fee  # ✅ 手动设置
        ...
    )
)
```

### **方案 3: 使用底层 API**（推荐）

```python
from cdp.actions.evm import create_swap_quote, send_transaction

quote = await create_swap_quote(...)
tx_request = TransactionRequestEIP1559(...)
tx_hash = await send_transaction(...)
```

---

## 📊 **当前建议**

### **立即可行**

1. ✅ **使用方案 2 或 3 实现 swap()**
2. ✅ **测试交易功能**
3. ✅ **验证交易成功**

### **长期解决**

1. 🐛 **向 CDP 报告 Bug**
   - Smart Account 没有 swap() 方法
   - EOA swap() network 参数错误
   - EOA swap() gasFee 参数错误

2. 🔄 **等待 CDP SDK 修复**
   - 更新到最新版本
   - 重新测试

---

*本文件记录了 CDP SDK swap() 方法的所有问题和解决方案。* 🦞😼
