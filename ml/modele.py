from __future__ import annotations

import os

import mlflow
import mlflow.keras

from ml.data_preparation import prepare_datasets
from ml.model_preparation import build_lstm_model, prepare_training_tensors, train_and_evaluate


def run_training(window_size: int = 30, epochs: int = 200, batch_size: int = 32) -> dict[str, float]:
    dataset_train, dataset_test, features, target = prepare_datasets()

    X_train_seq, y_train_seq, X_test_seq, y_test_seq, scaler_y = prepare_training_tensors(
        dataset_train=dataset_train,
        dataset_test=dataset_test,
        features=features,
        target=target,
        window_size=window_size,
    )

    model = build_lstm_model(window_size=window_size, n_features=X_train_seq.shape[2])

    with mlflow.start_run(run_name="lstm_brest_consumption"):
        mlflow.log_params(
            {
                "window_size": window_size,
                "epochs": epochs,
                "batch_size": batch_size,
                "n_features": len(features),
            }
        )

        history, _, _, metrics = train_and_evaluate(
            model=model,
            X_train_seq=X_train_seq,
            y_train_seq=y_train_seq,
            X_test_seq=X_test_seq,
            y_test_seq=y_test_seq,
            scaler_y=scaler_y,
            epochs=epochs,
            batch_size=batch_size,
        )

        final_val_loss = history.history.get("val_loss", [None])[-1]
        if final_val_loss is not None:
            mlflow.log_metric("val_loss", final_val_loss)
        mlflow.log_metrics(metrics)
        mlflow.keras.log_model(model, artifact_path="model")

    return metrics


if __name__ == "__main__":
    tracking_uri = os.getenv("MLFLOW_TRACKING_URI", "http://127.0.0.1:5000")
    mlflow.set_tracking_uri(tracking_uri)
    mlflow.set_experiment("brest_consumption_forecast")

    scores = run_training()
    print("Training terminé. Metrics:", scores)
