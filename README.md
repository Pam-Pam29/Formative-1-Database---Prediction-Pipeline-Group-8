# 🌾 Agricultural Crop Yield Prediction

**A Comparative Analysis of Traditional Machine Learning and Deep Learning Approaches**

---

## 📌 Project Overview

This project presents a comprehensive comparative study of traditional Machine Learning (ML) and Deep Learning (DL) models to predict agricultural crop yields using the Indian States Crop Yield Dataset (1997–2020). The research aims to contribute to food security planning and precision agriculture by building accurate, data-driven prediction models that can inform agricultural decision-making processes.

## 🎯 Objectives

- **Compare** traditional ML algorithms with DL architectures for crop yield prediction
- **Perform** systematic hyperparameter tuning and feature engineering
- **Identify** the most accurate and efficient model for prediction
- **Provide** actionable insights for practical agricultural decision-making

## 🧠 Models Implemented

### ✅ Traditional Machine Learning Models

| Model | Description |
|-------|-------------|
| **Linear Regression** | Baseline linear model for comparison |
| **Ridge & Lasso Regression** | Linear models with L2 and L1 regularization |
| **Elastic Net** | Linear model combining L1 and L2 regularization |
| **Decision Tree** | Non-parametric tree-based model |
| **Random Forest** | Ensemble of decision trees |
| **Gradient Boosting** | Sequential ensemble method |
| **Support Vector Regression** | Linear & RBF kernel-based models |
| **K-Nearest Neighbors** | Instance-based learning algorithm |

### 🤖 Deep Learning Models (TensorFlow)

| Model | Architecture | Description |
|-------|-------------|-------------|
| **Simple Feedforward** | 3 layers (128-64-32 neurons) | Basic neural network |
| **Deep Feedforward** | 6 layers + BatchNorm + Dropout | Advanced regularization |
| **Wide Deep Network** | Increasing width layers | Progressive complexity |
| **Functional API Model** | Multi-branch skip connections | Advanced architecture |
| **Regularized Model** | L1/L2 + Dropout | Comprehensive regularization |

## 📂 Dataset Information

**Dataset:** Indian States Crop Yield Dataset (1997–2020)  
**Total Records:** 19,689  
**Time Span:** 24 years of agricultural data  
**Geographic Coverage:** 30 Indian states and union territories  
**Crop Diversity:** 55 different crop types  

### Features Included:
- **Categorical:** Crop, State, Season
- **Numerical:** Area (hectares), Production (metric tons)
- **Environmental:** Annual Rainfall (mm)
- **Inputs:** Fertilizer & Pesticide usage (kg)
- **Target:** Yield (Production/Area)

## 🛠 Feature Engineering

### Engineered Features:
- **Efficiency Metrics:** `Fertilizer_per_Area`, `Pesticide_per_Area`, `Production_per_Area`
- **Categorical Binning:** Rainfall & Area categorization
- **Temporal Features:** Decade-based trends
- **Data Preprocessing:** OneHotEncoding for categorical data, StandardScaler for numerical features

## ⚙️ Methodology

1. **Data Cleaning & Visualization**
2. **Feature Engineering**
3. **Model Training & Validation** (80/20 train/test split)
4. **Hyperparameter Tuning** (RandomizedSearchCV with 5-fold cross-validation)
5. **Comprehensive Evaluation** using multiple metrics

### Evaluation Metrics:
- **R² Score** - Coefficient of determination
- **RMSE** - Root Mean Square Error
- **MAE** - Mean Absolute Error
- **Training Time** - Computational efficiency
- **Overfitting Analysis** - Generalization assessment

## 🏆 Results Summary

| Model Type | Best Model | R² Score | RMSE | Overfitting |
|------------|------------|----------|------|-------------|
| 🥇 **Deep Learning** | Simple Feedforward | **0.9953** | 61.15 | 0.0002 |
| 🥈 **Traditional ML** | Random Forest | **0.9946** | 66.01 | 0.0042 |

### Key Findings:
- ➡️ **Simple Feedforward Neural Network** outperformed all other models
- ➡️ **Well-engineered features** significantly boosted accuracy
- ➡️ **Complex DL architectures** performed worse than simpler models
- ➡️ **23+ systematic experiments** conducted with comprehensive analysis

## 📊 Key Visualizations

The main notebook includes comprehensive visualizations:

- **Data Distribution Analysis** - Yield patterns and correlations
- **Model Performance Comparison** - R² scores and RMSE analysis
- **Learning Curves** - Training/validation convergence patterns
- **Error Distribution Analysis** - Residual analysis and outlier detection
- **Feature Importance Rankings** - Interpretable model insights

## 💡 Key Insights

### ✅ Performance Insights:
- **Simpler neural networks** outperform complex architectures in agricultural datasets
- **Feature engineering** (especially resource efficiency metrics) significantly improves accuracy
- **Traditional ML models** like Random Forest remain valuable for interpretability and performance
- **Hyperparameter tuning** yields marginal improvements when the base model is already optimal

### ✅ Practical Applications:
- **Food Security Planning** - Accurate yield predictions for policy decisions
- **Resource Optimization** - Efficient allocation of fertilizers and pesticides
- **Agricultural Decision Support** - Data-driven farming recommendations
- **Climate Adaptation** - Understanding environmental factor impacts

## 🚧 Limitations & Future Work

### Current Limitations:
- **Geographic Scope:** Dataset limited to India (1997–2020) — may not generalize globally
- **Missing Variables:** No data on soil quality, pests, diseases, or real-time weather
- **Outlier Handling:** Extreme values underrepresented → higher error on outliers

### Future Enhancements:
- **Multi-region datasets** for global applicability
- **Real-time data integration** (weather stations, satellite imagery)
- **Advanced architectures** (CNNs for image data, LSTMs for temporal sequences)
- **Transfer learning** approaches for different crop types

## 📁 Project Structure

```
AgroYield/
├── Agroyield.ipynb          # Main analysis notebook
├── crop_yield.csv          # Dataset
├── README.md               # Project documentation
├── LICENSE                 # MIT License
└── .gitignore             # Git ignore file
```

## 🚀 Getting Started

1. **Clone the repository**
2. **Install dependencies:** `pip install pandas numpy matplotlib seaborn scikit-learn tensorflow`
3. **Run the notebook:** Open `Agroyield.ipynb` in Jupyter/Colab
4. **Execute cells sequentially** for complete analysis

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👨‍💻 Author

**Mugisha Samuel**  
