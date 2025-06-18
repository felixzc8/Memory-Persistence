import React, { useState } from 'react'
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  SafeAreaView,
  Alert,
  ActivityIndicator,
  KeyboardAvoidingView,
  Platform,
  StatusBar,
} from 'react-native'
import { router } from 'expo-router'
import { Ionicons } from '@expo/vector-icons'
import { useAuth } from '../../contexts/AuthContext'

export default function SignIn() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [showPassword, setShowPassword] = useState(false)
  
  const { signIn } = useAuth()

  const validateForm = () => {
    if (!email || !password) {
      Alert.alert('Error', 'please fill in all fields')
      return false
    }
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
        if (!emailRegex.test(email)) {
          Alert.alert('Error', 'Please enter a valid email address')
          return false
        }
    return true
  }

  const handleSignIn = async () => {
    if (!validateForm()) return

    setLoading(true)
    try {
      const result = await signIn(email, password)
      console.log('📥 Sign in result:', result)
      
      if (result.success) {
        router.replace('/chat')
      } else {
        Alert.alert('Sign In Failed', result.error)
      }
    } catch (error) {
      Alert.alert('Error', 'An unexpected error occurred')
    } finally {
      setLoading(false)
    }
  }

  return (
    <SafeAreaView className="flex-1 bg-white">
      <StatusBar barStyle="dark-content" />
      
      <KeyboardAvoidingView 
        className="flex-1" 
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
      >
        <View className="flex-1 px-6 py-8">
          {/* Header */}
          <View className="flex-row items-center mb-8">
            <TouchableOpacity 
              onPress={() => router.back()}
              className="p-2 -ml-2"
            >
              <Ionicons name="arrow-back" size={24} color="#374151" />
            </TouchableOpacity>
            <Text className="text-xl font-semibold text-gray-900 ml-4">Sign In</Text>
          </View>

          {/* Content */}
          <View className="flex-1 justify-center">
            <View className="mb-8">
              <Text className="text-3xl font-bold text-gray-900 mb-2">
                Welcome back
              </Text>
              <Text className="text-gray-600">
                Sign in to continue your conversation with Homi
              </Text>
            </View>

            {/* Form */}
            <View className="space-y-4">
              <View>
                <Text className="text-gray-700 font-medium mb-2">Email</Text>
                <TextInput
                  className="w-full px-4 py-3 border border-gray-300 rounded-xl bg-white"
                  placeholder="Enter your email"
                  value={email}
                  onChangeText={setEmail}
                  keyboardType="email-address"
                  autoCapitalize="none"
                  autoCorrect={false}
                />
              </View>

              <View>
                <Text className="text-gray-700 font-medium mb-2">Password</Text>
                <View className="relative">
                  <TextInput
                    className="w-full px-4 py-3 border border-gray-300 rounded-xl bg-white pr-12"
                    placeholder="Enter your password"
                    value={password}
                    onChangeText={setPassword}
                    secureTextEntry={!showPassword}
                    autoCorrect={false}
                  />
                  <TouchableOpacity
                    className="absolute right-3 top-3"
                    onPress={() => setShowPassword(!showPassword)}
                  >
                    <Ionicons 
                      name={showPassword ? "eye-off" : "eye"} 
                      size={20} 
                      color="#6B7280" 
                    />
                  </TouchableOpacity>
                </View>
              </View>

              <TouchableOpacity
                className="bg-blue-500 rounded-xl py-4 px-6 items-center mt-6"
                onPress={() => {
                  console.log('🔘 Sign in button pressed!')
                  handleSignIn()
                }}
                disabled={loading}
                activeOpacity={0.8}
                style={{ zIndex: 1 }} // Ensure button is tappable
              >
                {loading ? (
                  <ActivityIndicator color="white" />
                ) : (
                  <Text className="text-white text-lg font-semibold">Sign In</Text>
                )}
              </TouchableOpacity>

              <TouchableOpacity 
                className="py-2"
                onPress={() => {
                  Alert.alert('Password Reset', 'Password reset functionality coming soon!')
                }}
              >
                <Text className="text-blue-500 text-center">Forgot Password?</Text>
              </TouchableOpacity>
            </View>
          </View>

          {/* Footer */}
          <View className="pt-6">
            <View className="flex-row justify-center items-center">
              <Text className="text-gray-600">Don't have an account? </Text>
              <TouchableOpacity onPress={() => router.push('/auth/signup')}>
                <Text className="text-blue-500 font-medium">Sign Up</Text>
              </TouchableOpacity>
            </View>
          </View>
        </View>
      </KeyboardAvoidingView>
    </SafeAreaView>
  )
} 