"use client"

import { useState, useEffect } from "react"
import type { BugData } from "@/lib/data-utils"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { ArrowUpDown, Search, Bug, AlertTriangle, CheckCircle } from "lucide-react"
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip"

interface DataTableProps {
  data: BugData[]
}

export function DataTable({ data }: DataTableProps) {
  const [sortConfig, setSortConfig] = useState<{
    key: keyof BugData
    direction: "ascending" | "descending"
  }>({
    key: "count",
    direction: "descending",
  })

  const [searchTerm, setSearchTerm] = useState("")
  const [thresholds, setThresholds] = useState({ low: 0, medium: 0 })

  // Calculate severity thresholds based on data distribution
  useEffect(() => {
    if (data.length > 0) {
      const counts = [...data].map((item) => item.count).sort((a, b) => a - b)
      const getPercentile = (p: number) => counts[Math.floor((p / 100) * counts.length)]

      setThresholds({
        low: getPercentile(50) || 1, // 50th percentile (median)
        medium: getPercentile(85) || 2, // 85th percentile
      })
    }
  }, [data])

  // Get severity level for a bug count
  const getSeverityInfo = (count: number) => {
    if (count >= thresholds.medium) {
      return {
        icon: <Bug className="h-4 w-4" />,
        color: "bg-red-100 text-red-800",
        label: "High",
      }
    } else if (count >= thresholds.low) {
      return {
        icon: <AlertTriangle className="h-4 w-4" />,
        color: "bg-orange-100 text-orange-800",
        label: "Medium",
      }
    } else {
      return {
        icon: <CheckCircle className="h-4 w-4" />,
        color: "bg-green-100 text-green-800",
        label: "Low",
      }
    }
  }

  // Sort data
  const sortedData = [...data].sort((a, b) => {
    if (a[sortConfig.key] < b[sortConfig.key]) {
      return sortConfig.direction === "ascending" ? -1 : 1
    }
    if (a[sortConfig.key] > b[sortConfig.key]) {
      return sortConfig.direction === "ascending" ? 1 : -1
    }
    return 0
  })

  // Filter data based on search term
  const filteredData = sortedData.filter((item) => item.object_name.toLowerCase().includes(searchTerm.toLowerCase()))

  // Request sort
  const requestSort = (key: keyof BugData) => {
    let direction: "ascending" | "descending" = "ascending"
    if (sortConfig.key === key && sortConfig.direction === "ascending") {
      direction = "descending"
    }
    setSortConfig({ key, direction })
  }

  return (
    <TooltipProvider>
      <div className="space-y-4">
        <div className="relative">
          <Search className="absolute left-2 top-2.5 h-4 w-4 text-gray-500" />
          <Input
            placeholder="Search files or directories..."
            className="pl-8"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>

        <div className="flex items-center gap-4 text-sm text-gray-500">
          <span>Severity thresholds:</span>
          <span className="flex items-center gap-1">
            <div className="w-3 h-3 rounded-full bg-red-500"></div>
            High: ≥{thresholds.medium}
          </span>
          <span className="flex items-center gap-1">
            <div className="w-3 h-3 rounded-full bg-orange-500"></div>
            Medium: ≥{thresholds.low}
          </span>
          <span className="flex items-center gap-1">
            <div className="w-3 h-3 rounded-full bg-green-500"></div>
            Low: &lt;{thresholds.low}
          </span>
        </div>

        <div className="rounded-md border overflow-hidden">
          <div className="overflow-x-auto">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead className="w-[50%] max-w-[400px]">
                    <Button
                      variant="ghost"
                      onClick={() => requestSort("object_name")}
                      className="flex items-center gap-1 font-medium"
                    >
                      Path
                      <ArrowUpDown className="h-4 w-4" />
                    </Button>
                  </TableHead>
                  <TableHead className="w-[20%] text-center">
                    <Button
                      variant="ghost"
                      onClick={() => requestSort("count")}
                      className="flex items-center gap-1 font-medium justify-center"
                    >
                      Bug Count
                      <ArrowUpDown className="h-4 w-4" />
                    </Button>
                  </TableHead>
                  <TableHead className="w-[30%] text-center">Severity</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredData.length > 0 ? (
                  filteredData.map((item) => {
                    const severity = getSeverityInfo(item.count)
                    return (
                      <TableRow key={item.object_name}>
                        <TableCell className="font-mono text-sm max-w-[400px]">
                          <Tooltip>
                            <TooltipTrigger asChild>
                              <div className="truncate">{item.object_name}</div>
                            </TooltipTrigger>
                            <TooltipContent side="top" className="max-w-xs">
                              <div className="font-mono text-xs break-all">{item.object_name}</div>
                            </TooltipContent>
                          </Tooltip>
                        </TableCell>
                        <TableCell className="text-center">
                          <span className="inline-flex items-center justify-center rounded-full bg-purple-100 px-2.5 py-0.5 text-purple-800 font-medium">
                            {item.count}
                          </span>
                        </TableCell>
                        <TableCell className="text-center">
                          <span
                            className={`inline-flex items-center gap-1 rounded-full px-2.5 py-0.5 ${severity.color}`}
                          >
                            {severity.icon}
                            {severity.label}
                          </span>
                        </TableCell>
                      </TableRow>
                    )
                  })
                ) : (
                  <TableRow>
                    <TableCell colSpan={3} className="text-center py-6 text-gray-500">
                      No matching files found
                    </TableCell>
                  </TableRow>
                )}
              </TableBody>
            </Table>
          </div>
        </div>

        <div className="text-sm text-gray-500">
          Showing {filteredData.length} of {data.length} items
        </div>
      </div>
    </TooltipProvider>
  )
}

