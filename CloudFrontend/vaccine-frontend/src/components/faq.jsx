'use client'

import { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from "@/components/ui/accordion"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { ScrollArea } from "@/components/ui/scroll-area"
import { motion, AnimatePresence } from "framer-motion"
import { Search, HelpCircle, Syringe, Shield, AlertTriangle, ThumbsUp, MessagesSquare } from 'lucide-react'

export function Faq() {
  const [faqs, setFaqs] = useState([])
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedCategory, setSelectedCategory] = useState('all')
  const [expandedItems, setExpandedItems] = useState([])

  const categories = [
    { id: 'all', label: 'All Questions', icon: <HelpCircle className="h-4 w-4" /> },
    { id: 'general', label: 'General', icon: <MessagesSquare className="h-4 w-4" /> },
    { id: 'vaccination', label: 'Vaccination', icon: <Syringe className="h-4 w-4" /> },
    { id: 'safety', label: 'Safety', icon: <Shield className="h-4 w-4" /> },
    { id: 'side-effects', label: 'Side Effects', icon: <AlertTriangle className="h-4 w-4" /> },
    { id: 'aftercare', label: 'Aftercare', icon: <ThumbsUp className="h-4 w-4" /> },
  ]

  useEffect(() => {
    const fetchFaqs = async () => {
      const response = await new Promise(resolve => 
        setTimeout(() => resolve([
          { 
            id: 1, 
            category: 'general',
            question: "What vaccines do I need?", 
            answer: "The vaccines you need depend on various factors including your age, health conditions, and travel plans. Consult with your healthcare provider for personalized recommendations.",
            helpful: 156
          },
          { 
            id: 2, 
            category: 'safety',
            question: "Are vaccines safe?", 
            answer: "Yes, vaccines are thoroughly tested for safety before they are approved for use. While some people may experience mild side effects, serious adverse reactions are extremely rare.",
            helpful: 234
          },
          { 
            id: 3, 
            category: 'general',
            question: "How often do I need to get vaccinated?", 
            answer: "The frequency of vaccinations varies depending on the specific vaccine. Some vaccines provide lifelong immunity, while others require periodic boosters. Your healthcare provider can provide a recommended schedule.",
            helpful: 189
          },
          { 
            id: 4, 
            category: 'vaccination',
            question: "Can I get multiple vaccines at once?", 
            answer: "In many cases, yes. Your healthcare provider can advise on which vaccines can be safely administered together based on your health status and the types of vaccines.",
            helpful: 145
          },
          { 
            id: 5, 
            category: 'side-effects',
            question: "What are common vaccine side effects?", 
            answer: "Common side effects include soreness at the injection site, mild fever, and fatigue. These typically resolve within a few days and are signs that your body is building protection.",
            helpful: 278
          },
          { 
            id: 6, 
            category: 'aftercare',
            question: "What should I do after getting vaccinated?", 
            answer: "Stay at the vaccination site for 15-30 minutes after receiving your shot to monitor for any immediate reactions. Keep the injection site clean and dry. You can take over-the-counter pain relievers if needed.",
            helpful: 198
          },
        ]), 1000))
      setFaqs(response)
    }

    fetchFaqs()
  }, [])

  const filteredFaqs = faqs.filter(faq => {
    const matchesCategory = selectedCategory === 'all' || faq.category === selectedCategory
    const matchesSearch = faq.question.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         faq.answer.toLowerCase().includes(searchQuery.toLowerCase())
    return matchesCategory && matchesSearch
  })

  const handleAccordionChange = (value) => {
    setExpandedItems(prev => {
      if (prev.includes(value)) {
        return prev.filter(item => item !== value)
      }
      return [...prev, value]
    })
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
            <HelpCircle className="h-5 w-5 text-primary" />
            Frequently Asked Questions
          </CardTitle>
          <CardDescription>
            Find answers to common questions about vaccination
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Search and Filters */}
          <div className="space-y-4">
            <div className="relative">
              <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search questions..."
                className="pl-9"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
            </div>
            <div className="flex flex-wrap gap-2">
              {categories.map(category => (
                <Button
                  key={category.id}
                  variant={selectedCategory === category.id ? "default" : "outline"}
                  className="gap-2"
                  onClick={() => setSelectedCategory(category.id)}
                >
                  {category.icon}
                  {category.label}
                </Button>
              ))}
            </div>
          </div>

          {/* FAQ Accordion */}
          <ScrollArea className="h-[600px] pr-4">
            <AnimatePresence mode="wait">
              {filteredFaqs.length > 0 ? (
                <Accordion type="single" collapsible className="space-y-4">
                  {filteredFaqs.map((faq) => (
                    <motion.div
                      key={faq.id}
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, y: -10 }}
                      transition={{ duration: 0.2 }}
                    >
                      <AccordionItem value={faq.id.toString()} className="border rounded-lg px-4">
                        <AccordionTrigger className="hover:no-underline">
                          <div className="flex flex-col items-start gap-2 text-left">
                            <div className="font-semibold">{faq.question}</div>
                            <div className="flex items-center gap-2">
                              <Badge variant="secondary" className="text-xs">
                                {categories.find(c => c.id === faq.category)?.label}
                              </Badge>
                              <Badge variant="outline" className="text-xs">
                                <ThumbsUp className="mr-1 h-3 w-3" />
                                {faq.helpful} found this helpful
                              </Badge>
                            </div>
                          </div>
                        </AccordionTrigger>
                        <AccordionContent>
                          <div className="pt-4 pb-2">
                            <p className="text-muted-foreground">{faq.answer}</p>
                            <div className="mt-4 flex items-center justify-end gap-2">
                              <Button variant="outline" size="sm">
                                Share
                              </Button>
                              <Button variant="ghost" size="sm">
                                Was this helpful?
                              </Button>
                            </div>
                          </div>
                        </AccordionContent>
                      </AccordionItem>
                    </motion.div>
                  ))}
                </Accordion>
              ) : (
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  className="text-center py-8"
                >
                  <HelpCircle className="mx-auto h-12 w-12 text-muted-foreground/40" />
                  <h3 className="mt-4 text-lg font-medium">No questions found</h3>
                  <p className="mt-2 text-sm text-muted-foreground">
                    Try adjusting your search or filters
                  </p>
                </motion.div>
              )}
            </AnimatePresence>
          </ScrollArea>
        </CardContent>
      </Card>
    </motion.div>
  )
}