import re

# Named regular expression group
# In Python, the (?P<group_name>…) syntax allows one to refer to the matched string through its name:
'''
>>> import re
>>> match = re.search('(?P<name>.*) (?P<phone>.*)', 'John 123456')
>>> match.group('name')
>>> 'John'
'''


# how does ?: work
'''
Ordinarily, parentheses create a "capturing" group inside your regex:
>>> regex = re.compile("(set|let) var = (\\w+|\\d+)")
>>> print regex.match("set var = 12").groups()
>>> ('set', '12')

Later you can retrieve those groups by calling .groups() method on the result of a match. 
As you see whatever is inside parentheses is captured in "groups." But you might not care about all those groups.
Say you only want to find what's in the second group and not the first. 
You need the first set of parentheses in order to group "get" and "set" but you can turn off capturing by putting "?:" 
at the beginning:

>>> regex = re.compile("(?:set|let) var = (\\w+|\\d+)")
>>> print(regex.match("set var = 12").groups()regex = re.compile("(?:set|let) var = (\\w+|\\d+)"))
'''


def extract_number_convert_to_float():
    # This method will parse the suffix and return the corresponding multiplier, else 1
    def xNumber(arg):
        switcher = {
            "mln": 1000000,
            "million": 1000000,
            "bln": 1000000000,
            "billion": 1000000000,
            "thousand": 1000,
            "hundred": 100
        }
        return switcher.get(arg, 1)

    rx = re.compile(
        r'\$(?P<number>\d+(?:,\d{3})?(?:\.\d+)?(?:-\d+(?:,\d{3})?(?:\.\d+)?)?)(?:\s*(?P<suffix>mln|million|bln|billion|thousand|hundred))?')
    s = "$3 million, $910,000,$16.5-18 million"
    result = ""
    for match in rx.finditer(s):
        if match.group("suffix") and match.group("number").find("-") == -1:  # We have no range and have a suffix
            result = str(float(match.group("number")) * xNumber(match.group("suffix")))
        elif match.group("number").find("-") > -1:  # Range
            lst = [float(x) for x in match.group("number").split("-")]
            result = str(float(sum(lst)) / len(lst)) + (
                " {}".format(match.group("suffix")) if match.group("suffix") else "")
        else:
            result = float(match.group("number").replace(",", ""))  # Just return the number found converted to a float
        print(result)


def extract_number_from_text(s):
    rx = re.compile(
        r'\$*(?P<number>\d+(?:,\d{3})*(?:\.\d+)?)(?:\s*(?P<suffix>mln|million|bln|billion|thousand|hundred))?')

    res = []
    for i, match in enumerate(rx.finditer(s)):
        res.append(match.span())

    return res


def test_extract_number_from_text():
    s = "3 million, 910,000 16.5-18 million"
    matches = extract_number_from_text(s)
    for span in matches:
        print(span, s[span[0]:span[1]])


test_extract_number_from_text()
