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
};

import { Faq } from "./faq";
import { ProfileComponent } from "./profile";
import { HealthTipsComponent } from "./health-tips";
import { ReportsComponent } from "./reports";
import VaccinationRecordComponent from "./vaccinator-input-form";
import VaccinationDashboard from "./vaccination-dashboard";
import { getCurrentUserVaccineInfo } from "./api";
import VaccinationCheck from "./vaccination-check";

export default function Dashboard() {
  const componentMap = {
    "vaccination-input-form": VaccinationRecordComponent,
    "my-vaccinations": VaccinationDashboard,
    profile: ProfileComponent,
    reports: ReportsComponent,
    "health-tips": HealthTipsComponent,
    faq: Faq,
    "vaccination-checker": VaccinationCheck,
    // ... other components
  };

  const [userGroup, setUserGroup] = useState(null);
  const [isExpanded, setIsExpanded] = useState(false);
  const [isPinned, setIsPinned] = useState(false);
  const [activeComponent, setActiveComponent] = useState(null);
  const router = useRouter();

  useEffect(() => {
    const storedUserGroup = sessionStorage.getItem("userGroup");

    if (storedUserGroup === "1") {
      setActiveComponent("my-vaccinations");
    } else if (storedUserGroup === "2") {
      setActiveComponent("vaccination-input-form");
    }
    if (!storedUserGroup) {
      router.push("/login");
    } else {
      setUserGroup(storedUserGroup);
    }
  }, [router]);

  const handleLogout = () => {
    sessionStorage.clear();
    router.push("/login");
  };

  const togglePin = () => {
    setIsPinned(!isPinned);
    setIsExpanded(!isPinned);
  };

  const handleMenuItemClick = (componentName) => {
    setActiveComponent(componentName);
  };

  if (!userGroup) {
    return <div>Loading...</div>;
  }

  const filteredMenuItems = menuItems.filter(
    (item) => item.user_group === "all" || item.user_group === userGroup
  );

  return (
    <div className="flex h-screen bg-gray-100">
      <aside
        className={cn(
          "bg-white shadow-md transition-all duration-300 ease-in-out flex flex-col",
          isExpanded || isPinned ? "w-64" : "w-16"
        )}
        onMouseEnter={() => !isPinned && setIsExpanded(true)}
        onMouseLeave={() => !isPinned && setIsExpanded(false)}
      >
        <div className="p-4 flex items-center justify-between">
          <h2
            className={cn(
              "font-bold text-xl transition-opacity duration-300",
              isExpanded || isPinned ? "opacity-100" : "opacity-0 w-0"
            )}
          >
            Vaccine Dashboard
          </h2>
          <Button
            variant="ghost"
            size="icon"
            onClick={togglePin}
            className={cn(
              "transition-opacity duration-300",
              isExpanded || isPinned ? "opacity-100" : "opacity-0"
            )}
          >
            <ChevronRight
              className={cn(
                "h-4 w-4 transition-transform",
                isPinned && "rotate-180"
              )}
            />
          </Button>
        </div>
        <nav className="flex-1 overflow-y-auto">
          {filteredMenuItems.map((item, index) => {
            const Icon = iconMap[item.icon];
            return (
              <Button
                key={index}
                variant="ghost"
                className={cn(
                  "w-full justify-start px-4 py-2 transition-all duration-300 ease-in-out",
                  isExpanded || isPinned ? "text-left" : "justify-center"
                )}
                onClick={() => handleMenuItemClick(item.component)}
              >
                <Icon className="h-5 w-5 mr-2 flex-shrink-0" />
                <span
                  className={cn(
                    "transition-opacity duration-300 whitespace-nowrap",
                    isExpanded || isPinned ? "opacity-100" : "opacity-0 w-0"
                  )}
                >
                  {item.label}
                </span>
              </Button>
            );
          })}
          <Button
            variant="ghost"
            className={cn(
              "w-full justify-start px-4 py-2 transition-all duration-300 ease-in-out",
              isExpanded || isPinned ? "text-left" : "justify-center"
            )}
            onClick={handleLogout}
          >
            <LogOut className="h-5 w-5 mr-2 flex-shrink-0" />
            <span
              className={cn(
                "transition-opacity duration-300 whitespace-nowrap",
                isExpanded || isPinned ? "opacity-100" : "opacity-0 w-0"
              )}
            >
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
