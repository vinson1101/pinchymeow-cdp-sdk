# Multiple CDP SDK Bugs Preventing Smart Account Swap Functionality

## Summary
Multiple critical bugs in the CDP Python SDK (v1.39.1) prevent Smart Account swap functionality from working correctly. These issues span from data model validation errors to incorrect owner handling, making it impossible to execute token swaps through Smart Accounts as documented.

## Bug Report Details

### Bug 1: `get_smart_account()` returns `owners[0] = None`
**Severity**: Critical
**Location**: SDK's `get_smart_account()` method
**Impact**: Cannot execute swaps because Permit2 EIP-712 signature requires valid owner address

#### Description
The `get_smart_account()` method returns a SmartAccount object with `owners[0] = None`, even though the API response contains correct owner addresses. However, `list_smart_accounts()` correctly returns owners as strings.

#### Reproduction
```python
from cdp import CdpClient

async with CdpClient(api_key_id=..., api_key_secret=...) as client:
    smart_addr = "0x5Bae0994344d22E0a3377e81204CC7c030c65e96"

    # Bug: get_smart_account() returns None owner
    smart_account = await client.evm.get_smart_account(address=smart_addr)
    print(smart_account.owners)  # [None]

    # Workaround: list_smart_accounts() works correctly
    list_result = await client.evm.list_smart_accounts()
    for acc in list_result.accounts:
        if acc.address == smart_addr:
            print(acc.owners)  # ['0x145177cd8f0AD7aDE30de1CF65B13f5f45E19e91']
```

#### Impact
- Cannot generate Permit2 EIP-712 signatures
- Swap operations fail with `TRANSFER_FROM_FAILED`
- Workaround requires using `list_smart_accounts()` and manually patching the owner

---

### Bug 2: Pydantic validation error for `gasFee` and `protocolFee` fields
**Severity**: High
**File**: `/usr/local/lib/python3.11/site-packages/cdp/openapi_client/models/common_swap_response_fees.py`
**Lines**: 31-32

#### Description
The `CommonSwapResponseFees` Pydantic model doesn't properly allow `None` for `gasFee` and `protocolFee` fields, causing validation errors when these fields are optional in the API response.

#### Error
```
ValidationError: gasFee
  Input should be a valid dictionary or instance of TokenFee
  Input value: None
```

#### Current Code (Buggy)
```python
# common_swap_response_fees.py, lines 31-32
gas_fee: Optional[TokenFee] = Field(default=None, ...)
protocol_fee: Optional[TokenFee] = Field(default=None, ...)
```

#### Expected Fix
The model should allow `None` values without validation errors, possibly by adjusting the Pydantic field constraints.

---

### Bug 3: `liquidityAvailable` validation error using `StrictBool`
**Severity**: High
**File**: `/usr/local/lib/python3.11/site-packages/cdp/openapi_client/models/create_swap_quote_response.py`
**Lines**: 40, 69-74

#### Description
The model uses `StrictBool` which only accepts the strings `'true'` or `'false'`, but the API returns Python boolean values `True` or `False`, causing validation errors.

#### Error
```
ValidationError: liquidity_available
  Input should be a valid boolean, unable to interpret input
```

#### Current Code (Buggy)
```python
# create_swap_quote_response.py, line 40
liquidity_available: bool = Field(...)

# Lines 69-74: Has strict validator that rejects boolean True/False
@field_validator('liquidity_available')
def validate_liquidity_available(cls, v):
    if not isinstance(v, str) or v not in ['true', 'false']:
        raise ValueError("liquidity_available must be 'true' or 'false'")
    return v
```

#### Expected Fix
Remove the `@field_validator` or modify it to accept both string and boolean values:
```python
@field_validator('liquidity_available')
def validate_liquidity_available(cls, v):
    if isinstance(v, bool):
        return v
    if isinstance(v, str) and v in ['true', 'false']:
        return v == 'true'
    raise ValueError("liquidity_available must be a boolean or 'true'/'false'")
```

---

