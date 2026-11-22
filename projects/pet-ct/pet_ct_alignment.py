"""PET/CT alignment walkthrough extracted from the project notebook.

Requires NumPy, pandas, SimpleITK, Matplotlib, IPython, and local imaging data.
Usage: python pet_ct_alignment.py /path/to/imaging-root
"""

import argparse
from pathlib import Path
import numpy as np
import pandas as pd
import SimpleITK as sitk
import matplotlib.pyplot as plt
from IPython.display import display


# ============================================================
# 1. CONFIGURATION
# ============================================================

parser = argparse.ArgumentParser(description="Display CT and lesion masks resampled to a PET grid.")
parser.add_argument("input_root", type=Path, help="Directory containing CT, PET, and SEG subdirectories")
INPUT_ROOT = parser.parse_args().input_root

CT_ROOT = INPUT_ROOT / "CT"
PET_ROOT = INPUT_ROOT / "PET"
SEG_ROOT = INPUT_ROOT / "SEG"

# Automatically select one patient with CT, PET and SEG.
patient_ids = sorted(
    {p.name for p in CT_ROOT.iterdir() if p.is_dir()}
    & {p.name for p in PET_ROOT.iterdir() if p.is_dir()}
    & {p.name for p in SEG_ROOT.iterdir() if p.is_dir()}
)

if not patient_ids:
    raise RuntimeError("No patients with all three modalities were found.")

PATIENT_ID = patient_ids[0]

# Alternatively, specify a patient:
# PATIENT_ID = "PETCT_XXXXXXXX"

ct_path = CT_ROOT / PATIENT_ID / "body_ct.nii.gz"
pet_path = PET_ROOT / PATIENT_ID / "body_suv.nii.gz"
seg_path = SEG_ROOT / PATIENT_ID / "body_seg.nii.gz"

for path in [ct_path, pet_path, seg_path]:
    if not path.exists():
        raise FileNotFoundError(path)




# ============================================================
# 2. HELPER FUNCTIONS
# ============================================================

def read_geometry(path):
    """
    Read image metadata without loading voxel data.

    PET serves as the reference coordinate system.
    """
    reader = sitk.ImageFileReader()
    reader.SetFileName(str(path))
    reader.ReadImageInformation()

    return {
        "size": tuple(reader.GetSize()),
        "spacing": tuple(reader.GetSpacing()),
        "origin": tuple(reader.GetOrigin()),
        "direction": tuple(reader.GetDirection())
    }


def geometry_matches(image, reference, atol=1e-5):
    """
    Compare physical image geometry.
    """
    return (
        image.GetSize() == reference["size"]
        and np.allclose(
            image.GetSpacing(),
            reference["spacing"],
            atol=atol,
            rtol=0
        )
        and np.allclose(
            image.GetOrigin(),
            reference["origin"],
            atol=atol,
            rtol=0
        )
        and np.allclose(
            image.GetDirection(),
            reference["direction"],
            atol=atol,
            rtol=0
        )
    )


def geometry_summary(name, image, reference):
    """
    Produce one row of the alignment validation table.
    """
    return {
        "Modality": name,
        "Size": str(image.GetSize()),
        "Spacing (mm)": str(
            tuple(round(x, 4) for x in image.GetSpacing())
        ),
        "Origin (mm)": str(
            tuple(round(x, 4) for x in image.GetOrigin())
        ),
        "Matches PET": geometry_matches(image, reference)
    }


def count_nonzero_binary(image):
    """
    Count positive segmentation voxels using SimpleITK.
    """
    stats = sitk.LabelShapeStatisticsImageFilter()
    stats.Execute(image)

    if stats.HasLabel(1):
        return int(stats.GetNumberOfPixels(1))

    return 0


# ============================================================
# 3. READ PET REFERENCE GEOMETRY
# ============================================================

pet_geometry = read_geometry(pet_path)

print("\nPET reference geometry:")
print("Size     :", pet_geometry["size"])
print("Spacing  :", pet_geometry["spacing"])
print("Origin   :", pet_geometry["origin"])
print("Direction:", pet_geometry["direction"])


# ============================================================
# 4. LOAD CT AND SEGMENTATION
# ============================================================

ct = sitk.ReadImage(str(ct_path))
seg = sitk.ReadImage(str(seg_path))

if ct.GetDimension() != 3:
    raise ValueError("CT must be a 3D image.")

if seg.GetDimension() != 3:
    raise ValueError("SEG must be a 3D image.")

print("\nOriginal geometry:")
print("CT size :", ct.GetSize())
print("SEG size:", seg.GetSize())


# ============================================================
# 5. RESAMPLE CT TO PET GRID
# ============================================================

# Identity transform is appropriate when CT and PET
# physical coordinates already share a common frame.
# Resampling is not equivalent to image registration.

identity = sitk.Transform(3, sitk.sitkIdentity)

ct_aligned = sitk.Resample(
    ct,
    pet_geometry["size"],
    identity,
    sitk.sitkLinear,
    pet_geometry["origin"],
    pet_geometry["spacing"],
    pet_geometry["direction"],
    -1024.0,
    sitk.sitkFloat32
)

if not geometry_matches(ct_aligned, pet_geometry):
    raise RuntimeError("CT alignment geometry mismatch.")


# ============================================================
# 6. RESAMPLE SEGMENTATION TO PET GRID
# ============================================================

# Convert all positive lesion labels to binary foreground.
seg_binary = sitk.Cast(seg > 0, sitk.sitkUInt8)

lesion_before = count_nonzero_binary(seg_binary)

seg_aligned = sitk.Resample(
    seg_binary,
    pet_geometry["size"],
    identity,
    sitk.sitkNearestNeighbor,
    pet_geometry["origin"],
    pet_geometry["spacing"],
    pet_geometry["direction"],
    0,
    sitk.sitkUInt8
)

