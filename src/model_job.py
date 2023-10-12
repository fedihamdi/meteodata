import xarray as xr
import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error
import joblib
from sklearn.preprocessing import StandardScaler

class PollenPredictionJob:
    def __init__(self, data_file, start_date, end_date):
        self.data_file = data_file
        self.start_date = start_date
        self.end_date = end_date

    def load_data(self):
        df = pd.read_csv(self.data_file)
        return df

    def explore_data(self, df):
        print(df.head(3))
        print(df.describe())

        numeric_vars = ['temperature', 'relative_humidity', 'co_conc', 'o3_conc', 'dust', 'pm10_conc']
        df[numeric_vars].hist(bins=20, figsize=(12, 8))
        plt.show()

        sns.boxplot(data=df[numeric_vars], orient='h')
        plt.show()

        plt.figure(figsize=(18, 9))
        correlation_matrix = df.loc[:, ~df.columns.isin(['time'])].corr()
        sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm')
        plt.show()

    def preprocess_data(self, df):
        X = df[['temperature', 'relative_humidity', 'chocho_conc', 'co_conc',
                'dust', 'ecres_conc', 'ectot_conc', 'hcho_conc', 'nh3_conc',
                'nmvoc_conc', 'no2_conc', 'no_conc', 'o3_conc', 'pans_conc',
                'pm10_conc', 'pm2p5_conc', 'pmwf_conc', 'sia_conc', 'so2_conc']]
        y = df['average_pollen_concentration']
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=123)
        return X_train, X_test, y_train, y_test

    def train_model(self, X_train, y_train):
        model_rf = RandomForestRegressor()
        model_rf.fit(X_train, y_train)
        return model_rf

    def evaluate_model(self, model, X_test, y_test):
        y_pred = model.predict(X_test)
        mae = mean_absolute_error(y_test, y_pred)
        rmse = mean_squared_error(y_test, y_pred, squared=False)
        return mae, rmse

    def center_and_scale(self, X_train, X_test):
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        return X_train_scaled, X_test_scaled

    def save_model(self, model, filename):
        joblib.dump(model, filename)

    def run(self):
        df = self.load_data()
        self.explore_data(df)
        X_train, X_test, y_train, y_test = self.preprocess_data(df)
        model = self.train_model(X_train, y_train)
        mae, rmse = self.evaluate_model(model, X_test, y_test)
        print("Mean Absolute Error:", mae)
        print("Root Mean Squared Error:", rmse)
        X_train_scaled, X_test_scaled = self.center_and_scale(X_train, X_test)
        model_filename = 'pollen_prediction_model.pkl'
        self.save_model(model, model_filename)

if __name__ == "__main__":
    data_file = 'data_file_2022-07-10.csv'
    start_date = '2022-07-10 00:00:00'
    end_date = '2022-07-11 00:00:00'

    pollen_job = PollenPredictionJob(data_file, start_date, end_date)
    pollen_job.run()
