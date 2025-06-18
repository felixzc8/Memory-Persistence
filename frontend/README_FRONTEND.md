# Homi Frontend - React Native App

A beautiful, secure React Native app for the Homi chatbot with persistent memory and Supabase authentication.

## 🎯 Features

- **🔐 Complete Authentication Flow**: Sign up, sign in, Google OAuth (configurable)
- **💬 AI Chat Interface**: Beautiful chat UI with persistent memory
- **🎨 Modern Design**: TailwindCSS styling with smooth animations
- **📱 Cross-Platform**: Works on iOS, Android, and Web
- **🔒 Secure**: JWT token management and automatic session handling
- **⚡ Real-time**: Instant messaging with loading states

## 📱 Screenshots & UI Flow

1. **Landing Page**: Welcome screen with authentication options
2. **Sign In/Sign Up**: Clean forms with validation
3. **Chat Interface**: iMessage-style chat with your AI companion
4. **Google OAuth**: One-click authentication (requires setup)

## 🛠️ Tech Stack

- **React Native** with **Expo Router**
- **TypeScript** for type safety
- **TailwindCSS** (NativeWind) for styling
- **Supabase** for authentication
- **AsyncStorage** for local session persistence

## 🚀 Setup Instructions

### 1. Environment Configuration

Create a `.env` file in the frontend directory:

```env
EXPO_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
EXPO_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key_here
EXPO_PUBLIC_API_URL=http://localhost:8000
```

### 2. Install Dependencies

```bash
cd frontend
npm install
```

### 3. Start the Development Server

```bash
# For development
npm start

# For specific platforms
npm run ios
npm run android  
npm run web
```

## 📁 Project Structure

```
frontend/
├── app/                    # Expo Router pages
│   ├── index.tsx          # Main router logic
│   ├── landing.tsx        # Landing page
│   ├── chat.tsx           # Main chat interface
│   ├── auth/              # Authentication pages
│   │   ├── signin.tsx     # Sign in form
│   │   ├── signup.tsx     # Sign up form
│   │   └── google.tsx     # Google OAuth
│   ├── _layout.tsx        # Root layout with AuthProvider
│   └── globals.css        # Global styles
├── contexts/
│   └── AuthContext.tsx    # Authentication state management
├── lib/
│   ├── supabase.ts        # Supabase client setup
│   └── api.ts             # Backend API integration
└── config.example.ts      # Configuration template
```

## 🔐 Authentication Flow

### Sign Up Process
1. User enters email, password, and full name
2. Form validation (email format, password strength)
3. Supabase creates account and sends verification email
4. User redirected to sign in page

### Sign In Process  
1. User enters email and password
2. Supabase validates credentials
3. JWT tokens stored securely
4. User redirected to chat interface

### Google OAuth (Optional)
1. User clicks "Continue with Google"
2. Browser opens for Google authentication
3. Tokens returned to app
4. User signed in automatically

## 💬 Chat Features

### Core Functionality
- **Persistent Memory**: AI remembers previous conversations
- **Real-time Messaging**: Instant responses with loading states
- **Message History**: Conversation persists across sessions
- **Error Handling**: Graceful degradation on network issues

### UI/UX Features
- **iMessage-style Interface**: Familiar chat bubble design
- **Keyboard Handling**: Auto-resize and scroll optimization
- **Loading States**: Visual feedback during AI responses
- **Character Limits**: Prevents overly long messages

## 🔧 Configuration Options

### Supabase Setup
1. Create a Supabase project
2. Configure authentication providers
3. Set up Row Level Security (RLS)
4. Add environment variables

### Google OAuth Setup (Currently Disabled)
**Note: Google OAuth is currently disabled due to configuration complexity in Expo development environment.**

To enable Google OAuth, you need to:
1. Create Google Cloud Console project
2. Configure OAuth consent screen  
3. Add client IDs to Supabase
4. Update redirect URLs in Supabase Auth settings
5. Implement proper OAuth flow using `expo-auth-session`
6. Handle deep linking for OAuth callbacks

For now, use email/password authentication which is fully functional.

### Backend Integration
1. Ensure FastAPI backend is running
2. Update `EXPO_PUBLIC_API_URL` in environment
3. Test authentication endpoints

