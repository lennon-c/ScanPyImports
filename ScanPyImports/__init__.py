
"""**ScanPyImports** is a Python package designed to scan, track, and analyze import statements across Python files and Jupyter notebooks.
 
Modules:
    scan: Handles directory scanning and the parsing of Python scripts and notebooks.
    analyzer: Structures the parsed data into DataFrames and performs basic data cleaning and analysis.
    plotter: Manages visualization tools.

    
The core of the package uses a set of **regular expressions** to parse import statements.


<p align="center" width="100%">
    <img width="60%" src="https://imgs.xkcd.com/comics/regular_expressions.png" alt="Regular Expressions"> <br>
    Yep! super <b>Re</b>. Attribution: <a href="https://xkcd.com/208/">xkcd.com</a> 
</p>






"""
import ScanPyImports.scan  
import ScanPyImports.plotter  
import ScanPyImports.analyzer  

