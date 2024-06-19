"""
A module for generating visual representations of data using spiral plots and word clouds.

classes:
    PlotSettings: Manages plot settings, including defaults for spiral plots and WordCloud generation.
    Spiral: Generates spiral bar plots using given settings.
    Cloud: Generates word cloud plots using given settings.
    DataPlotter: Extends DataAnalyzer to provide methods for visualizing data on imported modules.

The module also includes utility functions to obtain the current file directory and load image masks.
"""
import os
from ScanPyImports.analyzer import DataAnalyzer
from matplotlib import pyplot as plt
import matplotlib

# from matplotlib.cm import get_cmap
 
from matplotlib.text import Text
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from matplotlib.image import AxesImage
from matplotlib.projections.polar import PolarAxes
from matplotlib.container import BarContainer
from wordcloud import WordCloud
import numpy as np
from PIL import Image
 

from typing import Dict, Any, Optional, Union, Tuple, List

def current_file_dir() -> str:
    """Get the directory containing the current file."""
    try:
        return os.path.dirname(os.path.abspath(__file__))
    except:
        return os.path.dirname(os.path.abspath('__file__'))

def mask_from_path(path: str) -> np.ndarray:
    """Loads an image from the given path and returns it as a NumPy array."""
    mask = np.array(Image.open(path))
    return mask

def get_fontname_list():
    """Get a list of available font names."""
    return sorted(matplotlib.font_manager.get_font_names())

def color_list(n : int = 3, colormap : str = 'Blues' , lower : float = 0.3,  upper : float = 1.0 , hex_colors : bool = True , reversed_cmap : bool = False) -> list :  
    """List of color codes based on the specified Matplotlib colormap. 

    Args:
        n: The number of color codes to be generated. 
        colormap: The name of the colormap to be used.
        lower: The lower bound of the color range to be selected from the colormap.
        upper: The upper bound of the color range to be selected from the colormap.
        hex_colors: If True, the color codes will be returned in hexadecimal format otherwise colors are in RGBA format.
        reversed_cmap: List colors in reverse order.

    Returns:
        A list of `n` color codes in either hexadecimal or RGBA format.
    """
    if colormap:
        # Get matplotlib colormap 
        colormap = matplotlib.colormaps[colormap]
        
        # Select colors list
        colors =  colormap(np.linspace(lower, upper, n ))
        
        # If reversed colors 
        if reversed_cmap :
            colors = colors[::-1]
                    
        if hex_colors :
            # Convert color codes to hexadecimal format
            colors = [matplotlib.colors.to_hex(c) for c in colors]
        
        return colors

class PlotSettings:
    """A class to manage plot settings, including defaults for spiral plots and WordCloud generation."""

    def __init__(self):
        """Initialize PlotSettings with default values."""
        self.fontpath: str = None
        """Path to the font file currently in use."""
        self.fontname: str = None
        """Name of the font."""
        self.fontfamily: str = None
        """Font family."""
        self.figsize: tuple[float,float] = (4.8,4.8)
        """Figure size."""

        # Only bar format
        self._spiral_defaults : dict = {
            'bottom': 30,
            'linewidth': 2,
            'edgecolor': 'white',
        }

        mask_path = os.path.join(current_file_dir(), "images", "mask.png")
        mask = mask_from_path(mask_path)
        self._cloud_defaults = {
            'background_color': None,
            'mode': "RGBA",
            'mask': mask,
            'font_path': None,
            'width': 1000,
            'height': 1000,
            'max_words': 200,
            'prefer_horizontal': 0.75,
            'repeat': True,
            'max_font_size': 100,
            'colormap': None
        }

    @property
    def spiral_defaults(self) -> dict:
        """Default parameters for bars in the spiral plot."""
        return self._spiral_defaults
    
    @spiral_defaults.setter
    def spiral_defaults(self, value: dict):
        """Set default parameters for bars in the spiral plot."""
        if not isinstance(value, dict):
            raise ValueError("Defaults must be provided as a dictionary.")

        self._spiral_defaults.update(value)

    @property
    def cloud_defaults(self) -> dict:
        """Default arguments for WordCloud generation."""
        return self._cloud_defaults
    
    @cloud_defaults.setter
    def cloud_defaults(self, value: dict):
        """Set default arguments for WordCloud generation."""
        if not isinstance(value, dict):
            raise ValueError("Default must be provided as a dictionary.")
        self._cloud_defaults.update(value)
    
    def set_font(self, name: str):
        """Set the font globally for plotting.
        This method updates the font settings for both WordCloud generation
        and Matplotlib plotting to use the specified font.

        Args:
            name (str): Matplotlib font name, such as `Arial`, `Verdana`, etc.
        """
        font_path = matplotlib.font_manager.findfont(name)
        prop = matplotlib.font_manager.FontProperties(fname=font_path)
        self.fontpath = font_path
        self.fontname = name
        self.fontfamily = prop.get_family()
        self.cloud_defaults = dict(font_path=font_path)

        # Change matplotlib globally
        matplotlib.rcParams[f'font.{self.fontfamily[0]}'] = self.fontname
        matplotlib.rcParams['font.family'] = self.fontfamily[0]

    def restore_font(self):
        """Restore default font from WordCloud and Matplotlib."""
        self.fontpath = None
        self.fontname = None
        self.fontfamily = None
        self.cloud_defaults = dict(font_path=None)
        matplotlib.rcdefaults()

