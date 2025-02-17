'use client'

import { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { motion, AnimatePresence } from "framer-motion"
import { Heart, Award, Clock, AlertTriangle, CheckCircle2, ArrowRight } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { ScrollArea } from '@/components/ui/scroll-area'

export function HealthTipsComponent() {
  const [tips, setTips] = useState([])
  const [selectedCategory, setSelectedCategory] = useState('all')

  const categories = [
    { id: 'all', label: 'All Tips', icon: Heart },
    { id: 'general', label: 'General Health', icon: Award },
    { id: 'vaccination', label: 'Vaccination', icon: CheckCircle2 },
    { id: 'emergency', label: 'Emergency', icon: AlertTriangle },
  ]

  useEffect(() => {
    // Placeholder for Axios data fetching
    const fetchTips = async () => {
      // Simulated API call
      const response = await new Promise(resolve => 
        setTimeout(() => resolve([
          { 
            id: 1, 
            category: 'general',
            title: "Stay Hydrated", 
            content: "Drink at least 8 glasses of water daily for optimal health.",
            importance: "high",
            timeToRead: "1 min"
          },
          { 
            id: 2, 
            category: 'general',
            title: "Exercise Regularly", 
            content: "Aim for 30 minutes of moderate exercise most days of the week to maintain good health and boost immunity.",
            importance: "medium",
            timeToRead: "2 min"
          },
          { 
            id: 3, 
            category: 'general',
            title: "Get Enough Sleep", 
            content: "Adults should aim for 7-9 hours of sleep per night to support immune function and overall health.",
            importance: "high",
            timeToRead: "1 min"
          },
          { 
            id: 4, 
            category: 'vaccination',
            title: "Pre-Vaccination Care", 
            content: "Get adequate rest and stay hydrated before your vaccination appointment. Inform your healthcare provider about any allergies or medical conditions.",
            importance: "critical",
            timeToRead: "3 min"
          },
          { 
            id: 5, 
            category: 'vaccination',
            title: "Post-Vaccination Care", 
            content: "Monitor for any side effects and keep the vaccination site clean. Use a cold compress if there's swelling.",
            importance: "critical",
            timeToRead: "3 min"
          },
          { 
            id: 6, 
            category: 'emergency',
            title: "When to Seek Help", 
            content: "Seek immediate medical attention if you experience severe allergic reactions like difficulty breathing or rapid heartbeat after vaccination.",
            importance: "critical",
            timeToRead: "2 min"
          },
        ]), 1000))
      setTips(response)
    }

    fetchTips()
  }, [])

  const filteredTips = tips.filter(tip => 
    selectedCategory === 'all' ? true : tip.category === selectedCategory
  )

  const importanceColor = {
    low: "bg-blue-100 text-blue-800",
    medium: "bg-yellow-100 text-yellow-800",
    high: "bg-orange-100 text-orange-800",
    critical: "bg-red-100 text-red-800"
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="space-y-6"
    >
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Heart className="h-5 w-5 text-primary" />
            Health Tips & Guidelines
          </CardTitle>
          <CardDescription>
            Essential health tips and guidelines for vaccination care
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Category Filters */}
          <div className="flex flex-wrap gap-2">
            {categories.map(category => {
              const Icon = category.icon
              return (
                <Button
                  key={category.id}
                  variant={selectedCategory === category.id ? "default" : "outline"}
                  className="gap-2"
                  onClick={() => setSelectedCategory(category.id)}
                >
                  <Icon className="h-4 w-4" />
                  {category.label}
                </Button>
              )
            })}
          </div>

          {/* Tips Grid */}
          <ScrollArea className="h-[600px] pr-4">
            <div className="grid gap-4 md:grid-cols-2">
              <AnimatePresence mode="wait">
                {filteredTips.map((tip) => (
                  <motion.div
                    key={tip.id}
                    initial={{ opacity: 0, scale: 0.95 }}
                    animate={{ opacity: 1, scale: 1 }}
                    exit={{ opacity: 0, scale: 0.95 }}
                    transition={{ duration: 0.2 }}
                  >
                    <Card className="card-hover">
                      <CardHeader className="pb-2">
                        <div className="flex items-start justify-between">
                          <CardTitle className="text-lg">{tip.title}</CardTitle>
                          <Badge variant="secondary" className="flex items-center gap-1">
                            <Clock className="h-3 w-3" />
                            {tip.timeToRead}
                          </Badge>
                        </div>
                        <Badge className={importanceColor[tip.importance]}>
                          {tip.importance.charAt(0).toUpperCase() + tip.importance.slice(1)} Priority
                        </Badge>
                      </CardHeader>
                      <CardContent>
                        <p className="text-sm text-muted-foreground">{tip.content}</p>
                        <Button variant="ghost" size="sm" className="mt-4 w-full">
                          Learn More <ArrowRight className="ml-2 h-4 w-4" />
                        </Button>
                      </CardContent>
                    </Card>
                  </motion.div>
                ))}
              </AnimatePresence>
            </div>
          </ScrollArea>
        </CardContent>
      </Card>
    </motion.div>
  )
}