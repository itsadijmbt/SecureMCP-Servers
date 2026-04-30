#!/usr/bin/env node

const webpack = require('webpack');
const WebpackDevServer = require('webpack-dev-server');
const path = require('path');

// Import webpack configuration
const config = require('./webpack.config.js');

console.log('🛠️  Starting Local UI development server...');

// Set development mode
process.env.NODE_ENV = 'development';

const compiler = webpack(config);
const devServerOptions = {
  ...config.devServer,
  host: 'localhost'
};

const server = new WebpackDevServer(devServerOptions, compiler);

const runServer = async () => {
  console.log('🌐 Starting development server...');
  await server.start();

  console.log('✅ Development server running at:');
  console.log(`   http://localhost:${devServerOptions.port}`);
  console.log('');
  console.log('📝 This is a development preview of the Local UI.');
  console.log('   Changes will be automatically reflected.');
  console.log('   To build for CLI integration, run: npm run build');
};

runServer().catch(err => {
  console.error('❌ Failed to start development server:', err);
  process.exit(1);
});

// Handle graceful shutdown
process.on('SIGINT', () => {
  console.log('\n🛑 Shutting down development server...');
  server.stop().then(() => {
    process.exit(0);
  });
});

process.on('SIGTERM', () => {
  console.log('\n🛑 Shutting down development server...');
  server.stop().then(() => {
    process.exit(0);
  });
});