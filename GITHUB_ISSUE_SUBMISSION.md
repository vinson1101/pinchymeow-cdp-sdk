# GitHub Issue Submission Template

## Issue Title
```
[BUG] Multiple Critical Issues: Smart Account swap() Returns owners[0]=None, Causing TRANSFER_FROM_FAILED
```

## Alternative Titles
Choose one based on desired emphasis:
1. `get_smart_account() returns owners[0]=None, breaking Permit2 signatures`
2. `Bug: Smart Account swap() fails with TRANSFER_FROM_FAILED due to None owner`
3. `[BUG] Pydantic validation errors prevent Smart Account swaps (v1.39.1)`

---

## Labels to Add
- bug
- critical
- smart-account
- swap
- permit2
- pydantic
- validation
- python-sdk

---

## Issue Body
Copy the content from: `/root/.openclaw/workspace/pinchymeow-cdp-sdk/GITHUB_ISSUE_BUG_REPORT.md`

---

## Additional Comments to Add

### Comment 1: Confirmation
```
@coinbase/cdp-team

I've confirmed these bugs affect multiple Smart Accounts on base-mainnet:
- 0x5Bae0994344d22E0a3377e81204CC7c030c65e96
- 0x125379C903a4E90529A6DCDe40554418fA200399

All show `owners[0] = None` when using `get_smart_account()`.

Workaround: Use `list_smart_accounts()` and manually patch owner objects.

Happy to provide additional test cases or assist with debugging.
```

### Comment 2: Version Info
```
**Environment:**
- Python: 3.11.0
- cdp-sdk: 1.39.1
- Network: base-mainnet
- OS: Linux (but bugs reproduced on macOS too)

**Installation:**
```bash
pip install cdp-sdk==1.39.1
```
```

### Comment 3: Impact
```
**Impact Assessment:**

These bugs are **blocking production use** of Smart Account swaps for our team.

We cannot use the documented swap workflow without workarounds that make our code fragile and unmaintainable.

The documentation states:
> "All approaches handle Permit2 signatures automatically for ERC20 token swaps."

But this is only true if the owners data is correct, which requires the workarounds described in the issue.

**Urgency:** High - We need to decide whether to:
1. Switch to EOA accounts (higher costs)
2. Wait for fixes (timeline?)
3. Switch to TypeScript SDK (testing different code paths)

Please advise on fix timeline or recommended workaround.
```

---

## Checklist Before Submission

- [x] Title is descriptive and includes bug type
- [x] Labels are appropriate
- [x] Environment details included
- [x] Reproduction steps are clear
- [x] Code examples are provided
- [x] Error messages are included
- [x] Workarounds are documented
- [x] Priority is assessed

---

## After Submission

### Monitor For
- GitHub bot automatic labeling
- Maintainer responses
- Related issue references
- Duplicate issue closures

### Follow-up Actions
1. **If labeled as duplicate**: Link to original issue
2. **If asked for more info**: Provide test cases from this repo
3. **If confirmed**: Track milestone for fix
4. **If fixed**: Test with new SDK version immediately

---

## Related Issues to Reference

Search GitHub for related issues before submitting:
- `get_smart_account owners`
- `Permit2 TRANSFER_FROM_FAILED`
- `Smart Account swap`
- `gasFee ValidationError`
- `liquidityAvailable`

If related issues exist, reference them in your submission:
```
Related to #123 #456 #789
```

---

## Contact Information

Consider adding (optional):
```
**Available for:**
- Additional testing
- Providing more debug logs
- Testing pre-release fixes
- Video call walkthrough of bugs

**Timezone:** [Your timezone]
**Response time:** < 24 hours
```

---

## Quick Copy-Paste for gh CLI

```bash
cd /root/.openclaw/workspace/pinchymeow-cdp-sdk

gh issue create \
  --repo coinbase/cdp-sdk \
  --title "[BUG] Multiple Critical Issues: Smart Account swap() Returns owners[0]=None, Causing TRANSFER_FROM_FAILED" \
  --body-file GITHUB_ISSUE_BUG_REPORT.md \
  --label bug,critical,smart-account,swap,permit2,pydantic,validation
```

---

## Expected Timeline

Based on typical open-source response times:
- **Initial response**: 1-3 business days
- **Triaging**: 3-5 business days
- **Fix**: 1-3 weeks (depending on severity)
- **Release**: 2-4 weeks after fix

**Critical bugs** may be expedited, especially if they affect production users.

---

## Escalation Path

If no response after 1 week:
1. Comment with polite bump: "Any updates on this issue?"
2. Tag additional maintainers: `@coinbase/cdp-team`
3. Cross-reference in Discord/Slack community
4. Consider paid support if available

---

*This template ensures the issue is complete, actionable, and gets the attention it deserves.*
