import pandas as pd
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor, GradientBoostingRegressor, VotingRegressor
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.svm import SVR
from sklearn.metrics import classification_report, mean_squared_error, accuracy_score, r2_score, mean_absolute_error
from sklearn.feature_selection import SelectKBest, f_regression
import numpy as np
import joblib
import warnings
warnings.filterwarnings('ignore')

# 1. Enhanced Features & Targets
features = [
    'annual_rainfall_mm', 'max_daily_rainfall_mm', 'rainy_days_count',
    'avg_temperature_c', 'evaporation_rate_mmday',
    'clay_pct', 'sand_pct', 'silt_pct',
    'latitude', 'longitude', 'elevation_m',
    'roof_area_m2', 'available_space_m2', 'roof_type',
    'infiltration_rate_mmhr', 'runoff_coefficient', 'annual_runoff_m3'
]

# Additional derived features
derived_features = [
    'rainfall_intensity',  # max_daily_rainfall / rainy_days_count
    'soil_water_capacity',  # clay_pct * 0.4 + silt_pct * 0.3 + sand_pct * 0.1
    'roof_efficiency',  # roof_area_m2 / available_space_m2
    'climate_aridity',  # evaporation_rate_mmday / (annual_rainfall_mm / 365)
    'harvest_potential',  # annual_rainfall_mm * roof_area_m2 * runoff_coefficient / 1000
    'temperature_factor',  # avg_temperature_c / 30 (normalized)
    'elevation_factor',  # elevation_m / 1000 (normalized)
]

target_class = 'feasibility_category'
target_reg   = 'feasibility_score'
target_reco  = 'recommended_structure'

# 2. Load dataset
df = pd.read_csv("groundwater_recharge_feasibility_with_rowid.csv")
print(f"Dataset loaded: {df.shape[0]} rows, {df.shape[1]} columns")

# 3. Enhanced Preprocessing
print("Creating derived features...")

# Create derived features
df['rainfall_intensity'] = df['max_daily_rainfall_mm'] / (df['rainy_days_count'] + 1)
df['soil_water_capacity'] = df['clay_pct'] * 0.4 + df['silt_pct'] * 0.3 + df['sand_pct'] * 0.1
df['roof_efficiency'] = df['roof_area_m2'] / (df['available_space_m2'] + 1)
df['climate_aridity'] = df['evaporation_rate_mmday'] / ((df['annual_rainfall_mm'] / 365) + 0.1)
df['harvest_potential'] = df['annual_rainfall_mm'] * df['roof_area_m2'] * df['runoff_coefficient'] / 1000
df['temperature_factor'] = df['avg_temperature_c'] / 30
df['elevation_factor'] = df['elevation_m'] / 1000

# Combine original and derived features
all_features = features + derived_features

# Handle missing values - only for numeric columns
numeric_columns = df.select_dtypes(include=[np.number]).columns
df[numeric_columns] = df[numeric_columns].fillna(df[numeric_columns].median())

# One-hot encode categorical variables
X = pd.get_dummies(df[all_features], columns=['roof_type'])

# Feature scaling
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

print(f"Features after preprocessing: {X_scaled.shape[1]}")
print(f"Feature names: {list(X.columns)}")

# 4. Enhanced Classification - Feasibility Category
print("\n=== Training Feasibility Category Classifier ===")
y_class = df[target_class]
X_train, X_test, y_train, y_test = train_test_split(X_scaled, y_class, test_size=0.2, random_state=42)

# Hyperparameter tuning for classifier
clf_params = {
    'n_estimators': [100, 200, 300],
    'max_depth': [10, 20, None],
    'min_samples_split': [2, 5, 10]
}

clf = RandomForestClassifier(random_state=42)
clf_grid = GridSearchCV(clf, clf_params, cv=5, scoring='accuracy', n_jobs=-1)
clf_grid.fit(X_train, y_train)
clf = clf_grid.best_estimator_

y_pred_class = clf.predict(X_test)
print("Best Classifier Parameters:", clf_grid.best_params_)
print("Classification Report:\n", classification_report(y_test, y_pred_class))
print("Cross-validation Score:", cross_val_score(clf, X_scaled, y_class, cv=5).mean())

joblib.dump(clf, "feasibility_category_model.joblib")

# 5. Enhanced Regression - Feasibility Score
print("\n=== Training Feasibility Score Regressor ===")
y_reg = df[target_reg]
X_train, X_test, y_train, y_test = train_test_split(X_scaled, y_reg, test_size=0.2, random_state=42)

# Create ensemble regressor
rf_reg = RandomForestRegressor(n_estimators=200, max_depth=20, random_state=42)
gb_reg = GradientBoostingRegressor(n_estimators=200, learning_rate=0.1, random_state=42)
ridge_reg = Ridge(alpha=1.0)

# Voting regressor for better performance
reg = VotingRegressor([
    ('rf', rf_reg),
    ('gb', gb_reg),
    ('ridge', ridge_reg)
])

reg.fit(X_train, y_train)
y_pred_reg = reg.predict(X_test)

print("Regression RMSE:", np.sqrt(mean_squared_error(y_test, y_pred_reg)))
print("Regression R²:", r2_score(y_test, y_pred_reg))
print("Regression MAE:", mean_absolute_error(y_test, y_pred_reg))
print("Cross-validation Score:", cross_val_score(reg, X_scaled, y_reg, cv=5).mean())

joblib.dump(reg, "feasibility_score_model.joblib")

# 6. Enhanced Recommendation - Recommended Structure
print("\n=== Training Structure Recommender ===")
y_reco = df[target_reco]
X_train, X_test, y_train, y_test = train_test_split(X_scaled, y_reco, test_size=0.2, random_state=42)

# Hyperparameter tuning for recommender
reco_params = {
    'n_estimators': [100, 200],
    'max_depth': [10, 20, None],
    'min_samples_split': [2, 5]
}

reco = RandomForestClassifier(random_state=42)
reco_grid = GridSearchCV(reco, reco_params, cv=5, scoring='accuracy', n_jobs=-1)
reco_grid.fit(X_train, y_train)
reco = reco_grid.best_estimator_

y_pred_reco = reco.predict(X_test)
print("Best Recommender Parameters:", reco_grid.best_params_)
print("Recommendation Accuracy:", accuracy_score(y_test, y_pred_reco))
print("Cross-validation Score:", cross_val_score(reco, X_scaled, y_reco, cv=5).mean())

joblib.dump(reco, "recommended_structure_model.joblib")

# 7. Feature Selection and Importance
print("\n=== Feature Analysis ===")
feature_importance = pd.DataFrame({
    'feature': X.columns,
    'importance': clf.feature_importances_
}).sort_values('importance', ascending=False)

print("Top 10 Most Important Features:")
print(feature_importance.head(10))

# Save the scaler and columns for later use in prediction
joblib.dump(scaler, "scaler.joblib")
joblib.dump(X.columns.tolist(), "model_features.joblib")
joblib.dump(feature_importance, "feature_importance.joblib")

print("\n=== Model Training Complete ===")
print("All models saved successfully!")