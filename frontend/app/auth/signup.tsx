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

export default function SignUp() {
  const [fullName, setFullName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [showPassword, setShowPassword] = useState(false)
  const [showConfirmPassword, setShowConfirmPassword] = useState(false)
  
  const { signUp } = useAuth()

  const validateForm = () => {
    if (!fullName || !email || !password || !confirmPassword) {
      Alert.alert('Error', 'Please fill in all fields')
      return false
    }

    if (password !== confirmPassword) {
      Alert.alert('Error', 'Passwords do not match')
      return false
    }

    if (password.length < 6) {
      Alert.alert('Error', 'Password must be at least 6 characters')
      return false
    }

    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
    if (!emailRegex.test(email)) {
      Alert.alert('Error', 'Please enter a valid email address')
      return false
    }

    return true
  }

  const handleSignUp = async () => {
    if (!validateForm()) return

    setLoading(true)
    try {
      const result = await signUp(email, password, fullName)
      if (result.success) {
        Alert.alert('Account created successfully')
        router.replace('/chat')
      } else {
        Alert.alert('Sign Up Failed', result.error || 'An unexpected error occurred')
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
            <Text className="text-xl font-semibold text-gray-900 ml-4">Create Account</Text>
          </View>

          {/* Content */}
          <View className="flex-1">
            <View className="mb-8">
              <Text className="text-3xl font-bold text-gray-900 mb-2">
                Join Homi
              </Text>
              <Text className="text-gray-600">
                Create your account to start chatting with your AI companion
              </Text>
            </View>

            {/* Form */}
            <View className="space-y-4 flex-1">
              <View>
                <Text className="text-gray-700 font-medium mb-2">Full Name</Text>
                <TextInput
                  className="w-full px-4 py-3 border border-gray-300 rounded-xl bg-white"
                  placeholder="Enter your full name"
                  value={fullName}
                  onChangeText={setFullName}
                  autoCapitalize="words"
                  autoCorrect={false}
                />
              </View>

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
                    placeholder="Create a password (min. 6 characters)"
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

              <View>
                <Text className="text-gray-700 font-medium mb-2">Confirm Password</Text>
                <View className="relative">
                  <TextInput
                    className="w-full px-4 py-3 border border-gray-300 rounded-xl bg-white pr-12"
                    placeholder="Confirm your password"
                    value={confirmPassword}
                    onChangeText={setConfirmPassword}
                    secureTextEntry={!showConfirmPassword}
                    autoCorrect={false}
                  />
                  <TouchableOpacity
                    className="absolute right-3 top-3"
                    onPress={() => setShowConfirmPassword(!showConfirmPassword)}
                  >
                    <Ionicons 
                      name={showConfirmPassword ? "eye-off" : "eye"} 
                      size={20} 
                      color="#6B7280" 
                    />
                  </TouchableOpacity>
                </View>
              </View>

              <TouchableOpacity
                className="bg-blue-500 rounded-xl py-4 px-6 items-center mt-6"
                onPress={handleSignUp}
                disabled={loading}
                activeOpacity={0.8}
              >
                {loading ? (
                  <ActivityIndicator color="white" />
                ) : (
                  <Text className="text-white text-lg font-semibold">Create Account</Text>
                )}
              </TouchableOpacity>
            </View>

            {/* Footer */}
            <View className="pt-6 flex-1 justify-end">
              <View className="flex-row justify-center items-center">
                <Text className="text-gray-600">Already have an account? </Text>
                <TouchableOpacity onPress={() => router.push('/auth/signin')}>
                  <Text className="text-blue-500 font-medium">Sign In</Text>
                </TouchableOpacity>
              </View>
            </View>
          </View>
        </View>
      </KeyboardAvoidingView>
    </SafeAreaView>
  )
} 