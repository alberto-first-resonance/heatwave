import { NextResponse } from "next/server"
import fs from "fs"
import path from "path"

export async function GET() {
  try {
    // Fix the file path construction
    const filePath = path.join(process.cwd(), "public", "bug-data.csv")

    // Check if the file exists before trying to read it
    if (!fs.existsSync(filePath)) {
      console.error(`File not found: ${filePath}`)
      return new NextResponse(`File not found: bug-data.csv`, { status: 404 })
    }

    // Read the file as text
    const csvData = fs.readFileSync(filePath, "utf-8")

    // Return the CSV data
    return new NextResponse(csvData, {
      status: 200,
      headers: {
        "Content-Type": "text/csv",
      },
    })
  } catch (error) {
    // Log the full error for debugging
    console.error("Error reading CSV file:", error)

    // Return a more detailed error message
    return new NextResponse(`Failed to read CSV file: ${error instanceof Error ? error.message : String(error)}`, {
      status: 500,
    })
  }
}

