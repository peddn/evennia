"""
Tests for the German contrib.

"""

from unittest import TestCase

from django.test import override_settings

from evennia import (
    DefaultCharacter,
    DefaultExit,
    DefaultObject,
    DefaultRoom,
    create_object,
)
from evennia.utils.batchprocessors import BATCHCODE
from evennia.utils.test_resources import BaseEvenniaCommandTest

from .german import CmdGrammatik, CmdSchau, GermanObjectMixin
from .grammar import noun_phrase, strip_article


class TestNounPhrase(TestCase):
    """Pure grammar, no database."""

    def test_no_gender_gives_bare_noun(self):
        self.assertEqual(noun_phrase("Anna", case="akk"), "Anna")

    def test_indefinite_article_by_gender_and_case(self):
        self.assertEqual(noun_phrase("Apfel", "m"), "ein Apfel")
        self.assertEqual(noun_phrase("Apfel", "m", case="akk"), "einen Apfel")
        self.assertEqual(noun_phrase("Lampe", "f", case="dat"), "einer Lampe")
        self.assertEqual(noun_phrase("Schwert", "n", case="akk"), "ein Schwert")

    def test_definite_article(self):
        self.assertEqual(noun_phrase("Apfel", "m", case="akk", definite=True), "den Apfel")
        self.assertEqual(noun_phrase("Lampe", "f", case="dat", definite=True), "der Lampe")
        self.assertEqual(noun_phrase("Schwert", "n", case="dat", definite=True), "dem Schwert")

    def test_adjective_endings(self):
        dolch = dict(noun="Dolch", gender="m", adjective="rostig")
        self.assertEqual(noun_phrase(**dolch), "ein rostiger Dolch")
        self.assertEqual(noun_phrase(**dolch, case="akk"), "einen rostigen Dolch")
        self.assertEqual(noun_phrase(**dolch, definite=True), "der rostige Dolch")
        self.assertEqual(noun_phrase(**dolch, case="dat", definite=True), "dem rostigen Dolch")
        self.assertEqual(noun_phrase("Schwert", "n", adjective="alt"), "ein altes Schwert")
        self.assertEqual(
            noun_phrase("Lampe", "f", adjective="klein", case="akk"), "eine kleine Lampe"
        )

    def test_plural(self):
        apfel = dict(noun="Apfel", gender="m", plural="Äpfel")
        self.assertEqual(noun_phrase(**apfel, count=2), "zwei Äpfel")
        self.assertEqual(noun_phrase(**apfel, count=13), "13 Äpfel")
        self.assertEqual(noun_phrase(**apfel, count=3, case="dat"), "drei Äpfeln")
        self.assertEqual(noun_phrase(**apfel, count=2, definite=True), "die zwei Äpfel")
        self.assertEqual(noun_phrase("Lampe", "f", "Lampen", count=2, case="dat"), "zwei Lampen")
        self.assertEqual(noun_phrase("Messer", "n", count=2), "zwei Messer")

    def test_plural_adjective(self):
        dolch = dict(noun="Dolch", gender="m", plural="Dolche", adjective="rostig", count=2)
        self.assertEqual(noun_phrase(**dolch), "zwei rostige Dolche")
        self.assertEqual(noun_phrase(**dolch, case="dat"), "zwei rostigen Dolchen")
        self.assertEqual(noun_phrase(**dolch, definite=True), "die zwei rostigen Dolche")

    def test_oblique_form(self):
        drache = dict(noun="Drache", gender="m", oblique="Drachen")
        self.assertEqual(noun_phrase(**drache), "ein Drache")
        self.assertEqual(noun_phrase(**drache, case="akk"), "einen Drachen")
        self.assertEqual(noun_phrase(**drache, case="dat", definite=True), "dem Drachen")

    def test_several_adjectives(self):
        dolch = dict(noun="Dolch", gender="m", plural="Dolche", adjective="alt rostig")
        self.assertEqual(noun_phrase(**dolch), "ein alter rostiger Dolch")
        self.assertEqual(noun_phrase(**dolch, case="akk"), "einen alten rostigen Dolch")
        self.assertEqual(noun_phrase(**dolch, count=2), "zwei alte rostige Dolche")

    def test_genitive(self):
        self.assertEqual(noun_phrase("Dolch", "m", case="gen", definite=True), "des Dolchs")
        self.assertEqual(noun_phrase("Schloss", "n", case="gen"), "eines Schlosses")
        self.assertEqual(noun_phrase("Lampe", "f", case="gen", definite=True), "der Lampe")
        self.assertEqual(
            noun_phrase("Dolch", "m", adjective="rostig", case="gen"), "eines rostigen Dolchs"
        )
        self.assertEqual(
            noun_phrase("Drache", "m", oblique="Drachen", case="gen", definite=True), "des Drachen"
        )
        self.assertEqual(
            noun_phrase("Herz", "n", genitive="Herzens", case="gen", definite=True), "des Herzens"
        )
        self.assertEqual(noun_phrase("Herz", "n", genitive="Herzens", case="akk"), "ein Herz")
        self.assertEqual(noun_phrase("Anna", case="gen"), "Annas")
        self.assertEqual(noun_phrase("Hans", case="gen"), "Hans'")
        apfel = dict(noun="Apfel", gender="m", plural="Äpfel", adjective="rot", count=2, case="gen")
        self.assertEqual(noun_phrase(**apfel), "zwei roter Äpfel")
        self.assertEqual(noun_phrase(**apfel, definite=True), "der zwei roten Äpfel")

    def test_strip_article(self):
        self.assertEqual(strip_article("den rostigen Dolch"), "rostigen Dolch")
        self.assertEqual(strip_article("Eine Lampe"), "Lampe")
        self.assertEqual(strip_article("Dolch"), "Dolch")
        self.assertEqual(strip_article("der"), "der")


