# ECG Waveform Detection on LUDB

## Project stage

This repository contains an **intermediate version of the ECG peak detector I developed**. The notebook implements and evaluates that version on LUDB. The higher metrics on my résumé come from a later evaluation of my final method.

## Evaluation dataset

The Lobachevsky University Electrocardiography Database (LUDB) v1.0.1 is a publicly available dataset of 200 annotated 12-lead ECG recordings. This notebook evaluates the detector on Lead II from all 200 records using the dataset’s manual annotations. [PhysioNet LUDB v1.0.1](https://physionet.org/content/ludb/1.0.1/)

## Method

The notebook applies a 60 Hz notch and a 1–40 Hz Butterworth band-pass filter at 500 Hz, then resamples to 128 Hz for detection. It uses Engzee with an energy-based fallback and R-peak refinement, then locates P and T peaks in windows anchored to the detected beats. The detector returns P and T peaks directly from their search windows. Q and S candidates appear in the plot. Scoring covers P, R and T peaks.

## Intermediate results

The intermediate detector achieved the following results across all 200 records. Predictions are matched one-to-one to manual annotations using greedy nearest-distance matching with a radius of 38 samples (76 ms at 500 Hz). Scoring uses the span from the first to the last manual annotation, padded by 20 ms on each side.

| Peak | TP | FP | FN | Sensitivity | Precision | F1 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| P | 1,337 | 276 | 64 | 95.43% | 82.89% | 88.72% |
| R | 1,801 | 23 | 30 | 98.36% | 98.74% | 98.55% |
| T | 1,509 | 104 | 133 | 91.90% | 93.55% | 92.72% |

Removing the extra distance-to-R post-filter increased P-wave F1 from **59.39%** to **88.72%** on the full dataset.

The notebook also reports a legacy comparison cohort with 176 records for P and 199 for R and T. The full-cohort table above gives the primary result.

## Portfolio figures

A single-record comparison shows clinician annotations and detector output, with 18 matches, one false positive and one missed peak within ±75 ms. A separate unfiltered Lead II excerpt shows clinician annotations only. Displayed figures omit record numbers.

## Run the notebook

1. Install the dependencies with `python -m pip install -r requirements.txt`.
2. Run `jupyter lab`, open [the notebook](notebooks/ludb_intermediate_peak_detection.ipynb), and run all cells in order.
3. The notebook downloads LUDB from PhysioNet to a temporary directory if a local copy is unavailable. For an offline run, set `DATA_DIR` to the extracted LUDB `data` directory containing the WFDB records.
4. Change `example_record_id` to inspect the manual and predicted peaks for any record.

See PhysioNet for dataset documentation, attribution and licensing. [LUDB v1.0.1](https://physionet.org/content/ludb/1.0.1/)

The ECG project shows a preprocessed public LUDB Lead II excerpt with automatic peak annotations from my detector. [PhysioNet LUDB and Open Data Commons Attribution License](https://physionet.org/content/ludb/1.0.1/)
