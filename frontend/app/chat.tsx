import React, { useState, useRef, useEffect } from 'react'
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  SafeAreaView,
  FlatList,
  Alert,
  ActivityIndicator,
  StatusBar,
  KeyboardAvoidingView,
  Platform,
} from 'react-native'
import { router } from 'expo-router'
import { Ionicons } from '@expo/vector-icons'
import { useAuth } from '../contexts/AuthContext'
import { apiService, ChatMessage } from '../lib/api'

export default function Chat() {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      role: 'assistant',
      content: 'Hello! I\'m Homi, your AI companion with persistent memory. How can I help you today?',
      timestamp: new Date().toISOString(),
    },
  ])
  const [inputText, setInputText] = useState('')
  const [loading, setLoading] = useState(false)
  const flatListRef = useRef<FlatList>(null)
  
  const { user, signOut } = useAuth()

  const sendMessage = async () => {
    if (!inputText.trim() || loading) return

    const userMessage: ChatMessage = {
      role: 'user',
      content: inputText.trim(),
      timestamp: new Date().toISOString(),
    }

    setMessages(prev => [...prev, userMessage])
    setInputText('')
    setLoading(true)

    try {
      const response = await apiService.sendMessage({
        message: userMessage.content,
      })

      const assistantMessage: ChatMessage = {
        role: 'assistant',
        content: response.response,
        timestamp: response.timestamp,
      }

      setMessages(prev => [...prev, assistantMessage])
    } catch (error) {
      console.error('Error sending message:', error)
      
      const errorMessage: ChatMessage = {
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please check your connection and try again.',
        timestamp: new Date().toISOString(),
      }
      
      setMessages(prev => [...prev, errorMessage])
      Alert.alert('Error', 'Failed to send message. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const handleSignOut = async () => {
    Alert.alert(
      'Sign Out',
      'Are you sure you want to sign out?',
      [
        { text: 'Cancel', style: 'cancel' },
        { 
          text: 'Sign Out', 
          style: 'destructive',
          onPress: async () => {
            await signOut()
            router.replace('/landing')
          }
        },
      ]
    )
  }

  const renderMessage = ({ item }: { item: ChatMessage }) => {
    const isUser = item.role === 'user'
    
    return (
      <View className={`mb-4 px-4 ${isUser ? 'items-end' : 'items-start'}`}>
        <View 
          className={`max-w-[85%] px-4 py-3 rounded-2xl ${
            isUser 
              ? 'bg-blue-500 rounded-br-md' 
              : 'bg-gray-100 rounded-bl-md'
          }`}
        >
          <Text className={`text-base ${isUser ? 'text-white' : 'text-gray-900'}`}>
            {item.content}
          </Text>
        </View>
      </View>
    )
  }

  return (
    <SafeAreaView className="flex-1 bg-white">
      <StatusBar barStyle="dark-content" />
      
      {/* Header */}
      <View className="flex-row items-center justify-between px-4 py-3 border-b border-gray-200">
        <View>
          <Text className="text-xl font-bold text-gray-900">Homi</Text>
          <Text className="text-sm text-gray-500">AI Assistant</Text>
        </View>
        
        <TouchableOpacity
          onPress={handleSignOut}
          className="p-2 rounded-full bg-gray-100"
        >
          <Ionicons name="log-out" size={20} color="#6B7280" />
        </TouchableOpacity>
      </View>

      <KeyboardAvoidingView 
        className="flex-1" 
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
      >
        {/* Messages */}
        <FlatList
          ref={flatListRef}
          data={messages}
          renderItem={renderMessage}
          keyExtractor={(_, index) => index.toString()}
          className="flex-1 pt-4"
          showsVerticalScrollIndicator={false}
        />

        {/* Loading indicator */}
        {loading && (
          <View className="flex-row items-center justify-center py-2">
            <ActivityIndicator size="small" color="#3B82F6" />
            <Text className="text-gray-500 ml-2">Homi is thinking...</Text>
          </View>
        )}

        {/* Input */}
        <View className="flex-row items-center px-4 py-3 border-t border-gray-200">
          <View className="flex-1 flex-row items-center bg-gray-100 rounded-full px-4 py-3">
            <TextInput
              className="flex-1 text-base"
              placeholder="Type your message..."
              value={inputText}
              onChangeText={setInputText}
              multiline
              editable={!loading}
            />
          </View>
          
          <TouchableOpacity
            onPress={sendMessage}
            disabled={!inputText.trim() || loading}
            className={`ml-3 p-3 rounded-full ${
              inputText.trim() && !loading ? 'bg-blue-500' : 'bg-gray-300'
            }`}
          >
            <Ionicons 
              name="send" 
              size={20} 
              color={inputText.trim() && !loading ? 'white' : '#9CA3AF'} 
            />
          </TouchableOpacity>
        </View>
      </KeyboardAvoidingView>
    </SafeAreaView>
  )
} 