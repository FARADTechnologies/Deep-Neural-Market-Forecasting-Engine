# Data Directory

This folder contains the datasets used for the Deep-Neural-Market-Forecasting-Engine.

## Structure
- **raw/**: Contains the original scraped data from Bayut. (Excluded from Git)
- **processed/**: Contains the cleaned and filtered data ready for modeling. (Excluded from Git)

## Note on Privacy and Size
Large CSV and JSON files are excluded from this repository via `.gitignore` to maintain a clean and lightweight codebase. To run the analysis:
1. Place your scraped listings in `data/raw/`.
2. Run the cleaning notebooks in `notebooks/` to generate the processed datasets.
