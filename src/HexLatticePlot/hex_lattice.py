from typing import Optional, Literal, Callable
from dataclasses import dataclass

import matplotlib.pyplot as plt
from matplotlib.axes._axes import Axes
from matplotlib.patches import Polygon, Circle
from matplotlib.colors import Normalize
from matplotlib.cm import ScalarMappable
from matplotlib.colorbar import Colorbar
import numpy as np

from .coordinates import AbstractCoordinate, Coordinate, ValidDirections, CartesianCoordinate
from .plot_config import PlotConfig

@dataclass
class HexCell(Coordinate):
    
    def __init__(
            self, 
            centre_coord: AbstractCoordinate,
            radius: float           = 1 / np.sqrt(3),
            text:   Optional[str]   = None,
            value:  Optional[float] = None,
            real_cartesian: Optional[CartesianCoordinate] = None
        ) -> None:
        super().__init__(centre_coord)
        # 将输入的坐标系统一转为内部的 Coordinate，便于后续绘图使用
        self.centre         = Coordinate(centre_coord)
        # 半径控制单元大小（默认使边长为 1）
        self.radius         = radius
        # 文本/数值是可选信息，绘图时根据模式选择显示
        self.text           = text
        self.value          = value
        # real_cartesian 用于缩放后的真实坐标，未传入则使用自身的 cartesian
        self.real_cartesian = self.cartesian if real_cartesian is None else real_cartesian
    
    def get_neighbour(self, direction: ValidDirections) -> 'HexCell':
        # 邻居计算使用 axial 坐标系，逻辑更简洁
        neighbour_axial_coord = self.centre.axial.get_neighbour(direction)
        return HexCell(Coordinate(neighbour_axial_coord))
    
    @property
    def vertexes_pointy(self) -> list[tuple[float, float]]:
        # pointy-top 六边形的顶点角度：30° 起每 60° 一个点
        res_list = list()
        for angle in range(30, 360, 60):
            angle_rad = angle / 180 * np.pi
            x = self.real_cartesian.x + self.radius * np.cos(angle_rad)
            z = self.real_cartesian.y + self.radius * np.sin(angle_rad)
            res_list.append(CartesianCoordinate(x, z).as_tuple())
        return res_list
    
    def __rmul__(self, factor: float) -> 'HexCell':
        """
        HexCell is multiplied when it it used for HexLattice.
        """
        # 只缩放半径和真实坐标，不改变中心坐标/文本/数值
        return HexCell(self.centre, factor*self.radius, self.text, self.value, factor*self.real_cartesian)
    
    # valued in HexLattice Object
    ObjectRelatedCoordinate: Optional[tuple] = None
    