class Spiral:
    """
    A class to generate spiral bar plots using given settings.

    Attributes:
        settings (PlotSettings): An instance of PlotSettings containing default plotting parameters.
    
    Methods:
        plot: Generate a spiral bar plot.
        add_labels: Helper function.
        get_ax: Helper function.
    """
    def __init__(self, settings: Optional[PlotSettings] = None):
        """
        Initialize a Spiral object.

        Args:
            settings: An instance of PlotSettings containing default plotting parameters.
        """
        if settings:
            self.settings = settings
        else:
            self.settings = PlotSettings()

        self.settings : PlotSettings  
        """A [PlotSettings][ScanPyImports.plotter.PlotSettings] instance."""

    def plot(self, labels: Optional[List[str]] = None,
             values: Optional[List[Union[float, int]]] = None,
             ax: Optional[PolarAxes] = None,
             zero_at: str = 'NE',
             label_padding: int = 2,
             defaults: bool = True,
             **kwargs: Any) -> Tuple[Figure, PolarAxes, BarContainer, List[Text]]:
        """
        Generate a spiral bar plot.

        Args:
            labels: List of labels for the bars.
            values: List of values for the bars. Order values in ascending order for a spiral effect.
            ax: The axes to plot on. If None, a new figure and axes are created. 
                The `ax` parameter must be an instance of PolarAxes.
            zero_at: Zero location for theta. Default is 'NE', which means that the largest value will point North-East (NE). 
                Other possible values: 'N', 'S', 'SE', 'NW', and 'SW'.
            label_padding: Padding for the labels.
            defaults: Whether to use default settings from the class.
            **kwargs: Additional keyword arguments for the bar plot to be passed to Matplotlib (see: [Axes.bar][matplotlib.axes.Axes.bar]).
                If there is a collision, `kwargs` will overwrite default settings.


        Notes:
            The `ax` parameter, if passed, must be an instance of [**PolarAxes**][matplotlib.projections.polar.PolarAxes].

            When creating `ax`, you should pass `polar` as the projection argument. Here are two ways to achieve this:

            ```python
            from matplotlib import pyplot as plt

            # One way:
            fig = plt.figure()
            ax = fig.add_subplot(projection='polar')

            # Another way:
            fig, ax = plt.subplots(subplot_kw={'projection': 'polar'})
            ```

            
        Returns:
            The figure, axes, bars, and texts of the plot.

        Raises:
            ValueError: If `labels` and `values` are not provided or if their lengths do not match.
        """
        if labels is None or values is None:
            raise ValueError("Both 'labels' and 'values' must be provided.")
        if len(labels) != len(values):
            raise ValueError("Length of 'labels' and 'values' must be the same.")

        if defaults:
            kwargs = {**self.settings.spiral_defaults, **kwargs}

        val_max = max(values)
        heights = [(val / val_max) * 120 + 5 for val in values]
        n = len(labels)
        width_bar = 2 * np.pi / n
        thetas = [bar * width_bar for bar in range(1, n + 1)]

        fig, ax = self.get_ax(ax)

        ax.set_theta_zero_location(zero_at)
        bars = ax.bar(x=thetas, height=heights, width=width_bar, **kwargs)

        texts = self.add_labels(ax, bars, labels, thetas, heights, label_padding)
        
        ax.set_axis_off()
        return fig, ax, bars, texts
    
    def add_labels(self, ax: Axes, bars: BarContainer, labels: List[str],
                    thetas: List[float], heights: List[float], label_padding: int) -> List[Text]:
        """
        Helper function to add labels to the bars in the spiral plot.

        Args:
            ax: The axes to add the labels to.
            bars: The bars of the spiral plot.
            labels: List of labels for the bars.
            thetas: List of theta values for the bars.
            heights: List of heights for the bars.
            label_padding: Padding for the labels.

        Returns:
            A list of Matplotlib text objects for the labels.
        """
        def theta_adj(theta):
            return (theta + ax.get_theta_offset()) % (np.pi * 2)

        def get_quadrant(theta):
            return theta // (np.pi / 2)

        def text_rot_theta(theta: float) -> float:
            quadrant = get_quadrant(theta_adj(theta))
            rotation = theta_adj(theta)
            if quadrant in [1, 2]:
                rotation += np.pi
            return rotation

        def text_rot_degree(theta: float) -> float:
            return np.rad2deg(text_rot_theta(theta))

        def text_ha(theta: float) -> str:
            return 'right' if get_quadrant(theta_adj(theta)) in [1, 2] else 'left'

        bottom = bars[0].xy[1]
        heights_pad = [y + label_padding + bottom for y in heights]

        texts = []
        for label, theta, y in zip(labels, thetas, heights_pad):
            text = ax.text(
                x=theta,
                y=y,
                s=label,
                ha=text_ha(theta),
                rotation=text_rot_degree(theta),
                va='center',
                rotation_mode="anchor"
            )
            texts.append(text)
        return texts
    
    def get_ax(self, ax: Optional[PolarAxes] = None) -> Tuple[Figure, PolarAxes]:
        """
        Helper function to get or create a Matplotlib Figure and Axes.

        Args:
            ax: An existing Matplotlib Axes object. 

        Returns:
            A tuple containing the Figure and Axes of the plot. If an Axes object is passed, the Axes and its figure will be returned. Otherwise, a new figure and Axes will be created.
        """
        if ax is None:
            fig = plt.figure(figsize=self.settings.figsize)
            ax = fig.add_subplot(projection='polar')
        else:
            fig = ax.get_figure()
        return fig, ax

