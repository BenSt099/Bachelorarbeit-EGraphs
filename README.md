# Bachelorarbeit - EGraphs <a href="https://github.com/BenSt099/Bachelorarbeit-EGraphs"><img src="logo.png" align="right" width="112" height="112"/></a>

Das Ziel dieser Bachelorarbeit ist es, ein sinnvolles Werkzeug für die Lehre zu erstellen,
um Studentinnen und Studenten die Themen **E-Graphs** und **Equality Saturation** näherzubringen.
Dabei sollen sie die Möglichkeit haben, sich sowohl auf theoretischer als auch praktischer Ebene mit E-Graphs auseinandersetzen zu können.
Die theoretische Ebene soll den Studenten die notwendigen Hintergrundkenntnisse vermitteln sowie einen Einblick in die Implementierung geben.
Die praktische Ebene soll Schritt für Schritt aufzeigen, wie der **E-Graph** aufgebaut wird, und wie an diesem **Equality Saturation** durchgeführt werden kann.
Für größtmöglichen Nutzen soll die Anwendung plattformunabhängig sein und möglichst nur von _Open-Source-Software_ (OSS) Gebrauch machen.
Damit wird das Problem der unterschiedlichen Betriebssysteme der Studenten umgangen und zeitgleich die Hürden für Erweiterungen gesenkt.

## Overview

<img src="egraph.png" alt="example of an egraph">

## Setup

1. Bitte installieren Sie die [Dependencies](##Dependencies).
2. Laden Sie sich den Code herunter.
3. Führen Sie den Befehl ``fastapi run server.py`` im _src_ Ordner aus.
4. Falls sich der Browser nicht automatisch öffnet, öffnen Sie ihn manuell unter der Adresse http://127.0.0.1:8000.

## Dokumentation

Die Dokumentation kann in der Anwendung unter _Dokumentation_ gefunden werden (bzw. unter der Adresse http://127.0.0.1:8000/dokumentation.html).

## Dependencies

1. [Graphviz](https://graphviz.org/download/)
   1. **PATH**: Achten Sie während der Installation darauf, Graphviz zum PATH hinzuzufügen.
   2. **Windows**: Achten Sie darauf, dass ``dot`` vom Terminal aus aufrufbar ist; überprüfbar mit ``dot --version``. [Komplette Anleitung für Windows](https://forum.graphviz.org/t/new-simplified-installation-procedure-on-windows/224).
2. Die notwendigen Pakete finden Sie in [requirements.txt](https://github.com/BenSt099/Bachelorarbeit-EGraphs/blob/main/code/requirements.txt):

```shell
pip install -r requirements.txt
```

## Tests

Wenn Sie die Tests ausführen möchten, fügen sie entweder Folgendes zu ``requirements.txt`` hinzu: ``pytest==8.3.3`` oder
installieren Sie das Paket händisch: ```pip install pytest==8.3.3```.

## License

Dieses Projekt wird unter der **MIT License** veröffentlicht. Für weiterführende Informationen klicken Sie bitte [hier](https://github.com/BenSt099/Bachelorarbeit-EGraphs/blob/main/LICENSE). Das Icon im Logo wurde aus dem Framework [Bootstrap](https://icons.getbootstrap.com/icons/tools/) genommen.