### Bug 4: `CommonSwapResponseIssues` validation error for `allowance` and `balance`
**Severity**: High
**File**: `/usr/local/lib/python3.11/site-packages/cdp/openapi_client/models/common_swap_response_issues.py`
**Lines**: 32-33

#### Description
The `allowance` and `balance` fields don't allow `None` values, causing validation errors when the API response doesn't include these optional fields.

#### Current Code (Buggy)
```python
# Lines 32-33
allowance: Optional[CommonSwapResponseIssuesAllowance] = Field(default=None, ...)
balance: Optional[CommonSwapResponseIssuesBalance] = Field(default=None, ...)
```

#### Expected Fix
Ensure the model properly handles `None` values for these optional fields.

---

## Test Environment
- **CDP SDK Version**: 1.39.1
- **Python**: 3.11
- **Network**: Base (base-mainnet)
- **Test Smart Account**: `0x5Bae0994344d22E0a3377e81204CC7c030c65e96`
- **Test Owner**: `0x145177cd8f0AD7aDE30de1CF65B13f5f45E19e91`

## Error Chain & Root Cause
```
get_smart_account()
  ↓
owners[0] = None (Bug #1)
  ↓
Permit2 EIP-712 signature generation fails
  ↓
Swap transaction executes without proper signature
  ↓
On-chain revert: TRANSFER_FROM_FAILED
```

## Documentation vs. Reality
According to [CDP SDK documentation](https://docs.cdp.coinbase.com/):
> "All approaches handle Permit2 signatures automatically for ERC20 token swaps."

**However**, this only works if the `owners` data is correct, which it isn't due to Bug #1.

## Test Results Summary
- ✅ Smart Account has 3 USDC balance
- ✅ Owner is CDP-managed account
- ✅ Swap quote creates successfully (when bugs #2-4 are patched)
- ❌ Swap fails with `TRANSFER_FROM_FAILED` due to Bug #1

## Workarounds Tested
1. **Use `list_smart_accounts()` instead of `get_smart_account()`**
   - Works for reading owner addresses
   - Still creates issues when SDK expects owner objects

2. **Monkey-patch owner objects**
   ```python
   class FixedOwner:
       def __init__(self, address: str):
           self.address = address

   fixed_owner = FixedOwner(real_owner_address)
   smart_account.owners = [fixed_owner]
   ```
   - Partially works
   - Not a production-ready solution

3. **Manually patch SDK files**
   - Fixes bugs #2-4 temporarily
   - Changes are lost on `pip install --upgrade`

## Expected Behavior
1. `get_smart_account()` should return valid owner objects with correct addresses
2. Pydantic models should accept `None` for optional fields
3. Boolean validators should accept Python `True`/`False` values
4. Smart Account swap should work as documented without workarounds

## Impact on Development
- **Cannot use Smart Accounts for swaps** in production
- **Forced to use EOA accounts** which have higher gas costs
- **Documentation is misleading** about automatic Permit2 handling
- **Multiple workarounds required** make code fragile

## Suggested Priority
1. **Critical**: Fix Bug #1 (owners = None) - blocks all Smart Account swaps
2. **High**: Fix Bug #3 (StrictBool) - common validation issue
3. **High**: Fix Bug #2 (gasFee validation) - blocks swap quotes
4. **Medium**: Fix Bug #4 (allowance/balance validation) - edge case

## Additional Context
Tested with multiple Smart Accounts:
- `0x5Bae0994344d22E0a3377e81204CC7c030c65e96` (PinchyMeow-Smart)
- `0x125379C903a4E90529A6DCDe40554418fA200399` (F0x-Smart)

All show the same `owners[0] = None` issue when using `get_smart_account()`.

## Related Files
- SDK source: `/usr/local/lib/python3.11/site-packages/cdp/`
- Test cases available in the reproducible example
- Python 3.11.0 on Linux

## References
- CDP SDK Docs: https://docs.cdp.coinbase.com/
- Permit2: https://docs.uniswap.org/contracts/permit2/overview
- EIP-712: https://eips.ethereum.org/EIPS/eip-712
