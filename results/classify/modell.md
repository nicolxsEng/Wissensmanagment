# Modellkarte AP10

- Datum: 2026-11-18T10:31:47
- Verfahren: setfit
- Macro-F1 auf der Testmenge: 0,76
- Einstellungen: `{"base_model": "sentence-transformers/all-mpnet-base-v2", "num_iterations": 10, "num_epochs": 1, "batch_size": 16, "max_seq_length": 256, "seed": 20261116}`
- Endmodell trainiert auf 456 Konsensfragen (Training + Test), angewendet auf 22829 Fragen
- Pakete: `{"scikit-learn": "1.9.1", "setfit": "1.2.0", "transformers": "5.23.0", "sentence-transformers": "6.3.0", "torch": "2.15.0"}`
- Zero-Shot-Modell: MoritzLaurer/deberta-v3-large-zeroshot-v2.0; SetFit-Basis: sentence-transformers/all-mpnet-base-v2
- Hypothesensätze (Zero-Shot): G: The solution can be worked out from the code and information given in the question itself.; U: The solution depends on the asker's environment, such as the operating system, installed versions, configuration, build tools, servers or cloud services.; S: This is not a concrete programming problem but a request for opinions, recommendations or a general explanation.
- Alle Modelle lokal; keine Cloud-API.
