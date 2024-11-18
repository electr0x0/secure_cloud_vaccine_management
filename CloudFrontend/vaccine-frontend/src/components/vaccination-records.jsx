'use client'

import { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { motion } from "framer-motion"

export function VaccinationRecordsComponent() {
  const [records, setRecords] = useState([])

  useEffect(() => {
    // Placeholder for Axios data fetching
    const fetchRecords = async () => {
      // Simulated API call
      const response = await new Promise(resolve => 
        setTimeout(() => resolve([
          { id: 1, patientName: "Alice Smith", vaccine: "COVID-19", date: "2023-01-15", nextDose: "2023-07-15" },
          { id: 2, patientName: "Bob Johnson", vaccine: "Flu", date: "2023-03-20", nextDose: "2024-03-20" },
          { id: 3, patientName: "Charlie Brown", vaccine: "Tetanus", date: "2023-05-10", nextDose: "2033-05-10" },
        ]), 1000))
      setRecords(response)
    }

    fetchRecords()
  }, [])

  return (
    (<motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}>
      <Card>
        <CardHeader>
          <CardTitle>Vaccination Records</CardTitle>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Patient Name</TableHead>
                <TableHead>Vaccine</TableHead>
                <TableHead>Date Administered</TableHead>
                <TableHead>Next Dose Due</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {records.map((record) => (
                <TableRow key={record.id}>
                  <TableCell>{record.patientName}</TableCell>
                  <TableCell>{record.vaccine}</TableCell>
                  <TableCell>{record.date}</TableCell>
                  <TableCell>{record.nextDose}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </motion.div>)
  );
}