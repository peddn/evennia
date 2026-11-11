"""
German commands and grammar

Contribution by peddn, 2026

German versions of player commands, with correct articles, cases and
adjective endings for the things they mention. See the README for setup.

"""

from evennia import CmdSet, default_cmds
from evennia.typeclasses.attributes import AttributeProperty
from evennia.utils.utils import iter_to_str

from .grammar import noun_phrase, strip_article

_SELF_WORDS = {"ich": "me", "mich": "me", "mir": "me", "hier": "here"}
_ALIAS_CATEGORY = "german_grammar"


def _listing(title, names, end=""):
    """
    Format one line of a room description, like "Ausgänge: Norden und Osten".

    Args:
        title (str): What is listed.
        names (iterable): The names to list.
        end (str, optional): Added after the last name.

    Returns:
        str: The line, or an empty string if there are no names.

    """
    names = iter_to_str(names, endsep=" und")
    return f"|w{title}:|n {names}{end}" if names else ""


class GermanObjectMixin:
    """
    Add this to your Object, Character and Room typeclasses, before the
    Evennia parent class.

    """

    gender = AttributeProperty(None, autocreate=False)
    plural = AttributeProperty(None, autocreate=False)
    adjective = AttributeProperty(None, autocreate=False)
    oblique = AttributeProperty(None, autocreate=False)

    def set_grammar(self, gender=None, plural=None, adjective=None, oblique=None):
        """
        Set the grammar of this object's key. Call again after renaming it.

        Args:
            gender (str, optional): One of "m", "f" or "n". `None` for proper names.
            plural (str, optional): Nominative plural, like "Dolche".
            adjective (str, optional): Adjective stem without ending, like "rostig".
            oblique (str, optional): Singular form used outside the nominative,
                for nouns like "Drache" -> "Drachen".

        Notes:
            This also stores aliases so the object is found by its inflected
            forms, like "rostigen Dolch".

        """
        self.gender, self.plural, self.adjective, self.oblique = gender, plural, adjective, oblique
        forms = [f"{adjective}{ending} {self.key}" for ending in ("e", "er", "es", "en")]
        self.aliases.clear(category=_ALIAS_CATEGORY)
        self.aliases.batch_add(
            *((form, _ALIAS_CATEGORY) for form in (forms if adjective else []) + [oblique] if form)
        )

    def get_numbered_name(self, count, looker, **kwargs):
        """
        Evennia hook, returning this object's name with article or number.

        Args:
            count (int): Number of objects of this type.
            looker (DefaultObject): Onlooker.

        Keyword Args:
            key (str): Noun to use instead of the object's display name.
            return_string (bool): Return only the form matching `count`
                instead of a tuple.
            no_article (bool): Return the bare noun if `count` is 1.
            case (str): One of "nom" (default), "akk" or "dat".
            definite (bool): Use the definite article.

        Returns:
            tuple or str: `(singular, plural)` or, with `return_string`, one of them.

        """
        key = kwargs.get("key", self.get_display_name(looker))
        grammar = dict(
            gender=self.gender,
            plural=self.plural,
            adjective=self.adjective,
            oblique=self.oblique,
            case=kwargs.get("case", "nom"),
            definite=kwargs.get("definite", False),
        )
        singular = key if kwargs.get("no_article") else noun_phrase(key, **grammar)
        plural = noun_phrase(key, count=count, **grammar) if count > 1 else singular
        if kwargs.get("return_string"):
            return plural
        return singular, plural

    def get_search_query_replacement(self, searchdata, **kwargs):
        """
        Evennia hook. Lets players search with a leading article.

        Args:
            searchdata (str): The search string.
            **kwargs: Same as passed to `search`.

        Returns:
            str: The search string to use.

        """
        searchdata = super().get_search_query_replacement(searchdata, **kwargs)
        return strip_article(searchdata) if isinstance(searchdata, str) else searchdata

    def get_search_direct_match(self, searchdata, **kwargs):
        """
        Evennia hook. Adds "ich", "mich", "mir" and "hier" to "me" and "here".

        Args:
            searchdata (str): The search string.
            **kwargs: Same as passed to `search`.

        Returns:
            tuple: `(should_return, str or Obj)`, see the parent method.

        """
        if isinstance(searchdata, str):
            searchdata = _SELF_WORDS.get(searchdata.lower(), searchdata)
        return super().get_search_direct_match(searchdata, **kwargs)

    def get_display_exits(self, looker, **kwargs):
        """
        Evennia hook, the exits line of the description.

        Args:
            looker (DefaultObject): Object doing the looking.
            **kwargs: Arbitrary data for use when overriding.

        Returns:
            str: The exits line.

        """
        exits = self.filter_visible(self.contents_get(content_type="exit"), looker, **kwargs)
        return _listing("Ausgänge", sorted(e.get_display_name(looker, **kwargs) for e in exits))

    def get_display_characters(self, looker, **kwargs):
        """
        Evennia hook, the characters line of the description.

        Args:
            looker (DefaultObject): Object doing the looking.
            **kwargs: Arbitrary data for use when overriding.

        Returns:
            str: The characters line.

        """
        chars = self.filter_visible(self.contents_get(content_type="character"), looker, **kwargs)
        return _listing("Personen", (c.get_display_name(looker, **kwargs) for c in chars))

    def get_display_things(self, looker, **kwargs):
        """
        Evennia hook, the things line of the description. Same-named things
        are grouped, like "zwei Lampen".

        Args:
            looker (DefaultObject): Object doing the looking.
            **kwargs: Arbitrary data for use when overriding.

        Returns:
            str: The things line.

        """
        groups = {}
        for thing in self.filter_visible(
            self.contents_get(content_type="object"), looker, **kwargs
        ):
            groups.setdefault(thing.get_display_name(looker, **kwargs), []).append(thing)
        names = (
            things[0].get_numbered_name(len(things), looker, key=name, case="akk")[len(things) > 1]
            for name, things in sorted(groups.items())
        )
        return _listing("Du siehst", names, end=".")


