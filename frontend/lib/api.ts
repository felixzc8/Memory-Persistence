const API_BASE_URL = process.env.EXPO_PUBLIC_API_URL || 'http://localhost:8000'

export interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
  timestamp?: string
}

export interface ChatRequest {
  message: string
  session_id?: string
}

export interface ChatResponse {
  response: string
  user_id: string
  session_id?: string
  memories_used: string[]
  timestamp: string
}

export interface MemorySearchRequest {
  query: string
  limit?: number
}

export interface MemorySearchResponse {
  memories: string[]
  user_id: string
  query: string
}

class ApiService {
  private baseUrl: string
  private accessToken: string | null = null

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl
  }

  setAccessToken(token: string | null) {
    this.accessToken = token
  }

  private async makeRequest<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
      ...options.headers,
    }

    if (this.accessToken) {
      headers['Authorization'] = `Bearer ${this.accessToken}`
    }

    const response = await fetch(url, {
      ...options,
      headers,
    })

    if (!response.ok) {
      const errorData = await response.text()
      throw new Error(`API Error: ${response.status} - ${errorData}`)
    }

    return response.json()
  }

  // Chat endpoints
  async sendMessage(request: ChatRequest): Promise<ChatResponse> {
    return this.makeRequest<ChatResponse>('/api/v1/chat', {
      method: 'POST',
      body: JSON.stringify(request),
    })
  }

  // Memory endpoints
  async searchMemories(request: MemorySearchRequest): Promise<MemorySearchResponse> {
    return this.makeRequest<MemorySearchResponse>('/api/v1/memories/search', {
      method: 'POST',
      body: JSON.stringify(request),
    })
  }

  async getMemorySummary(): Promise<{ user_id: string; summary: string }> {
    return this.makeRequest<{ user_id: string; summary: string }>('/api/v1/memories/summary')
  }

  async deleteMemories(): Promise<{ message: string }> {
    return this.makeRequest<{ message: string }>('/api/v1/memories', {
      method: 'DELETE',
    })
  }

  // Health check
  async healthCheck(): Promise<{ status: string }> {
    return this.makeRequest<{ status: string }>('/health')
  }
}

export const apiService = new ApiService() 