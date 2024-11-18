'use client'

import { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from "@/components/ui/accordion"
import { motion } from "framer-motion"

export function Faq() {
  const [faqs, setFaqs] = useState([])

  useEffect(() => {
    // Placeholder for Axios data fetching
    const fetchFaqs = async () => {
      // Simulated API call
      const response = await new Promise(resolve => 
        setTimeout(() => resolve([
          { id: 1, question: "What vaccines do I need?", answer: "The vaccines you need depend on various factors including your age, health conditions, and travel plans. Consult with your healthcare provider for personalized recommendations." },
          { id: 2, question: "Are vaccines safe?", answer: "Yes, vaccines are thoroughly tested for safety before they are approved for use. While some people may experience mild side effects, serious adverse reactions are extremely rare." },
          { id: 3, question: "How often do I need to get vaccinated?", answer: "The frequency of vaccinations varies depending on the specific vaccine. Some vaccines provide lifelong immunity, while others require periodic boosters. Your healthcare provider can provide a recommended schedule." },
          { id: 4, question: "Can I get multiple vaccines at once?", answer: "In many cases, yes. Your healthcare provider can advise on which vaccines can be safely administered together." },
        ]), 1000))
      setFaqs(response)
    }

    fetchFaqs()
  }, [])

  return (
    (<motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}>
      <Card>
        <CardHeader>
          <CardTitle>Frequently Asked Questions</CardTitle>
        </CardHeader>
        <CardContent>
          <Accordion type="single" collapsible>
            {faqs.map((faq) => (
              <AccordionItem key={faq.id} value={`item-${faq.id}`}>
                <AccordionTrigger>{faq.question}</AccordionTrigger>
                <AccordionContent>{faq.answer}</AccordionContent>
              </AccordionItem>
            ))}
          </Accordion>
        </CardContent>
      </Card>
    </motion.div>)
  );
}