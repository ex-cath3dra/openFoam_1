import os
import sys
import numpy as np
import trimesh
from scipy.spatial import cKDTree
import subprocess

# ------------------------------------------------------------------
# STL Utility Module for Preprocessing FreeCAD Output for OpenFOAM
# Author: ChatGPT (OpenAI)
# Description: Convert STL formats, snap boundary vertices, and merge multiple STL files
# ------------------------------------------------------------------

def _check_virtualenv():
    if sys.prefix == sys.base_prefix:
        print("⚠️  WARNING: You are NOT running inside a virtual environment.")
        print("   Please activate your CFD virtual environment (e.g., `source ~/cfdenv/bin/activate`)")
        print("   or install required packages safely before proceeding.\n")

_check_virtualenv()

def bin2ascii(input_path: str, output_path: str = None, quiet: bool = False) -> str:
    if output_path is None:
        output_path = input_path

    with open(input_path, 'rb') as f:
        header = f.read(80)
        is_ascii = header.startswith(b'solid')

    if is_ascii:
        if not quiet:
            print(f"{input_path} is already ASCII.")
        return output_path

    mesh = trimesh.load(input_path)
    #try:
    #    mesh.export(output_path, file_type='stl', encoding='ascii')
    # except TypeError:
        # Fallback for older trimesh versions
    ascii_stl = trimesh.exchange.stl.export_stl_ascii(mesh)
    #, mode='ascii')
    with open(output_path, 'w') as f:
        f.write(ascii_stl)

    if not quiet:
        print(f"Converted {input_path} to ASCII as {output_path}.")

    surface_check(output_path, quiet=True)
    return output_path

def cleanBoundaries(primary_stl: str, reference_stl: str, output_path: str, tol: float = 5e-4, quiet: bool = False) -> str:
    """
    Snaps the boundary vertices of one STL to match another, to ensure watertight joins.

    Parameters:
    - primary_stl (str): Path to the STL whose vertices will be modified.
    - reference_stl (str): Path to the STL whose boundary vertices will be used as the reference.
    - output_path (str): Path to save the corrected STL.
    - tol (float): Tolerance within which to snap points.
    - quiet (bool): If True, suppresses print output.

    Returns:
    - str: Path to the updated ASCII STL file.
    """
    import trimesh
    from scipy.spatial import cKDTree
    import numpy as np

    def get_boundary_vertices(mesh):
        # Count occurrences of each edge
        edges_sorted = np.sort(mesh.edges_unique, axis=1)
        edges_flat = [tuple(edge) for edge in edges_sorted]
        edge_counts = {edge: 0 for edge in edges_flat}

        for face in mesh.faces:
            edges = [(face[i], face[(i + 1) % 3]) for i in range(3)]
            for a, b in edges:
                edge = tuple(sorted((a, b)))
                if edge in edge_counts:
                    edge_counts[edge] += 1
                else:
                    edge_counts[edge] = 1

        # Boundary edges occur only once
        boundary_edges = [edge for edge, count in edge_counts.items() if count == 1]
        boundary_vertices = np.unique(np.array(boundary_edges).flatten())
        return boundary_vertices

    mesh_primary = trimesh.load(primary_stl, force='mesh')
    mesh_reference = trimesh.load(reference_stl, force='mesh')

    boundary_vertices_primary = get_boundary_vertices(mesh_primary)
    points_primary = mesh_primary.vertices[boundary_vertices_primary]

    boundary_vertices_ref = get_boundary_vertices(mesh_reference)
    points_ref = mesh_reference.vertices[boundary_vertices_ref]

    tree = cKDTree(points_ref)
    matches = tree.query_ball_point(points_primary, tol)

    snap_count = 0
    for i, match in enumerate(matches):
        if match:
            original_idx = boundary_vertices_primary[i]
            mesh_primary.vertices[original_idx] = points_ref[match[0]]
            snap_count += 1

    #try:
    #    mesh_primary.export(output_path, file_type='stl', encoding='ascii')
    #except TypeError:
        # Fallback for older trimesh versions
    ascii_stl = trimesh.exchange.stl.export_stl_ascii(mesh_primary)
    #, mode='ascii')
    with open(output_path, 'w') as f:
        f.write(ascii_stl)


    if not quiet:
        print(f"Snapped {snap_count} boundary points from {primary_stl} to align with {reference_stl}.")
        print(f"Saved cleaned mesh to {output_path}.")

    return output_path


def mergeSTLs(stl_paths: list, region_names: list, output_path: str, quiet: bool = False) -> str:
    if len(stl_paths) != len(region_names):
        raise ValueError("Number of STL paths and region names must match.")

    with open(output_path, 'w') as out_file:
        for stl_path, region in zip(stl_paths, region_names):
            with open(stl_path, 'r') as part_file:
                lines = part_file.readlines()

            out_file.write(f"solid {region}\n")
            for line in lines:
                if line.strip().startswith("solid") or line.strip().startswith("endsolid"):
                    continue
                out_file.write(line)
            out_file.write(f"endsolid {region}\n")

    if not quiet:
        print(f"Merged {len(stl_paths)} STLs into {output_path} with regions: {region_names}")

    surface_check(output_path, quiet=True)
    return output_path

def surface_check(stl_path: str, quiet: bool = True):
    try:
        result = subprocess.run(['surfaceCheck', stl_path], capture_output=True, text=True)
        if result.returncode != 0:
            print(f"❌ surfaceCheck failed on {stl_path}:\n{result.stdout}")
        elif not quiet:
            print(f"✅ surfaceCheck passed on {stl_path}:\n{result.stdout}")
    except FileNotFoundError:
        if not quiet:
            print("⚠️  surfaceCheck command not found. Skipping mesh validation.")
