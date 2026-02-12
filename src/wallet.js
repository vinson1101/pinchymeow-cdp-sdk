const dotenv = require('dotenv');
const { CdpClient } = require('@coinbase/cdp-sdk');
const { createPublicClient, http } = require('viem');
const { base } = require('viem/chains');
const fs = require('fs');
const path = require('path');

// 加载主配置环境变量
dotenv.config({ path: path.resolve(__dirname, '../../.env.cdp') });

const CONFIG = {
  network: process.env.NETWORK || 'base',
  usdcAddress: '0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913',
  addressPath: path.resolve(__dirname, '../.cdp-wallet-address')
};

/**
 * PinchyMeow CDP Wallet 管理类
 * 为 PinchyMeow 和 F0x 提供完整的钱包功能
 */
class PinchyMeowCDPWallet {
  constructor() {
    this.cdp = new CdpClient();
    this.account = null;
    this.publicClient = null;
  }
  
  async init() {
    console.log('🔐 初始化Coinbase CDP客户端...');
    
    this.publicClient = createPublicClient({
      chain: base,
      transport: http()
    });
    
    console.log('✅ CDP客户端已初始化');
  }
  
  async loadOrCreateAccount() {
    console.log('👤 加载Server Wallet账户...');
    
    // 1. 检查是否已保存地址
    if (fs.existsSync(CONFIG.addressPath)) {
      const savedAddress = fs.readFileSync(CONFIG.addressPath, 'utf8').trim();
      console.log(`📁 发现已保存的地址: ${savedAddress}`);
      
      // 验证地址格式
      if (savedAddress.startsWith('0x') && savedAddress.length === 42) {
        console.log(`✅ 使用现有账户: ${savedAddress}`);
        this.account = {
          address: savedAddress,
          type: 'evm-server'
        };
        return this.account;
      } else {
        console.log('⚠️  保存的地址格式错误，将创建新账户');
      }
    }
    
    // 2. 创建新账户
    console.log('🔑 创建新的Server Wallet账户...');
    this.account = await this.cdp.evm.createAccount();
    
    console.log(`✅ 新账户已创建: ${this.account.address}`);
    
    // 3. 保存地址
    fs.writeFileSync(CONFIG.addressPath, this.account.address);
    console.log(`✅ 地址已保存到: ${CONFIG.addressPath}`);
    
    return this.account;
  }
  
  async getBalance() {
    const balance = await this.publicClient.getBalance({
      address: this.account.address
    });
    
    const ethBalance = balance / 1e18;
    console.log(`💰 ETH余额: ${ethBalance} ETH`);
    
    return ethBalance;
  }
  
  async getUSDCBalance() {
    const balance = await this.publicClient.readContract({
      address: CONFIG.usdcAddress,
      abi: [{
        name: 'balanceOf',
        type: 'function',
        stateMutability: 'view',
        inputs: [{ name: 'account', type: 'address' }],
        outputs: [{ type: 'uint256' }]
      }],
      functionName: 'balanceOf',
      args: [this.account.address]
    });
    
    const usdcBalance = balance / 1e6;
    console.log(`💰 USDC余额: ${usdcBalance} USDC`);
    
    return usdcBalance;
  }
  
  async showInfo() {
    console.log('\n' + '='.repeat(60));
    console.log('🦞😼 PinchyMeow CDP Wallet 信息');
    console.log('='.repeat(60) + '\n');
    
    console.log(`📍 钱包地址: ${this.account.address}`);
    console.log(`⛓️  网络: Base (Chain ID: ${base.id})`);
    console.log(`🔐 类型: EVM Server Account`);
    console.log(`👤 管理方式: Coinbase CDP`);
    console.log('');
    
    await this.getBalance();
    await this.getUSDCBalance();
    
    console.log('');
  }
}

/**
 * CLI 接口
 */
async function main() {
  const wallet = new PinchyMeowCDPWallet();
  
  const command = process.argv[2] || 'info';
  
  try {
    await wallet.init();
    await wallet.loadOrCreateAccount();
    
    if (command === 'balance') {
      console.log('\n💰 查询余额\n');
      await wallet.getBalance();
      await wallet.getUSDCBalance();
    } else if (command === 'info') {
      await wallet.showInfo();
    } else {
      console.log(`
🦞 PinchyMeow CDP Wallet v1.0.0

用法: node src/wallet.js <command>

命令:
  balance       查询余额（ETH + USDC）
  info          显示钱包信息（默认）

示例:
  node src/wallet.js info
  node src/wallet.js balance
      `);
    }
  } catch (error) {
    console.error('❌ 错误:', error.message);
    process.exit(1);
  }
}

// CLI入口
if (require.main === module) {
  main();
}

module.exports = PinchyMeowCDPWallet;
