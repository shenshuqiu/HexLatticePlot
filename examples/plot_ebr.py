"""
Plot the axial distribution of power & nuclide density in EBR-II

@Author: LZK
@Date: 2023-6-6
"""
import os
import sys
package_path = os.path.dirname(os.getcwd())
sys.path.append(package_path)

from HexLattice import *

# MODE = "nodal_flux_162.26cm"
MODE = "zone_flux"
normalization_factor = 1.05484 / 1.07503

# Device compatibility
user_name = os.getlogin()
if user_name == '12247':
    dir_name = r'G:\Research\Research\Projects\LoongSARAXVerif'
else:
    dir_name = r'C:\SJTUGraduate\Research\Projects\LoongSARAXVerif'


if MODE == "nodal_flux_162.26cm":
    data_file_ver1 = r'data\EBRII-data\ver1_nodal_flux_distb_axisXY.csv'
    # data_file_ver2 = r'C:\SJTUGraduate\Research\Projects\LoongSARAXVerif\data\EBRII-data\ver2_nodal_flux_distb_axisXY.csv'
    data_file_ver2 = r'data\EBRII-data\ver2.5_nodal_flux_distb_axisXY.csv'
elif MODE == "zone_flux":
    data_file_ver1 = r'data\EBRII-data\ver1_nodal_flux_distb_SA.csv'
    data_file_ver2 = r'data\EBRII-data\ver2.5_nodal_flux_distb_SA.csv'

data_file_ver1 = os.path.join(dir_name, data_file_ver1)
data_file_ver2 = os.path.join(dir_name, data_file_ver2)


lattice = HexLattice(ring=16, pitch=5.8929)
lattice.genertate_lattice()
appender = RowAppender(lattice=lattice)

data_ver1 = list()
with open(data_file_ver1, 'r', encoding='utf-8') as data:
    data.readline()

    line_idx = 0
    cnt = 0
    for line in data.readlines():
        if MODE == "nodal_flux_162.26cm" and line_idx % 6 == 0:
            cnt += 1
            line_splited = line.split(',')
            # print(cnt, line_splited)
            material_id = int(line_splited[0])
            flux = normalization_factor * float(line_splited[1])
        
        if MODE == "zone_flux":
            cnt += 1
            line_splited = line.split(',')
            material_id = -1
            flux = normalization_factor * float(line_splited[0])

        data_ver1.append((material_id, flux))
        line_idx += 1

data_ver2 = list()
with open(data_file_ver2, 'r', encoding='utf-8') as data:
    data.readline()

    line_idx = 0
    cnt = 0
    for line in data.readlines():
        if MODE == "nodal_flux_162.26cm" and line_idx % 6 == 0:
            cnt += 1
            line_splited = line.split(',')
            # print(cnt, line_splited)
            material_id = int(line_splited[0])
            flux = normalization_factor * float(line_splited[1])
        
        if MODE == "zone_flux":
            cnt += 1
            line_splited = line.split(',')
            material_id = -1
            flux = normalization_factor * float(line_splited[0])

        data_ver2.append((material_id, flux))
        line_idx += 1

for cell_data_ver1, cell_data_ver2 in zip(data_ver1, data_ver2):
    material_id_ver1 = cell_data_ver1[0]
    material_id_ver2 = cell_data_ver2[0]
    flux_proportion = cell_data_ver2[1] / cell_data_ver1[1]
    
    # appender.append(
    #     key = 'material',
    #     value = material_id
    # )
    appender.append(
        key = 'flux_prop',
        value = flux_proportion
    )

# lattice.plot(
#     key = 'material',
#     save_path = 'plot/EBR-II/ver2_material.svg',
#     max_ring_idx = 8,
#     figsize = (8, 8),
#     dpi = 400
# )

lattice.plot_hex(
    key = 'flux_prop',
    save_path = 'plot/EBR-II/flux_zone_prop_v2.5.svg',
    max_ring_idx = 8,
    figsize = (11, 8),
    dpi = 400,
    color_map = 'jet'
)

