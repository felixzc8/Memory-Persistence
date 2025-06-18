const { getDefaultConfig } = require("expo/metro-config");
const { withNativeWind } = require('nativewind/metro');
 
const config = getDefaultConfig(__dirname)

// Add resolver configuration for better Node.js compatibility
config.resolver.platforms = ['ios', 'android', 'native', 'web'];
 
module.exports = withNativeWind(config, { input: './app/globals.css' })