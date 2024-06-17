Fixing links, hide title frnt matter 

**ScanPyImports** scans directories for import statements in Python scripts and Jupyter notebooks, providing tools to summarize and visualize the import statements across your projects.

Cloud plot            |  Spiral plot
:-------------------------:|:-------------------------:
<img width="350px" src="https://github.com/lennon-c/ScanPyImports/raw/main/docs/img/cloud_plot.svg" alt="image_name png" />|    <img width="350px" src="https://github.com/lennon-c/ScanPyImports/raw/main/docs/img/spiral_plot.svg" alt="image_name png" />
 
# Features
- **Directory Scanning**:
    - Recursively scans directories to locate all Python files (`.py`) and Jupyter notebooks (`.ipynb`), collecting import statements from the code.
    - Employs a set of regular expressions to find and parse import statements within the scripts.
- **Import Statement Data**:
    - Organizes import data using DataFrames and conducts basic analyses.
- **Data Visualization**:
    - Provides tools to visualize import data with various plotting options.
    - Currently includes spiral plots and word clouds of the import statements.

# Getting started
##  Dependencies 
ScanPyImports requires the following packages:

- pandas 
- matplotlib  
- numpy  
- wordcloud 
- pillow  
- nbformat 

## Clone or download the code into your computer.

 

# Demos, Tutorials
<div class="grid cards" markdown>

-  Data
    -  [Data](https://lennon-c.github.io/ScanPyImports/Examples/Data/)
            Getting the DataFrame of your imported modules.

- Vizualization
    - [Visualizing Imported Modules](https://lennon-c.github.io/ScanPyImports/Examples/PlotsImports/)
    - [Visualizing Any Data](https://lennon-c.github.io/ScanPyImports/Examples/Plots/)

- Viz. Customization
    - [Basics](https://lennon-c.github.io/ScanPyImports/Examples/CustomBasic)
    - [Masks for Spiral plots](https://lennon-c.github.io/ScanPyImports/Examples/Masks)
    - [More Complex Visualizations](https://lennon-c.github.io/ScanPyImports/Examples/Example)  

 </div>

 

# API

[ScanPyImports](https://lennon-c.github.io/ScanPyImports/Api/ScanPyImports/)

::: ScanPyImports 
 
 