"use client"

import { Treemap, ResponsiveContainer } from "recharts"
import { useState, useEffect } from "react"
import type { BugData } from "@/lib/data-utils"
import { FileText, FolderTree } from "lucide-react"
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip"
import { Switch } from "@/components/ui/switch"
import { Label } from "@/components/ui/label"

interface TreeMapChartProps {
  data: BugData[]
  viewMode: "files" | "directories"
}

// Updated color scheme: red, orange, yellow
const COLORS = {
  HIGH: "#FF4D4D", // Red
  MEDIUM: "#FF9900", // Orange
  LOW: "#FFEB3B", // Yellow
}

export function TreeMapChart({ data, viewMode }: TreeMapChartProps) {
  const [thresholds, setThresholds] = useState({ low: 0, medium: 0 })
  const [showFullPaths, setShowFullPaths] = useState(false)

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

  // Get color based on bug count and thresholds
  const getColorByCount = (count: number) => {
    if (count >= thresholds.medium) {
      return COLORS.HIGH
    } else if (count >= thresholds.low) {
      return COLORS.MEDIUM
    } else {
      return COLORS.LOW
    }
  }

  // Check if data is available
  if (!data || data.length === 0) {
    return (
      <div className="flex items-center justify-center h-full w-full bg-gray-50 rounded-lg">
        <p className="text-gray-500">No data available to visualize</p>
      </div>
    )
  }

  // Transform data for the treemap
  const transformedData = data.map((item) => {
    // For file view, show just the filename in the treemap
    // For directory view, show the directory name
    const displayName =
      viewMode === "files"
        ? item.object_name.split("/").pop() || item.object_name
        : item.object_name.split("/").pop() || item.object_name

    // Use full path if showFullPaths is true
    const nameToDisplay = showFullPaths ? item.object_name : displayName

    return {
      name: item.object_name,
      displayName: nameToDisplay,
      shortName: displayName,
      value: item.count,
      fill: getColorByCount(item.count),
    }
  })

  // Update the TreeMapChart component to move the toggle outside the treemap
  // and only show it in files view mode

  // Replace the entire return statement with this updated version:
  return (
    <TooltipProvider>
      <div className="space-y-2">
        {/* Only show the toggle in files view mode */}
        {viewMode === "files" && (
          <div className="flex items-center justify-end space-x-2 mb-2">
            <Label htmlFor="show-paths" className="text-xs flex items-center gap-1">
              {showFullPaths ? (
                <>
                  <FolderTree className="h-3 w-3" /> Show full paths
                </>
              ) : (
                <>
                  <FileText className="h-3 w-3" /> Show file names only
                </>
              )}
            </Label>
            <Switch id="show-paths" checked={showFullPaths} onCheckedChange={setShowFullPaths} />
          </div>
        )}

        <div className="relative h-[580px] w-full">
          {/* Legend with dynamic thresholds */}
          <div className="absolute top-0 right-0 flex items-center gap-4 z-10 bg-white/80 p-2 rounded-lg">
            <div className="flex items-center gap-1">
              <div className="w-3 h-3 rounded-full" style={{ backgroundColor: COLORS.HIGH }}></div>
              <span className="text-xs">High (≥{thresholds.medium})</span>
            </div>
            <div className="flex items-center gap-1">
              <div className="w-3 h-3 rounded-full" style={{ backgroundColor: COLORS.MEDIUM }}></div>
              <span className="text-xs">Medium (≥{thresholds.low})</span>
            </div>
            <div className="flex items-center gap-1">
              <div className="w-3 h-3 rounded-full" style={{ backgroundColor: COLORS.LOW }}></div>
              <span className="text-xs">Low (&lt;{thresholds.low})</span>
            </div>
          </div>

          <ResponsiveContainer width="100%" height="100%">
            <Treemap
              data={transformedData}
              dataKey="value"
              nameKey="displayName"
              stroke="#fff"
              animationDuration={500}
              // Custom content to display the number in each box
              content={({ x, y, width, height, name, displayName, shortName, value, fill, index }) => {
                const item = transformedData[index]
                const fullPath = item?.name || ""
                const displayText = showFullPaths
                  ? typeof displayName === "string" && displayName.length > 20
                    ? `${displayName.substring(0, 20)}...`
                    : displayName
                  : typeof item?.shortName === "string" && item.shortName.length > 15
                    ? `${item.shortName.substring(0, 15)}...`
                    : item?.shortName

                return (
                  <g>
                    <Tooltip>
                      <TooltipTrigger asChild>
                        <rect
                          x={x}
                          y={y}
                          width={width}
                          height={height}
                          fill={fill}
                          stroke="#fff"
                          strokeWidth={2}
                          className="transition-all duration-200 hover:opacity-90 hover:stroke-gray-300 cursor-pointer"
                          style={{
                            filter: "drop-shadow(0px 2px 3px rgba(0, 0, 0, 0.1))",
                            rx: "4px",
                            ry: "4px",
                          }}
                        />
                      </TooltipTrigger>
                      <TooltipContent side="top" className="max-w-xs">
                        <div className="font-mono text-xs break-all">
                          <div className="font-bold mb-1">{fullPath}</div>
                          <div className="flex justify-between">
                            <span>Bug Count:</span>
                            <span className="font-bold">{value}</span>
                          </div>
                        </div>
                      </TooltipContent>
                    </Tooltip>

                    {width > 30 && height > 30 && (
                      <>
                        <text
                          x={x + width / 2}
                          y={y + height / 2 - 10}
                          textAnchor="middle"
                          dominantBaseline="middle"
                          fill="#fff"
                          stroke="none"
                          fontSize={10}
                          fontWeight="bold"
                          className="pointer-events-none"
                          style={{
                            textShadow: "0px 1px 2px rgba(0, 0, 0, 0.5)",
                          }}
                        >
                          {displayText}
                        </text>
                        <text
                          x={x + width / 2}
                          y={y + height / 2 + 10}
                          textAnchor="middle"
                          dominantBaseline="middle"
                          fill="#fff"
                          stroke="none"
                          fontSize={12}
                          fontWeight="bold"
                          className="pointer-events-none"
                          style={{
                            textShadow: "0px 1px 2px rgba(0, 0, 0, 0.5)",
                          }}
                        >
                          {value}
                        </text>
                      </>
                    )}
                    {width > 30 && height <= 30 && (
                      <text
                        x={x + width / 2}
                        y={y + height / 2}
                        textAnchor="middle"
                        dominantBaseline="middle"
                        fill="#fff"
                        stroke="none"
                        fontSize={10}
                        fontWeight="bold"
                        className="pointer-events-none"
                        style={{
                          textShadow: "0px 1px 2px rgba(0, 0, 0, 0.5)",
                        }}
                      >
                        {value}
                      </text>
                    )}
                  </g>
                )
              }}
            />
          </ResponsiveContainer>
        </div>
      </div>
    </TooltipProvider>
  )
}

