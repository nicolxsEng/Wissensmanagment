"""AP10: die drei lokalen Kandidaten mit gleicher Schnittstelle fit(texts, labels) / predict(texts).

1. TfidfLogReg – Basislinie (scikit-learn)
2. SetFitClassifier – Sentence-Transformer, mit wenigen Beispielen feinabgestimmt
3. ZeroShotClassifier – NLI-Modell ohne Training; Kategorien als Hypothesensätze

Große Bibliotheken werden erst beim Gebrauch importiert.
"""

import time

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline

from sov import config


def device() -> str:
    import torch  # noqa: PLC0415

    return "mps" if torch.backends.mps.is_available() else "cpu"


class TfidfLogReg:
    name = "tfidf_logreg"

    def __init__(self, c: float = 2.0, seed: int = config.SEED):
        self.pipe = make_pipeline(
            TfidfVectorizer(sublinear_tf=True, ngram_range=(1, 2), min_df=2, max_features=50_000),
            LogisticRegression(C=c, class_weight="balanced", max_iter=2000, random_state=seed),
        )
        self.params = {"C": c}

    def fit(self, texts: list[str], labels: list[str]) -> "TfidfLogReg":
        self.pipe.fit(texts, labels)
        return self

    def predict(self, texts: list[str]) -> list[str]:
        return list(self.pipe.predict(texts))


class SetFitClassifier:
    name = "setfit"

    def __init__(
        self,
        base_model: str = config.SETFIT_BASE_MODEL,
        num_iterations: int = 10,
        max_seq_length: int = 256,
        num_epochs: int = 1,
        batch_size: int = 16,
        seed: int = config.SEED,
    ):
        self.params = {
            "base_model": base_model,
            "num_iterations": num_iterations,
            "num_epochs": num_epochs,
            "batch_size": batch_size,
            "max_seq_length": max_seq_length,
            "seed": seed,
        }
        self.model = None

    def fit(self, texts: list[str], labels: list[str]) -> "SetFitClassifier":
        from datasets import Dataset  # noqa: PLC0415
        from setfit import SetFitModel, Trainer, TrainingArguments  # noqa: PLC0415

        p = self.params
        self.model = SetFitModel.from_pretrained(p["base_model"], device=device())
        self.model.model_body.max_seq_length = p["max_seq_length"]
        args = TrainingArguments(
            batch_size=p["batch_size"], num_epochs=p["num_epochs"],
            num_iterations=p["num_iterations"], seed=p["seed"], report_to="none",
            output_dir=str(config.INTERIM_DIR / "setfit_checkpoints"),
        )  # fmt: skip
        trainer = Trainer(
            model=self.model, args=args,
            train_dataset=Dataset.from_dict({"text": texts, "label": labels}),
        )  # fmt: skip
        trainer.train()
        return self

    def predict(self, texts: list[str]) -> list[str]:
        return [str(x) for x in self.model.predict(texts)]


# Entwurf (Version 1): aus docs/kodierleitfaden_fragen.md; nur an den 450 Trainingsfragen schärfen
HYPOTHESES_V1 = {
    "G": "The solution can be worked out from the code and information given in the question "
    "itself.",
    "U": "The solution depends on the asker's environment, such as the operating system, "
    "installed versions, configuration, build tools, servers or cloud services.",
    "S": "This is not a concrete programming problem but a request for opinions, "
    "recommendations or a general explanation.",
}


class ZeroShotClassifier:
    name = "zero_shot"

    def __init__(
        self,
        model_name: str = config.ZERO_SHOT_MODEL,
        hypotheses: dict[str, str] | None = None,
        batch_size: int = 8,
    ):
        self.hypotheses = hypotheses or HYPOTHESES_V1
        self.params = {"model": model_name, "hypotheses": self.hypotheses,
                       "batch_size": batch_size, "template": "{}"}  # fmt: skip
        self.pipe = None
        self.seconds = 0.0

    def fit(self, texts=None, labels=None) -> "ZeroShotClassifier":
        """Kein Training; lädt nur das Modell."""
        from transformers import pipeline  # noqa: PLC0415

        rev = config.MODEL_REVISIONS.get(self.params["model"])
        self.pipe = pipeline(
            "zero-shot-classification", model=self.params["model"], revision=rev,
            device=device(),
        )  # fmt: skip
        return self

    def predict(self, texts: list[str]) -> list[str]:
        if self.pipe is None:
            self.fit()
        inv = {h: k for k, h in self.hypotheses.items()}
        t0 = time.perf_counter()
        out = self.pipe(
            texts, candidate_labels=list(self.hypotheses.values()), hypothesis_template="{}",
            multi_label=False, batch_size=self.params["batch_size"], truncation=True,
        )  # fmt: skip
        self.seconds = time.perf_counter() - t0
        out = out if isinstance(out, list) else [out]
        return [inv[o["labels"][0]] for o in out]
