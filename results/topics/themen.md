# Themen der Fragetitel (AP11)

Erzeugt: 18.11.2026 16:04. Namen: qwen3.5:9b; geprüft von qwen3.5:9b und phi4:14b (je Thema 10 Zufallstitel; bestanden, wenn beide ≥ 8/10). Auswahl nach D28.

## Vergleich der Verfahren im Hauptlauf

| Verfahren | Themen | bestanden | Anteil | mittlere Passung | „unclear“ |
|---|---|---|---|---|---|
| BERTopic | 30 | 1 | 3% | 22% | 0 |
| NMF | 30 | 0 | 0% | 22% | 9 |

**Gewinner: BERTopic**. Kriterium ≥ 80 % bestandene Themen: **nicht erfüllt** – Themenanalyse nur als Hinweis (D28).

## Themen (BERTopic), sortiert nach Veränderung

Anteile: Mittel 2015–2022 gegen 2023–2026. Inhaltlich gedeutet werden nur bestandene Themen.

| Code | Name | Schlüsselwörter | Beispiel | vorher | nachher | Δ (Pp.) | passt A/B | bestanden |
|---|---|---|---|---|---|---|---|---|
| T05 | C++ compilation and linking errors (nicht bestätigt) | c++, compiler, visual studio, compile, compiling | [C++/SDL "initial value of reference to a non-const must be an lvalue"](https://stackoverflow.com/q/52779227) | 4,5 % | 8,5 % | +4,0 | 0/4 | nein |
| T15 | Asynchronous concurrency patterns (nicht bestätigt) | concurrent, async, asynchronous, threading, multiprocessing | [How should I persist frequently updated in-memory state without blocki](https://stackoverflow.com/q/80010134) | 3,0 % | 5,5 % | +2,5 | 1/3 | nein |
| T20 | Real-time messaging and reconnection (nicht bestätigt) | websocket, socket.io, tcp, sockets, socket | [Listen to mqtt messages for x minutes](https://stackoverflow.com/q/64462761) | 2,1 % | 3,3 % | +1,2 | 1/1 | nein |
| T14 | Android Studio build errors (nicht bestätigt) | android studio, android, android app, studio, gradle | [Intellij Idea error while importing projet from Android studio](https://stackoverflow.com/q/58461940) | 3,6 % | 4,8 % | +1,1 | 1/1 | nein |
| T02 | Azure DevOps CI/CD pipelines (nicht bestätigt) | docker container, dockerfile, inside docker, docker, container | [CI / CD Salesforce - Bitbucket ENVIRONMENT variables issues in pipelin](https://stackoverflow.com/q/79059230) | 5,8 % | 6,9 % | +1,1 | 1/2 | nein |
| T03 | Python import and attribute errors (nicht bestätigt) | python django, django, typeerror, valueerror, python python | [Python NameError:](https://stackoverflow.com/q/52618663) | 5,4 % | 6,3 % | +0,9 | 0/0 | nein |
| T10 | OAuth2 API authentication (nicht bestätigt) | google api, web api, api, oauth2, http request | [Requests keeps returning 403 status, even when following evey step fro](https://stackoverflow.com/q/69758799) | 4,9 % | 5,6 % | +0,7 | 1/1 | nein |
| T23 | Unicode encoding and text display (nicht bestätigt) | unicode, encoding issue, font, encoding, characters | [How to display badly decoded Unicode characters in Excel cells in thei](https://stackoverflow.com/q/58637813) | 1,3 % | 2,0 % | +0,6 | 2/2 | nein |
| T21 | Plot customization and formatting (nicht bestätigt) | matplotlib, plot, axis, chart, y-axis | [Add more deciamals to matplotlib chart?](https://stackoverflow.com/q/58579265) | 1,9 % | 2,4 % | +0,5 | 5/8 | nein |
| T29 | Angle and coordinate calculation (nicht bestätigt) | angle, coordinates, coordinate, rotate, rotating | [how can I find the x, y from a rotated degree](https://stackoverflow.com/q/73922517) | 0,7 % | 0,9 % | +0,2 | 6/5 | nein |
| T26 | Enum identifiers and hashing (nicht bestätigt) | hash, hashmap, hash function, hashing, enum | [How to avoid duplicate enum value from other .cxx](https://stackoverflow.com/q/40125873) | 0,4 % | 0,6 % | +0,2 | 0/0 | nein |
| T22 | File upload implementation (nicht bestätigt) | upload file, upload image, upload files, uploading, upload | [How to upload picture into a database with a html form which have a ty](https://stackoverflow.com/q/40343671) | 2,3 % | 2,5 % | +0,1 | 2/3 | nein |
| T06 | iOS app development (nicht bestätigt) | flutter, widget, ios app, dart, swiftui | [Failed to build iOS app Error output from Xcode build , for flutter](https://stackoverflow.com/q/73991801) | 5,6 % | 5,7 % | +0,1 | 5/3 | nein |
| T08 | CSS layout and positioning (nicht bestätigt) | using css, css, div element, divs, div | [An element with position set to fixed in CSS extends beyond the bottom](https://stackoverflow.com/q/79052599) | 5,0 % | 5,1 % | +0,1 | 7/5 | nein |
| T27 | Java logging configuration (nicht bestätigt) | logging, logs, log, splunk, logout | [Is the configuration in the log4j2.xml file overrided by using the pro](https://stackoverflow.com/q/69481664) | 0,6 % | 0,6 % | +0,1 | 1/1 | nein |
| T17 | TypeScript and Java generics (nicht bestätigt) | generic, types, parameter type, type, return type | [Preserve type when getting nested property via a helper function](https://stackoverflow.com/q/77213436) | 2,9 % | 2,9 % | -0,1 | 0/0 | nein |
| T28 | WooCommerce product data retrieval (nicht bestätigt) | woocommerce, woocommerce order, products, wp query, jquery search | [How to get products name insade all arrray?](https://stackoverflow.com/q/74123320) | 0,7 % | 0,6 % | -0,1 | 0/1 | nein |
| T30 | Email sending with SMTP (nicht bestätigt) | smtp, sp_send_dbmail, send email, emails, email | [Send email with Visual Studio 2010 c# and external SMTP server](https://stackoverflow.com/q/64388638) | 0,5 % | 0,4 % | -0,1 | 1/2 | nein |
| T11 | Hibernate database exceptions (nicht bestätigt) | sql, sql query, database, pl sql, query | [hibernate doesn't build query correctly](https://stackoverflow.com/q/52905759) | 4,6 % | 4,5 % | -0,1 | 0/0 | nein |
| T18 | Date and time formatting (nicht bestätigt) | date format, datetime, dates, date, timestamp | [Wrong date and time showed](https://stackoverflow.com/q/73954195) | 2,2 % | 2,0 % | -0,2 | 2/4 | nein |
| T24 | Ruby on Rails development | ruby rails, rails, ruby, gem, rspec | [Ruby on rails: Model Form](https://stackoverflow.com/q/46945156) | 1,1 % | 0,7 % | -0,4 | 9/9 | ja |
| T25 | URL path manipulation (nicht bestätigt) | htaccess, rewrite, redirect, redirecting, url parameters | [How to remove Page URL from routing path in ASP.NET?](https://stackoverflow.com/q/64272633) | 1,6 % | 1,1 % | -0,5 | 3/3 | nein |
| T12 | MongoDB aggregation queries (nicht bestätigt) | mongodb, mongo, collection, aggregate, graphql | [Distinct values with geoQuery works in Mongo but not in Spring](https://stackoverflow.com/q/46761652) | 3,1 % | 2,5 % | -0,6 | 2/1 | nein |
| T19 | Laravel framework errors (nicht bestätigt) | laravel, laravel php, laravel project, codeigniter, symfony | [Laravel 5 variable not being recognised](https://stackoverflow.com/q/40202298) | 2,5 % | 1,8 % | -0,7 | 3/2 | nein |
| T16 | Button click event handling (nicht bestätigt) | button, buttons, clicking, click, modal | [How do I get the next button to be disabled until an option is selecte](https://stackoverflow.com/q/74017056) | 4,0 % | 3,1 % | -0,9 | 0/1 | nein |
| T07 | String pattern extraction and replacement (nicht bestätigt) | regex, regular expression, replace, extract text, expression | [Split and capture text ending with brackets and two letters](https://stackoverflow.com/q/80011025) | 5,4 % | 4,0 % | -1,4 | 1/1 | nein |
| T01 | React component and state issues (nicht bestätigt) | react js, react, react native, component using, component | [ReactJS error when passing a function as a props](https://stackoverflow.com/q/64218295) | 6,8 % | 5,3 % | -1,5 | 2/2 | nein |
| T13 | JSON parsing and manipulation (nicht bestätigt) | data json, parsing json, json string, json, json object | [Error while parsing JSON string using JQuery](https://stackoverflow.com/q/33156225) | 3,4 % | 1,7 % | -1,6 | 0/1 | nein |
| T09 | Pandas DataFrame column manipulation (nicht bestätigt) | dataframe, pandas dataframe, data frame, values column, column values | [How can I group by two columns interchangeably?](https://stackoverflow.com/q/64605551) | 6,2 % | 4,1 % | -2,1 | 0/2 | nein |
| T04 | Array iteration and indexing (nicht bestätigt) | array, array values, arrays, array object, list using | [Properly iterating values inside of a for loop](https://stackoverflow.com/q/74181089) | 8,1 % | 4,6 % | -3,4 | 4/3 | nein |
