import { Stack } from "expo-router";
import { AuthProvider } from "../contexts/AuthContext";
import './globals.css'

export default function RootLayout() {
  return (
    <AuthProvider>
      <Stack screenOptions={{ headerShown: false }} />
    </AuthProvider>
  );
}
