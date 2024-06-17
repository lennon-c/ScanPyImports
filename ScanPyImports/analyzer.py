"""
A module for processing and analyzing data on imported modules. 

classes:
    Data: Construct the base DataFrame of the import statement data.
    DataAnalyzer: Processe and analyze the data on imported modules.
"""

import os
import pandas as pd
from typing import List, Optional, Tuple, Union
from .scan import Directory

class Data:
    """
    Construct the base DataFrame of the import statement data.
    """

    def __init__(self, path: str) -> None:
        """
        Initialize a Data object with the given path.

        Args:
            path: Path to the directory.
        """
        self.path = path
        self.directory = Directory(path)
        
        if not self.directory.exists:
            raise ValueError("The provided directory path does not exist. Try another path!")
        
        self._df: Optional[pd.DataFrame] = None

        # Documentation
        self.path: str
        """Path to the directory."""
        self.directory: Directory 
        """An instance of [Directory][ScanPyImports.scan.Directory] initiated with the given path."""


        super().__init__()

    @property
    def df(self) -> Optional[pd.DataFrame]:
        """DataFrame containing import data or None if the directory does not exist.

        ??? info inline end "DataFrame content"
            The DataFrame contains the following columns: 
            
            - `imported_0`, `imported_1`, ...
                representing the imported  packages and modules.
                - where `imported_0` represents the top-level package or library being imported.
                - `imported_1` represents the module or submodule within the package being imported.
                - and so on `imported_2` represent further nested modules, submodules if present in the import statement.
            - `original`: The original line of text containing the import statement.
            - `alias`: Alias (if any) of the submodule.
            - `path`: Full path of the file containing the import.
            - `file`: File name.
            - `filename`: File name without extension.
            - `extension`: File extension.
            - `directory`: Directory path of the file.
   
        The data creation takes place in this [private method](create_df.md). One could modify this code to retreive a dictionary or a JSON file instead of a DataFrame.
        """
        if self._df is None:
            self._df = self._create_df()
        return self._df.copy()

    def _create_df(self) -> Optional[pd.DataFrame]:
        """
        Create a DataFrame with the data on imported modules.

        Returns:
            DataFrame with import data or None if the directory does not exist.
        """
        if not self.directory.exists:
            return None

        data_frames = []
        for file in self.directory.files:
            if not file.has_imports:
                continue

            file_data_frames = []
            for line in file.lines:
                line_df = pd.DataFrame(line.imports)
                line_df["alias"] = line.alias
                # line_df["alias"] = pd.Series(line.alias)
                line_df["original"] = line.original

                file_data_frames.append(line_df)

            file_df = pd.concat(file_data_frames, ignore_index=True)
            file_df['path'] = file.file
            file_df['extension'] = file.extension
            file_df['file'] = os.path.basename(file.file)
            file_df['filename'] = os.path.basename(file.file).split('.')[0]
            file_df['directory'] = os.path.dirname(file.file)
            data_frames.append(file_df)

        if not data_frames:
            return None

        directory_df = pd.concat(data_frames, ignore_index=True)

        cols = list(directory_df.columns)
        cols.sort( key= lambda c: str(c) )
        directory_df = directory_df[cols].rename(columns=lambda col: 
                                           f'imported_{col}' 
                                           if isinstance(col, int) else col)

        return directory_df