lesion_after = count_nonzero_binary(seg_aligned)

if not geometry_matches(seg_aligned, pet_geometry):
    raise RuntimeError("SEG alignment geometry mismatch.")

if lesion_before > 0 and lesion_after == 0:
    raise RuntimeError(
        "Segmentation became empty after resampling."
    )


# ============================================================
# 7. VALIDATE ALIGNMENT
# ============================================================

geometry_table = pd.DataFrame([
    geometry_summary("CT original", ct, pet_geometry),
    geometry_summary("SEG original", seg, pet_geometry),
    geometry_summary("CT aligned", ct_aligned, pet_geometry),
    geometry_summary("SEG aligned", seg_aligned, pet_geometry)
])

print("\n=== Geometry Validation ===")
display(geometry_table)

print("\n=== Lesion Mask Validation ===")
print(f"Lesion voxels before: {lesion_before:,}")
print(f"Lesion voxels after : {lesion_after:,}")

print("\nCT matches PET :", geometry_matches(ct_aligned, pet_geometry))
print("SEG matches PET:", geometry_matches(seg_aligned, pet_geometry))


# ============================================================
# 8. LOAD PET FOR VISUALIZATION
# ============================================================

# PET voxel data is loaded only at this stage,
# after CT/SEG alignment and validation.
pet = sitk.ReadImage(str(pet_path))

if not geometry_matches(pet, pet_geometry):
    raise RuntimeError("PET geometry differs from its header.")

# SimpleITK array order: (z, y, x)
ct_array = sitk.GetArrayFromImage(ct_aligned)
pet_array = sitk.GetArrayFromImage(pet)
seg_array = sitk.GetArrayFromImage(seg_aligned)

if not (
    ct_array.shape == pet_array.shape == seg_array.shape
):
    raise RuntimeError("CT/PET/SEG array shapes differ.")


# ============================================================
# 9. SELECT AN AXIAL SLICE
# ============================================================

# Choose the slice with the largest segmented lesion area.
lesion_area = np.count_nonzero(
    seg_array,
    axis=(1, 2)
)

if lesion_area.max() > 0:
    z = int(np.argmax(lesion_area))
else:
    z = ct_array.shape[0] // 2

ct_slice = ct_array[z]
pet_slice = pet_array[z]
seg_slice = seg_array[z]

print(f"\nSelected axial slice: {z}")
print(f"Lesion pixels on slice: {lesion_area[z]}")


# ============================================================
# 10. PREPARE DISPLAY PARAMETERS
# ============================================================

# Soft-tissue CT window in Hounsfield units.
CT_MIN = -200
CT_MAX = 300

finite_pet = pet_slice[np.isfinite(pet_slice)]

PET_MAX = (
    max(1.0, float(np.percentile(finite_pet, 99)))
    if finite_pet.size
    else 1.0
)

# Mask zero values to make the overlay transparent.
seg_mask = np.ma.masked_where(
    seg_slice == 0,
    seg_slice
)

pet_overlay = np.ma.masked_where(
    ~np.isfinite(pet_slice) | (pet_slice <= 0),
    pet_slice
)


# ============================================================
# 11. VISUALIZATION — DISPLAY DIRECTLY IN JUPYTER
# ============================================================

fig, axes = plt.subplots(
    1, 4,
    figsize=(19, 5.5)
)

# ------------------------------------------------------------
# Panel A: Aligned CT
# ------------------------------------------------------------

axes[0].imshow(
    ct_slice,
    cmap="gray",
    vmin=CT_MIN,
    vmax=CT_MAX,
    origin="lower"
)

axes[0].set_title(
    "A. Aligned CT",
    fontsize=13
)


# ------------------------------------------------------------
# Panel B: PET SUV
# ------------------------------------------------------------

im_pet = axes[1].imshow(
    pet_slice,
    cmap="hot",
    vmin=0,
    vmax=PET_MAX,
    origin="lower"
)

axes[1].set_title(
    "B. PET SUV",
    fontsize=13
)

fig.colorbar(
    im_pet,
    ax=axes[1],
    fraction=0.046,
    pad=0.04,
    label="SUV"
)


# ------------------------------------------------------------
# Panel C: CT with lesion mask
# ------------------------------------------------------------

axes[2].imshow(
    ct_slice,
    cmap="gray",
    vmin=CT_MIN,
    vmax=CT_MAX,
    origin="lower"
)

axes[2].imshow(
    seg_mask,
    cmap="autumn",
    vmin=0,
    vmax=1,
    alpha=0.65,
    origin="lower"
)

axes[2].set_title(
    "C. CT + Segmentation",
    fontsize=13
)


# ------------------------------------------------------------
# Panel D: CT/PET fusion with lesion boundary
# ------------------------------------------------------------

axes[3].imshow(
    ct_slice,
    cmap="gray",
    vmin=CT_MIN,
    vmax=CT_MAX,
    origin="lower"
)

axes[3].imshow(
    pet_overlay,
    cmap="hot",
    vmin=0,
    vmax=PET_MAX,
    alpha=0.40,
    origin="lower"
)

if np.any(seg_slice):
    axes[3].contour(
        seg_slice,
        levels=[0.5],
        colors=["cyan"],
        linewidths=1.5,
        origin="lower"
    )

axes[3].set_title(
    "D. CT/PET Fusion + Lesion",
    fontsize=13
)


# ------------------------------------------------------------
# Formatting
# ------------------------------------------------------------

for ax in axes:
    ax.axis("off")

fig.suptitle(
    f"CT/PET Spatial Alignment "
    f"(Axial Slice {z})",
    fontsize=15,
    fontweight="bold"
)

fig.tight_layout()

plt.show()