class Cloud:
    """
    A class to generate word cloud plots using given settings.

    Attributes:
        settings: An instance of PlotSettings containing default plotting parameters.

    Methods:
        plot: Generate a word cloud.
        get_ax: Helper function.
    """

    def __init__(self, settings: Optional[PlotSettings] = None) -> None:
        """
        Initialize a Cloud object.

        Args:
            settings: An instance of PlotSettings containing default plotting parameters. 
        """
        if settings:
            self.settings = settings
        else:
            self.settings = PlotSettings()

        self.settings: PlotSettings
        """An instance of PlotSettings for default plotting parameters."""

    def plot(self, data_dic: Dict[str, Union[int, float]], 
             defaults: bool = True, 
             ax: Optional[Axes] = None, 
             imshow: Optional[Dict[str, Any]] = {}, 
             **kwargs: Any ) -> Tuple[Figure, Axes, WordCloud, AxesImage]:
        """
        Generate a word cloud.

        Args:
            data_dic: Dictionary of word frequencies of label-value pairs.
            defaults: Whether to use default settings of the Class.  
            ax: The axes to plot on. If None, a new figure and axes are created.
            imshow: Additional arguments to pass to the Matplotlib imshow method (see: [Axes.imshow][matplotlib.axes.Axes.imshow]).
            **kwargs: Additional keyword arguments passed to the WordCloud object (see: [wordcloud.WordCloud](https://amueller.github.io/word_cloud/generated/wordcloud.WordCloud.html#wordcloud.WordCloud))

        Returns:
            A tuple containing the figure, axes, WordCloud object, and AxesImage object of the plot.
        """
        if defaults:
            kwargs = {**self.settings.cloud_defaults, **kwargs}

        wc = WordCloud(**kwargs)
        wc.generate_from_frequencies(data_dic)

        fig, ax = self.get_ax(ax)
        if imshow:
            im = ax.imshow(wc, **imshow)
        else:
            im = ax.imshow(wc)    
        ax.set_axis_off()

        return fig, ax, wc, im
    
    def get_ax(self, ax: Optional[Axes] = None) -> Tuple[Figure, Axes]:
        """
        Helper function to get or create a Matplotlib Figure and Axes object.

        Args:
            ax: An existing Matplotlib Axes object. 

        Returns:
            A tuple containing the figure and axes. If an Axes object is passed, the Axes and its figure will be returned. Otherwise, a new figure and Axes will be created.
        """
        if ax is None:
            fig = plt.figure(figsize=self.settings.figsize)
            ax = fig.add_subplot()
        else:
            fig = ax.get_figure()
        return fig, ax

