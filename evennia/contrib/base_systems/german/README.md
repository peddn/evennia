# German commands and grammar

Contribution by peddn, 2026

German versions of player commands that work next to the English ones, with
grammatically correct names for the things they mention: "Du siehst: einen
rostigen Dolch, zwei Lampen und eine Truhe."

| Command     | Replaces | Notes                                |
| ----------- | -------- | ------------------------------------ |
| `schau`     | `look`   | aliases `schaue`, `sieh`, `betrachte` |
| `grammatik` | -        | builders set an object's grammar     |

Players can search with articles and inflected adjectives (`schau den rostigen
Dolch`) and use `ich`, `mich`, `mir` and `hier` like `me` and `here`.

## Installation

Add the mixin to `ObjectParent`, which all your objects, characters, rooms
and exits inherit from:

```python
# in mygame/typeclasses/objects.py
from evennia.contrib.base_systems.german import GermanObjectMixin

class ObjectParent(GermanObjectMixin):
    ...
```

Add the commands:

```python
# in mygame/commands/default_cmdsets.py
from evennia.contrib.base_systems.german import GermanCmdSet

class CharacterCmdSet(default_cmds.CharacterCmdSet):
    def at_cmdset_creation(self):
        super().at_cmdset_creation()
        self.add(GermanCmdSet)
```

For the strings Evennia translates itself, also set `USE_I18N = True` and
`LANGUAGE_CODE = "de"` in your settings.

## Example world

With the mixin in place and the server reloaded, build a small test area
and get moved there (this also gives you the German commands):

    batchcode base_systems.german.example_world

Remove it again with `py [o.delete() for o in evennia.search_tag("german_example")]`.

## Grammar

German articles and endings cannot be guessed, so every object needs its
grammar set once. The key is the bare noun in nominative singular.

```python
dolch = create_object(Object, key="Dolch")
dolch.set_grammar("m", "Dolche", "alt rostig")         # gender, plural, adjective stems
drache.set_grammar("m", "Drachen", oblique="Drachen")  # der Drache, den Drachen
herz.set_grammar("n", "Herzen", genitive="Herzens")    # only for irregular genitives
```

Without `genitive`, the genitive is the `oblique` form or else the noun with
"-s" ("-es" after s, ß, x, z); feminine nouns stay unchanged.

In-game, builders use `grammatik Dolch = m, Dolche, alt rostig`. An object without
a gender is shown without article, as proper names should be.

Your own commands get inflected names from the standard Evennia hook:

```python
obj.get_numbered_name(1, looker, case="akk", return_string=True)                 # einen alten rostigen Dolch
obj.get_numbered_name(1, looker, case="gen", definite=True, return_string=True)  # des alten rostigen Dolchs
obj.get_numbered_name(3, looker, case="dat", return_string=True)                 # drei alten rostigen Dolchen
```

The grammar itself is available as the plain function `grammar.noun_phrase`.

## Limitations

- Call `set_grammar` again after renaming an object.
- English default commands keep working, but they do not ask for a case and
  so get the nominative, which is often wrong: "You pick up ein rostiger
  Dolch." Use the German commands instead.