## 🎨 Styling & Theming

### TailwindCSS Classes Used
- **Colors**: `bg-blue-500`, `text-gray-900`, `border-gray-300`
- **Layout**: `flex-1`, `items-center`, `justify-center`
- **Spacing**: `px-4`, `py-3`, `mb-8`, `space-y-4`
- **Borders**: `rounded-xl`, `border`, `shadow-lg`

### Custom Components
- **Landing Page**: Feature highlights with icons
- **Auth Forms**: Validation and password visibility toggles
- **Chat Bubbles**: User/assistant message differentiation
- **Loading States**: Spinners and "thinking" indicators

## 📱 Platform Considerations

### iOS
- Safe area handling with `SafeAreaView`
- Keyboard avoiding behavior configured
- StatusBar styling for light/dark themes

### Android
- Hardware back button support
- Keyboard resize mode configuration
- Material Design compatibility

### Web
- Responsive design for desktop/tablet
- Mouse and keyboard interactions
- Progressive Web App (PWA) ready

## 🔄 State Management

### AuthContext
- User authentication state
- Session management
- Token refresh handling
- Sign in/out methods

### Chat State
- Message array management
- Loading states
- Input handling
- Scroll position

## 🚨 Error Handling

### Network Errors
- Connection timeout handling
- Retry mechanisms
- User-friendly error messages
- Offline state detection

### Authentication Errors
- Invalid credentials
- Token expiration
- Session conflicts
- Account verification status

## 🧪 Testing & Development

### Development Commands
```bash
# Start development server
npm start

# Clear cache and restart
npx expo start --clear

# Run on specific platform
npx expo start --ios
npx expo start --android
npx expo start --web
```

### Debugging
- Use Expo Developer Tools
- React Native Debugger integration
- Console logging for API calls
- Network request monitoring

## 🔒 Security Features

### Authentication Security
- JWT token encryption
- Secure storage with AsyncStorage
- Automatic token refresh
- Session timeout handling

### API Security
- Authorization headers
- Request/response validation
- Error message sanitization
- CORS configuration

## 📦 Dependencies

### Core Dependencies
- `expo`: React Native framework
- `expo-router`: File-based routing
- `@supabase/supabase-js`: Authentication
- `nativewind`: TailwindCSS for React Native

### UI Dependencies
- `@expo/vector-icons`: Icon library
- `react-native-safe-area-context`: Safe area handling
- `expo-status-bar`: Status bar management

## 🚀 Deployment

### Expo Application Services (EAS)
1. Configure `eas.json`
2. Build for app stores
3. Submit to Apple App Store / Google Play

### Web Deployment
1. Build for web: `npx expo export --platform web`
2. Deploy to hosting platform (Vercel, Netlify)
3. Configure environment variables

## 🐛 Troubleshooting

### Common Issues

**"Network Error" when chatting:**
- Check backend server is running on correct port
- Verify `EXPO_PUBLIC_API_URL` in environment
- Test API endpoints with curl/Postman

**Supabase authentication errors:**
- Verify Supabase URL and anon key in `.env` file
- Check authentication provider configuration

**"Email not confirmed" error:**
- **Option 1 (Recommended for development)**: Disable email confirmation in Supabase
  1. Go to Supabase Dashboard > Authentication > Settings
  2. Find "Email Confirmation" and disable it
- **Option 2**: Use real email addresses and check confirmation emails

**"Email address invalid" error:**
- Avoid using `example.com` or other placeholder domains
- Use real email domains like `gmail.com`, `outlook.com`, etc.
- Check if your Supabase project has domain restrictions

**Styling not applying:**
- Restart development server with `--clear` flag
- Check TailwindCSS class names
- Verify NativeWind configuration

### Debug Mode
Enable debug logging by setting:
```typescript
// In lib/supabase.ts
const supabase = createClient(supabaseUrl, supabaseAnonKey, {
  auth: {
    debug: true, // Add this for auth debugging
    // ... other options
  },
})
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test on iOS/Android/Web
5. Submit a pull request

## 📄 License

This project is part of the Homi chatbot application. See the main repository for license information. 