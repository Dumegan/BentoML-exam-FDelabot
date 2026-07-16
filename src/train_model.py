"""Entraine un modele de regression lineaire et le sauvegarde dans BentoML."""

import bentoml
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

PROCESSED_DATA_DIR = "data/processed"
MODEL_NAME = "admission_lr"


def load_processed_data():
    X_train = pd.read_csv(f"{PROCESSED_DATA_DIR}/X_train.csv")
    X_test = pd.read_csv(f"{PROCESSED_DATA_DIR}/X_test.csv")
    y_train = pd.read_csv(f"{PROCESSED_DATA_DIR}/y_train.csv").squeeze()
    y_test = pd.read_csv(f"{PROCESSED_DATA_DIR}/y_test.csv").squeeze()
    return X_train, X_test, y_train, y_test


def train_model(X_train, y_train):
    model = LinearRegression()
    model.fit(X_train, y_train)
    return model


def evaluate_model(model, X_test, y_test):
    y_pred = model.predict(X_test)
    r2 = r2_score(y_test, y_pred)
    rmse = mean_squared_error(y_test, y_pred) ** 0.5
    mae = mean_absolute_error(y_test, y_pred)
    print(f"R2: {r2:.4f}")
    print(f"RMSE: {rmse:.4f}")
    print(f"MAE: {mae:.4f}")


if __name__ == "__main__":
    X_train, X_test, y_train, y_test = load_processed_data()

    model = train_model(X_train, y_train)
    evaluate_model(model, X_test, y_test)

    saved_model = bentoml.sklearn.save_model(MODEL_NAME, model)
    print("Modele sauvegarde dans le Model Store BentoML:", saved_model.tag)
