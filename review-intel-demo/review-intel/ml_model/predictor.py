
import re
from pathlib import Path
from functools import lru_cache

import torch
from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
)

MODEL_DIR = Path(__file__).resolve().parent / "updated_model"
MAX_LEN = 64

# Match the normalization used when training your notebook model.
def normalize(text):
    text = str(text).lower()
    text = text.replace("\u2019", "'").replace("`", "'")
    text = re.sub(r"(\w)'(\w)", r"\1\2", text)
    return re.sub(r"\s+", " ", text).strip()


@lru_cache(maxsize=1)
def _load_model():
    if not MODEL_DIR.is_dir():
        raise FileNotFoundError(
            f"Trained model folder not found: {MODEL_DIR}"
        )

    tokenizer = AutoTokenizer.from_pretrained(
        str(MODEL_DIR),
        local_files_only=True,
    )

    model = AutoModelForSequenceClassification.from_pretrained(
        str(MODEL_DIR),
        local_files_only=True,
    )

    device = torch.device("cpu")
    model.to(device)
    model.eval()

    return tokenizer, model, device


@torch.inference_mode()
def predict(text):
    """Return emotion and confidence for one review."""
    cleaned = normalize(text)

    if not cleaned:
        raise ValueError("Empty review text")

    tokenizer, model, device = _load_model()

    inputs = tokenizer(
        cleaned,
        return_tensors="pt",
        truncation=True,
        max_length=MAX_LEN,
    )

    inputs = {key: value.to(device)
              for key, value in inputs.items()}

    logits = model(**inputs).logits
    probabilities = torch.softmax(logits, dim=-1)[0]

    class_id = int(probabilities.argmax().item())
    id2label = model.config.id2label

    # Use the emotion labels saved with your trained model.
    emotion = id2label.get(
        class_id,
        id2label.get(str(class_id), f"LABEL_{class_id}")
    )

    return {
        "emotion": str(emotion).lower().strip(),
        "confidence": float(probabilities[class_id].item()),
    }
