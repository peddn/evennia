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

Add the mixin to your typeclasses, before the Evennia parent:

```python
# in mygame/typeclasses/objects.py (same for characters.py and rooms.py)
from evennia.contrib.base_systems.german import GermanObjectMixin

class Object(GermanObjectMixin, ObjectParent, DefaultObject):
    pass
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

## Grammar

German articles and endings cannot be guessed, so every object needs its
grammar set once. The key is the bare noun in nominative singular.

```python
dolch = create_object(Object, key="Dolch")
dolch.set_grammar("m", "Dolche", "rostig")          # gender, plural, adjective stem
drache.set_grammar("m", "Drachen", oblique="Drachen")  # der Drache, den Drachen
```

In-game, builders use `grammatik Dolch = m, Dolche, rostig`. An object without
a gender is shown without article, as proper names should be.

Your own commands get inflected names from the standard Evennia hook:

```python
obj.get_numbered_name(1, looker, case="akk", return_string=True)                 # einen rostigen Dolch
obj.get_numbered_name(1, looker, case="dat", definite=True, return_string=True)  # dem rostigen Dolch
obj.get_numbered_name(3, looker, case="akk", return_string=True)                 # drei rostige Dolche
```

The grammar itself is available as the plain function `grammar.noun_phrase`.

## Limitations

- Cases are nominative (`nom`), accusative (`akk`) and dative (`dat`); no genitive.
- Call `set_grammar` again after renaming an object.
- English default commands keep working but mix languages ("You pick up ein Dolch").
