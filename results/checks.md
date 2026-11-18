# Datenprüfung und Literaturabgleich (AP12)

Erzeugt: 18.11.2026 23:24. API-Abfrage: 18.11.2026 22:22 UTC; Download der Rohdaten 11.11.2026–14.11.2026.

## Abgleich von 20 Fragen mit der API

Stichprobe (D31): je Oktober 2008–2026 eine zufällige Frage und eine Frage eines neuen Fragetyps (Seed + 120), zusammen 20. Die gespeicherten Werte (AP01) werden mit einer erneuten Abfrage verglichen; Antworten im Fenster nach plan.md 5.2. Einzelwerte: `coding/checks/datenpruefung_20.csv`.

| Feld | gleich | abweichend, erklärt | abweichend, nicht erklärt |
|---|---|---|---|
| Erstellzeit | 19 | 1 | 0 |
| Tags | 18 | 2 | 0 |
| Antworten im Fenster | 18 | 2 | 0 |
| Zeit bis zur ersten Antwort (h) | 18 | 2 | 0 |
| akzeptiert im Fenster | 19 | 1 | 0 |
| Antworten heute (answer_count) | 18 | 2 | 0 |

Abweichungen im Einzelnen:

| Nr. | Frage | Feld | gespeichert | heute (API) | Erklärung |
|---|---|---|---|---|---|
| 19 | [80013008](https://stackoverflow.com/q/80013008) | Erstellzeit | 28.10.2026 05:13:56 | – | Frage seit dem Abruf gelöscht oder nicht mehr öffentlich (API liefert sie nicht) |
| 19 | [80013008](https://stackoverflow.com/q/80013008) | Tags | google-cloud-platform google-oauth youtube-api | – | Frage seit dem Abruf gelöscht oder nicht mehr öffentlich (API liefert sie nicht) |
| 19 | [80013008](https://stackoverflow.com/q/80013008) | Antworten im Fenster | 0 | – | Frage seit dem Abruf gelöscht oder nicht mehr öffentlich (API liefert sie nicht) |
| 19 | [80013008](https://stackoverflow.com/q/80013008) | Zeit bis zur ersten Antwort (h) | – | – | Frage seit dem Abruf gelöscht oder nicht mehr öffentlich (API liefert sie nicht) |
| 19 | [80013008](https://stackoverflow.com/q/80013008) | akzeptiert im Fenster | nein | – | Frage seit dem Abruf gelöscht oder nicht mehr öffentlich (API liefert sie nicht) |
| 19 | [80013008](https://stackoverflow.com/q/80013008) | Antworten heute (answer_count) | 0 | – | Frage seit dem Abruf gelöscht oder nicht mehr öffentlich (API liefert sie nicht) |
| 20 | [79802131](https://stackoverflow.com/q/79802131) | Tags | advice c# html javascript maui | c# html javascript maui | Tag des neuen Fragetyps fehlt heute (bearbeitet oder Typ umgestellt) |
| 20 | [79802131](https://stackoverflow.com/q/79802131) | Antworten im Fenster | 3 | 1 | 2 Antworten im Fenster seit dem Abruf gelöscht |
| 20 | [79802131](https://stackoverflow.com/q/79802131) | Zeit bis zur ersten Antwort (h) | 1,62 | 13,21 | früheste gespeicherte Antwort heute nicht mehr sichtbar (gelöscht) |
| 20 | [79802131](https://stackoverflow.com/q/79802131) | Antworten heute (answer_count) | 3 | 1 | heutiger Wert, seit dem Abruf verändert; geht in keine Kennzahl ein |

**Ergebnis:** In den Feldern, aus denen die Kennzahlen entstehen, gibt es 8 Abweichungen bei 2 von 20 Fragen, davon 0 nicht erklärt. Die Datenbasis stimmt mit der Website überein; Abweichungen entstehen nur durch spätere Änderungen auf der Website. Der heutige `answer_count` geht in keine Kennzahl ein (plan.md 5.2).

## Antwortende: 10 Antworten mit der API abgeglichen (Prüfung zu AP14)

Zufällige Antworten aus dem 7-Tage-Fenster aller Jahre (Seed + 121). Verglichen werden Frage, Erstellzeit, Konto (nur als Hash, keine Nutzer-IDs) und Akzeptanz. Einzelwerte: `coding/checks/antworten_10.csv`.

| Nr. | Antwort | Jahr | mit Konto | Frage | Zeit | Konto | akzeptiert | Erklärung |
|---|---|---|---|---|---|---|---|---|
| 1 | [1584234](https://stackoverflow.com/a/1584234) | 2009 | ja | ja | ja | ja | ja | – |
| 2 | [19547143](https://stackoverflow.com/a/19547143) | 2013 | ja | ja | ja | ja | ja | – |
| 3 | [26153861](https://stackoverflow.com/a/26153861) | 2014 | ja | ja | ja | ja | ja | – |
| 4 | [26501379](https://stackoverflow.com/a/26501379) | 2014 | ja | ja | ja | ja | ja | – |
| 5 | [39998466](https://stackoverflow.com/a/39998466) | 2016 | ja | ja | ja | ja | ja | – |
| 6 | [40341332](https://stackoverflow.com/a/40341332) | 2016 | ja | ja | ja | ja | ja | – |
| 7 | [46961825](https://stackoverflow.com/a/46961825) | 2017 | ja | ja | ja | ja | ja | – |
| 8 | [52952353](https://stackoverflow.com/a/52952353) | 2018 | ja | ja | ja | ja | ja | – |
| 9 | [58404141](https://stackoverflow.com/a/58404141) | 2019 | ja | ja | ja | ja | ja | – |
| 10 | [69599169](https://stackoverflow.com/a/69599169) | 2021 | ja | ja | ja | ja | ja | – |

**Ergebnis:** 10 von 10 Antworten stimmen in allen Feldern mit der Website überein.

Anteil der Antworten ohne Konto (gelöschte Konten; im Fenster, klassische Fragen), in AP14 nicht gezählt (D17):

| Jahr | 2008 | 2009 | 2010 | 2011 | 2012 | 2013 | 2014 | 2015 | 2016 | 2017 | 2018 | 2019 | 2020 | 2021 | 2022 | 2023 | 2024 | 2025 | 2026 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ohne Konto | 3,0 % | 1,8 % | 1,4 % | 1,4 % | 1,3 % | 1,5 % | 1,5 % | 1,6 % | 1,5 % | 1,6 % | 1,4 % | 1,3 % | 1,1 % | 1,4 % | 1,1 % | 1,0 % | 0,6 % | 0,9 % | 0,0 % |

## Neue Fragetypen (aus den Daten, AP02/T9)

| Jahr | Typ | Fragen | Anteil Score 0 | Antworten je Frage | unbeantwortet | akzeptiert | geschlossen |
|---|---|---|---|---|---|---|---|
| 2025 | advice | 23 | 74 % | 2,43 | 30 % | 0 % | 4 % |
| 2025 | best-practices | 18 | 89 % | 3,61 | 0 % | 6 % | 0 % |
| 2025 | klassisch | 5221 | 45 % | 0,77 | 42 % | 29 % | 7 % |
| 2026 | advice | 32 | 12 % | 0,97 | 50 % | 19 % | 34 % |
| 2026 | best-practices | 35 | 17 % | 1,60 | 26 % | 43 % | 23 % |
| 2026 | klassisch | 882 | 17 % | 0,98 | 32 % | 30 % | 27 % |

2025 erhielten die neuen Typen kaum Votes (74–89 % mit Score 0) und fast keine akzeptierte Antwort; 2026 tragen sie Votes und häufiger eine akzeptierte Antwort. Das stützt die getrennte Behandlung (plan.md 5.1). Die Durchsicht auf der Website (5 + 5 Fragen) war optional und entfällt.

## Literaturabgleich

Nur Richtung und Größenordnung sind vergleichbar: Die Studien schätzen den Unterschied zu Vergleichsplattformen bzw. zum Vorjahr in den ersten Monaten nach dem 30.11.2022; dieses Projekt vergleicht Oktober-Monate und die Fortschreibung des Trends 2015–2022, ohne Vergleichsplattform.

| | Daten und Vergleich | Zeitraum | Ergebnis |
|---|---|---|---|
| dieses Projekt | Fragen je Oktober; Vorher-nachher und Abweichung vom Trend 2015–2022 (keine Vergleichsplattform) | Okt. 2022 → Okt. 2023 / 2024 | Fragen 105.739 → 52.333 (**−50,5 %**), 2024: 23.161 (−78,1 %); Abweichung vom Trend −50,2 % (2023) bzw. −76,2 % (2024) |
| del Rio-Chanona, Laurentsyeva & Wachs (2024), *PNAS Nexus* 3(9), pgae400, doi:10.1093/pnasnexus/pgae400 | Beiträge (Fragen und Antworten) je Woche; Differenz-in-Differenzen gegen russisches Stack Overflow, Segmentfault, Mathematics, MathOverflow | Jan. 2022 – Mai 2023 | Mittel der ersten 6 Monate: Beiträge −15 %, Fragen −10 % (Tab. 1); bis Ende April 2023 ≈ −25 %, von den Autor:innen als Untergrenze bezeichnet; roh: ≈ 60.000 → 40.000 Beiträge je Woche in 6 Monaten, 60.000 → 30.000 von Mai 2022 bis Mai 2024 |
| Burtch, Lee & Chen (2024), *Scientific Reports* 14, 10413, doi:10.1038/s41598-024-61221-0 | Besuche je Tag (synthetische Kontrolle); Fragen je Thema, 50 häufigste Tags (Differenz-in-Differenzen gegen dasselbe Zeitfenster ein Jahr früher); Reddit-Entwicklerforen als Gegenprobe | Okt. 2022 – Mitte März 2023 | Besuche ≈ −12 % (≈ 1 Mio. je Tag); Fragen deutlich gesunken (im Haupttext keine Prozentzahl); Reddit ohne Veränderung |

**Richtung:** gleich (Rückgang der Fragen nach November 2022). **Größenordnung:** Der Rückgang hier ist größer als die geschätzten −10 % bis −25 %. Das passt zu den unterschiedlichen Vergleichen: Die Studien ziehen die Entwicklung auf Vergleichsplattformen ab und betrachten nur die ersten 4–6 Monate; der rohe Rückgang bei del Rio-Chanona et al. (≈ −33 % in 6 Monaten, −50 % in zwei Jahren) liegt nahe an den Werten hier.

**Unterschiede zwischen Themen (Bezug zu TF2):** Burtch et al. (Abschnitt „Heterogeneity … by topic“) finden die stärksten Rückgänge bei Themen der konkreten, abgeschlossenen Programmierarbeit und kaum Veränderung bei Spring, AWS, Firebase, Docker, SQL Server und Azure. del Rio-Chanona et al. nennen Python und JavaScript unter den am stärksten betroffenen Sprachen. Behaltensquote (Anteil 2024 / Anteil 2022, 1 = wie Stack Overflow insgesamt; Gruppe der Hauptauswertung in Klammern) für die von Burtch et al. genannten Tags:

- stark betroffen laut Burtch et al.: python 0,68, css 0,81 (G), flutter 0,97 (G), reactjs 0,57 (G), django 0,60 (G), sql 0,69 (G), arrays 0,37 (G), pandas 0,33 (G) – Median **0,64**
- kaum betroffen laut Burtch et al.: spring 1,23, spring-boot 1,54, amazon-web-services 0,85 (U), firebase 0,77, docker 1,10 (U), sql-server 1,17, azure 2,20 (U) – Median **1,17**

Die Richtung stimmt mit dem Gruppenvergleich hier überein (Umgebungs-Tags behalten ihren Anteil eher). Burtch et al. betrachten einen kürzeren Zeitraum und andere Vergleiche; die Übereinstimmung ist ein Hinweis, keine Bestätigung.
