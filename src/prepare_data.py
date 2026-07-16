"""Charge le CSV brut, le nettoie, et le divise en jeux d'entrainement/test."""

import pandas as pd
from sklearn.model_selection import train_test_split

RAW_DATA_PATH = "data/raw/admission.csv"
PROCESSED_DATA_DIR = "data/processed"

FEATURE_COLUMNS = [
    "GRE Score",
    "TOEFL Score",
    "University Rating",
    "SOP",
    "LOR",
    "CGPA",
    "Research",
]
TARGET_COLUMN = "Chance of Admit"


def load_data(path):
    df = pd.read_csv(path)
    df.columns = df.columns.str.strip()
    return df


def clean_data(df):
    df = df.drop(columns=["Serial No."])
    return df


def split_data(df):
    X = df[FEATURE_COLUMNS]
    y = df[TARGET_COLUMN]
    return train_test_split(X, y, test_size=0.2, random_state=42)


def save_data(X_train, X_test, y_train, y_test):
    X_train.to_csv(f"{PROCESSED_DATA_DIR}/X_train.csv", index=False)
    X_test.to_csv(f"{PROCESSED_DATA_DIR}/X_test.csv", index=False)
    y_train.to_csv(f"{PROCESSED_DATA_DIR}/y_train.csv", index=False)
    y_test.to_csv(f"{PROCESSED_DATA_DIR}/y_test.csv", index=False)


if __name__ == "__main__":
    df = load_data(RAW_DATA_PATH)
    df = clean_data(df)
    X_train, X_test, y_train, y_test = split_data(df)
    save_data(X_train, X_test, y_train, y_test)
    print("Donnees preparees et sauvegardees dans", PROCESSED_DATA_DIR)
    print("X_train:", X_train.shape, "X_test:", X_test.shape)
