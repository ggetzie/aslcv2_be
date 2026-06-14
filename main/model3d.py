"""Helpers for locating, packaging, and measuring archaeological 3D models.

3D models for a context are stored under
``MEDIA_ROOT/{H}/{Z}/{E}/{N}/{C}/bottom/exports/obj`` and consist of sets of
three same-named files: a ``.obj`` mesh, a ``.mtl`` material, and a ``.jpg``
texture. This module resolves that folder, selects a model set, computes the
bounding-box center of the mesh, and packages the set into an in-memory zip.
"""

import io
import pathlib
import zipfile

from django.conf import settings

MODEL_SUBFOLDER = "bottom/exports/obj"

TEXTURE_EXTENSIONS = (".jpg", ".jpeg", ".png")

# Hard-coded site origins keyed by (easting, northing). Models will later be
# organized with respect to these origins. Sites not listed here return "NA".
SITE_ORIGINS = {
    (478130, 4419430): [129.4, -1066.24, 429.592],
}


def context_subroot(
    utm_hemisphere,
    utm_zone,
    area_utm_easting_meters,
    area_utm_northing_meters,
    context_number,
):
    """Build the ``{H}/{Z}/{E}/{N}/{C}`` subroot under MEDIA_ROOT for a context."""
    return (
        f"{utm_hemisphere}/"
        f"{utm_zone}/"
        f"{area_utm_easting_meters}/"
        f"{area_utm_northing_meters}/"
        f"{context_number}"
    )


def model_obj_folder(
    utm_hemisphere,
    utm_zone,
    area_utm_easting_meters,
    area_utm_northing_meters,
    context_number,
):
    """Return the absolute path to the folder holding a context's 3D models."""
    subroot = context_subroot(
        utm_hemisphere,
        utm_zone,
        area_utm_easting_meters,
        area_utm_northing_meters,
        context_number,
    )
    return pathlib.Path(settings.MEDIA_ROOT) / subroot / MODEL_SUBFOLDER


def list_obj_files(folder: pathlib.Path):
    """Return all ``.obj`` files in the folder (case-insensitive)."""
    if not folder.exists():
        return []
    return [
        f
        for f in folder.iterdir()
        if f.is_file() and f.suffix.lower() == ".obj"
    ]


def select_obj_file(folder: pathlib.Path):
    """Select the ``.obj`` to serve.

    When multiple model sets are present, the one with the lowest file size is
    used by default.
    """
    objs = list_obj_files(folder)
    if not objs:
        return None
    return min(objs, key=lambda p: p.stat().st_size)


def companion_files(obj_path: pathlib.Path):
    """Gather the files that make up a model set for the given ``.obj``.

    Files sharing the obj's stem (the ``.obj``, ``.mtl`` and texture) are given
    priority. If no same-stem material/texture exists, fall back to any
    ``.mtl``/texture present in the folder so the export is still usable.
    """
    folder = obj_path.parent
    stem = obj_path.stem
    files = [obj_path]

    same_stem = [
        f
        for f in folder.iterdir()
        if f.is_file() and f != obj_path and f.stem == stem
    ]
    files.extend(same_stem)

    have_mtl = any(f.suffix.lower() == ".mtl" for f in files)
    have_texture = any(f.suffix.lower() in TEXTURE_EXTENSIONS for f in files)

    if not have_mtl:
        for f in folder.iterdir():
            if f.is_file() and f.suffix.lower() == ".mtl":
                files.append(f)
                break
    if not have_texture:
        for f in folder.iterdir():
            if f.is_file() and f.suffix.lower() in TEXTURE_EXTENSIONS:
                files.append(f)
                break

    return files


def obj_bbox_center(obj_path: pathlib.Path, ndigits: int = 4):
    """Compute the bounding-box center of the mesh from the ``.obj`` vertices.

    Returns ``[cx, cy, cz]`` (midpoint of min/max on each axis) or ``None`` if
    the file contains no vertices.
    """
    min_x = min_y = min_z = float("inf")
    max_x = max_y = max_z = float("-inf")
    found = False

    with obj_path.open("r", errors="ignore") as fh:
        for line in fh:
            if not line.startswith("v "):
                continue
            parts = line.split()
            if len(parts) < 4:
                continue
            try:
                x, y, z = float(parts[1]), float(parts[2]), float(parts[3])
            except ValueError:
                continue
            found = True
            min_x, max_x = min(min_x, x), max(max_x, x)
            min_y, max_y = min(min_y, y), max(max_y, y)
            min_z, max_z = min(min_z, z), max(max_z, z)

    if not found:
        return None

    return [
        round((min_x + max_x) / 2, ndigits),
        round((min_y + max_y) / 2, ndigits),
        round((min_z + max_z) / 2, ndigits),
    ]


def model_zip_name(obj_path: pathlib.Path):
    """The zip is named to match the ``.obj`` (e.g. ``context1.obj`` -> ``context1.zip``)."""
    return f"{obj_path.stem}.zip"


def build_model_zip(obj_path: pathlib.Path):
    """Package the model set into an in-memory zip.

    Returns a tuple of ``(zip_bytes, zip_filename)``.
    """
    files = companion_files(obj_path)
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        for f in files:
            zf.write(f, arcname=f.name)
    buffer.seek(0)
    return buffer.getvalue(), model_zip_name(obj_path)


def get_site_origin(area_utm_easting_meters, area_utm_northing_meters):
    """Return the hard-coded origin for a site, or ``"NA"`` if not configured."""
    key = (int(area_utm_easting_meters), int(area_utm_northing_meters))
    return SITE_ORIGINS.get(key, "NA")
