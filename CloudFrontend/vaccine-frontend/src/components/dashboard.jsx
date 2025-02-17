"use client";

import React from "react";
import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import {
  Syringe,
  UserCircle,
  Calendar,
  FileText,
  LogOut,
  ChevronRight,
  Bell,
  BarChart,
  Package,
  Heart,
  HelpCircle,
  Activity,
  Cpu,
  AlertTriangle
} from "lucide-react";
import { cn } from "@/lib/utils";
import menuItems from "@/data/menuItems.json";

const iconMap = {
  Syringe,
  UserCircle,
  Calendar,
  FileText,
  LogOut,
  BarChart,
  Package,
  Heart,
  HelpCircle,
  Activity,
  Cpu,
  AlertTriangle
};

import { Faq } from "./faq";
import { ProfileComponent } from "./profile";
import { ReportsComponent } from "./reports";
import VaccinationRecordComponent from "./vaccinator-input-form";
import VaccinationDashboard from "./vaccination-dashboard";
import VaccinationCheck from "./vaccination-check";
import { HealthTipsComponent } from "./health-tips";

const componentMap = {
  "vaccination-input-form": VaccinationRecordComponent,
  "my-vaccinations": VaccinationDashboard,
  "vaccination-checker": VaccinationCheck,
  "profile": ProfileComponent,
  "reports": ReportsComponent,
  "health-tips": HealthTipsComponent,
  "faq": Faq,
}

export default function Dashboard() {
  const [activeComponent, setActiveComponent] = useState(null);
  const router = useRouter();

  useEffect(() => {
    // Check if user is logged in
    const token = sessionStorage.getItem("access_token");
    if (!token) {
      router.push("/login");
    }
  }, [router]);

  const handleLogout = () => {
    sessionStorage.clear();
    router.push("/login");
  };

  const userGroup = sessionStorage.getItem("userGroup");
  const filteredMenuItems = menuItems.filter(
    item => item.user_group === userGroup || item.user_group === "all"
  );

  return (
    <div className="flex h-screen overflow-hidden">
      <aside className="w-64 bg-gray-800 text-white p-4">
        <nav className="space-y-2">
          {filteredMenuItems.map((item, index) => {
            const Icon = iconMap[item.icon];
            return (
              <Button
                key={index}
                variant="ghost"
                className={cn(
                  "w-full justify-start text-white hover:text-white hover:bg-gray-700",
                  activeComponent === item.component && "bg-gray-700"
                )}
                onClick={() => setActiveComponent(item.component)}
              >
                {Icon && <Icon className="mr-2 h-4 w-4" />}
                <span className="text-sm font-medium">
                  {item.label}
                </span>
              </Button>
            );
          })}

          <Button
            variant="ghost"
            className="w-full justify-start text-white hover:text-white hover:bg-gray-700"
            onClick={handleLogout}
          >
            <LogOut className="mr-2 h-4 w-4" />
            <span className="text-sm font-medium">
              Logout
            </span>
          </Button>
        </nav>
      </aside>
      <main className="flex-1 p-8 overflow-auto relative">
        <div className="flex justify-between items-center mb-6">
          <h1 className="text-2xl font-bold">
            Welcome,{" "}
            {sessionStorage.getItem("userName")
              ? sessionStorage.getItem("userName")
              : "Guest"}
            !
          </h1>
          <Button variant="ghost" size="icon" className="relative">
            <Bell className="h-6 w-6" />
            <span className="absolute top-0 right-0 bg-red-500 text-white text-xs rounded-full h-5 w-5 flex items-center justify-center">
              3
            </span>
          </Button>
        </div>
        <div className="bg-white p-6 rounded-lg shadow-md">
          {activeComponent && componentMap[activeComponent] ? (
            React.createElement(componentMap[activeComponent])
          ) : (
            <p className="text-gray-500">
              Select a menu item to view its content.
            </p>
          )}
        </div>
      </main>
    </div>
  );
}
