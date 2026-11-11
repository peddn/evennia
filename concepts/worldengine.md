# Konzept: World-Engine für Wilderness + ExtendedRoom

Status: **Konzept, noch nichts gebaut.** Arbeitsname offen (`grid/worldstate`?).

## Ziel

Ein Contrib, das Wilderness-Räume anhand ihrer Koordinaten mit Zuständen
füllt (Wetter, Ressourcen, Fluten, umkämpfte Gebiete) und diese über die
Zustände und Details von ExtendedRoom sichtbar macht. Dazu eine Kartenausgabe.

## Entschiedene Punkte

- **2D.** Koordinaten sind `(x, y)` wie in Wilderness. Mehrere Ebenen wären
  getrennte, benannte Karten.
- **Karten werden von Hand gezeichnet** (Textdatei + Legende). Die Legende
  legt pro Zeichen Name, Begehbarkeit, Beschreibung und Details fest.
- **Ressourcen werden von Hand eingezeichnet** (eigene Kartenebene), nicht
  per Noise gestreut.
- **Ressourcen sind virtuell**: Die Engine meldet "hier gibt es Eisen", ein
  Gegenstand entsteht erst beim Abbauen. Der Sammelbefehl selbst ist
  spielspezifisch und gehört nicht ins Contrib (nur Schnittstelle + Beispiel).
  *(Vorschlag, vom Spieler noch nicht ausdrücklich bestätigt.)*
- **Später beide Größen**: große freie Gebiete (Wilderness) und kleine
  Städte/Dungeons/Dörfer (eher XYZGrid, echte Räume).

## Aufbau

Zwei Bausteine, die Engine kennt keine konkrete Mechanik:

1. **Schichten** – Funktionen `(x, y, Zeit) → Zustände`.
   - Gezeichnete Ebenen (Gelände, Ressourcen): Gitter aus Datei, im
     Arbeitsspeicher.
   - Noise-Felder (Wetter): berechnet aus Seed + Spielzeit, kein Speicher,
     kein Ticker. Eigenes kleines Value-Noise statt Abhängigkeit.
2. **Abweichungen** – kleines Wörterbuch mit Ablaufzeit, das Schichten
   überschreibt (abgebaut, überflutet, umkämpft; Punkt oder Radius).

| Was | Wo | Nach Reload |
|---|---|---|
| Gezeichnete Karten | Datei → Arbeitsspeicher | neu geladen |
| Wetter | berechnet | ergibt dasselbe |
| Abweichungen | Arbeitsspeicher + Datenbank | gesichert, nur bei Änderung geschrieben |

Skizze der Nutzung:

```python
world.states((12, 40))                                   # {"gebirge", "regen", "eisen"}
world.override((12, 40), "eisen", False, duration=7200)  # abgebaut
world.override((50, 50), "ueberflutet", True, radius=5, duration=86400)
```

## Anbindung an die Contribs

Raumklasse aus `WildernessRoom` + `ExtendedRoom` mit drei kleinen
Überschreibungen:

- `room_states` kommt aus der Engine statt aus Tags (keine Schreibzugriffe
  beim Bewegen).
- Beschreibung pro Koordinate läuft durch den ExtendedRoom-Parser, damit
  `$state(regen, ...)` funktioniert (Wilderness gibt `ndb.active_desc` sonst
  roh zurück).
- Details pro Koordinate (`ndb.active_details`), ebenfalls mit `$state(...)`.

Nur Inline-`$state()` nutzen: ExtendedRoom zeigt von `desc_<zustand>` immer
nur eine, Zustände wären so nicht kombinierbar.

## Karte

Eigene Renderfunktion: Ausschnitt um den Spieler, pro Feld Engine abfragen,
Symbol nach Priorität (Spieler > Abweichung > Ressource > Gelände).
`ingame_map_display` passt nicht (läuft echte Räume über Ausgänge ab).

## Geplante Schritte (je ein Branch + PR)

1. Engine (Schichten, Abweichungen) + Raumklasse, mit Wetter und einer
   Ressource als Beispiel
2. Kartenausgabe + `karte`-Befehl
3. Meldungen bei Zustandswechsel ("Es beginnt zu regnen") – braucht Ticker
   über belegte Räume

Grobe Größe für 1 + 2: etwa 350 Zeilen plus Tests.

## Offene Punkte

- **Engine unabhängig von Wilderness?** Wenn später auch XYZGrid-Gebiete
  Wetter usw. bekommen sollen, darf die Engine nur Kartenname + Koordinaten
  kennen; Wilderness wäre dann nur ein Abnehmer. Übergänge zwischen
  Wilderness und Städten sind ungeklärt.
- Diskrete Wetterzustände oder auch Werte (Temperatur, Windstärke)?
- Ressourcen: nur vorhanden/abgebaut mit Nachwachszeit, oder Mengen?
- Dateiformat der Karten (eine Datei pro Ebene? Größe bis ~2000 × 2000?)
- Individuelle Beschreibungen einzelner Felder (bisher: eine pro Geländetyp)
- Name des Contribs