class DataAnalyzer(Data):
    """A class to process the data on imported modules.
    """

    def __init__(self, path: str, to_exclude : List[str] = None) -> None:
        """Initiate DataAnalyzer

        Args:
            path: Path to the directory.
            to_exclude: List of packages' names to exclude from the analysis.

        methods: 
            get_frequencies: Return frequency of imported modules.

        """        
        super().__init__(path)
        self._clean_df = None
        self._own_processed_df = None
        self.to_exclude= to_exclude if to_exclude else []

        # Documentation
        self.to_exclude: List[str]
        """List of packages' names to exclude from the analysis.""" 

    @property
    def clean_df(self) -> pd.DataFrame:
        """A cleaned copy of [df][ScanPyImports.analyzer.Data.df] after conducting some minor changes.
        """
        if self._clean_df is None:
            self._clean_df = self._get_clean_data()
        return self._clean_df.copy()

    @property
    def own_processed_df(self) -> pd.DataFrame:
        """ A copy of the DataFrame ([df][ScanPyImports.analyzer.Data.df]) after processing own-created modules.
        
        ??? info inline end "Own-created modules"
            Own-created modules are defined as Python scripts that are imported as modules and reside in the same folder as the script containing the import statement.

            A natural extension would be to also include own-created packages residing in the same folder as the .py or .ipynb file where the import statment resides.
 
        In the returned DataFrame, own-created modules are dropped and replaced by the import statements residing inside the own-created module script, provided they relate to external libraries.
        

        """
        if self._own_processed_df is None:
            self._own_processed_df, self.own_modules= self._process_own_modules()
        return self._own_processed_df.copy()

    def _get_clean_data(self) -> pd.DataFrame:
        """
        Perform cleaning operations on the DataFrame.

        Returns:
            pd.DataFrame: Cleaned DataFrame with duplicates removed and certain conditions applied.
        """
        df = self.df.drop_duplicates()
        df = df[df['imported_0'] != ''] # relative imports
        return df

    def _process_own_modules(self) -> pd.DataFrame:
        """Process imports corresponding to own-created modules.
        
        Drop own created modules, where own modules are identified as .py files that reside in the same folder as the file from where the modules are being imported. 

        Todo: 

            Extend the functionality to packages residing in the same folder as the script file.  
        """
        df = self.clean_df
        parent_files = self._get_python_files_by_directory()

        # Tag rows of own-created modules
        df['is_own_module'] = df.apply(lambda row: 
                                       row['imported_0'] in parent_files[row['directory']], axis=1)
        
        # Extract list of own-created modules 
        own_modules_list = df[df['is_own_module']==True]
        own_modules_list = own_modules_list['imported_0'].unique().tolist()

        # Set of tuples : (own-created module, its directory)
        own_modules = {(row['imported_0'], row['directory']) 
                       for _, row in df.iterrows() if row['is_own_module']}

        def _own_module_df(module: Tuple[str, str]) -> pd.DataFrame:
            """Get imports of an own-created module,
            excluding imports of other own-created modules.

            Args:
                module : A tuple containing the name of the own-created module and its directory.
            """
            own_module, directory = module
            condition = ((df['filename'] == own_module) 
                        & (df['directory'] == directory) 
                        & (~df['is_own_module']))
            return df[condition].copy()

        # Count how many times each own-created module is imported
        own_module_usage_count = (df[df['is_own_module']]
                                  .groupby(['imported_0', 'directory'])
                                  .size())
        
        # Not own-created modules
        external_df = df[~df['is_own_module']]

        # DataFrames for each own-created module's imports
        # Duplicated based on their usage count
        own_dfs = []
        for module in own_modules:
            count = own_module_usage_count[module]
            own_df = _own_module_df(module)
            own_dfs.append(pd.concat([own_df] * count, ignore_index=True))

        # Combine external and internal dfs
        if own_dfs:
            internal_df = pd.concat(own_dfs, ignore_index=True)
            final_df = pd.concat([external_df, internal_df], ignore_index=True)
        else:
            final_df = external_df


        return final_df.drop(columns='is_own_module'), own_modules_list

    def _get_python_files_by_directory(self) -> dict:
        """
        Retrieve a dictionary of scripts per parent directory.

        Returns:
            dict: A dictionary where keys are the directory path, and values are lists of .py files (excluding the '.py' extension).
        """
        directories = self.clean_df['directory'].unique()
        dic = {d: [f.replace('.py', '') for f in os.listdir(d) if f.endswith('.py')] for d in directories}
        return dic

    def get_frequencies(self, exclude: bool = True, process_own_modules: bool = True) -> pd.Series:
        """
        Get the frequency of imported modules.
 
        Args:
            exclude: Whether to exclude the packages listed in [to_exclude][ScanPyImports.analyzer.DataAnalyzer.to_exclude].
            process_own_modules: Whether to process own-created modules.

        Returns:
            pd.Series: Series of import frequencies sorted in descending order.
        """
        df = self.own_processed_df if process_own_modules else self.clean_df
        count_series = (df.groupby('imported_0')
                        .size()
                        .sort_values(ascending=False))
        
        count_series.index.name = 'Imports'

        if exclude:
            count_series = count_series[~count_series.index.isin(self.to_exclude)]

        return count_series

