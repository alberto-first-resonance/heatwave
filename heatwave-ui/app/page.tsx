"use client"

import { useEffect, useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { TreeMapChart } from "@/components/tree-map-chart"
import { DataTable } from "@/components/data-table"
import { type BugData, aggregateByDirectory, parseCsvData } from "@/lib/data-utils"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Loader2 } from "lucide-react"
import { Button } from "@/components/ui/button"

export default function BugHotspotTracker() {
  const [bugData, setBugData] = useState<BugData[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [viewMode, setViewMode] = useState<"files" | "directories">("files")

  // Load CSV data on component mount
  useEffect(() => {
    async function loadCsvData() {
      try {
        setLoading(true)
        setError(null)

        // Fetch the CSV file from our API route
        const response = await fetch("/api/get-bug-data")

        if (!response.ok) {
          throw new Error(`Failed to load CSV file: ${response.status} ${response.statusText}`)
        }

        const csvText = await response.text()
        const data = parseCsvData(csvText)

        console.log(`Loaded ${data.length} bug data entries from CSV`)
        setBugData(data)
      } catch (err) {
        console.error("Error loading CSV data:", err)
        setError(err instanceof Error ? err.message : String(err))
      } finally {
        setLoading(false)
      }
    }

    loadCsvData()
  }, [])

  // Aggregate data by directory when in directory view mode
  const aggregatedData = viewMode === "directories" ? aggregateByDirectory(bugData) : bugData

  return (
    <div className="container mx-auto py-8 px-4">
      <h1 className="text-3xl font-bold mb-6">HEATWAVE 🔥 </h1>
      <h2 className="text-1xl font-bold mb-6">Bug Hotspot Tracker</h2>

      {loading ? (
        <div className="flex justify-center items-center h-64">
          <Loader2 className="h-8 w-8 animate-spin text-gray-500" />
          <span className="ml-2 text-lg">Loading bug data from CSV...</span>
        </div>
      ) : (
        <>
          {error && (
            <Card className="bg-yellow-50 mb-6">
              <CardContent className="pt-6">
                <p className="text-yellow-800">{error}</p>
              </CardContent>
            </Card>
          )}

          {bugData.length === 0 && !error ? (
            <Card className="bg-yellow-50 mb-6">
              <CardContent className="pt-6">
                <p className="text-yellow-800">No bug data found in the CSV file.</p>
              </CardContent>
            </Card>
          ) : (
            <Tabs defaultValue="treemap">
              <div className="flex justify-between items-center mb-6">
                <TabsList>
                  <TabsTrigger value="treemap">Tree Map</TabsTrigger>
                  <TabsTrigger value="table">Data Table</TabsTrigger>
                </TabsList>

                <div className="flex items-center gap-2">
                  <span className="text-sm text-gray-500">View:</span>
                  <div className="bg-gray-100 rounded-lg p-1">
                    <Button
                      variant={viewMode === "files" ? "default" : "ghost"}
                      size="sm"
                      onClick={() => setViewMode("files")}
                      className="rounded-lg"
                    >
                      Files
                    </Button>
                    <Button
                      variant={viewMode === "directories" ? "default" : "ghost"}
                      size="sm"
                      onClick={() => setViewMode("directories")}
                      className="rounded-lg"
                    >
                      Directories
                    </Button>
                  </div>
                </div>
              </div>

              <TabsContent value="treemap">
                <Card className="shadow-md rounded-2xl">
                  <CardHeader>
                    <CardTitle>Bug Distribution</CardTitle>
                    <CardDescription>
                      Visualization of bug counts across {viewMode === "directories" ? "directories" : "files"}. Block
                      size and color represent bug count.
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="h-[600px] w-full">
                      <TreeMapChart data={aggregatedData} viewMode={viewMode} />
                    </div>
                  </CardContent>
                </Card>
              </TabsContent>

              <TabsContent value="table">
                <Card className="shadow-md rounded-2xl">
                  <CardHeader>
                    <CardTitle>Bug Data</CardTitle>
                    <CardDescription>
                      Tabular view of bug counts per {viewMode === "directories" ? "directory" : "file"}
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <DataTable data={aggregatedData} />
                  </CardContent>
                </Card>
              </TabsContent>
            </Tabs>
          )}
        </>
      )}
    </div>
  )
}

