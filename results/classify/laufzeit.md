# Laufzeittest AP10 (ohne Labels)

Erzeugt: 16.11.2026 00:40. 200 zufällige Fragen der Anwendungsstichprobe (22829 Fragen gesamt). Gerät: Apple-GPU (mps), falls verfügbar.

| Verfahren | Sekunden je Frage | Hochrechnung Anwendung |
|---|---|---|
| Zero-Shot deberta-v3-large-zeroshot-v2.0 | 1.126 | 428 min |
| Zero-Shot deberta-v3-base-zeroshot-v2.0 | 0.398 | 152 min |
| SetFit (Vorhersage) | 0.038 | 14 min |

SetFit-Probetraining: 60 Fragen, 5 Iterationen in 236 s → hochgerechnet auf 450 Fragen, 20 Iterationen: etwa 118 min je Training (bei 5-facher Kreuzvalidierung × 5).

Die Platzhalter-Labels dienen nur der Zeitmessung; dieser Lauf sagt nichts über Güte.
Pakete: {"scikit-learn": "1.9.1", "setfit": "1.2.0", "transformers": "5.23.0", "sentence-transformers": "6.3.0", "torch": "2.15.0"}

## Nachtrag 16.11.2026: SetFit beschleunigt (D21)

Mit 256 statt 384 Token Eingabelänge und 10 statt 20 Iterationen: 60 Fragen / 5 Iterationen in 102 s (vorher 236 s) → ein Training auf 450 Fragen etwa 25 min. Kreuzvalidierung für SetFit nur optional (`SOV_SETFIT_CV=1`), weil SetFit mit festen Standardeinstellungen läuft.

**Geschätzter Gesamtaufwand nach der Kodierung:** `select` ≈ 10 min (TF-IDF Sekunden, Zero-Shot auf 450 Fragen ≈ 8 min) · `test` ≈ 30 min · `apply` je nach Gewinner: TF-IDF Sekunden, SetFit ≈ 50 min, Zero-Shot groß ≈ 7 h (über Nacht) bzw. klein ≈ 2,5 h.
