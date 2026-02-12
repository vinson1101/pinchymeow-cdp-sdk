const { PinchyMeowCDPWallet } = require('./wallet');

/**
 * ETH 转账功能
 */
async function transferETH() {
  const wallet = new PinchyMeowCDPWallet();
  
  await wallet.init();
  await wallet.loadOrCreateAccount();
  
  const to = process.argv[2];
  const amount = process.argv[3];
  
  if (!to || !amount) {
    console.error('❌ 缺少参数');
    console.log(`
用法: node src/transfer-eth.js <收货地址> <ETH 数量>

示例:
  node src/transfer-eth.js 0xD75f990150D00EB02CfA22Ff49c659486C1AE4C6 0.001
    `);
    process.exit(1);
  }
  
  console.log('\n💸 发送交易:');
  console.log(`   收款: ${to}`);
  console.log(`   金额: ${amount} ETH`);
  
  try {
    const result = await wallet.cdp.evm.sendTransaction({
      address: wallet.account.address,
      network: 'base',
      transaction: {
        to,
        value: amount
      }
    });
    
    console.log('\n✅ 交易已发送!');
    console.log(`   交易哈希: ${result.transactionHash}`);
    console.log(`   BaseScan: https://basescan.org/tx/${result.transactionHash}`);
  } catch (error) {
    console.error('\n❌ 转账失败:', error.message);
    if (error.stack) {
      console.error('堆栈信息:', error.stack);
    }
    process.exit(1);
  }
}

// CLI入口
if (require.main === module) {
  transferETH();
}

module.exports = { transferETH };
