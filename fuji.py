# -*- coding: utf-8 -*-
"""Fuji.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1MjBn44pB_DvHBnyDUbbyQIDJcakL0czL
"""

from sqlite3 import DatabaseError
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.metrics import mean_absolute_percentage_error
from sklearn.multioutput import RegressorChain
from sklearn.svm import SVR
from catboost import CatBoostRegressor
from sklearn.ensemble import RandomForestRegressor
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np


# Load data
path = "Apple462.csv"
data = pd.read_csv(path)
data.head()

# Filter for Canada and avoid SettingWithCopyWarning by using .copy()
data['Date'] = pd.to_datetime(data['Date'], dayfirst=True)
data.set_index('Date', inplace=True)

# sort date
data.sort_index(inplace=True)

data_canada = data[data['region'] == 'Canada'].copy()  # Use .copy() to avoid SettingWithCopyWarning

# Convert columns to numeric dtype
data_canada[['Envi', 'Fuji', 'Gala']] = data_canada[['Envi', 'Fuji', 'Gala']].apply(pd.to_numeric, errors='coerce')

# Interpolate missing values for the 'Canada' region dataset
data_canada_interpolated = data_canada.interpolate()

# What type of Apple

Apple_type = "Fuji" #Change here

# Shift 'Fuji' column by one to get the target variable 'y'
data_canada_interpolated['y'] = data_canada_interpolated[Apple_type].shift(-1)

# Separate data set into a training and test set
train = data_canada_interpolated[:-156]
test = data_canada_interpolated[-156:-1]  # Exclude the last row

# Prepare data for Decision Tree regressor
X_train = train[[Apple_type]].values  # Features
y_train = train['y'].values  # Target variable
X_test = test[[Apple_type]].values

# Initialize the models
dt_reg = DecisionTreeRegressor(random_state=42)
gbr = GradientBoostingRegressor(random_state=42)
svr = SVR(kernel='rbf', C=1.0, epsilon=0.1)
cbr = CatBoostRegressor(verbose=0)
rfr = RandomForestRegressor(n_estimators=100, random_state=42)

# Fit the models
dt_reg.fit(X_train, y_train)
gbr.fit(X_train, y_train.ravel())
svr.fit(X_train, y_train)
cbr.fit(X_train, y_train)
rfr.fit(X_train, y_train)

# Make predictions
dt_pred = dt_reg.predict(X_test)
gbr_pred = gbr.predict(X_test)
svr_pred = svr.predict(X_test)
cbr_pred = cbr.predict(X_test)
rfr_pred = rfr.predict(X_test)

# Assign predictions to new columns in test
test['dt_pred'] = dt_pred
test['gbr_pred'] = gbr_pred
test['svr_pred'] = svr_pred
test['cbr_pred'] = cbr_pred
test['rfr_pred'] = rfr_pred
test['baseline_pred'] = test[Apple_type]

# Calculate MAPE for baseline, Decision Tree, and Gradient Boosting models
def mape(y_true, y_pred):
    return round(np.mean(np.abs((y_true - y_pred) / y_true)) * 100, 2)

baseline_mape = mape(test['y'], test['baseline_pred'])
dt_mape = mape(test['y'], test['dt_pred'])
gbr_mape = mape(test[Apple_type], test['gbr_pred'])
svr_mape = mape(test['y'], test['svr_pred'])
cbr_mape = mape(test['y'], test['cbr_pred'])
rfr_mape = mape(test['y'], test['rfr_pred'])

# Create bar graph
fig, ax = plt.subplots(figsize=(8, 5))

x = ['Baseline', 'Decision Tree', 'Gradient Boosting','SVR','CBR','RFR']
y = [round(baseline_mape,2), round(dt_mape,2), round(gbr_mape,2),round(svr_mape,2), round(cbr_mape,2) ,round(rfr_mape,2)]



ax.bar(x, y, width=0.4)
ax.set_xlabel('Regressor models')
ax.set_ylabel('MAPE (%)')
ax.set_ylim(0, 100)  # Adjusted ylim to make the differences more visible

# Add text labels to the bars
for index, value in enumerate(y):
    plt.text(x=index, y=value + 0.02, s=str(value), ha='center')

plt.tight_layout()

def window_input(window_length: int, data:pd.DataFrame) -> pd.DataFrame:
    df = data.copy()

    i = 1
    while i < window_length:
        df[f'x_{i}'] = df[Apple_type].shift(-i)
        i = i + 1

    if i == window_length:
        df[f'y'] = df[Apple_type].shift(-i)

    #Drop rows where there is a Nan
    df = df.dropna(axis=0)

    return df

