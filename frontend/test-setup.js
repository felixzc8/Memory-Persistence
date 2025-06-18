#!/usr/bin/env node

const fs = require('fs');
const path = require('path');

console.log('🧪 Homi Frontend Setup Test');
console.log('============================\n');

// Check if key files exist
const requiredFiles = [
  'package.json',
  'app/index.tsx',
  'app/landing.tsx', 
  'app/chat.tsx',
  'app/auth/signin.tsx',
  'app/auth/signup.tsx',
  'contexts/AuthContext.tsx',
  'lib/supabase.ts',
  'lib/api.ts',
];

console.log('📁 Checking required files...');
let allFilesExist = true;

requiredFiles.forEach(file => {
  const filePath = path.join(__dirname, file);
  if (fs.existsSync(filePath)) {
    console.log(`✅ ${file}`);
  } else {
    console.log(`❌ ${file} - MISSING`);
    allFilesExist = false;
  }
});

console.log('');

// Check environment configuration
console.log('🔧 Checking environment configuration...');

const envFile = path.join(__dirname, '.env');
if (fs.existsSync(envFile)) {
  console.log('✅ .env file exists');
  
  try {
    const envContent = fs.readFileSync(envFile, 'utf8');
    const requiredEnvVars = [
      'EXPO_PUBLIC_SUPABASE_URL',
      'EXPO_PUBLIC_SUPABASE_ANON_KEY',
      'EXPO_PUBLIC_API_URL'
    ];
    
    requiredEnvVars.forEach(envVar => {
      if (envContent.includes(envVar)) {
        console.log(`✅ ${envVar} configured`);
      } else {
        console.log(`⚠️  ${envVar} not found in .env`);
      }
    });
  } catch (error) {
    console.log('❌ Error reading .env file');
  }
} else {
  console.log('⚠️  .env file not found (create from config.example.ts)');
}

console.log('');

// Check package.json dependencies
console.log('📦 Checking dependencies...');

try {
  const packageJson = JSON.parse(fs.readFileSync('package.json', 'utf8'));
  const requiredDeps = [
    '@supabase/supabase-js',
    'expo-router',
    'nativewind',
    '@expo/vector-icons',
    '@react-native-async-storage/async-storage'
  ];
  
  requiredDeps.forEach(dep => {
    if (packageJson.dependencies && packageJson.dependencies[dep]) {
      console.log(`✅ ${dep}`);
    } else {
      console.log(`❌ ${dep} - Missing dependency`);
    }
  });
} catch (error) {
  console.log('❌ Error reading package.json');
}

console.log('');

// Final status
if (allFilesExist) {
  console.log('🎉 All required files are present!');
  console.log('');
  console.log('📋 Next steps:');
  console.log('1. Create .env file with your Supabase credentials');
  console.log('2. Run: npm install');
  console.log('3. Start development: npm start');
  console.log('4. Test authentication and chat features');
} else {
  console.log('⚠️  Some files are missing. Please check the setup.');
}

console.log('');
console.log('📚 For detailed setup instructions, see README_FRONTEND.md'); 