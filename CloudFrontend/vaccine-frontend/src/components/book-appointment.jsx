'use client'

import { useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { motion } from "framer-motion"

export function BookAppointmentComponent() {
  const [formData, setFormData] = useState({
    name: '',
    date: '',
    time: '',
    vaccine: ''
  })

  const handleChange = (e) => {
    const { name, value } = e.target
    setFormData(prevData => ({
      ...prevData,
      [name]: value
    }))
  }

  const handleSubmit = (e) => {
    e.preventDefault()
    // Placeholder for Axios data posting
    console.log('Appointment booked:', formData)
    // Reset form after submission
    setFormData({ name: '', date: '', time: '', vaccine: '' })
  }

  return (
    (<motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}>
      <Card>
        <CardHeader>
          <CardTitle>Book an Appointment</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <Label htmlFor="name">Name</Label>
              <Input
                id="name"
                name="name"
                value={formData.name}
                onChange={handleChange}
                required />
            </div>
            <div>
              <Label htmlFor="date">Date</Label>
              <Input
                id="date"
                name="date"
                type="date"
                value={formData.date}
                onChange={handleChange}
                required />
            </div>
            <div>
              <Label htmlFor="time">Time</Label>
              <Input
                id="time"
                name="time"
                type="time"
                value={formData.time}
                onChange={handleChange}
                required />
            </div>
            <div>
              <Label htmlFor="vaccine">Vaccine</Label>
              <Select
                name="vaccine"
                onValueChange={(value) => handleChange({ target: { name: 'vaccine', value } })}>
                <SelectTrigger>
                  <SelectValue placeholder="Select a vaccine" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="covid19">COVID-19</SelectItem>
                  <SelectItem value="flu">Flu</SelectItem>
                  <SelectItem value="tetanus">Tetanus</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <Button type="submit">Book Appointment</Button>
          </form>
        </CardContent>
      </Card>
    </motion.div>)
  );
}