class GermanObject(GermanObjectMixin, DefaultObject):
    """Test typeclass."""


class GermanCharacter(GermanObjectMixin, DefaultCharacter):
    """Test typeclass."""


class GermanRoom(GermanObjectMixin, DefaultRoom):
    """Test typeclass."""


class GermanExit(GermanObjectMixin, DefaultExit):
    """Test typeclass."""


class TestGermanCommands(BaseEvenniaCommandTest):
    """Mixin and commands against real objects."""

    object_typeclass = GermanObject
    character_typeclass = GermanCharacter
    room_typeclass = GermanRoom

    def setUp(self):
        super().setUp()
        self.obj1.key = "Dolch"
        self.obj1.set_grammar("m", "Dolche", "rostig")
        self.obj2.key = "Lampe"
        self.obj2.set_grammar("f", "Lampen")

    def test_numbered_name(self):
        name = self.obj1.get_numbered_name
        self.assertEqual(
            name(1, self.char2, case="akk", return_string=True), "einen rostigen Dolch"
        )
        self.assertEqual(name(2, self.char2), ("ein rostiger Dolch", "zwei rostige Dolche"))
        self.assertEqual(name(1, self.char2, no_article=True, return_string=True), "Dolch")

    def test_schau_room(self):
        create_object(GermanObject, key="Lampe", location=self.room1).set_grammar("f", "Lampen")
        create_object(GermanObject, key="Stein", location=self.room1)
        self.call(
            CmdSchau(),
            "",
            "Room\nroom_desc\nAusgänge: out\nPersonen: Char\n"
            "Du siehst: einen rostigen Dolch, zwei Lampen und Stein.",
            caller=self.char2,
        )

    def test_schau_object(self):
        self.obj1.db.desc = "Scharf ist er nicht mehr."
        for query in ("Dolch", "den Dolch", "den rostigen Dolch", "rostiger dolch"):
            self.call(CmdSchau(), query, "Dolch\nScharf ist er nicht mehr.", caller=self.char2)

    def test_search_several_adjectives(self):
        self.obj1.set_grammar("m", "Dolche", "alt rostig")
        for query in ("alten Dolch", "den rostigen Dolch", "alten rostigen Dolch"):
            self.assertEqual(self.char2.search(query), self.obj1)
        self.assertIsNone(self.char2.search("rostigen alten Dolch", quiet=True) or None)

    def test_schau_self_and_here(self):
        self.call(CmdSchau(), "mich", "Char2", caller=self.char2)
        self.call(CmdSchau(), "hier", "Room", caller=self.char2)

    def test_grammatik(self):
        self.call(CmdGrammatik(), "Lampe = f, Lampen, klein", "Lampe: eine kleine Lampe, zwei")
        self.assertEqual(self.obj2.adjective, "klein")
        self.call(CmdGrammatik(), "Lampe", "Lampe: eine kleine Lampe, zwei kleine Lampen")
        self.call(
            CmdGrammatik(), "Lampe = f, Lampen, alt klein, , Lampes", "Lampe: eine alte kleine"
        )
        self.assertEqual(self.obj2.genitive, "Lampes")
        self.call(CmdGrammatik(), "Lampe = x", "Das Geschlecht muss m, f oder n sein.")
        self.call(CmdGrammatik(), "", "Verwendung: grammatik")

    @override_settings(
        BASE_OBJECT_TYPECLASS=f"{__name__}.GermanObject",
        BASE_CHARACTER_TYPECLASS=f"{__name__}.GermanCharacter",
        BASE_ROOM_TYPECLASS=f"{__name__}.GermanRoom",
        BASE_EXIT_TYPECLASS=f"{__name__}.GermanExit",
    )
    def test_example_world(self):
        for code in BATCHCODE.parse_file("base_systems.german.example_world"):
            self.assertIsNone(BATCHCODE.code_exec(code, extra_environ={"caller": self.char2}))
        self.call(
            CmdSchau(),
            "",
            "Marktplatz\nEin staubiger Platz unter alten Linden.\nAusgänge: Norden\n"
            "Du siehst: drei rote Äpfel, einen alten rostigen Dolch, zwei Lampen, Stein "
            "und eine schwere Truhe.",
            caller=self.char2,
        )
        self.char2.execute_cmd("norden")
        self.call(CmdSchau(), "den kleinen Drachen", "Drache\nEr döst", caller=self.char2)
