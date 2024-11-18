'use client'

import { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Button } from "@/components/ui/button"
import { motion } from "framer-motion"

export function VaccineInventoryComponent() {
  const [inventory, setInventory] = useState([])

  useEffect(() => {
    // Placeholder for Axios data fetching
    const fetchInventory = async () => {
      // Simulated API call
      const response = await new Promise(resolve => 
        setTimeout(() => resolve([
          { id: 1, name: "COVID-19 Vaccine", quantity: 500, expiryDate: "2024-06-30" },
          { id: 2, name: "Flu Vaccine", quantity: 1000, expiryDate: "2024-03-31" },
          { id: 3, name: "Tetanus Vaccine", quantity: 200, expiryDate: "2025-12-31" },
        ]), 1000))
      setInventory(response)
    }

    fetchInventory()
  }, [])

  const handleReorder = (id) => {
    // Placeholder for reorder logic
    console.log(`Reorder vaccine with id ${id}`)
  }

  return (
    (<motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}>
      <Card>
        <CardHeader>
          <CardTitle>Vaccine Inventory</CardTitle>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Vaccine Name</TableHead>
                <TableHead>Quantity</TableHead>
                <TableHead>Expiry Date</TableHead>
                <TableHead>Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {inventory.map((item) => (
                <TableRow key={item.id}>
                  <TableCell>{item.name}</TableCell>
                  <TableCell>{item.quantity}</TableCell>
                  <TableCell>{item.expiryDate}</TableCell>
                  <TableCell>
                    <Button onClick={() => handleReorder(item.id)}>Reorder</Button>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </motion.div>)
  );
}