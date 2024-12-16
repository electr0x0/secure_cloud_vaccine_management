'use client'

import { useState } from 'react'
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import LoginForm from './login-form'
import SignupForm from './signup-form'
import VaccinationCheck from './vaccination-check'

export default function AuthForm() {
  const [activeTab, setActiveTab] = useState("login")

  return (
    <div className="flex items-center justify-center min-h-screen bg-gradient-to-r from-blue-100 to-green-100">
      <Card className="w-full max-w-4xl">
        <CardHeader className="space-y-1">
          <CardTitle className="text-2xl font-bold text-center">Vaccination Portal</CardTitle>
          <CardDescription className="text-center">
            Login or sign up to access your vaccination records
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Tabs value={activeTab} onValueChange={setActiveTab}>
            <TabsList className="grid w-full grid-cols-3">
              <TabsTrigger value="login">Login</TabsTrigger>
              <TabsTrigger value="signup">Sign Up</TabsTrigger>
              <TabsTrigger value="check">Check Vaccination</TabsTrigger>
            </TabsList>

            <TabsContent value="login">
              <LoginForm />
            </TabsContent>

            <TabsContent value="signup">
              <SignupForm />
            </TabsContent>

            <TabsContent value="check">
              <VaccinationCheck />
            </TabsContent>
          </Tabs>
        </CardContent>
      </Card>
    </div>
  )
}

