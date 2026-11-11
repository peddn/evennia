"""
German noun phrases.

Pure functions building phrases like "einen rostigen Dolch" or "zwei Äpfeln"
from a noun and its grammar data. Supports nominative, accusative and dative.

"""

_GENDERS = "mfn"
# per case: masculine, feminine, neuter, plural
_DEFINITE = {
    "nom": ("der", "die", "das", "die"),
    "akk": ("den", "die", "das", "die"),
    "dat": ("dem", "der", "dem", "den"),
}
_INDEFINITE = {
    "nom": ("ein", "eine", "ein"),
    "akk": ("einen", "eine", "ein"),
    "dat": ("einem", "einer", "einem"),
}
# adjective endings in singular, after a definite/indefinite article
_ENDINGS_DEFINITE = {"nom": ("e", "e", "e"), "akk": ("en", "e", "e"), "dat": ("en", "en", "en")}
_ENDINGS_INDEFINITE = {
    "nom": ("er", "e", "es"),
    "akk": ("en", "e", "es"),
    "dat": ("en", "en", "en"),
}
_NUMBERS = dict(
    enumerate("zwei drei vier fünf sechs sieben acht neun zehn elf zwölf".split(), start=2)
)
_ARTICLES = {
    word for table in (_DEFINITE, _INDEFINITE) for forms in table.values() for word in forms
}


def noun_phrase(
    noun,
    gender=None,
    plural=None,
    adjective=None,
    oblique=None,
    count=1,
    case="nom",
    definite=False,
):
    """
    Build a German noun phrase with article, adjective and number.

    Args:
        noun (str): The noun in nominative singular, like "Dolch".
        gender (str, optional): One of "m", "f" or "n". Without it, a single
            thing gets no article or adjective (as for proper names).
        plural (str, optional): Nominative plural, like "Dolche". Defaults to `noun`.
        adjective (str, optional): Adjective stem without ending, like "rostig".
        oblique (str, optional): Singular form used outside the nominative,
            for nouns like "Drache" -> "Drachen".
        count (int, optional): How many things there are.
        case (str, optional): One of "nom", "akk" or "dat".
        definite (bool, optional): Use the definite article.

    Returns:
        str: The phrase, like "einen rostigen Dolch" or "zwei Äpfeln".

    """
    if count == 1:
        if not gender:
            return noun
        index = _GENDERS.index(gender)
        article = (_DEFINITE if definite else _INDEFINITE)[case][index]
        ending = (_ENDINGS_DEFINITE if definite else _ENDINGS_INDEFINITE)[case][index]
        if oblique and case != "nom":
            noun = oblique
    else:
        number = _NUMBERS.get(count, str(count))
        article = f"{_DEFINITE[case][3]} {number}" if definite else number
        ending = "en" if definite or case == "dat" else "e"
        noun = plural or noun
        if case == "dat" and noun[-1] not in "ns":
            noun += "n"
    return f"{article} {adjective}{ending} {noun}" if adjective else f"{article} {noun}"


def strip_article(text):
    """
    Remove a leading article, so "den Dolch" can be searched for as "Dolch".

    Args:
        text (str): Text as typed by a player.

    Returns:
        str: The text without its leading article, if it had one.

    """
    first, _, rest = text.partition(" ")
    return rest.strip() if rest.strip() and first.lower() in _ARTICLES else text
