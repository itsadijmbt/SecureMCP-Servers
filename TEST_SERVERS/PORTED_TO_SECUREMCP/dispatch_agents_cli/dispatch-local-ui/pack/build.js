#!/usr/bin/env node

const webpack = require('webpack');
const path = require('path');
const fs = require('fs');

// Import webpack configuration
const config = require('./webpack.config.js');

console.log('🚀 Building Local UI components...');

// Set production mode
process.env.NODE_ENV = 'production';

// Update the configuration for production
config.mode = 'production';

// Run webpack with the configuration
const compiler = webpack(config);

compiler.run((err, stats) => {
  if (err) {
    console.error('❌ Build failed with error:', err);
    process.exit(1);
  }

  if (stats.hasErrors()) {
    console.error('❌ Build completed with errors:');
    console.error(stats.toString({
      colors: true,
      errors: true,
      warnings: false,
      chunks: false,
      modules: false
    }));
    process.exit(1);
  }

  if (stats.hasWarnings()) {
    console.warn('⚠️  Build completed with warnings:');
    console.warn(stats.toString({
      colors: true,
      errors: false,
      warnings: true,
      chunks: false,
      modules: false
    }));
  }

  console.log('✅ Build completed successfully!');
  console.log(stats.toString({
    colors: true,
    hash: false,
    version: false,
    timings: true,
    assets: true,
    chunks: false,
    modules: false,
    reasons: false,
    children: false,
    source: false,
    errors: false,
    warnings: false,
    publicPath: false
  }));

  // Check output files
  const outputPath = path.resolve(__dirname, '../../dispatch_cli/router/static');
  const files = ['index.html', 'components.js', 'components.css'].filter(file => {
    const filePath = path.join(outputPath, file);
    return fs.existsSync(filePath);
  });

  console.log(`\n📦 Generated files in ${outputPath}:`);
  files.forEach(file => {
    const filePath = path.join(outputPath, file);
    const stats = fs.statSync(filePath);
    const size = (stats.size / 1024).toFixed(2);
    console.log(`   ${file} (${size} KB)`);
  });

  console.log('\n🎉 Local UI build complete! You can now run:');
  console.log('   dispatch router start');

  compiler.close(() => {
    // Build completed and closed
  });
});