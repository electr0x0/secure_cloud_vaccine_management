"use client"

import { useState } from "react"
import { motion, AnimatePresence } from "framer-motion"
import axios from "axios"
import { Syringe, Loader2, ArrowLeft } from 'lucide-react'

import { Button } from "@/components/ui/button"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import {
  Form,
  FormControl,
  FormDescription,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { Input } from "@/components/ui/input"
import { useToast } from "@/hooks/use-toast"
import { zodResolver } from "@hookform/resolvers/zod"
import { useForm } from "react-hook-form"
import * as z from "zod"
import VaccinationTracker from "./vaccination-tracker"

const vaccines = [
  { code: "BCG", name: "Bacillus Calmette-Guérin (BCG)" },
  { code: "PENTAVALENT", name: "Pentavalent (DPT, Hepatitis B, Hib)" },
  { code: "OPV", name: "Oral Polio Vaccine" },
  { code: "PCV", name: "Pneumococcal Conjugate Vaccine" },
  { code: "IPV", name: "Inactivated Polio Vaccine" },
  { code: "MR", name: "Measles and Rubella Vaccine" },
]

const formSchema = z.object({
  email: z.string().email("Please enter a valid email address"),
  vaccine_code: z.string({
    required_error: "Please select a vaccine",
  }),
  dose_number: z.coerce
    .number()
    .min(1, "Dose number must be between 1 and 5")
    .max(5, "Dose number must be between 1 and 5"),
  vaccination_date: z.string({
    required_error: "Please select a date",
  }),
})

export default function VaccinationRecordComponent() {
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [vaccinationData, setVaccinationData] = useState(null)
  const [recipientInfo, setRecipientInfo] = useState(null)
  const { toast } = useToast()

  const form = useForm({
    resolver: zodResolver(formSchema),
    defaultValues: {
      email: "",
      vaccination_date: new Date().toISOString().split("T")[0],
    },
  })

  const resetView = () => {
    setVaccinationData(null)
    setRecipientInfo(null)
    form.reset()
  }

  const API = process.env.NEXT_PUBLIC_API_URL

  async function onSubmit(values) {
    setIsSubmitting(true)
    try {
      // Record the vaccination
      await axios.post(`${API}/api/vaccinations/vaccination-history`, {
        ...values,
        is_taken: true,
        token : sessionStorage.getItem('access_token'),
      })
      
      // Fetch updated vaccination history
      const response = await axios.get(`${API}/api/vaccinations/history?email=${values.email}`)
      
      
      setVaccinationData(response.data)
      setRecipientInfo({
        name: response.data.user_info.user_name,
        email: values.email
      })
      
      toast({
        title: "Success",
        description: "Vaccination record has been updated successfully",
      })
    } catch (error) {
      toast({
        title: "Error",
        description: error.response.data.detail || "Failed to update vaccination record. Please try again.",
        variant: "destructive",
      })
      resetView()
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    (<div className="container mx-auto p-6">
      <AnimatePresence mode="wait">
        {!vaccinationData ? (
          <motion.div
            key="form"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            transition={{ duration: 0.5 }}>
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Syringe className="h-6 w-6 text-primary" />
                  Record Vaccination
                </CardTitle>
                <CardDescription>
                  Enter vaccination details for the recipient
                </CardDescription>
              </CardHeader>
              <CardContent>
                <Form {...form}>
                  <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
                    <FormField
                      control={form.control}
                      name="email"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Recipient Email</FormLabel>
                          <FormControl>
                            <Input placeholder="recipient@example.com" {...field} />
                          </FormControl>
                          <FormDescription>
                            Enter the email address of the vaccine recipient
                          </FormDescription>
                          <FormMessage />
                        </FormItem>
                      )} />

                    <FormField
                      control={form.control}
                      name="vaccine_code"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Vaccine</FormLabel>
                          <Select onValueChange={field.onChange} defaultValue={field.value}>
                            <FormControl>
                              <SelectTrigger>
                                <SelectValue placeholder="Select a vaccine" />
                              </SelectTrigger>
                            </FormControl>
                            <SelectContent>
                              {vaccines.map((vaccine) => (
                                <SelectItem key={vaccine.code} value={vaccine.code}>
                                  {vaccine.name}
                                </SelectItem>
                              ))}
                            </SelectContent>
                          </Select>
                          <FormDescription>
                            Select the vaccine being administered
                          </FormDescription>
                          <FormMessage />
                        </FormItem>
                      )} />

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      <FormField
                        control={form.control}
                        name="dose_number"
                        render={({ field }) => (
                          <FormItem>
                            <FormLabel>Dose Number</FormLabel>
                            <Select onValueChange={field.onChange} defaultValue={field.value?.toString()}>
                              <FormControl>
                                <SelectTrigger>
                                  <SelectValue placeholder="Select dose number" />
                                </SelectTrigger>
                              </FormControl>
                              <SelectContent>
                                {[1, 2, 3, 4, 5].map((num) => (
                                  <SelectItem key={num} value={num.toString()}>
                                    Dose {num}
                                  </SelectItem>
                                ))}
                              </SelectContent>
                            </Select>
                            <FormDescription>
                              Select which dose number is being administered
                            </FormDescription>
                            <FormMessage />
                          </FormItem>
                        )} />

                      <FormField
                        control={form.control}
                        name="vaccination_date"
                        render={({ field }) => (
                          <FormItem>
                            <FormLabel>Vaccination Date</FormLabel>
                            <FormControl>
                              <Input type="date" {...field} />
                            </FormControl>
                            <FormDescription>
                              Select the date of vaccination
                            </FormDescription>
                            <FormMessage />
                          </FormItem>
                        )} />
                    </div>

                    <Button type="submit" className="w-full" disabled={isSubmitting}>
                      {isSubmitting ? (
                        <>
                          <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                          Recording...
                        </>
                      ) : (
                        "Record Vaccination"
                      )}
                    </Button>
                  </form>
                </Form>
              </CardContent>
            </Card>
          </motion.div>
        ) : (
          <motion.div
            key="tracker"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            transition={{ duration: 0.5 }}>
            <div className="mb-4">
              <Button variant="outline" onClick={resetView} className="flex items-center gap-2">
                <ArrowLeft className="h-4 w-4" />
                Record Another Vaccination
              </Button>
            </div>
            <VaccinationTracker data={vaccinationData} userInfo={recipientInfo} />
          </motion.div>
        )}
      </AnimatePresence>
    </div>)
  );
}

