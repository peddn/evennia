# Small example world for trying out the German contrib.
#
# Run in-game, as a superuser or builder, with
#
#     batchcode base_systems.german.example_world
#
# It builds two rooms with a few things, gives you the German commands and
# moves you there. Everything created is tagged "german_example".

# HEADER

from evennia import create_object, settings
from evennia.contrib.base_systems.german import GermanCmdSet, GermanObjectMixin

# CODE

if not isinstance(caller, GermanObjectMixin):
    raise RuntimeError(
        "Zuerst das Mixin einrichten (siehe README): in typeclasses/objects.py "
        "'class ObjectParent(GermanObjectMixin):', dann 'reload'."
    )


def create(typeclass, key, location=None, grammar=(), desc=None, **kwargs):
    """Create a tagged object with grammar and description."""
    obj = create_object(typeclass, key=key, location=location, tags=["german_example"], **kwargs)
    obj.set_grammar(*grammar)
    obj.db.desc = desc or obj.db.desc
    return obj


room, exit_, thing = (
    settings.BASE_ROOM_TYPECLASS,
    settings.BASE_EXIT_TYPECLASS,
    settings.BASE_OBJECT_TYPECLASS,
)

markt = create(room, "Marktplatz", desc="Ein staubiger Platz unter alten Linden.")
schmiede = create(room, "Schmiede", desc="Hitze und Hammerschläge erfüllen den Raum.")
create(exit_, "Norden", markt, aliases=["n"], destination=schmiede)
create(exit_, "Süden", schmiede, aliases=["s"], destination=markt)

create(thing, "Dolch", markt, ("m", "Dolche", "alt rostig"), "Scharf ist er nicht mehr.")
create(thing, "Truhe", markt, ("f", "Truhen", "schwer"))
create(thing, "Stein", markt, desc="Ein Gegenstand ohne Grammatik, also ohne Artikel.")
for _ in range(3):
    create(thing, "Apfel", markt, ("m", "Äpfel", "rot"))
for _ in range(2):
    create(thing, "Lampe", markt, ("f", "Lampen"))

create(thing, "Schwert", schmiede, ("n", "Schwerter", "alt"))
create(thing, "Drache", schmiede, ("m", "Drachen", "klein", "Drachen"), "Er döst in der Esse.")
create(settings.BASE_CHARACTER_TYPECLASS, "Anna", schmiede, desc="Die Schmiedin.")

caller.cmdset.add(GermanCmdSet, persistent=True)
caller.move_to(markt, quiet=True)
caller.msg("Beispielwelt erstellt. Probiere: schau, schau den alten Dolch, norden, schau mich")
