from dataclasses import dataclass
from pathlib import Path
from typing import Literal, Optional, Callable

import matplotlib.pyplot as plt
import matplotlib as mpl
import matplotlib.colors as mcolors
from matplotlib.colors import LinearSegmentedColormap

AllowedImageType = Literal['jpg', 'png', 'eps', 'svg']

# blue - orange
high_contrast_colors = ['#90C9E6', '#269EBC', '#136784', '#023048', '#FFB702', '#FDA003', '#FB8502']

# red
red_gradient_colors = ['#F9E3D6', '#F4B498', '#DA6F5B', '#B42C34', '#6C0E20']

# purple
purple_gradient_colors = ['#FDF2EE', '#FDF2EE', '#FABFBE', '#F598B3', '#F0659F', '#DB3694', '#AD207F', '#7B2577', '#50226A']

# Color list
COLOR_LIST = purple_gradient_colors

def text_color_based_on_bgcolor(bg_color):
    """return proper text color based on background color
    """
    color = mcolors.to_rgb(bg_color)
    luminance = 0.299 * color[0] + 0.587 * color[1] + 0.114 * color[2]  
    return 'white' if luminance < 0.5 else 'black'

@dataclass
class PlotConfig:
    
    # image path
    image_name: str
    image_root_dir: Path            = Path('examples/plot')
    image_type: AllowedImageType    = 'png'
    @property
    def image_path(self) -> Path:
        return self.image_root_dir / f'{self.image_name}.{self.image_type}'
    
    # text
    text_size       : float         = 20
    text_color_func : Callable      = text_color_based_on_bgcolor
    text_color      : str           = 'black'
    
    # hex
    plot_style      : str           = 'bmh'
    hex_face_color  : str           = high_contrast_colors[-1]
    hex_edge_color  : str           = 'black'

    # figure
    figure_dpi      : float         = 300
    figure_size     : tuple[float]  = (15, 15)
    figure_expand   : float         = 0.1
    
    # axes
    axes_titlesize  : float         = 25
    axes_titleweight: str           = 'normal'
    axes_titley     : float         = 0.95
    
    @property
    def color_map(self):
        return LinearSegmentedColormap.from_list("my_cmap", COLOR_LIST)

    def set_plot_config(self):
        # picture style
        plt.style.use(self.plot_style)

        # rcParams
        rc = {
            'font.family'                   : 'Times New Roman',
            'mathtext.fontset'              : 'stix',
            'text.usetex'                   : True,
            'figure.dpi'                    : self.figure_dpi,
            'figure.figsize'                : self.figure_size,
            'axes.titlesize'                : self.axes_titlesize,
            'axes.titleweight'              : self.axes_titleweight,
            'axes.titley'                   : self.axes_titley
        }
        mpl.rcParams.update(rc)

