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
  AlertTriangle,
  Menu
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
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [userGroup, setUserGroup] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [userName, setUserName] = useState("");
  const router = useRouter();

  useEffect(() => {
    // Initialize client-side state
    const token = sessionStorage.getItem("access_token");
    if (!token) {
      router.push("/login");
      return;
    }

    const group = sessionStorage.getItem("userGroup");
    const name = sessionStorage.getItem("userName");
    setUserGroup(group);
    setUserName(name || "Guest");

    // Set default component based on user group
    if (group === "1") {
      setActiveComponent("my-vaccinations");
    } else if (group === "2") {
      setActiveComponent("vaccination-input-form");
    }
    setIsLoading(false);
  }, [router]);

  const handleLogout = () => {
    sessionStorage.clear();
    router.push("/login");
  };

  // Only filter menu items if userGroup is available
  const filteredMenuItems = userGroup 
    ? menuItems.filter(item => item.user_group === userGroup || item.user_group === "all")
    : [];

  if (isLoading) {
    return (
      <div className="flex h-screen items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
      </div>
    );
  }

  return (
    <div className="flex h-screen overflow-hidden bg-gray-50">
      {/* Sidebar */}
      <aside className={cn(
        "fixed inset-y-0 left-0 z-50 w-64 transform transition-transform duration-200 ease-in-out md:relative md:translate-x-0",
        isMobileMenuOpen ? "translate-x-0" : "-translate-x-full md:translate-x-0"
      )}>
        <div className="flex h-full flex-col bg-white shadow-lg">
          {/* Logo */}
          <div className="flex h-16 items-center border-b px-6">
            <h1 className="font-heading text-xl font-bold text-primary">
              VaxGuard
            </h1>
          </div>

          {/* Navigation */}
          <nav className="flex-1 space-y-1 px-3 py-4">
            {filteredMenuItems.map((item) => {
              const Icon = iconMap[item.icon];
              return (
                <Button
                  key={item.component}
                  variant={activeComponent === item.component ? "default" : "ghost"}
                  className={cn(
                    "w-full justify-start text-sm font-medium transition-colors",
                    activeComponent === item.component 
                      ? "bg-primary text-primary-foreground hover:bg-primary/90"
                      : "text-gray-600 hover:bg-gray-100 hover:text-gray-900"
                  )}
                  onClick={() => setActiveComponent(item.component)}
                >
                  {Icon && <Icon className="mr-3 h-4 w-4" />}
                  {item.label}
                </Button>
              );
            })}

            <Button
              variant="ghost"
              className="w-full justify-start text-sm font-medium text-gray-600 hover:bg-gray-100 hover:text-gray-900"
              onClick={handleLogout}
            >
              <LogOut className="mr-3 h-4 w-4" />
              Logout
            </Button>
          </nav>
        </div>
      </aside>

      {/* Main Content */}
      <div className="flex flex-1 flex-col overflow-hidden">
        {/* Header */}
        <header className="flex h-16 items-center justify-between border-b bg-white px-6">
          <Button
            variant="ghost"
            size="icon"
            className="md:hidden"
            onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
          >
            <Menu className="h-6 w-6" />
          </Button>

          <div className="flex items-center space-x-4">
            <h2 className="font-heading text-lg font-semibold text-gray-800">
              Welcome, {userName}!
            </h2>
          </div>

          <div className="flex items-center space-x-4">
            <Button variant="ghost" size="icon" className="relative">
              <Bell className="h-5 w-5" />
              <span className="absolute -right-1 -top-1 flex h-4 w-4 items-center justify-center rounded-full bg-primary text-[10px] font-medium text-primary-foreground">
                3
              </span>
            </Button>
          </div>
        </header>

        {/* Main Content Area */}
        <main className="flex-1 overflow-auto bg-gray-50 p-6">
          <div className="mx-auto max-w-7xl">
            <div className="rounded-lg border bg-white p-6 shadow-sm">
              {activeComponent && componentMap[activeComponent] ? (
                React.createElement(componentMap[activeComponent])
              ) : (
                <div className="flex flex-col items-center justify-center py-12 text-center">
                  <Syringe className="h-12 w-12 text-primary/40" />
                  <h3 className="mt-4 font-heading text-lg font-medium text-gray-900">
                    Welcome to VaxGuard
                  </h3>
                  <p className="mt-2 text-sm text-gray-500">
                    Select a menu item to get started with managing your vaccinations.
                  </p>
                </div>
              )}
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}
