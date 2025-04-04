# Bug Hotspot Tracker UI - Technical Design Document

---

## 🔍 Overview

The Bug Hotspot Tracker is a UI-based tool designed to visualize bug distribution across a codebase using a **Tree Map View** and a **Data Table View**. It helps identify hot spots in the codebase by color-coding based on bug severity. Users can toggle between viewing files and directories, and also search for specific files or directories.

---

## 📈 Functional Requirements

### ✅ **Views**

1. **Tree Map View**
    - Displays bug data as a hierarchical tree map.
    - Supports toggling between viewing by **file paths** and **directories**.
    - Uses **color-coding** based on calculated severity (using percentiles).
    - Allows search for specific files or directories.
2. **Data Table View**
    - Tabular representation of the data.
    - Columns: `Path`, `Bug Count`, `Severity`.
    - Supports toggling between **file paths** and **directories**.
    - Severity calculated on-the-fly using percentiles.
    - Allows search for specific files or directories.

---

## 🎨 UI Specifications

### 🌳 **Tree Map View**

- **Libraries:** Recharts (for rendering the Tree Map), Tailwind CSS (for styling).
- **Color Coding:**
    - Severity is determined by calculating the **percentile of bug counts** within the current view (file vs. directory).
    - Colors:
        - High Severity: **Red (#FF4D4D)**
        - Medium Severity: **Orange (#FF9900)**
        - Low Severity: **Green (#4CAF50)**
- **Tooltip Support:**
    - Display `Path` and `Bug Count` when hovering over a block.
- **Toggle Support:**
    - Toggle between viewing **file paths** and **directories**.
- **Search Functionality:**
    - Real-time filtering of the tree map by file or directory name.

### 📋 **Data Table View**

- **Libraries:** Tailwind CSS (for styling), Recharts (for sorting support).
- **Columns:** `Path`, `Bug Count`, `Severity`.
- **Sorting & Filtering:**
    - Sortable by `Bug Count` or `Severity`.
    - Searchable by path or directory name.
- **Toggle Support:**
    - Toggle between viewing **file paths** and **directories**.
- **Severity Calculation:**
    - Severity is calculated dynamically using **percentiles**.
    - Severity Levels:
        - **High:** 75th percentile and above.
        - **Medium:** Between 25th and 75th percentile.
        - **Low:** Below 25th percentile.

---

## 📊 Data Processing

- The CSV file is stored locally and loaded directly into the application.
- Aggregation by **directories** or **files** is done on-the-fly depending on the current toggle state.
- Bug counts are **aggregated** based on hierarchy when toggling between file paths and directories.
- Severity is recalculated whenever toggles or filtering are applied.

---

## 📂 Project Structure

- `src/components/`: React components for rendering Tree Map and Data Table views.
- `src/utils/`: Utility functions for CSV parsing, data aggregation, percentile calculations, and search filtering.
- `src/styles/`: Tailwind styling configuration.

---

## 📌 Key Features to Implement

1. **Tree Map View (With Color Coding & Tooltips)**
2. **Data Table View (Sortable, Searchable)**
3. **Toggle Functionality (File Paths vs. Directories)**
4. **Search Functionality (Real-Time Filtering)**
5. **Severity Calculation Using Percentiles**
6. **Tailwind Styling for Polished UI**

---

## 🚀 Deployment

- Deploy on Vercel using Vite + React + Tailwind + Recharts.

---

## 📅 Next Steps

1. Build initial Tree Map view with toggling functionality.
2. Add Data Table view with search and sorting.
3. Implement severity calculation based on percentiles.
4. Style with Tailwind CSS.
5. Deploy to Vercel.