class CmdSchau(default_cmds.CmdLook):
    """
    Umgebung oder Gegenstand ansehen

    Verwendung:
      schau
      schau <Gegenstand>
      schau *<Konto>

    Betrachtet deinen Aufenthaltsort oder etwas in deiner Nähe.
    """

    key = "schau"
    aliases = ["schaue", "sieh", "betrachte"]
    help_category = "Allgemein"

    def func(self):
        """Handle the looking."""
        caller = self.caller
        target = caller.search(self.args) if self.args else caller.location
        if self.args and not target:
            return
        if not target:
            caller.msg("Du bist nirgendwo, es gibt nichts zu sehen!")
            return
        self.msg(text=(caller.at_look(target), {"type": "look"}), options=None)


class CmdGrammatik(default_cmds.MuxCommand):
    """
    Grammatik eines Gegenstands festlegen

    Verwendung:
      grammatik <Gegenstand>
      grammatik <Gegenstand> = <Geschlecht>[, <Mehrzahl>[, <Adjektiv>[, <Beugung>]]]

    Beispiele:
      grammatik Dolch = m, Dolche, rostig
      grammatik Drache = m, Drachen, , Drachen

    Das Geschlecht ist m, f oder n. Das Adjektiv wird ohne Endung angegeben
    ("rostig", "teur"). Die Beugung ist nur für Wörter nötig, die außerhalb
    des Nominativs eine Endung bekommen ("der Drache", aber "den Drachen").
    Ohne Angaben wird die aktuelle Grammatik angezeigt.
    """

    key = "grammatik"
    locks = "cmd:perm(Builder)"
    help_category = "Building"

    def func(self):
        """Set or show the grammar."""
        if not self.lhs:
            self.msg(
                "Verwendung: grammatik <Gegenstand> = <Geschlecht>[, <Mehrzahl>[, <Adjektiv>]]"
            )
            return
        obj = self.caller.search(self.lhs)
        if not obj:
            return
        if self.rhs:
            gender, *rest = (part.strip() or None for part in self.rhs.split(","))
            if gender not in ("m", "f", "n"):
                self.msg("Das Geschlecht muss m, f oder n sein.")
                return
            obj.set_grammar(gender, *rest[:3])
        self.msg(f"{obj.key}: " + ", ".join(obj.get_numbered_name(2, self.caller, key=obj.key)))


class GermanCmdSet(CmdSet):
    """
    German player commands. They are added next to the English ones.

    """

    def at_cmdset_creation(self):
        """Populate the cmdset."""
        self.add(CmdSchau)
        self.add(CmdGrammatik)