@dataclass
class HexLattice:
    
    def __init__(self, HexCells: list[HexCell], pitch: float = 1) -> None:
        self.pitch = pitch
        real_hex_cells: list[HexCell] = list()
        record = list()
        for hex_cell in HexCells:
            if hex_cell in record:
                continue
            else:
                record.append(hex_cell)
                
                # Only hex_cell.real_cartesian is changed when pitch multiply hex_cell
                real_hex_cells.append(pitch * hex_cell)
                
        self.HexCells = real_hex_cells
    
    @property
    def value_list(self) -> np.ndarray:
        # 将 None 统一视为 0，便于后续归一化与颜色映射
        hex_cell_value_list = [hex_cell.value for hex_cell in self.HexCells]
        if all(hex_cell_value is None for hex_cell_value in hex_cell_value_list):
            return np.array([0 for _ in hex_cell_value_list])
        else:
            return np.array([0 if hex_cell_value is None else hex_cell_value for hex_cell_value in hex_cell_value_list])
    
    @property
    def normed_value_list(self) -> np.ndarray:
        # 归一化到 [0, 1]，用于色图映射
        value_list = self.value_list
        value_min  = np.min(value_list)
        value_max  = np.max(value_list)
        return (value_list - value_min) / (value_max - value_min)
    
    def mappable(self, pc: PlotConfig) -> ScalarMappable:
        # 提供与当前数据匹配的色图对象，便于外部绘制 colorbar
        norm = Normalize(vmin=np.min(self.value_list), vmax=np.max(self.value_list))
        cmap = pc.color_map
        return ScalarMappable(norm, cmap)
        
    
    def assign_object_related_coordinates(self, assigner: Callable[[HexCell], tuple]):
        """
        Assigns a tuple to ObjectRelatedCoordinate of each HexCell using a provided function.

        Args:
            assigner (Callable[[HexCell], tuple]): Function to generate a tuple for each HexCell.
        """
        for cell in self.HexCells:
            cell.ObjectRelatedCoordinate = assigner(cell)

    def _setup_ax(self, pc: PlotConfig, ax: Optional[Axes]) -> Axes:
        # 统一设置画布与坐标系范围，避免每个绘图方法重复计算
        pc.set_plot_config()
        if ax is None:
            _, ax = plt.subplots(figsize=pc.figure_size, constrained_layout=pc.constrained_layout)
        elif pc.constrained_layout and pc.layout_mode == 'legacy':
            fig = ax.get_figure(root=True)
            if fig is not None:
                setter = getattr(fig, "set_constrained_layout", None)
                if callable(setter):
                    setter(True)
        all_x = [[v[0] for v in cell.vertexes_pointy] for cell in self.HexCells]
        all_z = [[v[1] for v in cell.vertexes_pointy] for cell in self.HexCells]
        ax.set_xlim((np.min(all_x) - pc.figure_expand, np.max(all_x) + pc.figure_expand))
        ax.set_ylim((np.min(all_z) - pc.figure_expand, np.max(all_z) + pc.figure_expand))
        ax.set_aspect('equal')
        ax.axis('off')
        return ax

    def _resolve_text_mode(self, requested: Optional[Literal['value', 'text']]) -> Literal['value', 'text']:
        # 若未指定模式，默认优先显示 text；全部为空则回退到 value
        if requested is None:
            return 'text' if all(cell.text is not None for cell in self.HexCells) else 'value'
        return requested

    def _build_style(self, index: int, cell: HexCell, pc: PlotConfig, text_mode: Literal['value', 'text']) -> tuple:
        # 样式计算与数据无关，集中在这里便于统一调整
        if text_mode == 'value':
            color = pc.color_map(self.normed_value_list[index])
            value = 0.0 if cell.value is None else cell.value
            label = f"{round(value, 2)}"
            text_color = pc.text_color_func(color)
        elif text_mode == 'text':
            color = pc.hex_face_color
            label = "" if cell.text is None else cell.text
            text_color = pc.text_color
        else:
            raise TypeError('Wrong Plot Type!')
        return color, label, text_color

    def _draw_cell(self, ax: Axes, cell: HexCell, patch, label: str, text_color, pc: PlotConfig) -> None:
        # 只做绘制，不关心颜色/文字如何计算
        ax.add_patch(patch)
        ax.text(
            cell.real_cartesian.x,
            cell.real_cartesian.y,
            label,
            ha='center',
            va='center',
            fontsize=pc.text_size,
            color=text_color,
            fontfamily=pc.font_family,
        )

    def _render(self, ax: Axes, pc: PlotConfig, shape_func: Callable, text_mode: Literal['value', 'text']) -> Axes:
        # 渲染流程统一封装：样式计算 -> patch 生成 -> 绘制
        for i, cell in enumerate(self.HexCells):
            facecolor, label, text_color = self._build_style(i, cell, pc, text_mode)
            patch = shape_func(cell, facecolor, pc.hex_edge_color)
            self._draw_cell(ax, cell, patch, label, text_color, pc)
        return ax

    def _shape_polygon(self, cell: HexCell, facecolor, edgecolor):
        # pointy-top 六边形 patch
        return Polygon(
            cell.vertexes_pointy,
            closed=True,
            facecolor=facecolor,
            edgecolor=edgecolor
        )

    def _shape_circle(self, cell: HexCell, facecolor, edgecolor):
        # 圆形 patch（半径按六边形内切圆等效）
        return Circle(
            cell.real_cartesian.as_tuple(),
            radius=cell.radius * np.sqrt(3) / 2,
            facecolor=facecolor,
            edgecolor=edgecolor
        )

    def plot(
        self,
        pc: PlotConfig,
        shape: Literal['hex', 'circle'] = 'hex',
        ax: Optional[Axes] = None,
        text_mode: Optional[Literal['value', 'text']] = None,
        colorbar: bool = False,
        colorbar_label: Optional[str] = None,
        colorbar_kwargs: Optional[dict] = None,
        save: bool = False,
        show: bool = False,
        close: bool = False,
    ) -> tuple[Axes, Optional[Colorbar]]:
        # 对外统一绘图入口：创建画布 -> 渲染 -> 可选色标/保存/展示
        title_ax: Optional[Axes] = None
        cbar_ax: Optional[Axes] = None

        if ax is None and pc.layout_mode == 'grid':
            fig = plt.figure(figsize=pc.figure_size)
            fig.subplots_adjust(
                left=pc.layout_left,
                right=pc.layout_right,
                bottom=pc.layout_bottom,
                top=pc.layout_top,
                wspace=pc.layout_wspace,
                hspace=pc.layout_hspace,
            )
            if colorbar:
                gs = fig.add_gridspec(
                    2,
                    2,
                    height_ratios=[pc.layout_title_ratio, 1.0],
                    width_ratios=[1.0, pc.layout_cbar_ratio],
                )
                title_ax = fig.add_subplot(gs[0, 0])
                ax = fig.add_subplot(gs[1, 0])
                cbar_ax = fig.add_subplot(gs[1, 1])
            else:
                gs = fig.add_gridspec(
                    2,
                    1,
                    height_ratios=[pc.layout_title_ratio, 1.0],
                )
                title_ax = fig.add_subplot(gs[0, 0])
                ax = fig.add_subplot(gs[1, 0])

        ax = self._setup_ax(pc, ax)
        mode = self._resolve_text_mode(text_mode)

        if shape == 'hex':
            shape_func = self._shape_polygon
        elif shape == 'circle':
            shape_func = self._shape_circle
        else:
            raise ValueError(f"Unknown shape '{shape}', expected 'hex' or 'circle'.")

        self._render(ax, pc, shape_func, mode)

        fig = ax.get_figure(root=True)
        if fig is None:
            raise RuntimeError("Cannot resolve Figure from axes; ax.get_figure() returned None.")
        if title_ax is not None:
            title_ax.set_axis_off()
            title_ax.text(
                0.0,
                1.0,
                pc.image_name,
                ha='left',
                va='top',
                fontsize=pc.axes_titlesize,
                fontweight=pc.axes_titleweight,
                wrap=pc.title_wrap,
                fontfamily=pc.font_family,
                transform=title_ax.transAxes,
            )
        else:
            ax.set_title(
                pc.image_name,
                loc='left',
                pad=pc.axes_titlepad,
                wrap=pc.title_wrap,
                fontfamily=pc.font_family,
            )
        cbar: Optional[Colorbar] = None
        if colorbar:
            cb_kwargs = {} if colorbar_kwargs is None else colorbar_kwargs
            if cbar_ax is None:
                cbar = fig.colorbar(self.mappable(pc), ax=ax, **cb_kwargs)
            else:
                cbar = fig.colorbar(self.mappable(pc), cax=cbar_ax, **cb_kwargs)
            cbar.ax.tick_params(labelsize=pc.cbar_tick_size)
            if colorbar_label:
                cbar.set_label(colorbar_label, fontsize=pc.cbar_label_size, fontfamily=pc.font_family)
            for tick_label in cbar.ax.get_yticklabels():
                tick_label.set_fontfamily(pc.font_family)

        if save:
            pc.image_path.parent.mkdir(parents=True, exist_ok=True)
            fig.savefig(pc.image_path)
        if show:
            plt.show()
        if close:
            plt.close(fig)

        return ax, cbar

    def plot_hex(self, pc: PlotConfig, ax: Optional[Axes] = None) -> Axes:
        text_mode = self._resolve_text_mode(None)
        ax, _ = self.plot(pc, shape='hex', ax=ax, text_mode=text_mode)
        return ax

    def plot_circle(self, pc: PlotConfig, ax: Optional[Axes] = None, plot_type: Literal['value', 'text'] = 'value') -> Axes:
        ax, _ = self.plot(pc, shape='circle', ax=ax, text_mode=plot_type)
        return ax

        