def window_input_output(input_length: int, output_length: int, data:
    pd.DataFrame) -> pd.DataFrame:

    df = data.copy()

    i = 1
    while i<input_length:
        df[f'x_{i}'] = df[Apple_type].shift(-i)
        i = i + 1

    j = 0
    while j < output_length:
        df[f'y_{j}'] = df[Apple_type].shift(-output_length-j)
        j = j + 1

    df = df.dropna(axis=0)

    return df

seq_df = window_input_output(26,26,data_canada)
print(seq_df)

print(data_canada_interpolated.head())
print(test.head())

X_cols = [col for col in seq_df.columns if col.startswith('x')]

X_cols.insert(0, Apple_type)

y_cols = [col for col in seq_df.columns if col.startswith('y')]

X_train = seq_df[X_cols][:-2].values
y_train = seq_df[y_cols][:-2].values

X_test = seq_df[X_cols][-2:].values
y_test = seq_df[y_cols][-2:].values

dt_seq = DecisionTreeRegressor(random_state=42)
dt_seq.fit(X_train, y_train)
dt_seq_preds = dt_seq.predict(X_test)
dt_seq_preds.size

gbr_seq = GradientBoostingRegressor(random_state = 42)
chained_gbr = RegressorChain(gbr_seq)
chained_gbr.fit(X_train, y_train)
gbr_seq_preds = chained_gbr.predict(X_test)
gbr_seq_preds.size

svr_seq = SVR(kernel='rbf', C=1.0, epsilon=0.1)
chained_svr = RegressorChain(svr_seq)
chained_svr.fit(X_train, y_train)
svr_seq_preds = chained_svr.predict(X_test)
svr_seq_preds.size

cbr_seq = CatBoostRegressor(verbose=0)
chained_cbr = RegressorChain(cbr_seq)
chained_cbr.fit(X_train, y_train)
cbr_seq_preds = chained_cbr.predict(X_test)
cbr_seq_preds.size

rfr_seq = RandomForestRegressor(n_estimators=100, random_state=42)
chained_rfr = RegressorChain(rfr_seq)
chained_rfr.fit(X_train, y_train)
rfr_seq_preds = chained_rfr.predict(X_test)
rfr_seq_preds.size

mape_dt_seq = mape(dt_seq_preds.reshape(1, -1), y_test.reshape(1, -1))
mape_gbr_seq = mape(gbr_seq_preds.reshape(1, -1), y_test.reshape(1, -1))
mape_baseline = mape(X_test.reshape(1, -1), y_test.reshape(1, -1))
mape_cbr = mape(cbr_seq_preds.reshape(1, -1), y_test.reshape(1, -1))
mape_svr = mape(svr_seq_preds.reshape(1, -1), y_test.reshape(1, -1))
mape_rfr = mape(rfr_seq_preds.reshape(1, -1), y_test.reshape(1, -1))
#Generate the bar plot

fig, ax = plt.subplots(figsize=(10, 5))

x = ['Baseline', 'Decision Tree', 'Gradient Boosting','CatBoostRegressor','SVR','RandomForestRegressor']
y = [round(baseline_mape,2), round(dt_mape,2), round(gbr_mape,2),round(svr_mape,2), round(cbr_mape,2) ,round(rfr_mape,2)]

ax.bar(x, y, width=0.4)
ax.set_xlabel('Regressor models')
ax.set_ylabel('MAPE (%)')

ax.set_ylim(0, 100)

# Add text labels to the bars
for index, value in enumerate(y):
    plt.text(x=index, y=value + 0.05, s=str(value), ha='center')

plt.tight_layout()

fig, ax = plt.subplots(figsize=(16, 11))

ax.plot(np.arange(0, 26, 1), X_test[1], 'b-', label = 'input')
ax.plot(np.arange(26,52, 1), y_test[1], marker= '.', color = 'blue',
label = 'Actual')
ax.plot(np.arange(26, 52, 1), X_test[1], marker = 'o', color = 'red',
label = 'Baseline')
ax.plot(np.arange(26, 52, 1), dt_seq_preds[1], marker='^',
color='green',label = 'Decision Tree')
ax.plot(np.arange(26, 52, 1), gbr_seq_preds[1], marker='P',
color = 'black', label= 'Gradient Boosting')

ax.plot(np.arange(26, 52, 1), cbr_seq_preds[1], marker='*',
color = 'purple', label= 'CatBoostRegressor')

ax.plot(np.arange(26, 52, 1), svr_seq_preds[1], marker='x',
color = 'brown', label= 'SVR')

ax.plot(np.arange(26, 52, 1), rfr_seq_preds[1], marker='d',
color = 'cyan', label= 'RandomForestRegressor')

ax.set_xlabel('Year')
ax.set_ylabel(Apple_type)

plt.xticks(np.arange(1, 104, 52), np.arange(2015, 2020, 4))

plt.legend(loc =2)

fig.autofmt_xdate()
plt.tight_layout()