import 'react-native-url-polyfill/auto'
import AsyncStorage from '@react-native-async-storage/async-storage'
import { createClient, SupabaseClient } from '@supabase/supabase-js'
import { Platform } from 'react-native'

const supabaseUrl = process.env.EXPO_PUBLIC_SUPABASE_URL || 'your-supabase-url'
const supabaseAnonKey = process.env.EXPO_PUBLIC_SUPABASE_ANON_KEY || 'your-supabase-anon-key'

// Validate environment variables
if (supabaseUrl === 'your-supabase-url' || supabaseAnonKey === 'your-supabase-anon-key') {
  console.warn('⚠️ Supabase environment variables not configured properly!')
}

// Create storage adapter that works across platforms
const createStorage = () => {
  // Check if we're in a browser environment
  if (typeof window !== 'undefined' && window.localStorage) {
    return {
      getItem: (key: string) => {
        try {
          return Promise.resolve(window.localStorage.getItem(key))
        } catch {
          return Promise.resolve(null)
        }
      },
      setItem: (key: string, value: string) => {
        try {
          window.localStorage.setItem(key, value)
          return Promise.resolve()
        } catch {
          return Promise.resolve()
        }
      },
      removeItem: (key: string) => {
        try {
          window.localStorage.removeItem(key)
          return Promise.resolve()
        } catch {
          return Promise.resolve()
        }
      },
    }
  }
  
  // For React Native platforms or fallback, try AsyncStorage
  try {
    return AsyncStorage
  } catch {
    // Fallback storage if AsyncStorage fails
    return {
      getItem: () => Promise.resolve(null),
      setItem: () => Promise.resolve(),
      removeItem: () => Promise.resolve(),
    }
  }
}

// Lazy initialization of Supabase client
let _supabase: SupabaseClient | null = null

export const getSupabaseClient = (): SupabaseClient => {
  if (!_supabase) {
    try {
      console.log('🔧 Initializing Supabase client...')
      _supabase = createClient(supabaseUrl, supabaseAnonKey, {
        auth: {
          storage: createStorage(),
          autoRefreshToken: true,
          persistSession: true,
          detectSessionInUrl: false,
        },
      })
      console.log('✅ Supabase client initialized successfully')
    } catch (error) {
      console.warn('❌ Failed to initialize Supabase client:', error)
      // Create a minimal client for fallback
      _supabase = createClient(supabaseUrl, supabaseAnonKey, {
        auth: {
          autoRefreshToken: false,
          persistSession: false,
          detectSessionInUrl: false,
        },
      })
      console.log('⚠️ Using fallback Supabase client')
    }
  }
  return _supabase
}

// Export a proxy that lazily initializes the client
export const supabase = new Proxy({} as SupabaseClient, {
  get(target, prop) {
    const client = getSupabaseClient()
    return client[prop as keyof SupabaseClient]
  }
}) 