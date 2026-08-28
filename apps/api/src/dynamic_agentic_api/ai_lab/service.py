from __future__ import annotations

import asyncio
import platform
import re
import time
from dataclasses import dataclass
from typing import Any

import numpy as np
import sklearn
import torch
from sklearn.cluster import KMeans
from sklearn.datasets import load_diabetes, load_iris
from sklearn.decomposition import PCA
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    mean_absolute_error,
    mean_squared_error,
    precision_score,
    r2_score,
    recall_score,
    silhouette_score,
)
from sklearn.model_selection import cross_val_score, train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.tree import DecisionTreeClassifier

from dynamic_agentic_api.config import Settings
from dynamic_agentic_api.errors import AppError

ALGORITHMS: dict[str, tuple[str, ...]] = {
    "data": ("profile",),
    "classical_ml": (
        "linear_regression",
        "logistic_regression",
        "decision_tree",
        "random_forest",
        "knn",
        "kmeans",
        "pca",
    ),
    "deep_learning": ("mlp",),
    "nlp": ("tfidf_logistic_regression",),
    "transformer": ("pretrained_inference",),
}


def _integer_parameter(value: object, default: int) -> int:
    if value is None:
        return default
    if isinstance(value, bool) or not isinstance(value, (int, float, str)):
        raise AppError(
            status_code=422,
            code="INVALID_EXPERIMENT_PARAMETER",
            message="Numeric experiment parameters must contain a valid integer.",
        )
    try:
        return int(value)
    except ValueError as exc:
        raise AppError(
            status_code=422,
            code="INVALID_EXPERIMENT_PARAMETER",
            message="Numeric experiment parameters must contain a valid integer.",
        ) from exc


@dataclass(frozen=True, slots=True)
class LabResult:
    metrics: dict[str, object]
    artifact_metadata: dict[str, object]
    library_versions: dict[str, object]


