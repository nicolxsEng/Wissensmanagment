# Kodierleitfaden: Einordnung von Fragetexten (Entwurf)

*Version 0.2 · 16.11.2026 (Zusatzregeln nach der Kalibrierung) · Version 0.1 · 15.11.2026 · nach der Kalibrierung (30 Fragen) schärfen, danach einfrieren. Aus diesem Leitfaden werden auch die Hypothesensätze des Zero-Shot-Modells in AP10 abgeleitet.*

## Ziel

Jede Frage wird **allein anhand von Titel und Text** einer von drei Kategorien zugeordnet. Jahr, Tags und Score sind in der Kodieransicht ausgeblendet.

## Kategorien

| Code | Kategorie | Kurzdefinition |
|---|---|---|
| **G** | Grundlagenfrage | Die Lösung lässt sich aus der Frage selbst ableiten. Alles Nötige (Code, Daten, Fehlermeldung, gewünschtes Ergebnis) steht im Text oder ist allgemeines Programmierwissen. |
| **U** | Umgebungsfrage | Die Lösung hängt an der Umgebung der fragenden Person: Betriebssystem, installierte Versionen und Abhängigkeiten, Konfiguration, Build- und Deploy-Werkzeuge, Entwicklungsumgebung, Container, Server, Netzwerk, Rechte, Cloud-Dienste, externe Dienste und deren aktuelle Programmierschnittstellen. |
| **S** | Sonstige | Keine konkrete Problemlösungsfrage: Meinungs-, Empfehlungs- und Designfragen ohne konkretes Problem, Verständnisfragen zu Konzepten ohne Code, unverständliche oder nicht programmierbezogene Fragen. |

## Entscheidungsweg

1. **Gibt es ein konkretes Programmier- oder Technikproblem, das gelöst werden soll?**
   Nein → **S**.
2. **Könnte eine kompetente Person die Lösung allein aus dem Text ableiten**, ohne Zugriff auf den Rechner, die Konfiguration oder die genauen Versionen der fragenden Person?
   Ja → **G**.
3. **Hängt die Lösung an mindestens einem Umgebungsmerkmal** (Liste oben)?
   Ja → **U**.
4. Passt nichts eindeutig: die Kategorie wählen, die auf **die Ursache des Problems** zutrifft, und `unsicher` markieren.

## Zusatzregeln (Version 0.2, nach der Kalibrierung vom 16.11.2026)

- **Prüfstein für U ist fehlende Information über die Umgebung:** U nur, wenn eine richtige Antwort Angaben über die Umgebung der fragenden Person braucht, die nicht in der Frage stehen und sich zwischen Umgebungen unterscheiden (installierte Version, Betriebssystem, Konfiguration, Netzwerk, Aufbau eines Servers, einer Cloud oder eines externen Dienstes, Verhalten eines Werkzeugs oder einer IDE).
- **Ein Framework-, Bibliotheks- oder Werkzeugname macht eine Frage nicht zu U.** Dokumentiertes, versionsunabhängiges Verhalten einer Sprache, eines Frameworks oder einer Bibliothek gilt als allgemeines Programmierwissen → G.
- **Logikfehler, falsche Verwendung einer Schnittstelle, Rekursion, Zustand, zeitliche Abläufe oder Datenverarbeitung**, die sich aus dem gezeigten Code erklären lassen → G.
- **„Wie mache ich X?“ mit konkretem technischem Ziel** ist eine Problemlösungsfrage (G oder U), nicht S. S nur für Meinungen, Empfehlungen, Vergleiche ohne konkretes Problem, rein konzeptionelle Fragen ohne Aufgabe oder unklare Fragen.

## Grenzfälle

| Situation | Kategorie | Begründung |
|---|---|---|
| Fehlermeldung bei Installation, Import eines Pakets, Build oder Start | U | Ursache liegt in Umgebung oder Versionen |
| Verwendung einer Bibliotheksfunktion mit Beispieldaten (z. B. Tabelle umformen) | G | aus der Frage lösbar |
| Gleicher Code verhält sich nach einem Versionswechsel anders | U | Versionsabhängigkeit |
| Verhalten laut Sprachstandard („warum kompiliert das in Standard X, aber nicht in Y?“) | G | aus Standard ableitbar, kein Zugriff auf Umgebung nötig |
| SQL-Abfrage liefert falsches Ergebnis | G | Abfragelogik |
| Verbindung zur Datenbank schlägt fehl | U | Konfiguration, Netzwerk, Rechte |
| Konfigurationsdatei eines Werkzeugs (Build, Linter, Server) | U | |
| Aufruf einer externen Programmierschnittstelle (z. B. eines KI-Dienstes): was sie kann oder warum sie einen Fehler meldet | U | hängt am aktuellen Stand des Dienstes |
| Algorithmus zu langsam, Komplexität verbessern | G | |
| Darstellungsproblem in HTML/CSS mit vollständigem Code | G | aus Code reproduzierbar |
| Darstellungsproblem nur in einem bestimmten Browser oder Gerät | U | |
| „Welche Bibliothek sollte ich nehmen?“, „Was ist besser, A oder B?“ | S | keine konkrete Problemlösung |
| Frage ist unverständlich oder enthält kein Problem | S | |

## Ankerbeispiele (aus der Voruntersuchung, in der Kalibrierung bestätigen)

| Frage (gekürzt) | Kategorie |
|---|---|
| Wie füge ich einem pandas-DataFrame Daten hinzu, ohne ihn neu zu erzeugen? | G |
| Abfrage mit MAX-Funktion schreiben (SQL) | G |
| Doppelte Objekte mit niedrigerem Index aus einem Array entfernen (JavaScript) | G |
| Warum funktioniert mein Programm in C23, aber nicht in C11? | G |
| Wie migriere ich von Poetry zum Paketmanager uv? | U |
| Bild über die API an ChatGPT hochladen | U |
| Wie stelle ich sicher, dass Antworten aus meinem feinabgestimmten Datensatz kommen? | S oder U → in der Kalibrierung festlegen |

## Ablauf

1. **Kalibrierung:** beide kodieren die 30 Kalibrierungsfragen unabhängig, dann gemeinsam besprechen. Leitfaden schärfen (neue Grenzfälle eintragen, Version erhöhen).
2. **Kodierung:** Person A kodiert alle 600, Person B die 150 markierten (Kodier-App, `notebooks/kodier_app.py`). Keine Absprache während der Kodierung.
3. **Konsens:** Für die 150 Doppelten werden Abweichungen besprochen und ein Konsenslabel festgelegt. Kappa wird **vor** dem Konsens berechnet.
4. Nach der Kalibrierung wird der Leitfaden nicht mehr geändert.
