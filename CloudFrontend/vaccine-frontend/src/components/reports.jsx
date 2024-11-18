'use client'

import { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'
import { motion } from "framer-motion"

export function ReportsComponent() {
  const [reportType, setReportType] = useState('monthly')
  const [reportData, setReportData] = useState([])

  useEffect(() => {
    // Placeholder for Axios data fetching
    const fetchReportData = async () => {
      // Simulated API call
      const response = await new Promise(resolve => 
        setTimeout(() => resolve([
          { name: 'Jan', vaccinations: 400 },
          { name: 'Feb', vaccinations: 300 },
          { name: 'Mar', vaccinations: 200 },
          { name: 'Apr', vaccinations: 278 },
          { name: 'May', vaccinations: 189 },
          { name: 'Jun', vaccinations: 239 },
        ]), 1000))
      setReportData(response)
    }

    fetchReportData()
  }, [reportType])

  return (
    (<motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}>
      <Card>
        <CardHeader>
          <CardTitle>Vaccination Reports</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="mb-4">
            <Select value={reportType} onValueChange={setReportType}>
              <SelectTrigger>
                <SelectValue placeholder="Select report type" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="monthly">Monthly</SelectItem>
                <SelectItem value="quarterly">Quarterly</SelectItem>
                <SelectItem value="yearly">Yearly</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <ResponsiveContainer width="100%" height={400}>
            <BarChart data={reportData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey="vaccinations" fill="#8884d8" />
            </BarChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>
    </motion.div>)
  );
}