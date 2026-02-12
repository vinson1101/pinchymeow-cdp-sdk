const dotenv = require('dotenv');
const { CdpClient } = require('@coinbase/cdp-sdk');
const { createPublicClient, http } = require('viem');
const { base } = require('viem/chains');
const fs = require('fs');
const path = require('path');

dotenv.config({ path: path.resolve(__dirname, '../../.env.cdp') });

const CONFIG = {
  network: process.env.NETWORK || 'base',
  usdcAddress: '0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913',
  addressPath: path.resolve(__dirname, '../../.cdp-wallet-address')
};

/**
 * PinchyMeow USDC 转账功能
 * 使用 CDP SDK 的 transfer 方法（需要 accountTransferStrategy）
 */
async function main() {
  console.log('🔐 初始化Coinbase CDP客户端...');
  
  const publicClient = createPublicClient({
    chain: base,
    transport: http()
  });
  
  const cdp = new CdpClient();
  
  const to = process.argv[2];
  const amount = process.argv[3];
  
  if (!to || !amount) {
    console.error('❌ 缺少参数');
    console.log(`
用法: node transfer-usdc.js <收货地址> <USDC数量>

示例:
  node transfer-usdc.js 0xD75f990150D00EB02CfA22Ff49c659486C1AE4C6 2
    `);
    process.exit(1);
  }
  
  console.log(`💸 发送USDC:`);
  console.log(`   收款: ${to}`);
  console.log(`   金额: ${amount} USDC`);
  
  // 从 .env 读取 API 密钥
  const apiKeyId = process.env.CDP_API_KEY_ID;
  const apiKeySecret = process.env.CDP_API_KEY_SECRET;
  const walletSecret = process.env.CDP_WALLET_SECRET;
  
  if (!apiKeyId || !apiKeySecret || !walletSecret) {
    console.error('❌ 缺少 CDP API 密钥');
    console.log('请在 .env.cdp 中配置:');
    console.log('  CDP_API_KEY_ID=your-api-key-id');
    console.log('  CDP_API_KEY_SECRET=your-api-key-secret');
    console.log('  CDP_WALLET_SECRET=your-wallet-secret');
    process.exit(1);
  }
  
  try {
    // 转换金额为 6 位小数（USDC 使用 6 位小数）
    const amountWei = BigInt(amount * 1e6);
    
    // 编码 transfer 函数调用
    const transferData = {
      to: CONFIG.usdcAddress,
      data: `0xa9059cbb${to.slice(2).padStart(64, '0')}${amountWei.toString(16).padStart(64, '0')}`
    };
    
    const result = await cdp.evm.sendTransaction({
      address: '0x145177cd8f0AD7aDE30de1CF65B13f5f45E19e91',  // PinchyMeow CDP 钱包
      network: CONFIG.network,
      transaction: {
        to: transferData.to,
        data: transferData.data,
        value: '0'
      }
    });
    
    console.log('\n✅ USDC转账成功!');
    console.log(`   交易哈希: ${result.transactionHash}`);
    console.log(`   BaseScan: https://basescan.org/tx/${result.transactionHash}`);
    console.log(`   验证: https://basescan.org/address/${to}`);
    
  } catch (error) {
    console.error('\n❌ USDC转账失败:', error.message);
    if (error.stack) {
      console.error('堆栈信息:', error.stack);
    }
    process.exit(1);
  }
}

// CLI 入口
if (require.main === module) {
  main();
}
