"""Unit tests for locating a context's 3D model set on disk.

Pure filesystem tests over a temp tree: no database, no live server, no real
model data. They cover the layouts seen on the server, where an export lands
either directly in ``bottom/exports`` or in a subfolder such as ``obj`` or
``obj-small``.
"""

import io
import pathlib
import zipfile

from main import model3d


def write_model_set(folder: pathlib.Path, stem: str, vertices=2, texture_bytes=100):
    """Write an obj/mtl/jpg trio into folder and return the path of the .obj."""
    folder.mkdir(parents=True, exist_ok=True)

    obj_path = folder / f"{stem}.obj"
    lines = [f"mtllib {stem}.mtl"]
    for i in range(vertices):
        lines.append(f"v {i}.0 {i * 2}.0 {i * 3}.0")
    obj_path.write_text("\n".join(lines) + "\n")

    (folder / f"{stem}.mtl").write_text(f"newmtl {stem}\nmap_Kd {stem}.jpg\n")
    (folder / f"{stem}.jpg").write_bytes(b"\xff" * texture_bytes)

    return obj_path


def test_obj_in_exports_root_is_found(tmp_path):
    expected = write_model_set(tmp_path, "context7")

    assert model3d.select_obj_file(tmp_path) == expected
    assert model3d.model_folder_label(expected, tmp_path) == "bottom/exports"


def test_obj_in_subfolder_is_found(tmp_path):
    """The reported bug: the only model set lives in exports/obj-small."""
    expected = write_model_set(tmp_path / "obj-small", "context7")

    selected = model3d.select_obj_file(tmp_path)

    assert selected == expected
    assert model3d.model_folder_label(selected, tmp_path) == (
        "bottom/exports/obj-small"
    )


def test_smallest_obj_wins_across_subfolders(tmp_path):
    write_model_set(tmp_path / "obj", "context7", vertices=50)
    expected = write_model_set(tmp_path / "obj-small", "context7", vertices=2)

    assert model3d.select_obj_file(tmp_path) == expected


def test_equal_sized_objs_break_the_tie_on_total_set_size(tmp_path):
    """Variants often share a byte-identical mesh; the lighter texture wins."""
    write_model_set(tmp_path / "obj", "context7", vertices=5, texture_bytes=5000)
    expected = write_model_set(
        tmp_path / "obj-small", "context7", vertices=5, texture_bytes=50
    )

    heavy = tmp_path / "obj" / "context7.obj"
    assert heavy.stat().st_size == expected.stat().st_size

    assert model3d.select_obj_file(tmp_path) == expected


def test_root_level_model_beats_subfolders(tmp_path):
    """A model set in exports itself is used even if a subfolder has a smaller one."""
    expected = write_model_set(tmp_path, "context7", vertices=50)
    write_model_set(tmp_path / "obj-small", "context7", vertices=2)

    assert model3d.select_obj_file(tmp_path) == expected


def test_deeply_nested_model_is_found(tmp_path):
    expected = write_model_set(tmp_path / "obj" / "v2", "context7")

    selected = model3d.select_obj_file(tmp_path)

    assert selected == expected
    assert model3d.model_folder_label(selected, tmp_path) == (
        "bottom/exports/obj/v2"
    )


def test_intermediate_folders_without_obj_are_skipped(tmp_path):
    """Sub-folders holding only loose material/texture files are not model sets."""
    stray = tmp_path / "textures"
    stray.mkdir()
    (stray / "atlas.jpg").write_bytes(b"\xff" * 10)
    expected = write_model_set(tmp_path / "obj-small", "context7")

    assert model3d.select_obj_file(tmp_path) == expected


def test_no_model_returns_none(tmp_path):
    """Empty and missing export roots both yield None, so the views 404."""
    assert model3d.select_obj_file(tmp_path) is None
    assert model3d.select_obj_file(tmp_path / "does-not-exist") is None


def test_search_stops_below_max_depth(tmp_path):
    too_deep = tmp_path
    for level in range(model3d.MAX_SEARCH_DEPTH + 1):
        too_deep = too_deep / f"level{level}"
    write_model_set(too_deep, "context7")

    assert model3d.select_obj_file(tmp_path) is None


def test_zip_contains_only_the_winning_folder(tmp_path):
    write_model_set(tmp_path / "obj", "context7", vertices=50, texture_bytes=5000)
    write_model_set(tmp_path / "obj-small", "context7-small", vertices=2)

    selected = model3d.select_obj_file(tmp_path)
    zip_bytes, zip_filename = model3d.build_model_zip(selected)

    assert zip_filename == "context7-small.zip"
    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as zf:
        names = sorted(zf.namelist())
    assert names == ["context7-small.jpg", "context7-small.mtl", "context7-small.obj"]


def test_bbox_center_of_selected_model(tmp_path):
    write_model_set(tmp_path / "obj-small", "context7", vertices=3)

    selected = model3d.select_obj_file(tmp_path)

    # vertices are (0,0,0), (1,2,3), (2,4,6)
    assert model3d.obj_bbox_center(selected) == [1.0, 2.0, 3.0]


def test_model_obj_folder_points_at_exports(settings, tmp_path):
    settings.MEDIA_ROOT = str(tmp_path)

    folder = model3d.model_obj_folder("N", 38, 478130, 4419430, 7)

    assert folder == tmp_path / "N/38/478130/4419430/7/bottom/exports"
