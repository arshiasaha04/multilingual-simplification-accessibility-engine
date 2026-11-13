from pathlib import Path
from uuid import uuid4

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from app.config import get_settings


def generate_evaluation_report(records: list[dict], output_path: str | Path | None = None) -> Path:
    """Save a CSV summary and a readability comparison chart."""
    if not records:
        raise ValueError("At least one evaluation record is required")

    frame = pd.DataFrame.from_records(records)
    required = {"language", "source_words_per_sentence", "output_words_per_sentence"}
    missing = required.difference(frame.columns)
    if missing:
        raise ValueError(f"Missing evaluation fields: {', '.join(sorted(missing))}")

    plots_dir = Path(get_settings().plots_dir)
    plots_dir.mkdir(parents=True, exist_ok=True)
    chart_path = Path(output_path) if output_path else plots_dir / f"readability-{uuid4().hex}.png"
    chart_path.parent.mkdir(parents=True, exist_ok=True)

    long_frame = frame.melt(
        id_vars="language",
        value_vars=["source_words_per_sentence", "output_words_per_sentence"],
        var_name="version",
        value_name="words_per_sentence",
    )
    plt.figure(figsize=(9, 5))
    sns.barplot(data=long_frame, x="language", y="words_per_sentence", hue="version")
    plt.ylabel("Average words per sentence")
    plt.xlabel("Language")
    plt.tight_layout()
    plt.savefig(chart_path, dpi=160)
    plt.close()

    frame.to_csv(chart_path.with_suffix(".csv"), index=False)
    return chart_path
