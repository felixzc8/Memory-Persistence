import React, { createContext, useContext, useEffect, useState } from 'react'
import { Session, User, AuthError } from '@supabase/supabase-js'
import { supabase } from '../lib/supabase'
import { apiService } from '../lib/api'

interface AuthContextType {
  user: User | null
  session: Session | null
  loading: boolean
  signUp: (email: string, password: string, fullName: string) => Promise<{ success: boolean; error?: string }>
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
    const initializeAuth = async () => {
      try {
        const { data: { session }, error } = await supabase.auth.getSession()
        if (error) {
          console.warn('Error getting initial session:', error.message)
        }
        setSession(session)
        setUser(session?.user ?? null)
        
        apiService.setAccessToken(session?.access_token ?? null)
      } catch (error) {
        console.warn('Failed to initialize auth:', error)
      } finally {
        setLoading(false)
      }
    }

    initializeAuth()
  }, [])

  useEffect(() => {
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

    return () => subscription.unsubscribe()
  }, [])

  const signUp = async (email: string, password: string, fullName: string) => {
    try {
      const metadata = { full_name: fullName }
      
      const { data, error } = await supabase.auth.signUp({
        email: email.trim().toLowerCase(),
        password,
        options: {
          data: metadata,
        },
      })

      if (error) {
        console.error('Sign up error:', error)
        return { success: false, error: error.message }
      }
      
      console.log('Sign up successful:', data)
      console.log('Session created:', !!data.session)
      console.log('User created:', !!data.user)
      
      return { success: true }
    } catch (error) {
      console.error('Sign up exception:', error)
      return { success: false, error: 'An unexpected error occurred' }
    }
  }

    const signIn = async (email: string, password: string) => {
    try {
      const { data, error } = await supabase.auth.signInWithPassword({
        email: email.trim().toLowerCase(),
        password,
      })
      return { success: true }
    } catch (error) {
      return { success: false, error: error instanceof Error ? error.message : 'An unexpected error occurred' }
    }
  }

  const signInWithGoogle = async () => {
    try {
      return { 
        success: false, 
        error: 'Google OAuth requires additional configuration. Please use email/password authentication for now.' 
      }
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