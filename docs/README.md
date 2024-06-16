---
title: ScanPyImports
---
<!-- hide title -->
<style>
  .md-typeset h1,
  .md-content__button {
    display: none;
  }
</style>
**ScanPyImports** scans directories for import statements in Python scripts and Jupyter notebooks, providing tools to summarize and visualize the import statements across your projects.


![](img\cloud_plot.svg){: style="height:15em;width:15em"}
![](img\spiral_plot.svg){: style="height:15em;width:15em"}

# Features
- **Directory Scanning**:
    - Recursively scans directories to locate all Python files (`.py`) and Jupyter notebooks (`.ipynb`), collecting import statements from the code.
    - Employs a set of regular expressions to find and parse import statements within the scripts.
- **Import Statement Data**:
    - Organizes import data using DataFrames and conducts basic analyses.
- **Data Visualization**:
    - Provides tools to visualize import data with various plotting options.
    - Currently includes spiral plots and word clouds of the import statements.

--8<-- "installation.md"

# Demos, Tutorials
--8<-- "Examples\demos_index.md"

# API
--8<-- "Api\ScanPyImports.md"
 
 