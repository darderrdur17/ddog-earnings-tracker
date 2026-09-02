from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd
from sklearn.linear_model import Ridge
from sklearn.metrics import (
    mean_absolute_percentage_error,
    mean_squared_error,
)
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from .config import Settings


def _metrics(
    actual: pd.Series, pred: pd.Series, baseline: pd.Series | None = None
) -> dict[str, float]:
    out = {
        "n_test": int(len(actual)),
        "rmse": float(mean_squared_error(actual, pred) ** 0.5),
        "mape": float(mean_absolute_percentage_error(actual, pred)),
        "directional_hit_rate": float((np.sign(actual) == np.sign(pred)).mean()),
    }
    if baseline is not None and len(actual):
        out["directional_change_hit_rate"] = float(
            (np.sign(actual - baseline) == np.sign(pred - baseline)).mean()
        )
    return out


def walk_forward(
    panel: pd.DataFrame,
    feature_cols: list[str],
    settings: Settings,
    target: str = "revenue_yoy",
) -> tuple[pd.DataFrame, dict[str, Any]]:
    usable = panel.dropna(subset=[target, *feature_cols]).reset_index(drop=True)
    preds: list[dict[str, Any]] = []
    start = settings.min_train_rows
    for i in range(start, len(usable)):
        train = usable.iloc[:i]
        test = usable.iloc[[i]]
        model = make_pipeline(
            StandardScaler(), Ridge(alpha=settings.ridge_alpha)
        )
        model.fit(train[feature_cols], train[target])
        pred = float(model.predict(test[feature_cols])[0])
        ridge: Ridge = model.named_steps["ridge"]
        scaled = model.named_steps["standardscaler"].transform(
            test[feature_cols]
        )[0]
        contributions = {
            col: float(coef * value)
            for col, coef, value in zip(feature_cols, ridge.coef_, scaled)
        }
        naive = float(train[target].iloc[-1])
        preds.append(
            {
                "quarter": test.iloc[0]["quarter"],
                "actual": float(test.iloc[0][target]),
                "pred": pred,
                "naive_persistence": naive,
                "error": pred - float(test.iloc[0][target]),
                "contributions": contributions,
            }
        )

    predictions = pd.DataFrame(preds)
    if predictions.empty:
        return predictions, {}

    last_n = predictions.tail(settings.test_horizon)
    metrics = {
        "ridge": _metrics(
            predictions["actual"],
            predictions["pred"],
            predictions["naive_persistence"],
        ),
        "naive_persistence": _metrics(
            predictions["actual"],
            predictions["naive_persistence"],
            predictions["naive_persistence"],
        ),
        "ridge_recent_window": _metrics(
            last_n["actual"], last_n["pred"], last_n["naive_persistence"]
        ),
        "naive_persistence_recent_window": _metrics(
            last_n["actual"],
            last_n["naive_persistence"],
            last_n["naive_persistence"],
        ),
        "feature_cols": feature_cols,
        "n_usable": int(len(usable)),
        "n_walk_forward": int(len(predictions)),
        "recent_window_quarters": last_n["quarter"].tolist(),
    }
    return predictions, metrics


def next_quarter(quarter: str) -> str:
    year = int(quarter[:4])
    qtr = int(quarter[-1])
    if qtr == 4:
        return f"{year + 1}Q1"
    return f"{year}Q{qtr + 1}"


def latest_estimate(
    panel: pd.DataFrame,
    feature_cols: list[str],
    signal_yoy_cols: list[str],
    settings: Settings,
    target: str = "revenue_yoy",
) -> dict[str, Any]:
    """One-quarter-ahead call using the latest complete signal YoY as lag-1."""
    labeled = panel.dropna(subset=[target, *feature_cols])
    latest_signals = panel.dropna(subset=signal_yoy_cols)
    if len(labeled) < settings.min_train_rows or latest_signals.empty:
        return {}
    model = make_pipeline(StandardScaler(), Ridge(alpha=settings.ridge_alpha))
    model.fit(labeled[feature_cols], labeled[target])
    last_signals = latest_signals.iloc[-1]
    x_next = pd.DataFrame(
        [last_signals[signal_yoy_cols].tolist()],
        columns=feature_cols,
    )
    pred = float(model.predict(x_next)[0])
    ridge: Ridge = model.named_steps["ridge"]
    scaled = model.named_steps["standardscaler"].transform(x_next)[0]
    naive = float(labeled[target].iloc[-1])
    delta = pred - naive
    if delta > 0.01:
        tracking = "ahead"
    elif delta < -0.01:
        tracking = "behind"
    else:
        tracking = "in_line"
    last_reported = labeled.iloc[-1]
    return {
        "quarter": next_quarter(str(last_reported["quarter"])),
        "pred": pred,
        "naive_persistence": naive,
        "tracking": tracking,
        "delta_vs_baseline": delta,
        "contributions": {
            col: float(coef * value)
            for col, coef, value in zip(feature_cols, ridge.coef_, scaled)
        },
        "has_actual": False,
        "actual": None,
        "last_reported_quarter": str(last_reported["quarter"]),
        "signal_as_of_quarter": str(last_signals["quarter"]),
        "confidence": "exploratory",
    }
