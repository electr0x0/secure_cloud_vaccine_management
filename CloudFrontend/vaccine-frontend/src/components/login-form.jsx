'use client'

import { useState } from 'react'
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Mail, Lock, Loader2 } from 'lucide-react'
import { useToast } from "@/hooks/use-toast"
import { loginUser } from './api'
import { useRouter } from 'next/navigation'

export default function LoginForm() {
  const [isLoading, setIsLoading] = useState(false)
  const { toast } = useToast()
  const router = useRouter()

  const handleSubmit = async (event) => {
    event.preventDefault()
    setIsLoading(true)
    
    const formData = new FormData(event.currentTarget)
    const data = Object.fromEntries(formData.entries())

    try {
      const result = await loginUser(data)
      if (result.success) {
        toast({
          title: "Success",
          description: "Successfully Logged In"
        })
        router.push('/dashboard')
      } else {
        toast({
          title: "Error",
          description: "An error occurred during login",
          variant: "destructive",
        })
      }
    } catch (error) {
      toast({
        title: "Error",
        description: error.response?.data?.detail || "An error occurred during login",
        variant: "destructive",
      })
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div className="space-y-2">
        <Label htmlFor="email">Email</Label>
        <div className="relative">
          <Mail className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
          <Input
            id="email"
            name="email"
            placeholder="m@example.com"
            type="email"
            className="pl-8"
            required
          />
        </div>
      </div>
      <div className="space-y-2">
        <Label htmlFor="password">Password</Label>
        <div className="relative">
          <Lock className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
          <Input 
            id="password" 
            name="password" 
            type="password" 
            className="pl-8" 
            required 
          />
        </div>
      </div>
      <Button type="submit" className="w-full" disabled={isLoading}>
        {isLoading ? (
          <>
            <Loader2 className="mr-2 h-4 w-4 animate-spin" />
            Logging in...
          </>
        ) : (
          "Login"
        )}
      </Button>
    </form>
  )
}

