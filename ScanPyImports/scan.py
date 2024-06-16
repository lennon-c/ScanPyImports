"""
This module provides a set of classes and functions to extract import statements from Python files (`.py`) and Jupyter notebooks (`.ipynb`) of a given directory.

Classes:
    Line: Parses a single import statement.
    File: Manages the parsing of Python files and Jupyter notebooks.
    Directory: Manages a collection of files in a directory, extracting import statements from all Python and notebook files found.
"""
import os
import re
from typing import List, Tuple, Optional, Union
import nbformat

class Line:
    """A single import statement."""

    def __init__(self, text: str) -> None:
        """
        Initialize a Line object.

        Args:
            text: A string with an import statement.
        """
        self.original = text
        self.lfrom,self.limports = self.get_from_import(self.original)
        self.imports = self.get_imports(self.lfrom,self.limports )
        self.imports, self.alias = self.get_alias_list(self.imports)
        # self.alias, self.statement = self.get_alias(text) 

        # Documentation
        self.original: str 
        """The original line of code with the import statement."""
        self.lfrom: str  
        """The `from` part of the import statement, if any."""
        self.limports: str  
        """The `import` part of the import statement."""
        self.imports: List[List[str]] 
        """A list of lists, where each inner list represents an imported submodule, containing the package name, modules, and the submodule itself."""
        self.alias: List[str] 
        """The aliases used in the import statement, if any."""

    def compile_alias(self) -> re.Pattern:
        """Match alias in import statements.

        Returns:
            A compiled regular expression pattern.
        """
        pattern = r'(.*?)(\bas\b)( .*)'
        return re.compile(pattern)


    def compile_from_import(self) -> re.Pattern:
        """
        Match and group `from` package and `import` modules 
        from statements.

        Returns:
            A compiled regular expression pattern.
        """
        pattern = r'(?:from(.*?))*(?:import)(.*)'
        return re.compile(pattern)

    def get_from_import(self, statement:str) -> Tuple[str, str]:
        """
        Extract from-import components from the line of code.
        
        Args:
            statement: Line of code. 

        Returns:
            A tuple containing the 'from' part and the 'import' part.
        """
        compiled = self.compile_from_import()
        c = compiled.search(statement)
        if c is None:
            lfrom, limport  =  "", "" # False, False
        else:
            from_import = c.groups()
            from_import = [i.replace('(','').strip() if i is not None else '' for i in from_import]
            lfrom, limport = from_import
        return lfrom, limport

    def get_imports(self, lfrom: str, limports:str) -> List[List[str]]:
        """
        Extract the imported submodules from the import statement.

        Each imported submodule is represented as an ordered list containing:\n
        - The package of the submodule
        - The module
        - The submodule
        - ...
        - The submodule itself with alias, if any.

        Returns:
                A list of lists, where each inner list represents an imported submodule.
        """
        from_items = lfrom.split(".") if lfrom else []
        import_items = [i.strip() for i in limports.split(',')]

        imported_list = []
        for i in import_items:
            i_list = from_items + i.split('.')
            imported_list.append(i_list)
            
        return imported_list

    def get_alias_list(self, imports: List[List[str]])-> Tuple[List[List[str]], List[str]]:
        """Get the alias list and subtract aliases from the import list.

        Args:
            imports: List of imported submodules.

        Returns:
            List of imports without aliases, and list of aliases. Both lists have the same length. Empty strings indicate that the submodule does not have an alias. 
        """
        alias_list = []
        for item in imports:
            alias, submodule = self.get_alias(item[-1])
            item[-1] = submodule
            alias_list.append(alias)

        return imports, alias_list 
        
    def get_alias(self, statement:str) -> Tuple[str, str]:
        """Extract alias from the line of code.

        Args:
            statement: Line of code. 

        Returns:
            A tuple containing the alias and the statement without the alias.
        """        
        compiled = self.compile_alias()
        c = compiled.search(statement)
        if c is None:
            alias = ""
            line = statement
        else:
            line = c.group(1).strip()
            alias = c.group(3).strip()
        return alias, line

