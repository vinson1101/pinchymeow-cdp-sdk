# Quick Bug Reference - CDP SDK Smart Account Issues

## The One-Paragraph Summary
CDP Python SDK v1.39.1 has 4 bugs preventing Smart Account swaps: (1) `get_smart_account()` returns `owners[0]=None` breaking Permit2 signatures, (2) `gasFee` field rejects None, (3) `liquidityAvailable` validator rejects boolean True/False, (4) `allowance`/`balance` fields don't allow None. Result: All Smart Account swaps fail with `TRANSFER_FROM_FAILED`.

---

## Bug #1: Owners = None (CRITICAL)
```python
# BROKEN
smart_account = await client.evm.get_smart_account(address=addr)
print(smart_account.owners)  # [None] ← BROKEN

# WORKAROUND
list_result = await client.evm.list_smart_accounts()
owner = [acc.owners[0] for acc in list_result.accounts if acc.address == addr][0]
print(owner)  # '0x...' ← WORKS
```

**Impact**: Cannot sign Permit2 → swap fails with `TRANSFER_FROM_FAILED`

---

## Bug #2: gasFee ValidationError (HIGH)
**File**: `common_swap_response_fees.py:31-32`
**Error**: `Input should be a valid dictionary or instance of TokenFee. Input value: None`
**Fix**: Allow None in Pydantic model

---

## Bug #3: StrictBool ValidationError (HIGH)
**File**: `create_swap_quote_response.py:40,69-74`
**Error**: `liquidity_available must be 'true' or 'false'` (but gets boolean True/False)
**Fix**: Accept both string and boolean values

---

## Bug #4: allowance/balance ValidationError (MEDIUM)
**File**: `common_swap_response_issues.py:32-33`
**Error**: Optional fields reject None values
**Fix**: Properly handle None for optional fields

---

## Test Environment
- SDK: `cdp-sdk==1.39.1`
- Python: 3.11.0
- Network: Base (base-mainnet)
- Account: `0x5Bae0994344d22E0a3377e81204CC7c030c65e96`

---

## Error Chain
```
get_smart_account()
  → owners[0] = None
  → Cannot generate Permit2 signature
  → Swap executes without signature
  → TRANSFER_FROM_FAILED
```

---

## Workarounds

### 1. Use list_smart_accounts()
```python
list_result = await client.evm.list_smart_accounts()
owner = next(acc.owners[0] for acc in list_result.accounts if acc.address == addr)
```

### 2. Monkey-patch owner
```python
class FixedOwner:
    def __init__(self, address):
        self.address = address

smart_account.owners = [FixedOwner(owner_addr)]
```

### 3. Use EOA instead (not recommended)
Higher gas costs, defeats purpose of Smart Accounts.

---

## Priority
1. **Bug #1**: CRITICAL - Blocks all Smart Account swaps
2. **Bug #3**: HIGH - Common validation issue
3. **Bug #2**: HIGH - Blocks swap quotes
4. **Bug #4**: MEDIUM - Edge case

---

## GitHub Issue
See `GITHUB_ISSUE_BUG_REPORT.md` for full report with:
- Detailed reproduction steps
- Code examples for all bugs
- Test results and error logs
- Suggested fixes

---

*Created: 2026-02-14 | SDK: 1.39.1 | Python: 3.11*
