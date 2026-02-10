from __future__ import annotations

import numpy as np
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.callbacks import EarlyStopping
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.models import Sequential


def create_sequences_for_multivariate(X: np.ndarray, y: np.ndarray, window_size: int) -> tuple[np.ndarray, np.ndarray]:
    X_seq, y_seq = [], []
    for i in range(window_size, len(X)):
        X_seq.append(X[i - window_size : i])
        y_seq.append(y[i])
    return np.array(X_seq), np.array(y_seq)


def prepare_training_tensors(
    dataset_train,
    dataset_test,
    features: list[str],
    target: str,
    window_size: int,
):
    scaler_x = MinMaxScaler(feature_range=(0, 1))
    scaler_y = MinMaxScaler(feature_range=(0, 1))

    X_train = dataset_train[features].values
    y_train = dataset_train[target].values
    X_test = dataset_test[features].values
    y_test = dataset_test[target].values

    X_train_scaled = scaler_x.fit_transform(X_train)
    X_test_scaled = scaler_x.transform(X_test)
    y_train_scaled = scaler_y.fit_transform(y_train.reshape(-1, 1))
    y_test_scaled = scaler_y.transform(y_test.reshape(-1, 1))

    X_train_seq, y_train_seq = create_sequences_for_multivariate(X_train_scaled, y_train_scaled, window_size)
    X_test_seq, y_test_seq = create_sequences_for_multivariate(X_test_scaled, y_test_scaled, window_size)

    return X_train_seq, y_train_seq, X_test_seq, y_test_seq, scaler_y


def build_lstm_model(window_size: int, n_features: int) -> Sequential:
    model = Sequential(
        [
            LSTM(50, activation="relu", input_shape=(window_size, n_features), return_sequences=False),
            Dropout(0.2),
            Dense(1),
        ]
    )
    model.compile(optimizer="adam", loss="mean_squared_error")
    return model


def train_and_evaluate(
    model: Sequential,
    X_train_seq: np.ndarray,
    y_train_seq: np.ndarray,
    X_test_seq: np.ndarray,
    y_test_seq: np.ndarray,
    scaler_y: MinMaxScaler,
    epochs: int,
    batch_size: int,
):
    early_stop = EarlyStopping(monitor="val_loss", patience=30, restore_best_weights=True)
    history = model.fit(
        X_train_seq,
        y_train_seq,
        epochs=epochs,
        batch_size=batch_size,
        validation_split=0.1,
        callbacks=[early_stop],
        verbose=1,
    )

    predictions_scaled = model.predict(X_test_seq)
    y_pred = scaler_y.inverse_transform(predictions_scaled)
    y_actual = scaler_y.inverse_transform(y_test_seq)

    mae = mean_absolute_error(y_actual, y_pred)
    rmse = np.sqrt(mean_squared_error(y_actual, y_pred))
    mape = np.mean(np.abs((y_actual - y_pred) / y_actual)) * 100

    return history, y_pred, y_actual, {"mae": mae, "rmse": rmse, "mape": mape}
