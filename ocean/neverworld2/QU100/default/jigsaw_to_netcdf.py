from __future__ import absolute_import, division, print_function, \
    unicode_literals

import numpy as np

from netCDF4 import Dataset as NetCDFFile
from mpas_tools.mesh.creation.open_msh import readmsh
from mpas_tools.mesh.creation.util import circumcenter

import argparse


def jigsaw_to_netcdf(msh_filename, output_name, on_sphere, sphere_radius=None):
    """
    Converts mesh data defined in triangle format to NetCDF

    Parameters
    ----------
    msh_filename : str
        A JIGSAW mesh file name
    output_name: str
        The name of the output file
    on_sphere : bool
        Whether the mesh is spherical or planar
    sphere_radius : float, optional
        The radius of the sphere in meters.  If ``on_sphere=True`` this argument
        is required, otherwise it is ignored.
    """
    # Authors: Phillip J. Wolfram, Matthew Hoffman and Xylar Asay-Davis

    grid = NetCDFFile(output_name, 'w', format='NETCDF3_CLASSIC')

    # Get dimensions
    # Get nCells
    msh = readmsh(msh_filename)
    nCells = msh['POINT'].shape[0]

    # Get vertexDegree and nVertices
    vertexDegree = 3  # always triangles with JIGSAW output
    nVertices = msh['TRIA3'].shape[0]

    if vertexDegree != 3:
        ValueError("This script can only compute vertices with triangular "
                   "dual meshes currently.")

    grid.createDimension('nCells', nCells)
    grid.createDimension('nVertices', nVertices)
    grid.createDimension('vertexDegree', vertexDegree)

    # Create cell variables and sphere_radius
    xCell_full = msh['POINT'][:, 0]
    yCell_full = msh['POINT'][:, 1]
    zCell_full = msh['POINT'][:, 2]
    for cells in [xCell_full, yCell_full, zCell_full]:
        assert cells.shape[0] == nCells, 'Number of anticipated nodes is' \
                                         ' not correct!'
    if on_sphere:
        grid.on_a_sphere = "YES"
        grid.sphere_radius = sphere_radius
        # convert from km to meters
        xCell_full *= 1e3
        yCell_full *= 1e3
        zCell_full *= 1e3
    else:
        grid.on_a_sphere = "NO"
        grid.sphere_radius = 0.0

    # Create cellsOnVertex
    cellsOnVertex_full = msh['TRIA3'][:, :3] + 1
    assert cellsOnVertex_full.shape == (nVertices, vertexDegree), \
        'cellsOnVertex_full is not the right shape!'

    # Create vertex variables
    xVertex_full = np.zeros((nVertices,))
    yVertex_full = np.zeros((nVertices,))
    zVertex_full = np.zeros((nVertices,))

    for iVertex in np.arange(0, nVertices):
        cell1 = cellsOnVertex_full[iVertex, 0]
        cell2 = cellsOnVertex_full[iVertex, 1]
        cell3 = cellsOnVertex_full[iVertex, 2]

        x1 = xCell_full[cell1 - 1]
        y1 = yCell_full[cell1 - 1]
        z1 = zCell_full[cell1 - 1]
        x2 = xCell_full[cell2 - 1]
        y2 = yCell_full[cell2 - 1]
        z2 = zCell_full[cell2 - 1]
        x3 = xCell_full[cell3 - 1]
        y3 = yCell_full[cell3 - 1]
        z3 = zCell_full[cell3 - 1]

        pv = circumcenter(on_sphere, x1, y1, z1, x2, y2, z2, x3, y3, z3)
        xVertex_full[iVertex] = pv.x
        yVertex_full[iVertex] = pv.y
        zVertex_full[iVertex] = pv.z

    meshDensity_full = grid.createVariable(
        'meshDensity', 'f8', ('nCells',))

    for iCell in np.arange(0, nCells):
        meshDensity_full[iCell] = 1.0

    del meshDensity_full

    var = grid.createVariable('xCell', 'f8', ('nCells',))
    var[:] = xCell_full
    var = grid.createVariable('yCell', 'f8', ('nCells',))
    var[:] = yCell_full
    var = grid.createVariable('zCell', 'f8', ('nCells',))
    var[:] = zCell_full
    var = grid.createVariable('xVertex', 'f8', ('nVertices',))
    var[:] = xVertex_full
    var = grid.createVariable('yVertex', 'f8', ('nVertices',))
    var[:] = yVertex_full
    var = grid.createVariable('zVertex', 'f8', ('nVertices',))
    var[:] = zVertex_full
    var = grid.createVariable(
        'cellsOnVertex', 'i4', ('nVertices', 'vertexDegree',))
    var[:] = cellsOnVertex_full

    grid.sync()
    grid.close()


def main():
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument(
        "-m",
        "--msh",
        dest="msh",
        required=True,
        help="input .msh file generated by JIGSAW.",
        metavar="FILE")
    parser.add_argument(
        "-o",
        "--output",
        dest="output",
        default="grid.nc",
        help="output file name.",
        metavar="FILE")
    parser.add_argument(
        "-s",
        "--spherical",
        dest="spherical",
        action="store_true",
        default=False,
        help="Determines if the input/output should be spherical or not.")
    parser.add_argument(
        "-r",
        "--sphere_radius",
        dest="sphere_radius",
        type=float,
        help="The radius of the sphere in meters")

    args = parser.parse_args()

    jigsaw_to_netcdf(args.msh, args.output, args.spherical, args.sphere_radius)
