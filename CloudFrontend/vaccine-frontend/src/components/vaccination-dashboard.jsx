"use client";

import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { PDFDownloadLink } from '@react-pdf/renderer'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { useToast } from "@/hooks/use-toast"
import VaccinationTracker from './vaccination-tracker'
import VaccineCardPDF from './vaccine-card-pdf'
import VaccineCertificatePDF from './vaccine-certificate-pdf'
import { getCurrentUserVaccineInfo } from './api'

export default function VaccinationDashboard() {
  const [data, setData] = useState(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState(null)
  const [selectedVaccine, setSelectedVaccine] = useState(null)
  const { toast } = useToast()

  useEffect(() => {
    async function fetchData() {
      try {
        setIsLoading(true)
        const result = await getCurrentUserVaccineInfo()
        if (result.success === false) {
          throw new Error(result.error)
        }
        setData(result)
        setError(null)
      } catch (err) {
        setError(err.message)
        toast({
          title: "Error",
          description: "Failed to fetch vaccination data. Please try again.",
          variant: "destructive",
        })
      } finally {
        setIsLoading(false)
      }
    }

    fetchData()
  }, [toast])

  if (isLoading) {
    return <div className="flex justify-center items-center h-screen">Loading...</div>
  }

  if (error) {
    return <div className="flex justify-center items-center h-screen">Error: {error}</div>
  }

  if (!data) {
    return <div className="flex justify-center items-center h-screen">No data available</div>
  }

  const vaccines = data.vaccination_history.map(v => ({
    code: v.vaccine_code,
    name: v.vaccine_name
  }))

  const selectedVaccineData = data.vaccination_history.find(v => v.vaccine_code === selectedVaccine)

  const isFullyVaccinated = selectedVaccineData?.doses.every(dose => dose.is_taken) || false

  return (
    <div className="container mx-auto p-6 space-y-8">
      <VaccinationTracker data={data} />
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.4 }}>
        <Card>
          <CardHeader>
            <CardTitle>Download Vaccination Documents</CardTitle>
            <CardDescription>Get your vaccine card or certificate</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <Select onValueChange={(value) => setSelectedVaccine(value)}>
              <SelectTrigger className="w-full">
                <SelectValue placeholder="Select vaccine type" />
              </SelectTrigger>
              <SelectContent>
                {vaccines.map((vaccine) => (
                  <SelectItem key={vaccine.code} value={vaccine.code}>
                    {vaccine.name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            
            <div className="flex space-x-4">
              {selectedVaccineData && (
                <PDFDownloadLink
                  document={<VaccineCardPDF data={data} selectedVaccine={selectedVaccineData} />}
                  fileName={`${data.user_info.user_name}_vaccine_card.pdf`}>
                  {({ blob, url, loading, error }) => (
                    <Button
                      disabled={loading}
                      onClick={() => {
                        if (!error) {
                          toast({
                            title: "Success",
                            description: "Vaccine card downloaded successfully",
                          })
                        } else {
                          console.error("PDF generation error:", error)
                          toast({
                            title: "Error",
                            description: "Failed to generate vaccine card. Please try again.",
                            variant: "destructive",
                          })
                        }
                      }}>
                      Download Vaccine Card
                    </Button>
                  )}
                </PDFDownloadLink>
              )}

              {selectedVaccineData && isFullyVaccinated && (
                <PDFDownloadLink
                  document={<VaccineCertificatePDF data={data} selectedVaccine={selectedVaccineData} />}
                  fileName={`${data.user_info.user_name}_vaccine_certificate.pdf`}>
                  {({ blob, url, loading, error }) => (
                    <Button
                      disabled={loading}
                      onClick={() => {
                        if (!error) {
                          toast({
                            title: "Success",
                            description: "Vaccine certificate downloaded successfully",
                          })
                        } else {
                          console.error("PDF generation error:", error)
                          toast({
                            title: "Error",
                            description: "Failed to generate vaccine certificate. Please try again.",
                            variant: "destructive",
                          })
                        }
                      }}>
                      Download Vaccine Certificate
                    </Button>
                  )}
                </PDFDownloadLink>
              )}
            </div>
          </CardContent>
        </Card>
      </motion.div>
    </div>
  )
}