# PET/CT Spatial Alignment

A Python workflow for visualizing aligned CT, PET SUV, and lesion segmentation. The script uses SimpleITK to resample CT with linear interpolation and lesion labels with nearest-neighbor interpolation, using PET as the reference grid. It checks the output geometry and displays the axial slice with the largest segmented lesion area.

The workflow assumes that the input images share a physical coordinate frame.

## Run locally

Install the dependencies and pass a local imaging directory to the script.

```sh
pip install numpy pandas SimpleITK matplotlib ipython
python pet_ct_alignment.py /path/to/imaging-root
```

The input directory should have `CT`, `PET`, and `SEG` subdirectories, each containing the same case folder name. The expected filenames are `body_ct.nii.gz`, `body_suv.nii.gz`, and `body_seg.nii.gz`, respectively. The script selects the first case available across all three modalities.

## Segmentation evaluation

I ran nnU-Net and compared its lesion masks with clinician ground truth. The reported positive mean Dice was **61.69%**. This repository contains the PET/CT spatial alignment workflow. My nnU-Net training and inference code is not published here.
