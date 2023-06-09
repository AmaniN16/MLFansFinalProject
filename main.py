import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler, OrdinalEncoder
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.naive_bayes import GaussianNB
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report
from sklearn.decomposition import PCA
from imblearn.over_sampling import SMOTE
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.feature_selection import SelectKBest, chi2

# Load the dataset


df = pd.read_csv('D:/google download/as/train (version 2).csv')

# Split the dataset into training and testing sets
train_df, test_df = train_test_split(df, test_size=0.3, random_state=42)

# Check for missing values
print(df.isnull().sum())

# Check the data types
print(df.dtypes)

# Summary statistics
print(df.describe())

# Data visualization
sns.histplot(df['max_torque (Nm)'])
plt.title('Distribution of Max Torque')
plt.show()

sns.scatterplot(x='max_power (bhp)', y='gross_weight', data=df)
plt.title('Max Power vs Gross Weight')
plt.show()

sns.boxplot(x='airbags', y='is_claim', data=df)
plt.title('Airbags vs Insurance Claim')
plt.show()

# Correlation analysis
df_numeric = df.select_dtypes(include=['float64', 'int64'])
corr_matrix = df_numeric.corr()
sns.heatmap(corr_matrix, annot=True, cmap='coolwarm')
plt.title('Correlation Matrix')
plt.show()

cat_attribs = ['area_cluster', 'segment', 'model', 'fuel_type', 'engine_type', 'transmission_type',
               'rear_brakes_type', 'steering_type', 'is_speed_alert']

num_attribs = ['policy_tenure', 'age_of_car', 'age_of_policyholder', 'population_density', 'make',
               'max_torque (Nm)', 'rpm_max_torque', 'rpm_max_power', 'max_power (bhp)', 'airbags',
               'displacement', 'cylinder', 'gear_box', 'turning_radius', 'length', 'width', 'height', 'gross_weight',
               'is_esc', 'is_adjustable_steering', 'is_tpms', 'is_parking_sensors', 'is_parking_camera',
               'is_front_fog_lights', 'is_rear_window_wiper', 'is_rear_window_washer', 'is_rear_window_defogger',
               'is_brake_assist', 'is_power_door_locks', 'is_central_locking', 'is_power_steering',
               'is_driver_seat_height_adjustable',
               'is_day_night_rear_view_mirror', 'is_ecw', 'ncap_rating']

int_encoder = OrdinalEncoder()

num_pipeline = Pipeline([
    ('mm_scaler', MinMaxScaler()),
    ('pca', PCA(n_components=10))  # Feature extraction: adjust the number of components
])

full_pipeline = ColumnTransformer([
    ('num', num_pipeline, num_attribs),
    ('cat', int_encoder, cat_attribs)
])

X_train = full_pipeline.fit_transform(train_df.drop(['is_claim'], axis=1))
y_train = train_df['is_claim']
X_test = full_pipeline.transform(test_df.drop(['is_claim'], axis=1))
y_test = test_df['is_claim']

# X_train = train_df.drop(['is_claim'], axis=1)
# y_train = train_df['is_claim']
# X_test = test_df.drop(['is_claim'], axis=1)
# y_test = test_df['is_claim']

# Apply SMOTE to the training set
# To balance dataset:
smote = SMOTE(random_state=42)
X_train_resampled, y_train_resampled = smote.fit_resample(X_train, y_train.values.ravel())


# Train and test the models
models = [
    ('Logistic Regression', LogisticRegression(max_iter=5000)),
    ('Gradient Boosting', GradientBoostingClassifier(n_estimators=200, learning_rate=0.1, max_depth=3)),
    ('Naive Bayes', GaussianNB()),
    ('Random Forest', RandomForestClassifier()),                 # Random Forest always has the best performance;
    # ('Support Vector Machine', SVC(kernel='linear', shrinking=True, cache_size=50))     SVM is discarded because it's
    # not suitable for large dataset
]

for name, model in models:
    model.fit(X_train_resampled, y_train_resampled)
    y_pred = model.predict(X_test)

    # Save the predictions to a CSV file
    prediction_df = test_df.copy()
    prediction_df['predicted_claim'] = y_pred
    prediction_df.to_csv(f"{name}_predictions.csv", index=False)

    accuracy = accuracy_score(y_test, y_pred)
    cm = confusion_matrix(y_test, y_pred)
    print(f"{name} Accuracy: {accuracy}")
    print(f"{name} Confusion Matrix:\n {cm}")
    print(classification_report(y_test, y_pred, zero_division=1))
