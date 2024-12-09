"use client";
import { motion } from "framer-motion"
import { ChevronRight, Mail, Shield, ShieldCheck, User } from 'lucide-react'
import Image from "next/image"

import { Button } from "@/components/ui/button"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip"

const vaccineInfo = {
  BCG: "BCG vaccine provides protection against tuberculosis (TB). It's usually given to infants and young children in countries where TB is common.",
  PENTAVALENT: "Pentavalent vaccine provides protection against five diseases: diphtheria, pertussis, tetanus, hepatitis B and Haemophilus influenzae type b (Hib).",
  OPV: "OPV is an oral vaccine used to prevent poliomyelitis (polio). It contains a mixture of live attenuated poliovirus strains.",
  PCV: "PCV protects against pneumococcal disease, which can cause serious infections of the lungs (pneumonia), blood (bacteremia), and brain/spinal cord (meningitis).",
  IPV: "IPV is an injectable vaccine used to prevent poliomyelitis (polio). It contains inactivated strains of poliovirus.",
  MR: "MR vaccine provides protection against measles and rubella (German measles). These are highly contagious viral infections that can cause serious complications.",
}

export default function VaccinationTracker({
  data
}) {
  return (
    (<div className="container mx-auto p-6 space-y-8">
      {data && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}>
          <Card>
            <CardContent className="flex items-center gap-6 p-6">
              <div className="relative h-20 w-20 rounded-full overflow-hidden bg-muted">
                <Image src="https://placehold.co/400x300" alt="User avatar" fill className="object-cover" />
              </div>
              <div className="space-y-2">
                <div className="flex items-center gap-2">
                  <User className="h-4 w-4 text-muted-foreground" />
                  <h3 className="font-medium">{data.user_info.user_name}</h3>
                </div>
                <div className="flex items-center gap-2">
                  <Mail className="h-4 w-4 text-muted-foreground" />
                  <p className="text-sm text-muted-foreground">{data.user_info.user_email}</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </motion.div>
      )}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.2 }}>
        <Card>
          <CardHeader>
            <CardTitle>Vaccination History</CardTitle>
            <CardDescription>Track your vaccination status and upcoming doses</CardDescription>
          </CardHeader>
          <CardContent>
            <TooltipProvider>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead className="w-[200px]">Vaccine</TableHead>
                    <TableHead>Dose 1</TableHead>
                    <TableHead>Dose 2</TableHead>
                    <TableHead>Dose 3</TableHead>
                    <TableHead>Dose 4</TableHead>
                    <TableHead>Dose 5</TableHead>
                    <TableHead className="text-right">Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {data.vaccination_history.map((vaccine) => (
                    <TableRow key={vaccine.vaccine_code}>
                      <TableCell className="font-medium">
                        <div className="space-y-1">
                          <div>{vaccine.vaccine_code}</div>
                          <div className="text-xs text-muted-foreground">{vaccine.vaccine_name}</div>
                        </div>
                      </TableCell>
                      {vaccine.doses.map((dose, doseIndex) => (
                        <TableCell key={doseIndex}>
                          <Tooltip>
                            <TooltipTrigger>
                              <motion.div whileHover={{ scale: 1.1 }} whileTap={{ scale: 0.9 }}>
                                {dose.is_taken ? (
                                  <ShieldCheck className="h-5 w-5 text-green-500" />
                                ) : (
                                  <Shield className="h-5 w-5 text-muted-foreground/40" />
                                )}
                              </motion.div>
                            </TooltipTrigger>
                            <TooltipContent>
                              {dose.is_taken 
                                ? `Vaccinated on ${new Date(dose.vaccination_date).toLocaleDateString()}`
                                : "Vaccination pending"}
                            </TooltipContent>
                          </Tooltip>
                        </TableCell>
                      ))}
                      <TableCell className="text-right">
                        <Dialog>
                          <DialogTrigger asChild>
                            <Button variant="ghost" className="space-x-2">
                              <span>View Details</span>
                              <ChevronRight className="h-4 w-4" />
                            </Button>
                          </DialogTrigger>
                          <DialogContent>
                            <DialogHeader>
                              <DialogTitle>{vaccine.vaccine_name}</DialogTitle>
                              <DialogDescription className="pt-4">
                                {vaccineInfo[vaccine.vaccine_code]}
                              </DialogDescription>
                            </DialogHeader>
                          </DialogContent>
                        </Dialog>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TooltipProvider>
          </CardContent>
        </Card>
      </motion.div>
    </div>)
  );
}

