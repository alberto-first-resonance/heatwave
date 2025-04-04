// Clearly define the BugData interface
export interface BugData {
  object_name: string // Path to the file or directory
  count: number // Number of bugs found
}

export function parseCsvData(csvText: string): BugData[] {
  // Check if CSV text is empty
  if (!csvText || csvText.trim() === "") {
    throw new Error("CSV file is empty")
  }

  try {
    // Split the CSV text into lines and trim each line
    const lines = csvText
      .trim()
      .split("\n")
      .map((line) => line.trim())

    // Make sure we have at least a header and one data row
    if (lines.length < 2) {
      throw new Error("CSV file must contain a header row and at least one data row")
    }

    // Extract headers (first line) and trim each header
    const headers = lines[0].split(",").map((header) => header.trim())

    // Find the indices of the required columns (case insensitive)
    const objectNameIndex = headers.findIndex((h) => h.toLowerCase() === "object_name")
    const countIndex = headers.findIndex((h) => h.toLowerCase() === "count")

    // Check if required columns exist
    if (objectNameIndex === -1 || countIndex === -1) {
      throw new Error(`CSV file must contain "object_name" and "count" columns. Found columns: ${headers.join(", ")}`)
    }

    // Parse data rows
    const data: BugData[] = []

    for (let i = 1; i < lines.length; i++) {
      // Skip empty lines
      if (!lines[i]) continue

      const values = lines[i].split(",").map((value) => value.trim())

      // Skip lines with insufficient values
      if (values.length <= Math.max(objectNameIndex, countIndex)) continue

      const objectName = values[objectNameIndex]
      const countStr = values[countIndex]

      // Parse count as number
      const count = Number.parseInt(countStr, 10)

      if (objectName && !isNaN(count)) {
        data.push({
          object_name: objectName,
          count: count,
        })
      }
    }

    // Check if we have any valid data
    if (data.length === 0) {
      throw new Error("No valid data found in CSV file")
    }

    return data
  } catch (error) {
    // Re-throw with more context if it's not already an Error object
    if (error instanceof Error) {
      throw error
    } else {
      throw new Error(`Error parsing CSV data: ${error}`)
    }
  }
}

// Function to aggregate data by directory
export function aggregateByDirectory(data: BugData[]): BugData[] {
  const directoryCounts: Record<string, number> = {}

  // Aggregate counts by directory
  data.forEach((item) => {
    // Split the path into segments
    const pathSegments = item.object_name.split("/")

    // Create all possible directory paths
    for (let i = 1; i < pathSegments.length; i++) {
      const directoryPath = pathSegments.slice(0, i).join("/")

      // Skip empty paths
      if (!directoryPath) continue

      // Add to directory count
      if (directoryCounts[directoryPath]) {
        directoryCounts[directoryPath] += item.count
      } else {
        directoryCounts[directoryPath] = item.count
      }
    }
  })

  // Convert to BugData array
  return Object.entries(directoryCounts).map(([directory, count]) => ({
    object_name: directory,
    count,
  }))
}