class DataPlotter(DataAnalyzer):
    """DataPlotter extends DataAnalyzer to provide methods for visualizing data on imported modules.

    Methods:
        get_frequencies: Return frequency of imported modules.
        cloud_frequencies: Generate a word cloud plot of data frequencies.
        spiral_frequencies: Generate a spiral bar plot based on data frequencies.
    """

    def __init__(self, path: str, to_exclude : List[str] = None):
        """Initiate DataPlotter.
        
        Args:
            path: Path to the directory.
            to_exclude: List of packages' names to exclude from the analysis.
        """
        super().__init__(path, to_exclude=to_exclude)
        self.settings = PlotSettings() # setting shared by all plots
        """An instance of PlotSettings containing default plotting parameters."""

    def cloud_frequencies(self
                          , exclude: bool = True
                          , process_own_modules: bool = True
                          , defaults: bool = True
                          , ax: Optional[Axes] = None
                          , imshow: Optional[Dict[str, Any]] = None
                          , **kwargs: Any) -> Tuple[Figure, Axes, WordCloud, AxesImage]: 
        """Generate a word cloud plot of data frequencies.

        Args:
            exclude: Whether to exclude the packages listed in [to_exclude][ScanPyImports.plotter.DataPlotter.to_exclude].
            process_own_modules: Whether to process own-created modules.
            defaults: Whether to use default settings defined in [settings][ScanPyImports.plotter.DataPlotter.settings].
            ax: The axes to plot on. If None, a new figure and axes are created.
            imshow: Additional arguments to pass to the Matplotlib imshow method (see: [Axes.imshow][matplotlib.axes.Axes.imshow]).
            **kwargs: Additional keyword arguments passed to the WordCloud object (see: [wordcloud.WordCloud](https://amueller.github.io/word_cloud/generated/wordcloud.WordCloud.html#wordcloud.WordCloud))

        Returns:
            The figure, axe , WordCloud object, and image axe.
        """
        s = self.get_frequencies(exclude=exclude,
                                 process_own_modules=process_own_modules)

        cloud_plot = Cloud(self.settings)
        fig, ax, wc, im = cloud_plot.plot(data_dic=dict(s), defaults=defaults,
                               ax=ax, imshow=imshow, **kwargs)
        return fig, ax, wc, im 

    def spiral_frequencies(self, exclude: bool = True
                           , process_own_modules: bool = True
                           , top: Optional[int] = 25
                           , ax: Optional[Axes] = None
                           , zero_at: str = 'NE'
                           , defaults: bool = True
                           , label_padding: int = 2
                           , **kwargs: Any) -> Tuple[Figure, Axes, BarContainer, List[Text]]:
        """ 
        Generate a spiral bar plot based on data frequencies. 

        Args:
            exclude: Whether to exclude the packages listed in [to_exclude][ScanPyImports.plotter.DataPlotter.to_exclude].
            process_own_modules: Whether to process own-created modules.
            defaults: Whether to use default settings defined in [settings][ScanPyImports.plotter.DataPlotter.settings].
            ax: The axes to plot on. If None, a new figure and axes are created.
            top: Number of top most frequent modules to include. If None, all modules are included.
            zero_at: Zero location for theta. Default is 'NE', which means that the largest value will point North-East (NE). 
                Other possible values: 'N', 'S', 'SE', 'NW', and 'SW'.
            label_padding: Padding for the labels.
            **kwargs: Additional keyword arguments for the bar plot (see: [Axes.bar][matplotlib.axes.Axes.bar])

        Notes:
            The `ax` parameter, if passed, must be an instance of [**PolarAxes**][matplotlib.projections.polar.PolarAxes].

            When creating `ax`, you should pass `polar` as the projection argument. Here are two ways to achieve this:

            ```python
            from matplotlib import pyplot as plt

            # One way:
            fig = plt.figure()
            ax = fig.add_subplot(projection='polar')

            # Another way:
            fig, ax = plt.subplots(subplot_kw={'projection': 'polar'})
            ```


        Returns:
            The figure, axes, bars, and texts of the plot.
        """
        s = self.get_frequencies(exclude=exclude,
                                process_own_modules=process_own_modules)

        if top is not None:
            s = s[:top]

        s = s.sort_values()
        values = list(s.values)
        labels = list(s.index)

        spiral = Spiral(self.settings)
        fig, ax, bars, texts = spiral.plot(labels=labels, values=values,
                                            ax=ax, zero_at=zero_at, defaults=defaults,label_padding=label_padding, **kwargs)

        return fig, ax, bars, texts 

# if __name__ == '__main__':
 
#     path = r'D:\Dropbox\Python\My_packages\MultiInvaders'
#     # path = r'D:\Dropbox'
#     plot = DataPlotter(path)
#     fig, ax, wc, im = plot.cloud_frequencies()
#     fig.show()

#     fig, ax, bars, texts = plot.spiral_frequencies()
#     fig.show() 

