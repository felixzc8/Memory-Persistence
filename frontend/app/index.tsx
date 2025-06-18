import React, { useEffect } from 'react'
import { View, ActivityIndicator } from 'react-native'
import { useAuth } from '../contexts/AuthContext'
import { apiService } from '../lib/api'
import { router } from 'expo-router'

export default function Index() {
  const { user, session, loading } = useAuth()

  useEffect(() => {
    console.log('🔄 Index.tsx auth state changed:')
    console.log('  - loading:', loading)
    console.log('  - user:', !!user)
    console.log('  - session:', !!session)
    
    if (session?.access_token) {
      console.log('🔑 Setting access token for API calls')
      apiService.setAccessToken(session.access_token)
    }

    if (!loading) {
      if (user) {
        console.log('✅ User authenticated, navigating to chat')
        router.replace('/chat')
      } else {
        console.log('❌ No user, navigating to landing')
        router.replace('/landing')
      }
    } else {
      console.log('⏳ Still loading auth state...')
    }
  }, [user, session, loading])

  return (
    <View className="flex-1 justify-center items-center bg-white">
      <ActivityIndicator size="large" color="#3B82F6" />
    </View>
  )
}
