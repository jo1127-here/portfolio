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

An interactive synthetic example is available in the [portfolio](https://github.com/jo1127-here/portfolio/blob/main/index.html).
