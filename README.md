# Fahrplangenerator Team_NULL

Für den informatiCup 2022 soll ein Fahrplan für ein Schienennetzwerk erstellt werden. Das Ziel ist eine Software für die Berechnung von optimalen Fahrplänen, die die Gesamtverspätung aller Fahrgäste minimiert und somit insgesamt die Zufriedenheit der Kunden mit dem Schienenverkehr verbessert.

## Installation

1. Repository klonen
```bash
git clone https://github.com/Speedo/Team_NULL.git
```
2. Docker Image erstellen
```bash
docker build -t [Name] .
```

## Ausführen

Damit das Programm korrekt ausgeführt werden kann muss folgendes gegeben sein:

- Der Docker-Container muss im interactive-mode ausgeführt werden
- Inputs müssen über den Standardinput übergeben werden

Sind diese Vorraussetzungen gegeben, kann das Programm mit folgendem Befehl ausgeführt werden
```bash
cat /pfad/zum/input | docker run -i --rm [Name]
```

## Teilnehmer
- Silas Trippler (silas.trippler@web.de)
- Johannes Böhmer (johannesboehmer0@gmail.com)
- Ferdinand Pfeifer (ferdinand.pfeifer@student.uni-siegen.de)
- Jens Vollmer (jens.vollmer@student.uni-siegen.de)

## Wettbewerb

[informatiCup 2022](https://github.com/informatiCup/informatiCup2022)
