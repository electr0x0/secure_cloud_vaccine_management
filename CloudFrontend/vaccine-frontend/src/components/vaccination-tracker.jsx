"use client";
import { motion, AnimatePresence } from "framer-motion";
import { ChevronRight, Mail, Shield, ShieldCheck, User, Calendar, Info } from 'lucide-react';
import Image from "next/image";
import { useState } from "react";

import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { 
  Tooltip, 
  TooltipContent, 
  TooltipProvider, 
  TooltipTrigger 
} from "@/components/ui/tooltip";
import { Progress } from "@/components/ui/progress";

const vaccineInfo = {
  BCG: "BCG vaccine provides protection against tuberculosis (TB). It's usually given to infants and young children in countries where TB is common.",
  PENTAVALENT: "Pentavalent vaccine provides protection against five diseases: diphtheria, pertussis, tetanus, hepatitis B and Haemophilus influenzae type b (Hib).",
  OPV: "OPV is an oral vaccine used to prevent poliomyelitis (polio). It contains a mixture of live attenuated poliovirus strains.",
  PCV: "PCV protects against pneumococcal disease, which can cause serious infections of the lungs (pneumonia), blood (bacteremia), and brain/spinal cord (meningitis).",
  IPV: "IPV is an injectable vaccine used to prevent poliomyelitis (polio). It contains inactivated strains of poliovirus.",
  MR: "MR vaccine provides protection against measles and rubella (German measles). These are highly contagious viral infections that can cause serious complications.",
};

export default function VaccinationTracker({ data }) {
  const [selectedVaccine, setSelectedVaccine] = useState(null);

  const calculateProgress = (vaccine) => {
    const totalDoses = vaccine.doses.length;
    const takenDoses = vaccine.doses.filter(dose => dose.is_taken).length;
    return (takenDoses / totalDoses) * 100;
  };

  return (
    <AnimatePresence mode="wait">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: -20 }}
        transition={{ duration: 0.5 }}
        className="space-y-6"
      >
        {/* Overview Cards */}
        <div className="grid gap-4 md:grid-cols-3">
          <Card className="card-hover">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">Total Vaccines</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{data.vaccination_history.length}</div>
              <div className="text-xs text-muted-foreground mt-1">Registered vaccines</div>
            </CardContent>
          </Card>
          <Card className="card-hover">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">Completed</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-success">
                {data.vaccination_history.filter(v => 
                  v.doses.every(d => d.is_taken)
                ).length}
              </div>
              <div className="text-xs text-muted-foreground mt-1">Fully vaccinated</div>
            </CardContent>
          </Card>
          <Card className="card-hover">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">Pending</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-warning">
                {data.vaccination_history.filter(v => 
                  v.doses.some(d => !d.is_taken)
                ).length}
              </div>
              <div className="text-xs text-muted-foreground mt-1">Need attention</div>
            </CardContent>
          </Card>
        </div>

        {/* Vaccination History Table */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Calendar className="h-5 w-5 text-primary" />
              Vaccination History
            </CardTitle>
            <CardDescription>Track your vaccination status and upcoming doses</CardDescription>
          </CardHeader>
          <CardContent>
            <TooltipProvider>
              <div className="rounded-md border">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead className="w-[250px]">Vaccine</TableHead>
                      <TableHead>Progress</TableHead>
                      <TableHead className="text-right">Status</TableHead>
                      <TableHead className="w-[100px]">Info</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {data.vaccination_history.map((vaccine) => (
                      <TableRow key={vaccine.vaccine_code} className="group">
                        <TableCell className="font-medium">
                          <div className="space-y-1">
                            <div className="font-semibold">{vaccine.vaccine_code}</div>
                            <div className="text-xs text-muted-foreground">{vaccine.vaccine_name}</div>
                          </div>
                        </TableCell>
                        <TableCell>
                          <div className="space-y-2">
                            <Progress value={calculateProgress(vaccine)} className="h-2" />
                            <div className="flex justify-between text-xs text-muted-foreground">
                              <span>
                                {vaccine.doses.filter(d => d.is_taken).length} of {vaccine.doses.length} doses
                              </span>
                              <span>
                                {calculateProgress(vaccine)}% Complete
                              </span>
                            </div>
                          </div>
                        </TableCell>
                        <TableCell className="text-right">
                          <div className="flex items-center justify-end gap-2">
                            {vaccine.doses.map((dose, doseIndex) => (
                              <Tooltip key={`${vaccine.vaccine_code}-dose-${doseIndex}`}>
                                <TooltipTrigger>
                                  <motion.div 
                                    whileHover={{ scale: 1.1 }} 
                                    whileTap={{ scale: 0.9 }}
                                    className="relative"
                                  >
                                    {dose.is_taken ? (
                                      <ShieldCheck className="h-5 w-5 text-success" />
                                    ) : (
                                      <Shield className="h-5 w-5 text-muted-foreground/40" />
                                    )}
                                    <span className="absolute -bottom-1 -right-1 text-[10px]">{doseIndex + 1}</span>
                                  </motion.div>
                                </TooltipTrigger>
                                <TooltipContent>
                                  {dose.is_taken 
                                    ? `Dose ${doseIndex + 1} taken on ${new Date(dose.vaccination_date).toLocaleDateString()}`
                                    : `Dose ${doseIndex + 1} pending`}
                                </TooltipContent>
                              </Tooltip>
                            ))}
                          </div>
                        </TableCell>
                        <TableCell>
                          <Dialog>
                            <DialogTrigger asChild>
                              <Button 
                                variant="ghost" 
                                size="icon"
                                className="opacity-0 group-hover:opacity-100 transition-opacity"
                              >
                                <Info className="h-4 w-4" />
                              </Button>
                            </DialogTrigger>
                            <DialogContent>
                              <DialogHeader>
                                <DialogTitle>{vaccine.vaccine_name} (${vaccine.vaccine_code})</DialogTitle>
                                <DialogDescription>
                                  {vaccineInfo[vaccine.vaccine_code]}
                                </DialogDescription>
                              </DialogHeader>
                              <div className="mt-4 space-y-4">
                                <h4 className="font-medium">Vaccination Schedule</h4>
                                <div className="space-y-2">
                                  {vaccine.doses.map((dose, index) => (
                                    <div key={`${vaccine.vaccine_code}-dose-${index}`} className="flex items-center gap-2">
                                      <div className={`h-2 w-2 rounded-full ${dose.is_taken ? 'bg-success' : 'bg-muted'}`} />
                                      <span className="text-sm">
                                        Dose {index + 1}: {dose.is_taken 
                                          ? `Taken on ${new Date(dose.vaccination_date).toLocaleDateString()}`
                                          : 'Pending'}
                                      </span>
                                    </div>
                                  ))}
                                </div>
                              </div>
                            </DialogContent>
                          </Dialog>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </div>
            </TooltipProvider>
          </CardContent>
        </Card>
      </motion.div>
    </AnimatePresence>
  );
}

