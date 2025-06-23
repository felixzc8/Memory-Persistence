import React from 'react'
import {
  View,
  Text,
  TouchableOpacity,
  SafeAreaView,
  Image,
  StatusBar,
} from 'react-native'
import { router } from 'expo-router'
import { Ionicons } from '@expo/vector-icons'

export default function Landing() {
  return (
    <SafeAreaView className="flex-1 bg-gradient-to-br from-blue-50 to-indigo-100">
      <StatusBar barStyle="dark-content" backgroundColor="transparent" translucent />
      
      <View className="flex-1 px-6 py-8">
        {/* Header Section */}
        <View className="flex-1 justify-center items-center">
          <View className="mb-8">
            <View className="w-20 h-20 bg-blue-500 rounded-full items-center justify-center mb-4">
              <Ionicons name="chatbubbles" size={40} color="white" />
            </View>
            <Text className="text-4xl font-bold text-gray-900 text-center mb-2">
              Homi
            </Text>
            <Text className="text-lg text-gray-600 text-center max-w-sm">
              Your intelligent companion with persistent memory
            </Text>
          </View>

          {/* Features */}
          <View className="w-full max-w-sm space-y-4 mb-8">
            <FeatureItem 
              icon="save-outline" 
              title="Persistent Memory" 
              description="Remembers your conversations across sessions"
            />
            <FeatureItem 
              icon="shield-checkmark" 
              title="Secure & Private" 
              description="Your data is encrypted and protected"
            />
            <FeatureItem 
              icon="flash" 
              title="AI-Powered" 
              description="Powered by advanced language models"
            />
          </View>
        </View>

        {/* Action Buttons */}
        <View className="gap-2">
          <TouchableOpacity
            className="bg-blue-500 rounded-xl py-4 px-6 flex-row items-center justify-center shadow-lg"
            onPress={() => router.push('/auth/signin')}
            activeOpacity={0.8}
          >
            <Text className="text-white text-lg font-semibold">Sign In</Text>
          </TouchableOpacity>

          <TouchableOpacity
            className="bg-white border-2 border-blue-500 rounded-xl py-4 px-6 flex-row items-center justify-center"
            onPress={() => router.push('/auth/signup')}
            activeOpacity={0.8}
          >
            <Text className="text-blue-500 text-lg font-semibold">Create Account</Text>
          </TouchableOpacity>

          <View className="flex-row items-center">
            <View className="flex-1 h-px bg-gray-300" />
            <Text className="mx-4 text-gray-500 text-sm">or</Text>
            <View className="flex-1 h-px bg-gray-300" />
          </View>

          <TouchableOpacity
            className="bg-gray-400 rounded-xl py-4 px-6 flex-row items-center justify-center shadow-lg opacity-60"
            onPress={() => router.push('/auth/google')}
            activeOpacity={0.8}
          >
            <Ionicons name="logo-google" size={20} color="white" style={{ marginRight: 8 }} />
            <Text className="text-white text-lg font-semibold">Continue with Google</Text>
          </TouchableOpacity>
        </View>

        {/* Footer */}
        <View className="mt-8">
          <Text className="text-center text-xs text-gray-500">
            By continuing, you agree to our Terms of Service and Privacy Policy
          </Text>
        </View>
      </View>
    </SafeAreaView>
  )
}

interface FeatureItemProps {
  icon: keyof typeof Ionicons.glyphMap
  title: string
  description: string
}

function FeatureItem({ icon, title, description }: FeatureItemProps) {
  return (
    <View className="flex-row items-center space-x-3">
      <View className="w-10 h-10 bg-blue-100 rounded-full items-center justify-center">
        <Ionicons name={icon} size={20} color="#3B82F6" />
      </View>
      <View className="flex-1">
        <Text className="text-gray-900 font-medium">{title}</Text>
        <Text className="text-gray-600 text-sm">{description}</Text>
      </View>
    </View>
  )
} 