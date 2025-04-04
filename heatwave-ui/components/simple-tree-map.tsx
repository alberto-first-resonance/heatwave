"use client"

import { Treemap, ResponsiveContainer } from "recharts"
import type { BugData } from "@/lib/data-utils"

interface SimpleTreeMapProps {
  data: BugData[]
  viewMode: "files" | "directories"
}

// Updated color scheme: red, orange, yellow
const COLORS = {
  HIGH: "#FF4D4D", // Red
  MEDIUM: "#FF9900", // Orange
  LOW: "#FFEB3B", // Yellow
}

export function SimpleTreeMap({ data, viewMode }: SimpleTreeMapProps) {
  // Check if data is available
  if (!data || data.length === 0) {
    return (
      <div className="flex items-center justify-center h-full w-full bg-gray-50 rounded-lg">
        <p className="text-gray-500">No data available to visualize</p>
      </div>
    )
  }

  // Find the maximum count for color scaling
  const maxCount = Math.max(...data.map((item) => item.count))

  // Transform data for the treemap
  const transformedData = data.map((item) => {
    // For file view, show just the filename in the treemap
    // For directory view, show the directory name
    const displayName = viewMode === "files" ? item.object_name.split("/").pop() || item.object_name : item.object_name

    // Determine color based on count
    let fill
    if (item.count >= maxCount * 0.7) {
      fill = COLORS.HIGH
    } else if (item.count >= maxCount * 0.3) {
      fill = COLORS.MEDIUM
    } else {
      fill = COLORS.LOW
    }

    return {
      name: item.object_name,
      displayName,
      value: item.count,
      fill,
    }
  })

  return (
    <div className="relative h-full w-full">
      {/* Legend */}
      <div className="absolute top-0 right-0 flex items-center gap-4 z-10 bg-white/80 p-2 rounded-lg">
        <div className="flex items-center gap-1">
          <div className="w-3 h-3 rounded-full" style={{ backgroundColor: COLORS.HIGH }}></div>
          <span className="text-xs">High</span>
        </div>
        <div className="flex items-center gap-1">
          <div className="w-3 h-3 rounded-full" style={{ backgroundColor: COLORS.MEDIUM }}></div>
          <span className="text-xs">Medium</span>
        </div>
        <div className="flex items-center gap-1">
          <div className="w-3 h-3 rounded-full" style={{ backgroundColor: COLORS.LOW }}></div>
          <span className="text-xs">Low</span>
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
          content={({ x, y, width, height, name, value, fill, index }) => (
            <g>
              <rect
                x={x}
                y={y}
                width={width}
                height={height}
                fill={fill}
                stroke="#fff"
                strokeWidth={2}
                className="transition-all duration-200 hover:opacity-90 hover:stroke-gray-300"
                style={{
                  filter: "drop-shadow(0px 2px 3px rgba(0, 0, 0, 0.1))",
                  rx: "4px",
                  ry: "4px",
                }}
              />
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
                    {typeof name === "string" && name.length > 15 ? `${name.substring(0, 15)}...` : name}
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
          )}
        />
      </ResponsiveContainer>
    </div>
  )
}

