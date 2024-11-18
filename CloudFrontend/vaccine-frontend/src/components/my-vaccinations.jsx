'use client'

import { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { motion } from "framer-motion"

export function MyVaccinationsComponent() {
  const [vaccinations, setVaccinations] = useState([])

  useEffect(() => {
    // Placeholder for Axios data fetching
    const fetchVaccinations = async () => {
      // Simulated API call
      const response = await new Promise(resolve => 
        setTimeout(() => resolve([
          { id: 1, vaccine: "COVID-19", date: "2023-01-15", location: "City Hospital" },
          { id: 2, vaccine: "Flu", date: "2023-03-20", location: "Community Clinic" },
          { id: 3, vaccine: "Tetanus", date: "2023-05-10", location: "Family Doctor" },
        ]), 1000))
      setVaccinations(response)
    }

    fetchVaccinations()
  }, [])

  return (
    (<motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}>
      <Card>
        <CardHeader>
          <CardTitle>My Vaccinations</CardTitle>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Vaccine</TableHead>
                <TableHead>Date</TableHead>
                <TableHead>Location</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {vaccinations.map((vaccination) => (
                <TableRow key={vaccination.id}>
                  <TableCell>{vaccination.vaccine}</TableCell>
                  <TableCell>{vaccination.date}</TableCell>
                  <TableCell>{vaccination.location}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </motion.div>)
  );
}