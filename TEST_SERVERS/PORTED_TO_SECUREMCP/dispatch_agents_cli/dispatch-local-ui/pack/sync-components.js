#!/usr/bin/env node

const fs = require('fs').promises;
const path = require('path');

const WEB_APP_COMPONENTS_DIR = path.resolve(__dirname, '../../../web-app/src/components/ui');
const LOCAL_APP_SHARED_DIR = path.resolve(__dirname, '../src/shared');

// Components we want to sync from web-app
const COMPONENTS_TO_SYNC = [
  'button.tsx',
  'card.tsx',
  'badge.tsx',
  'input.tsx',
  'textarea.tsx',
  'utils.ts', // Utility functions like cn()
];

async function ensureDirectory(dir) {
  try {
    await fs.mkdir(dir, { recursive: true });
  } catch (error) {
    if (error.code !== 'EEXIST') {
      throw error;
    }
  }
}

async function copyFile(source, destination) {
  try {
    await fs.copyFile(source, destination);
    return true;
  } catch (error) {
    console.warn(`⚠️  Could not copy ${path.basename(source)}: ${error.message}`);
    return false;
  }
}

async function syncComponents() {
  console.log('🔄 Syncing components from web-app...');

  // Ensure shared directory exists
  await ensureDirectory(LOCAL_APP_SHARED_DIR);

  let syncedCount = 0;
  let failedCount = 0;

  for (const componentFile of COMPONENTS_TO_SYNC) {
    const sourcePath = path.join(WEB_APP_COMPONENTS_DIR, componentFile);
    const destPath = path.join(LOCAL_APP_SHARED_DIR, componentFile);

    console.log(`📋 Syncing ${componentFile}...`);

    const success = await copyFile(sourcePath, destPath);
    if (success) {
      syncedCount++;
      console.log(`   ✅ ${componentFile}`);
    } else {
      failedCount++;
      console.log(`   ❌ ${componentFile}`);
    }
  }

  console.log(`\n📊 Sync Summary:`);
  console.log(`   ✅ Synced: ${syncedCount} components`);
  if (failedCount > 0) {
    console.log(`   ❌ Failed: ${failedCount} components`);
  }

  // Create an index file for easier imports
  const indexContent = COMPONENTS_TO_SYNC
    .filter(file => file.endsWith('.tsx'))
    .map(file => {
      const componentName = path.basename(file, '.tsx');
      const pascalName = componentName.charAt(0).toUpperCase() + componentName.slice(1);
      return `export * from './${file}';`;
    })
    .join('\n');

  const indexPath = path.join(LOCAL_APP_SHARED_DIR, 'index.ts');
  await fs.writeFile(indexPath, indexContent + '\n');
  console.log(`📝 Created index.ts for easier imports`);

  if (failedCount === 0) {
    console.log('\n🎉 All components synced successfully!');
  } else {
    console.log('\n⚠️  Some components failed to sync. Check the web-app directory structure.');
  }
}

// Run the sync
syncComponents().catch(error => {
  console.error('❌ Sync failed:', error);
  process.exit(1);
});