# Kodierleitfaden: Einordnung der Tags (Entwurf)

*Version 0.2 · 16.11.2026 (zweite Runde nach κ = 0,37 in Runde 1, D25; geschärft nur an 40 Tags außerhalb der 269) · Version 0.1 vom 15.11.2026 galt für Runde 1*

## Ziel

Jeder der 269 Tags mit mindestens 150 Fragen im Oktober 2022 (nach Zusammenführen der Synonyme, D15) wird einer von drei Kategorien zugeordnet. Beide Kodierenden arbeiten **unabhängig**, ohne Absprache und **ohne Fragezahlen oder Entwicklungen anzusehen**. In eine Gruppe kommen nur Tags, die beide gleich einordnen.

## Leitfrage

> Stell dir eine typische Frage mit diesem Tag vor. Ergibt sich die Lösung normalerweise **aus der Frage selbst** (Code, Daten, Fehlermeldung im Text), oder hängt sie typischerweise an der **konkreten Umgebung** der fragenden Person, die eine außenstehende Person nicht sieht?

## Kategorien

| Code | Kategorie | Definition | Typische Tags (Beispiele, keine Vorgabe) |
|---|---|---|---|
| **G** | Grundlagen | Die Lösung ergibt sich typischerweise aus dem, was in der Frage steht: Sprachkonstrukte, Datenstrukturen, Algorithmen, Datenverarbeitung, Abfragelogik, Textmuster, richtige Verwendung der Programmierschnittstelle einer Bibliothek oder eines Frameworks. Eine kompetente Person könnte die Frage ohne Zugriff auf den Rechner der fragenden Person beantworten. | Sprachkonstrukte (Schleifen, Klassen, Rekursion), Datenstrukturen, reguläre Ausdrücke, Bibliotheken zur Datenverarbeitung, SQL-Abfragen |
| **U** | Umgebung | Die Lösung hängt typischerweise an Betriebssystem, installierten Versionen, Konfiguration, Werkzeugen, Build- und Paketverwaltung, Containern, Servern, Netzwerk, Rechten oder Cloud-Diensten. | Betriebssysteme, Entwicklungsumgebungen, Paketmanager, Build-Werkzeuge, Container und Orchestrierung, Cloud-Dienste, Webserver, Versionsverwaltung und CI |
| **K** | keine eindeutige | Der Tag umfasst in großer Zahl beides, oder passt in keine der beiden Kategorien. | ganze Programmiersprachen, breite Frameworks und Plattformen, Fachdomänen |

## Entscheidungsregeln

0. **Vorgehen (seit v0.2):** Zuerst Regel 2 prüfen (ganze Programmiersprache → K). Sonst den Anteil typischer Fragen schätzen, die G bzw. U sind (zusammen 100 %), und dann Regel 1 anwenden. Beispiele: 80/20 → G; 70/30 → G; 60/40 → K; 50/50 → K; 30/70 → U. **Dass beide Arten vorkommen, ist allein kein Grund für K** – fast jeder Tag hat einige Einrichtungsfragen und einige Codefragen.
1. **Zwei-Drittel-Regel:** G oder U nur, wenn schätzungsweise mindestens zwei Drittel der typischen Fragen mit diesem Tag in diese Kategorie fallen. Sonst **K**.
2. **Ganze Programmiersprachen** (z. B. eine Sprache als Ganzes) → **K**, weil sie beides in großer Zahl enthalten. Ausnahme nur, wenn der Tag ausdrücklich einen Versions- oder Plattformaspekt bezeichnet (dann meist U).
3. **Frameworks und Bibliotheken:** Entscheidend ist, wofür sie typischerweise gefragt werden.
   - Bibliothek oder Framework (auch Web-, Oberflächen-, CSS-, ORM-, Test-Frameworks), bei dem meist die Verwendung der Programmierschnittstelle gefragt wird (falsche Verwendung, Logik, Syntax, Gestaltung, Abfragen; das Problem steht in der Frage) → eher **G** (wie Fragen-Leitfaden v0.2).
   - Framework, bei dem meist Einrichtung, Konfiguration, Versionen oder Zusammenspiel mit Werkzeugen gefragt werden → eher **U**.
   - Beides etwa gleich häufig → **K**.
4. **Versionierte Tags** (Tag enthält eine Versionsnummer) → in der Regel **U**.
5. **Datenbanken:** Tag für eine Abfragesprache → eher **G**; Tag für ein konkretes Datenbanksystem → nach Regel 3 entscheiden (Abfragen vs. Installation, Verbindung, Konfiguration).
6. **Fachdomänen und Konzepte** ohne klaren Bezug (z. B. Sicherheit allgemein, Leistung allgemein) → **K**, außer Regel 1 trifft klar zu.
7. **Unsicher?** Trotzdem eine Kategorie wählen und Spalte `unsicher` mit `x` markieren. Keine Recherche zu Fragezahlen oder Entwicklungen. Erlaubt ist nur der Wiki-Auszug im Bogen und eigenes Fachwissen.

## Ablauf

1. Beide lesen diesen Leitfaden, besprechen Unklarheiten **vor** der Kodierung (nicht anhand der 269 Tags, sondern anhand von 10 Übungstags, die nicht in der Liste stehen).
2. Jede Person füllt ihren eigenen Bogen aus (`coding/tags/tags_kodierer_A.csv` bzw. `_B.csv`), Reihenfolge wie im Bogen.
3. Keine Absprache, bis beide fertig sind.
4. Danach berechnet AP05 Cohens Kappa. Strittige Tags werden **nicht** nachträglich vereinheitlicht, sie kommen in keine Gruppe. Liegt Kappa unter 0,61, wird der Leitfaden geschärft und eine zweite Runde dokumentiert (Exposé Abschnitt 6).

## Offenlegung

Eine Person kennt aus der Voruntersuchung die Entwicklung von 40 Tags. Das wird im Paper als Grenze genannt.
