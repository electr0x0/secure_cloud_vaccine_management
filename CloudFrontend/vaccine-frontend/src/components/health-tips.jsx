'use client'

import { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { motion } from "framer-motion"

export function HealthTipsComponent() {
  const [tips, setTips] = useState([])

  useEffect(() => {
    // Placeholder for Axios data fetching
    const fetchTips = async () => {
      // Simulated API call
      const response = await new Promise(resolve => 
        setTimeout(() => resolve([
          { id: 1, title: "Stay Hydrated", content: "Drink at least 8 glasses of water daily." },
          { id: 2, title: "Exercise Regularly", content: "Aim for 30 minutes of moderate exercise most days of the week." },
          { id: 3, title: "Get Enough Sleep", content: "Adults should aim for 7-9 hours of sleep per night." },
          { id: 4, title: "Eat a Balanced Diet", content: "Include a variety of fruits, vegetables, whole grains, and lean proteins in your diet." },
        ]), 1000))
      setTips(response)
    }

    fetchTips()
  }, [])

  return (
    (<motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}>
      <Card>
        <CardHeader>
          <CardTitle>Health Tips</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4">
            {tips.map((tip) => (
              <Card key={tip.id}>
                <CardHeader>
                  <CardTitle className="text-lg">{tip.title}</CardTitle>
                </CardHeader>
                <CardContent>
                  <p>{tip.content}</p>
                </CardContent>
              </Card>
            ))}
          </div>
        </CardContent>
      </Card>
    </motion.div>)
  );
}