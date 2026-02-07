# Deep-Neural-Market-Forecasting-Engine

An end-to-end real estate market analysis and forecasting engine for **Riyadh** and **Jeddah**. This project utilizes geospatial intelligence (Uber's H3) and is designed to evolve from statistical baselines into deep neural architectures.

## 🚀 Project Evolution
To maintain engineering rigor, this project follows a phased development roadmap. The "Neural Engine" is the target state, built upon validated geospatial and statistical foundations.

- **Phase 1 (Current):** Data Acquisition & Baseline Modeling (Linear Regression, ~0.64 R²).
- **Phase 2 (In-Progress):** Geospatial Feature Engineering (H3 Multi-resolution indexing).
- **Phase 3 (Upcoming):** Deep Neural Network (DNN) implementation for non-linear valuation.

## 📁 Repository Structure
```text
.
├── data/                    # Dataset management (GitIgnored)
├── docs/                    # Technical roadmap and documentation
├── notebooks/               # Exploratory Data Analysis & Cleaning
├── reports/                 
│   ├── figures/             # Model metrics and visualizations
│   └── interactive/         # Geospatial HTML maps
├── src/                     # Core Production Logic
│   ├── data/                # Scrapers and preprocessors
│   ├── models/              # Baseline and planned DNN models
│   └── visualization/       # Map builders and graphing utilities
├── requirements.txt         # Dependency list
└── README.md
```

## 📊 Core Features
- **Hybrid Cleaning:** Advanced outlier filtering using H3 geospatial resolution + room-based grouping.
- **Interactive Visualization:** Multi-layer maps with property-level markers and district-level heatmaps.
- **Baseline Model:** A validated Linear Regression regressor accounting for ~64% of price variance.

## 🛠️ Getting Started
1. **Clone & Install:**
   ```bash
   pip install -r requirements.txt
   ```
2. **Data Setup:** See [data/README.md](data/README.md) for instructions on where to place your local datasets.
3. **Execution:**
   - Run baseline training: `python src/models/baseline_regressor.py`
   - Generate maps: `python src/visualization/map_builder.py`

## 📜 License
This project is licensed under the MIT License.
