const { createPublicClient, http } = require('viem');
const { base } = require('viem/chains');
const dotenv = require('dotenv');
const fs = require('fs');

dotenv.config({ path: '.env.cdp' });

const CONFIG = {
  network: 'base',
  usdcAddress: '0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913',
  pinchyMeowAddress: '0x145177cd8f0AD7aDE30de1CF65B13f5f45E19e91',
  f0xAddress: '0xD75f990150D00EB02CfA22Ff49c659486C1AE4C6'
};

async function main() {
  const client = createPublicClient({
    chain: base,
    transport: http()
  });
  
  const to = process.argv[2];
  const amount = parseFloat(process.argv[3]);
  
  if (!to || !amount || isNaN(amount)) {
    console.error('❌ 缺少或无效参数');
    console.log(`
用法: node check-transfer.js <收货地址> <USDC数量>

示例:
  node check-transfer.js 0xD75f990150D00EB02CfA22Ff49c659486C1AE4C6 2.5
  node check-transfer.js 0xD75f990150D00EB02CfA22Ff49c659486C1AE4C6 5
    `);
    process.exit(1);
  }
  
  if (amount < 0.5 || amount > 5) {
    console.error('❌ 转账金额超出范围');
    console.log('⚠️  单次转账范围: 0.5 - 5 USDC');
    process.exit(1);
  }
  
  console.log('\n💸 发送USDC:');
  console.log(`   收款: ${to}`);
  console.log(`   金额: ${amount} USDC`);
  console.log(`   从: PinchyMeow CDP钱包`);
  console.log(`   网络: Base`);
  console.log('');
  
  // 查询当前余额
  const usdcBalance = await client.readContract({
    address: CONFIG.usdcAddress,
    abi: [{
      name: 'balanceOf',
      type: 'function',
      stateMutability: 'view',
      inputs: [{ name: 'account', type: 'address' }],
      outputs: [{ type: 'uint256' }]
    }],
    functionName: 'balanceOf',
    args: [CONFIG.pinchyMeowAddress]
  });
  
  const pinchyMeowUSDC = parseInt(usdcBalance) / 1e6;
  const f0xBalance = await client.readContract({
    address: CONFIG.usdcAddress,
    abi: [{
      name: 'balanceOf',
      type: 'function',
      stateMutability: 'view',
      inputs: [{ name: 'account', type: 'address' }],
      outputs: [{ type: 'uint256' }]
    }],
    functionName: 'balanceOf',
    args: [CONFIG.f0xAddress]
  });
  const f0xUSDC = parseInt(f0xBalance) / 1e6;
  
  console.log('💰 当前余额:');
  console.log(`   PinchyMeow: ${pinchyMeowUSDC} USDC`);
  console.log(`   F0x: ${f0xUSDC} USDC`);
  console.log(`   合计: ${(pinyMeowUSDC + f0xUSDC) / 1e6} USDC`);
  console.log('');
  
  if (pinchMeowUSDC < amount) {
    console.error('❌ PinchyMeow余额不足');
    console.log(`   需要: ${amount} USDC`);
    console.log(`   当前: ${pinchyMeowUSDC} USDC`);
    process.exit(1);
  }
  
  console.log('✅ 余额验证通过，开始转账...\n');
  
  // 发送转账（手动构建交易）
  // 这里只能验证，实际转账需要 CDP SDK
  console.log('📋 转账说明:');
  console.log('   由于CDP SDK限制，请使用以下方式之一：');
  console.log('');
  console.log('   方案1（推荐）: Vinson 手动转账');
  console.log(`   从 ${CONFIG.pinchyMeowAddress} 转账 ${amount} USDC`);
  console.log(`   到 ${to}`);
  console.log('');
  console.log('   方案2: 从其他来源转账');
  console.log('   然后 F0x 可以在 Uniswap 等DEX兑换成 ETH');
  console.log('');
  console.log('   方案3: 等待我修复 CDP SDK 转账功能');
  
  process.exit(0);
}

if (require.main === module) {
  main();
}
