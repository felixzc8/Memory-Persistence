import React, { useEffect, useState } from 'react'
import {
  View,
  Text,
  TouchableOpacity,
  SafeAreaView,
  Alert,
  ActivityIndicator,
  StatusBar,
} from 'react-native'
import { router } from 'expo-router'
import { Ionicons } from '@expo/vector-icons'
import { useAuth } from '../../contexts/AuthContext'

export default function GoogleAuth() {
  const [loading, setLoading] = useState(false)
  const { signInWithGoogle } = useAuth()

  const handleGoogleSignIn = async () => {
    setLoading(true)
    try {
      const result = await signInWithGoogle()
      if (!result.success) {
        Alert.alert('Google Sign In Failed', result.error || 'An unexpected error occurred')
      }
      // Navigation will be handled by the auth context
    } catch (error) {
      Alert.alert('Error', 'An unexpected error occurred')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    // Automatically trigger Google sign in when component mounts
    handleGoogleSignIn()
  }, [])

  return (
    <SafeAreaView className="flex-1 bg-white">
      <StatusBar barStyle="dark-content" />
      
      <View className="flex-1 px-6 py-8">
        {/* Header */}
        <View className="flex-row items-center mb-8">
          <TouchableOpacity 
            onPress={() => router.back()}
            className="p-2 -ml-2"
          >
            <Ionicons name="arrow-back" size={24} color="#374151" />
          </TouchableOpacity>
          <Text className="text-xl font-semibold text-gray-900 ml-4">Google Sign In</Text>
        </View>

        {/* Content */}
        <View className="flex-1 justify-center items-center">
          <View className="items-center mb-8">
            <View className="w-20 h-20 bg-red-500 rounded-full items-center justify-center mb-4">
              <Ionicons name="logo-google" size={40} color="white" />
            </View>
            <Text className="text-2xl font-bold text-gray-900 mb-2">
              Continue with Google
            </Text>
            <Text className="text-gray-600 text-center max-w-sm">
              Sign in securely using your Google account
            </Text>
          </View>

          {loading ? (
            <View className="items-center">
              <ActivityIndicator size="large" color="#EF4444" />
              <Text className="text-gray-600 mt-4">Connecting to Google...</Text>
            </View>
          ) : (
            <View className="w-full max-w-sm space-y-4">
              <TouchableOpacity
                className="bg-red-500 rounded-xl py-4 px-6 flex-row items-center justify-center shadow-lg"
                onPress={handleGoogleSignIn}
                activeOpacity={0.8}
              >
                <Ionicons name="logo-google" size={20} color="white" style={{ marginRight: 8 }} />
                <Text className="text-white text-lg font-semibold">Continue with Google</Text>
              </TouchableOpacity>

              <TouchableOpacity
                className="bg-white border border-gray-300 rounded-xl py-4 px-6 items-center"
                onPress={() => router.back()}
                activeOpacity={0.8}
              >
                <Text className="text-gray-700 text-lg font-medium">Use Email Instead</Text>
              </TouchableOpacity>
            </View>
          )}
        </View>

        {/* Note */}
        <View className="items-center">
          <Text className="text-xs text-gray-500 text-center max-w-sm">
            Google OAuth requires additional setup. Please use email/password authentication for now.
          </Text>
        </View>
      </View>
    </SafeAreaView>
  )
} 