"use client";

import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import dynamic from "next/dynamic";
import { motion } from "framer-motion";
import axios from "axios";
import { Loader2 } from "lucide-react";

// Import ApexCharts dynamically to avoid SSR issues
const Chart = dynamic(() => import("react-apexcharts"), { ssr: false });

const COLORS = [
  "#0088FE",
  "#00C49F", 
  "#FFBB28",
  "#FF8042",
  "#8884d8",
  "#82ca9d",
];

const ChartWrapper = ({ children }) => {
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted) return null;
  
  return (
    <div className="w-full h-full">
      {children}
    </div>
  );
};

const SafeChart = ({ options, series, type, height }) => {
  try {
    return (
      <Chart
        options={options}
        series={series}
        type={type}
        height={height}
      />
    );
  } catch (error) {
    console.error('Chart Error:', error);
    return <div>Error loading chart</div>;
  }
};

export function ReportsComponent() {
  const [monthlyData, setMonthlyData] = useState([]);
  const [vaccineData, setVaccineData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [chartsMounted, setChartsMounted] = useState(false);

  useEffect(() => {
    setChartsMounted(true);
    return () => setChartsMounted(false);
  }, []);

  const API = process.env.NEXT_PUBLIC_API_URL

  useEffect(() => {
    const fetchStats = async () => {
      try {
        setLoading(true);
        const token = sessionStorage.getItem("access_token");
        const response = await axios.post(
          `${API}/api/vaccination-stats`,
          {
            token: token,
          }
        );

        if (response.data) {
          setMonthlyData(response.data.monthly_data || []);
          setVaccineData(response.data.vaccine_distribution || []);
        }
      } catch (err) {
        setError(err.response?.data?.detail || "Failed to fetch statistics");
      } finally {
        setLoading(false);
      }
    };

    fetchStats();
  }, []);

  const barChartOptions = {
    chart: {
      type: 'bar',
      height: 400,
      animations: {
        enabled: true
      }
    },
    plotOptions: {
      bar: {
        horizontal: false,
        columnWidth: '55%',
      },
    },
    dataLabels: {
      enabled: false
    },
    xaxis: {
      categories: monthlyData.map(item => item.month) || [],
      type: 'category'
    },
    yaxis: {
      labels: {
        formatter: function (val) {
          return val.toFixed(0)
        }
      },
      min: 0
    },
    colors: ['#0088FE']
  };

  const barChartSeries = [{
    name: 'Vaccinations',
    data: monthlyData?.map(item => item.vaccinations) || []
  }];

  const pieChartOptions = {
    chart: {
      type: 'pie',
      height: 400
    },
    labels: vaccineData.map(item => item.name),
    colors: COLORS,
    responsive: [{
      breakpoint: 480,
      options: {
        chart: {
          width: 200
        },
        legend: {
          position: 'bottom'
        }
      }
    }],
    yaxis: {
      show: false
    }
  };

  const pieChartSeries = vaccineData?.map(item => item.value) || [];

  const lineChartOptions = {
    chart: {
      type: 'line',
      height: 400,
      animations: {
        enabled: true
      }
    },
    stroke: {
      curve: 'smooth'
    },
    xaxis: {
      categories: monthlyData.map(item => item.month)
    },
    colors: ['#10B981'],
    yaxis: {
      labels: {
        formatter: function (val) {
          return val.toFixed(0)
        }
      },
      min: 0
    }
  };

  const lineChartSeries = [{
    name: 'Vaccinations',
    data: monthlyData?.map(item => item.vaccinations) || []
  }];

  const canRenderCharts = typeof window !== 'undefined' && 
                         monthlyData.length > 0 && 
                         vaccineData.length > 0 && 
                         chartsMounted;

  if (loading)
    return (
      <div className="flex justify-center items-center h-screen">
        <Loader2 className="h-8 w-8 animate-spin" />
      </div>
    );
  if (error)
    return <div className="text-red-500 text-center">Error: {error}</div>;
  if (!canRenderCharts) return null;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="grid grid-cols-1 gap-6 md:grid-cols-2"
    >
      {/* Monthly Vaccinations Bar Chart */}
      <Card>
        <CardHeader>
          <CardTitle>Monthly Vaccinations</CardTitle>
        </CardHeader>
        <CardContent>
          <ChartWrapper>
            <SafeChart 
              options={barChartOptions}
              series={barChartSeries}
              type="bar"
              height={400}
            />
          </ChartWrapper>
        </CardContent>
      </Card>

      {/* Vaccine Distribution Pie Chart */}
      <Card>
        <CardHeader>
          <CardTitle>Vaccine Distribution</CardTitle>
        </CardHeader>
        <CardContent>
          <ChartWrapper>
            <Chart
              options={pieChartOptions}
              series={pieChartSeries}
              type="pie"
              height={400}
            />
          </ChartWrapper>
        </CardContent>
      </Card>

      {/* Monthly Vaccinations Line Chart */}
      <Card className="md:col-span-2">
        <CardHeader>
          <CardTitle>Vaccination Trend</CardTitle>
        </CardHeader>
        <CardContent>
          <ChartWrapper>
            <Chart
              options={lineChartOptions}
              series={lineChartSeries}
              type="line"
              height={400}
            />
          </ChartWrapper>
        </CardContent>
      </Card>
    </motion.div>
  );
}