class File:
    """
    A Python file or a Jypiter notebook.
     
    A File class bundles a set of Line objects.
    """

    def __init__(self, filepath: str) -> None:
        """
        Initialize a File object.

        Args:
            filepath: Path to the Python file or notebook file.
        """
        self.file = filepath
        self.extension = filepath.split('.')[-1]
        self.code = self.get_code()
        self.code_lines = self.get_code_lines()
        self.statements = self.get_import_lines(self.code_lines)
        self.has_imports = len(self.statements) > 0
        self.lines = self.get_lines_obj()

        # Documentation 
        self.file: str  
        """Path to the Python or notebook file."""
        self.extension: str  
        """The file extension (i.e. py or ipynb)"""
        self.code: str  
        """Text from py file or notebook."""
        self.code_lines: List[str]  
        """All lines of code in the file."""
        self.statements: List[str] 
        """List of import statements in the file."""
        self.has_imports : bool 
        """Indicates if the file has any import statements."""
        self.lines: List[Line]  
        """[Line][ScanPyImports.scan.Line] objects for each import statement."""

    def remove_all_comments(self, code:str) -> str:
        """Remove comments from code. 

        Args:
            code: Line of code

        Returns:
            Line of code with  comments removed.
        """        
        pattern = r'\"\"\"(.|\n)*?\"\"\"|\'\'\'(.|\n)*?\'\'\'|(#.*)'
        # Explanation of the pattern:
        # r'\"\"\"(.|\n)*?\"\"\"' matches triple double quoted strings,
        # r'\'\'\'(.|\n)*?\'\'\'' matches triple single quoted strings,
        # r'(#.*)' matches single-line comments
        return re.sub(pattern, '', code)
    
    def get_code(self) -> str:
        """
        Get code text from py file or notebook.

        For Jupyter notebooks, only the content of the code cells is extracted and returned as a single string.

        Returns: 
            The content of the Python file or the concatenated code cells from the Jupyter notebook.

        """
        if self.extension == 'py':
            try:
                with open(self.file, encoding='utf-8') as py:
                    file = py.read()
                return file 
            except Exception as e:
                if '__MACOSX' not in self.file:
                    print(f'ERROR: Cannot read {self.file}')
                    print(e)  
        else: # ipynb
            try:
                with open(self.file, encoding='utf-8') as nb:
                    notebook = nbformat.read(nb, nbformat.NO_CONVERT)
            except Exception as e:
                print(f'ERROR: Cannot read {self.file}')   
                print(e)
            else: 
                code_cells = [c.source for c in notebook.cells 
                              if c.cell_type == 'code']
                file = "\n".join(code_cells)
                return file   
            
    # TODO: clean new lines "\n" character between parentheses. 
    def get_code_lines(self) -> List[str]:
        """
        Extracts all lines of code from the file.

        Returns:
            A list of strings, each representing a line of code without comments.
        """
        if not self.code:
            lines = []
        else:
            # exclude comments 
            code = self.remove_all_comments(self.code)
            # code to lines 
            lines: List[str] = code.split('\n')
        
        return lines 

    def compile_import(self) -> re.Pattern:
        """
        Match text starting with either `import` or `from`.
        
        Text can be precedeed by blanks.

        Returns:
            Compiled pattern
        """
        pattern = r'^\s*(import|from) '
        return re.compile(pattern, flags=re.MULTILINE)

    def get_import_lines(self, lines:List[str]) -> List[str]:
        """Extract import statements of the file.
        
        Args: 
            lines: A list of strings, each representing a line of code.

        Returns:
            A list of strings with the import statement.
        """
        c = self.compile_import()
        import_lines = []
        for l in lines:
            if c.search(l):
                import_lines.append(l.strip())
        return import_lines

    def get_lines_obj(self) -> List[Line]:
        """
        Line objects of the file.

        Returns:
            A list of Line objects if the file has import statements,    otherwise an empty list. 
        """
        if self.has_imports:
            lines = [Line(l) for l in self.statements]
        else:
            lines = []
        return lines

class Directory:
    """
    The root directory that bundles a set of File objects. 
    
    Files in the root directory are scanned in search for import statements. 
    """

    def __init__(self, path: str) -> None:
        """
        Initialize a Directory object.

        Args:
            path: Path to the directory. Path to python or notebook files are also accepted.
        """
        self.path = path
        try:
            if os.path.exists(path) is False:
                self.exists = False
                raise Exception(f'ERROR: Path "{path}" does not exist.')
        except Exception as e:
            print(e)
        else:
            self.exists= True
            self.isfile = os.path.isfile(path)
            self.isdir = not self.isfile
            self.filepaths = self.get_filepaths()
            self.files = self.get_files_obj()
    
        # Documentation 
        self.path: str 
        """Path to the directory."""
        self.exists: bool  
        """Indicates if the directory exists."""
        self.isfile: bool  
        """Indicates if the path is a file."""
        self.isdir: bool  
        """Indicates if the path is a directory."""
        self.filepaths: List[str]  
        """Paths to .py or .ipynb files in the directory."""
        self.files: Optional[List[File]] 
        """[File][ScanPyImports.scan.File] objects for each file path."""

    def get_filepaths(self) -> List[str]:
        """
        Get paths to .py and .ipynb files within a directory and its subdirectories.

        Returns:
            A list of file paths.
        """
        if not self.exists:
            return []

        if self.isdir:
            filepaths = []
            for dirpath, dirnames, filenames in os.walk(self.path):
                for filename in filenames:
                    if filename.endswith(".py") or filename.endswith(".ipynb") :
                        filepath = os.path.join(dirpath, filename)
                        filepaths.append(filepath)
        else:
            filepaths = [self.path]

        return filepaths

    def get_files_obj(self) -> Optional[List[File]]:
        """
        Get File objects for each file path.

        Returns:
            A list of File objects or None if the directory does not exist.
        """
        if not self.exists:
            return None
        files = [File(path) for path in self.filepaths]
        return files


# if (__name__ == '__main__'):
#     # text = "import numpy as np"
    # text = "import numpy as np # a comment"
    # text = "import numpy as np # a comment"
    # text = "from os import path"
    # text = "import pandas, numpy, os"
    # text = "import happens # nowhere "
    

    # line = Line(text)
    # line.alias
    # line.imports
    # line.statement
    # line.lfrom
    # line.limports