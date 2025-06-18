import React, { createContext, useContext, useEffect, useState } from 'react'
import { Session, User } from '@supabase/supabase-js'
import { supabase } from '../lib/supabase'
import { apiService } from '../lib/api'

interface AuthContextType {
  user: User | null
  session: Session | null
  loading: boolean
  signUp: (email: string, password: string, fullName?: string) => Promise<{ success: boolean; error?: string }>
  signIn: (email: string, password: string) => Promise<{ success: boolean; error?: string }>
  signInWithGoogle: () => Promise<{ success: boolean; error?: string }>
  signOut: () => Promise<void>
  refreshSession: () => Promise<void>
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function useAuth() {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}

interface AuthProviderProps {
  children: React.ReactNode
}

export function AuthProvider({ children }: AuthProviderProps) {
  const [user, setUser] = useState<User | null>(null)
  const [session, setSession] = useState<Session | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // Get initial session with error handling
    const initializeAuth = async () => {
      try {
        const { data: { session }, error } = await supabase.auth.getSession()
        if (error) {
          console.warn('Error getting initial session:', error.message)
        }
        setSession(session)
        setUser(session?.user ?? null)
        
        // Set API service token
        apiService.setAccessToken(session?.access_token ?? null)
      } catch (error) {
        console.warn('Failed to initialize auth:', error)
        // Continue without auth if there's an error
        apiService.setAccessToken(null)
      } finally {
        setLoading(false)
      }
    }

    initializeAuth()

    // Listen for auth changes with error handling
    let subscription: any
    try {
      const {
        data: { subscription: authSubscription },
      } = supabase.auth.onAuthStateChange((_event, session) => {
        setSession(session)
        setUser(session?.user ?? null)
        setLoading(false)
        
        // Set API service token whenever session changes
        apiService.setAccessToken(session?.access_token ?? null)
      })
      subscription = authSubscription
    } catch (error) {
      console.warn('Failed to set up auth listener:', error)
      setLoading(false)
      apiService.setAccessToken(null)
    }

    return () => {
      if (subscription) {
        subscription.unsubscribe()
      }
    }
  }, [])

  const signUp = async (email: string, password: string, fullName?: string) => {
    try {

      
      // Validate inputs
      if (!email || !password) {
        return { success: false, error: 'Email and password are required' }
      }
      
      if (!email.includes('@')) {
        return { success: false, error: 'Please enter a valid email address' }
      }
      
      if (password.length < 6) {
        return { success: false, error: 'Password must be at least 6 characters long' }
      }
      
      const metadata = fullName ? { full_name: fullName } : {}
      
      const { data, error } = await supabase.auth.signUp({
        email: email.trim().toLowerCase(),
        password,
        options: {
          data: metadata,
        },
      })

      if (error) {

        return { success: false, error: error.message }
      }


      
      // Check if email confirmation is required
      if (data.user && !data.user.email_confirmed_at) {
        return { 
          success: true, 
          error: 'Please check your email and click the confirmation link before signing in.' 
        }
      }
      
      return { success: true }
    } catch (error) {
      
      return { success: false, error: 'An unexpected error occurred' }
    }
  }

    const signIn = async (email: string, password: string) => {
    try {
      console.log('🔑 AuthContext signIn called with:', email)
      
      // Validate inputs
      if (!email || !password) {
        console.log('❌ Validation failed: missing email or password')
        return { success: false, error: 'Email and password are required' }
      }
      
      if (!email.includes('@')) {
        console.log('❌ Validation failed: invalid email format')
        return { success: false, error: 'Please enter a valid email address' }
      }
      
      console.log('📡 Calling Supabase signInWithPassword...')
      const { data, error } = await supabase.auth.signInWithPassword({
        email: email.trim().toLowerCase(),
        password,
      })

      console.log('📥 Supabase response - data:', !!data, 'error:', error?.message)

      if (error) {
        console.log('❌ Supabase error:', error)
        
        // Handle specific error cases
        if (error.message === 'Email not confirmed') {
          return { 
            success: false, 
            error: 'Please check your email and click the confirmation link before signing in.' 
          }
        }
        
        if (error.message === 'Invalid login credentials') {
          return { 
            success: false, 
            error: 'Invalid email or password. Please check your credentials and try again.' 
          }
        }
        
        return { success: false, error: error.message }
      }

      console.log('✅ Sign in successful, user ID:', data?.user?.id)
      return { success: true }
    } catch (error) {
      console.log('💥 Unexpected error in signIn:', error)
      return { success: false, error: 'An unexpected error occurred' }
    }
  }

  const signInWithGoogle = async () => {
    try {
      // For now, return an error indicating Google OAuth needs additional setup
      return { 
        success: false, 
        error: 'Google OAuth requires additional configuration. Please use email/password authentication for now.' 
      }
      
      // TODO: Implement proper Google OAuth with expo-auth-session
      // This requires:
      // 1. Setting up Google OAuth credentials in Supabase
      // 2. Configuring redirect URLs in Supabase Auth settings
      // 3. Using expo-auth-session for proper OAuth flow in Expo
    } catch (error) {
      return { success: false, error: 'An unexpected error occurred' }
    }
  }

  const signOut = async () => {
    const { error } = await supabase.auth.signOut()
    if (error) {
      console.error('Error signing out:', error.message)
    }
    // Clear API service token on sign out
    apiService.setAccessToken(null)
  }

  const refreshSession = async () => {
    const { error } = await supabase.auth.refreshSession()
    if (error) {
      console.error('Error refreshing session:', error.message)
    }
  }

  const value: AuthContextType = {
    user,
    session,
    loading,
    signUp,
    signIn,
    signInWithGoogle,
    signOut,
    refreshSession,
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
} 