class AiLabService:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._semaphore = asyncio.Semaphore(settings.lab_max_concurrent_experiments)

    async def run(
        self,
        *,
        lab_type: str,
        algorithm: str,
        dataset: str,
        parameters: dict[str, object],
        seed: int,
    ) -> LabResult:
        if algorithm not in ALGORITHMS.get(lab_type, ()):
            raise AppError(
                status_code=422,
                code="UNSUPPORTED_EXPERIMENT",
                message="The selected lab algorithm is not allowlisted.",
            )
        rows = _integer_parameter(parameters.get("max_rows"), 500)
        if rows < 20 or rows > self._settings.lab_max_dataset_rows:
            raise AppError(
                status_code=422,
                code="LAB_DATASET_LIMIT_EXCEEDED",
                message="The requested dataset size exceeds the AI Lab limit.",
            )
        epochs = _integer_parameter(parameters.get("epochs"), 12)
        if epochs < 1 or epochs > self._settings.lab_max_epochs:
            raise AppError(
                status_code=422,
                code="LAB_EPOCH_LIMIT_EXCEEDED",
                message="The requested epoch count exceeds the AI Lab limit.",
            )
        async with self._semaphore:
            try:
                async with asyncio.timeout(self._settings.lab_max_runtime_seconds):
                    result = await asyncio.to_thread(
                        self._run_sync,
                        lab_type,
                        algorithm,
                        dataset,
                        parameters,
                        seed,
                        rows,
                        epochs,
                    )
            except TimeoutError as exc:
                raise AppError(
                    status_code=408,
                    code="LAB_RUNTIME_LIMIT_EXCEEDED",
                    message="The experiment exceeded the configured runtime limit.",
                ) from exc
        return result

    def _run_sync(
        self,
        lab_type: str,
        algorithm: str,
        dataset: str,
        parameters: dict[str, object],
        seed: int,
        rows: int,
        epochs: int,
    ) -> LabResult:
        started = time.perf_counter()
        if lab_type == "data":
            metrics = self._data_lab(seed, rows)
        elif lab_type == "classical_ml":
            metrics = self._classical(algorithm, seed, rows, parameters)
        elif lab_type == "deep_learning":
            metrics = self._deep_learning(seed, epochs)
        elif lab_type == "nlp":
            metrics = self._nlp(seed)
        else:
            metrics = self._transformer(str(parameters.get("text", "AI systems require evidence.")))
        metrics["experiment_duration_ms"] = round((time.perf_counter() - started) * 1000)
        metrics["educational_explanation"] = self._explanation(algorithm)
        return LabResult(
            metrics=self._json(metrics),
            artifact_metadata={
                "storage": "none",
                "dataset_isolated": True,
                "production_state_mutated": False,
            },
            library_versions={
                "python": platform.python_version(),
                "numpy": np.__version__,
                "scikit_learn": sklearn.__version__,
                "torch": torch.__version__,
            },
        )

    @staticmethod
    def _data_lab(seed: int, rows: int) -> dict[str, object]:
        rng = np.random.default_rng(seed)
        capped = min(rows, 500)
        numeric = rng.normal(50, 12, size=(capped, 3))
        numeric[1, 1] = np.nan
        numeric[-1] = numeric[0]
        categories = np.array(["north", "south", "west"])[np.arange(capped) % 3]
        imputed = SimpleImputer(strategy="mean").fit_transform(numeric)
        standardized = StandardScaler().fit_transform(imputed)
        train, test = train_test_split(standardized, test_size=0.2, random_state=seed)
        return {
            "row_count": capped,
            "feature_types": {"numeric": 3, "categorical": 1},
            "missing_values": int(np.isnan(numeric).sum()),
            "duplicate_rows": 1,
            "descriptive_statistics": {
                "mean": np.nanmean(numeric, axis=0).round(4).tolist(),
                "standard_deviation": np.nanstd(numeric, axis=0).round(4).tolist(),
                "minimum": np.nanmin(numeric, axis=0).round(4).tolist(),
                "maximum": np.nanmax(numeric, axis=0).round(4).tolist(),
            },
            "preview": [
                {
                    "features": [
                        None if np.isnan(value) else round(float(value), 3) for value in row
                    ],
                    "region": str(categories[index]),
                }
                for index, row in enumerate(numeric[:5])
            ],
            "preprocessing": ["mean_imputation", "standardization", "categorical_index_encoding"],
            "category_mapping": {name: index for index, name in enumerate(sorted(set(categories)))},
            "train_rows": len(train),
            "test_rows": len(test),
        }

    @staticmethod
    def _classical(
        algorithm: str, seed: int, rows: int, parameters: dict[str, object]
    ) -> dict[str, object]:
        if algorithm == "linear_regression":
            data = load_diabetes()
            x, y = data.data[:rows], data.target[:rows]
            x_train, x_test, y_train, y_test = train_test_split(
                x, y, test_size=0.2, random_state=seed
            )
            model = LinearRegression().fit(x_train, y_train)
            predicted = model.predict(x_test)
            mse = mean_squared_error(y_test, predicted)
            return {
                "mae": mean_absolute_error(y_test, predicted),
                "mse": mse,
                "rmse": float(np.sqrt(mse)),
                "r2": r2_score(y_test, predicted),
                "train_rows": len(x_train),
                "test_rows": len(x_test),
            }
        iris = load_iris()
        x, y = iris.data[:rows], iris.target[:rows]
        if algorithm == "kmeans":
            scaled = StandardScaler().fit_transform(x)
            clusters = _integer_parameter(parameters.get("clusters"), 3)
            if clusters < 2 or clusters > 8 or clusters >= len(x):
                raise AppError(
                    status_code=422,
                    code="INVALID_CLUSTER_COUNT",
                    message="The cluster count is outside the safe range.",
                )
            model = KMeans(n_clusters=clusters, random_state=seed, n_init=10).fit(scaled)
            return {
                "inertia": model.inertia_,
                "silhouette_score": silhouette_score(scaled, model.labels_),
                "cluster_counts": np.bincount(model.labels_).tolist(),
            }
        if algorithm == "pca":
            scaled = StandardScaler().fit_transform(x)
            components = min(_integer_parameter(parameters.get("components"), 2), x.shape[1])
            model = PCA(n_components=components, random_state=seed).fit(scaled)
            variance = model.explained_variance_ratio_
            return {
                "explained_variance": variance.tolist(),
                "cumulative_explained_variance": np.cumsum(variance).tolist(),
                "components": components,
            }
        models: dict[str, Any] = {
            "logistic_regression": LogisticRegression(max_iter=300, random_state=seed),
            "decision_tree": DecisionTreeClassifier(
                max_depth=_integer_parameter(parameters.get("max_depth"), 4),
                random_state=seed,
            ),
            "random_forest": RandomForestClassifier(
                n_estimators=min(_integer_parameter(parameters.get("estimators"), 50), 100),
                random_state=seed,
            ),
            "knn": KNeighborsClassifier(
                n_neighbors=min(_integer_parameter(parameters.get("neighbors"), 5), 15)
            ),
        }
        model = make_pipeline(StandardScaler(), models[algorithm])
        x_train, x_test, y_train, y_test = train_test_split(
            x, y, test_size=0.2, random_state=seed, stratify=y
        )
        model.fit(x_train, y_train)
        predicted = model.predict(x_test)
        cross_validation = cross_val_score(model, x, y, cv=3, scoring="accuracy")
        comparison: list[dict[str, float | int]] = []
        if algorithm == "decision_tree":
            for depth in (2, 4, 6):
                candidate = DecisionTreeClassifier(max_depth=depth, random_state=seed)
                scores = cross_val_score(candidate, x, y, cv=3, scoring="accuracy")
                comparison.append({"max_depth": depth, "cv_accuracy": float(scores.mean())})
        elif algorithm == "knn":
            for neighbors in (3, 5, 9):
                candidate = make_pipeline(
                    StandardScaler(), KNeighborsClassifier(n_neighbors=neighbors)
                )
                scores = cross_val_score(candidate, x, y, cv=3, scoring="accuracy")
                comparison.append({"neighbors": neighbors, "cv_accuracy": float(scores.mean())})
        return {
            "accuracy": accuracy_score(y_test, predicted),
            "precision": precision_score(y_test, predicted, average="macro", zero_division=0),
            "recall": recall_score(y_test, predicted, average="macro", zero_division=0),
            "f1": f1_score(y_test, predicted, average="macro", zero_division=0),
            "confusion_matrix": confusion_matrix(y_test, predicted).tolist(),
            "cross_validation_accuracy": cross_validation.tolist(),
            "cross_validation_mean": cross_validation.mean(),
            "hyperparameter_comparison": comparison,
        }

    @staticmethod
    def _deep_learning(seed: int, epochs: int) -> dict[str, object]:
        torch.manual_seed(seed)
        np.random.seed(seed)
        iris = load_iris()
        x_train, x_validation, y_train, y_validation = train_test_split(
            iris.data.astype("float32"),
            iris.target.astype("int64"),
            test_size=0.2,
            random_state=seed,
            stratify=iris.target,
        )
        scaler = StandardScaler().fit(x_train)
        train_x = torch.tensor(scaler.transform(x_train), dtype=torch.float32)
        validation_x = torch.tensor(scaler.transform(x_validation), dtype=torch.float32)
        train_y = torch.tensor(y_train, dtype=torch.long)
        validation_y = torch.tensor(y_validation, dtype=torch.long)
        model = torch.nn.Sequential(
            torch.nn.Linear(4, 12),
            torch.nn.ReLU(),
            torch.nn.Dropout(0.15),
            torch.nn.Linear(12, 3),
        )
        optimizer = torch.optim.Adam(model.parameters(), lr=0.02, weight_decay=0.0005)
        loss_function = torch.nn.CrossEntropyLoss()
        losses: list[float] = []
        batch_size = 16
        for _ in range(epochs):
            model.train()
            epoch_losses: list[float] = []
            for start in range(0, len(train_x), batch_size):
                optimizer.zero_grad()
                output = model(train_x[start : start + batch_size])
                loss = loss_function(output, train_y[start : start + batch_size])
                loss.backward()
                optimizer.step()
                epoch_losses.append(float(loss.detach()))
            losses.append(float(np.mean(epoch_losses)))
        model.eval()
        with torch.no_grad():
            validation_output = model(validation_x)
            validation_loss = float(loss_function(validation_output, validation_y))
            accuracy = float((validation_output.argmax(dim=1) == validation_y).float().mean())
        return {
            "epochs": epochs,
            "batch_size": batch_size,
            "training_loss": losses,
            "validation_loss": validation_loss,
            "validation_accuracy": accuracy,
            "activation": "ReLU",
            "optimizer": "Adam",
            "regularization": ["dropout", "weight_decay"],
        }

    @staticmethod
    def _nlp(seed: int) -> dict[str, object]:

        texts = [
            "excellent reliable service",
            "helpful fast response",
            "great product quality",
            "accurate and friendly support",
            "terrible delayed service",
            "poor broken product",
            "unhelpful slow response",
            "bad quality and errors",
            "reliable friendly team",
            "excellent accurate answer",
            "delayed broken order",
            "poor unhelpful support",
        ]
        labels = np.array([1, 1, 1, 1, 0, 0, 0, 0, 1, 1, 0, 0])
        train_text, test_text, train_y, test_y = train_test_split(
            texts, labels, test_size=0.33, random_state=seed, stratify=labels
        )
        vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2), max_features=100)
        train_x = vectorizer.fit_transform(train_text)
        test_x = vectorizer.transform(test_text)
        model = LogisticRegression(random_state=seed).fit(train_x, train_y)
        predicted = model.predict(test_x)
        sample = "Reliable support resolved the customer issue quickly."
        tokens = re.findall(r"[a-z]+", sample.casefold())
        return {
            "accuracy": accuracy_score(test_y, predicted),
            "f1": f1_score(test_y, predicted, zero_division=0),
            "vocabulary_size": len(vectorizer.vocabulary_),
            "tokenization_sample": tokens,
            "normalized_sample": " ".join(tokens),
            "ngrams": [1, 2],
            "stop_words": "english",
            "entity_token_analysis": {
                "capitalized_entities": ["Reliable"],
                "token_count": len(tokens),
            },
            "embedding_comparison": (
                "TF-IDF is sparse and corpus-specific; neural embeddings are dense and contextual."
            ),
        }

    def _transformer(self, text: str) -> dict[str, object]:
        try:
            from transformers import AutoModel, AutoTokenizer

            tokenizer = AutoTokenizer.from_pretrained(
                self._settings.transformer_model,
                local_files_only=not self._settings.transformer_allow_download,
            )
            model = AutoModel.from_pretrained(
                self._settings.transformer_model,
                local_files_only=not self._settings.transformer_allow_download,
            )
            encoded = tokenizer(text[:500], return_tensors="pt", truncation=True, max_length=128)
            with torch.no_grad():
                output = model(**encoded)
            representation = output.last_hidden_state.mean(dim=1)[0]
            return {
                "available": True,
                "model": self._settings.transformer_model,
                "tokens": tokenizer.convert_ids_to_tokens(encoded["input_ids"][0]),
                "token_ids": encoded["input_ids"][0].tolist(),
                "attention_mask": encoded["attention_mask"][0].tolist(),
                "embedding_dimension": int(representation.shape[0]),
                "embedding_preview": representation[:8].tolist(),
                "mode": "pretrained_inference_only",
            }
        except Exception:
            return {
                "available": False,
                "model": self._settings.transformer_model,
                "reason": "The optional pretrained model is not cached or currently available.",
                "mode": "pretrained_inference_not_run",
            }

    @staticmethod
    def _explanation(algorithm: str) -> str:
        return {
            "profile": (
                "Data profiling finds missing values, duplicates, feature types, and "
                "scale differences before modeling."
            ),
            "linear_regression": (
                "Linear regression estimates a continuous target; MAE and RMSE "
                "measure prediction error."
            ),
            "logistic_regression": (
                "Logistic regression estimates class probabilities. F1 balances "
                "precision and recall."
            ),
            "decision_tree": (
                "A decision tree learns interpretable feature splits but can overfit "
                "without depth limits."
            ),
            "random_forest": (
                "A random forest averages many trees to reduce variance and improve robustness."
            ),
            "knn": (
                "KNN classifies from nearby training examples and is sensitive to feature scale."
            ),
            "kmeans": (
                "K-Means is unsupervised; silhouette score measures cluster separation when valid."
            ),
            "pca": "PCA is unsupervised and retains directions of greatest variance.",
            "mlp": (
                "The MLP uses forward passes, cross-entropy loss, mini-batches, Adam, "
                "dropout, and validation metrics."
            ),
            "tfidf_logistic_regression": (
                "TF-IDF weights informative words and n-grams; logistic regression "
                "performs the final classification."
            ),
            "pretrained_inference": (
                "Transformer inference tokenizes text, builds attention masks, and "
                "produces contextual representations without training a large model."
            ),
        }[algorithm]

    @classmethod
    def _json(cls, value: object) -> Any:
        if value is None or isinstance(value, (str, int, bool)):
            return value
        if isinstance(value, float):
            return value if np.isfinite(value) else None
        if isinstance(value, np.generic):
            return cls._json(value.item())
        if isinstance(value, np.ndarray):
            return [cls._json(item) for item in value.tolist()]
        if isinstance(value, dict):
            return {str(key): cls._json(item) for key, item in value.items()}
        if isinstance(value, (list, tuple)):
            return [cls._json(item) for item in value]
        return str(value)
