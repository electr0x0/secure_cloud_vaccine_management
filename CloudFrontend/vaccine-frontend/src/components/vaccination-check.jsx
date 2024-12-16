'use client'

import { useState } from 'react'
import { Label } from "@/components/ui/label"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { Mail, Loader2 } from 'lucide-react'
import VaccinationTracker from './vaccination-tracker'
import { useToast } from "@/hooks/use-toast"
import axios from 'axios'

export default function VaccinationCheck() {
  const [isLoading, setIsLoading] = useState(false)
  const [vaccinationData, setVaccinationData] = useState(null)
  const [noLoginFetchErrorMsg, setnoLoginFetchErrorMsg] = useState(null)
  const { toast } = useToast()

  const handleCheckVaccination = async (event) => {
    event.preventDefault()
    setIsLoading(true)
    const email = event.target.email.value

    try {
      const response = await axios.get(`http://localhost:8000/api/vaccination-history?email=${email}`)
      setVaccinationData(response.data)
      toast({
        title: "Success",
        description: "Vaccination history retrieved successfully"
      })
    } catch (error) {
      if (error.response && error.response.status === 404) {
        setnoLoginFetchErrorMsg(error.response.data.detail || "User with this email not found")
      }
      
      toast({
        title: "Error",
        description: noLoginFetchErrorMsg || "Failed to fetch vaccination history",
        variant: "destructive"
      })
      setVaccinationData(null)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="space-y-4">
      <form onSubmit={handleCheckVaccination}>
        <div className="space-y-2">
          <Label htmlFor="check-email">Email</Label>
          <div className="relative">
            <Mail className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
            <Input
              id="check-email"
              name="email"
              placeholder="m@example.com"
              type="email"
              className="pl-8"
              required
            />
          </div>
        </div>
        <Button type="submit" className="w-full mt-4" disabled={isLoading}>
          {isLoading ? (
            <>
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              Checking...
            </>
          ) : (
            'Check Vaccination History'
          )}
        </Button>
      </form>
      {vaccinationData && (
        <div className="mt-6">
          <VaccinationTracker data={vaccinationData} />
        </div>
      )}
    </div>
  )
}