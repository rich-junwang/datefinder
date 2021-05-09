import regex as re

NUMBERS_PATTERN = r"first|second|third|fourth|fifth|sixth|seventh|eighth|ninth|tenth"
POSITIONNAL_TOKENS = r"next|last|previous"
DIGITS_PATTERN = r"\d+"
DIGITS_SUFFIXES = r"st|th|rd|nd"
DAYS_PATTERN = "monday|tuesday|wednesday|thursday|friday|saturday|sunday|mon|tue|tues|wed|thur|thurs|fri|sat|sun"
MONTHS_PATTERN = r"january|february|march|april|may|june|july|august|september|october|november|december" \
                 r"|enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|octubre|noviembre|diciembre" \
                 r"|jan\.?|ene\.?|feb\.?|mar\.?|apr\.?|abr\.?|may\.?|jun\.?|jul\.?|aug\.?" \
                 r"|sep\.?|sept\.?|oct\.?|nov\.?|dec\.?|dic\.?"

YYYY_PATTERN = r"19\d\d|20\d\d"
YYYYMM_PATTERN = r"19\d\d01|20\d\d01|19\d\d02|20\d\d02|19\d\d03|20\d\d03|19\d\d04|20\d\d04|19\d\d05|20\d" \
                 r"\d05|19\d\d06|20\d\d06|19\d\d07|20\d\d07|19\d\d08|20\d\d08|19\d\d09|20\d\d09|19\d\d10|20" \
                 r"\d\d10|19\d\d11|20\d\d11|19\d\d12|20\d\d12"

YYYYMMDD_PATTERN = r"19\d\d01[0123]\d|20\d\d01[0123]\d|19\d\d02[0123]\d|20\d\d02[0123]\d|19\d\d03[0123]\d|20\d" \
                   r"\d03[0123]\d|19\d\d04[0123]\d|20\d\d04[0123]\d|19\d\d05[0123]\d|20\d\d05[0123]\d|19\d" \
                   r"\d06[0123]\d|20\d\d06[0123]\d|19\d\d07[0123]\d|20\d\d07[0123]\d|19\d\d08[0123]\d|20\d" \
                   r"\d08[0123]\d|19\d\d09[0123]\d|20\d\d09[0123]\d|19\d\d10[0123]\d|20\d\d10[0123]\d|19\d" \
                   r"\d11[0123]\d|20\d\d11[0123]\d|19\d\d12[0123]\d|20\d\d12[0123]\d"

DELIMITERS_PATTERN = r"[/\:\-\,\.\s\_\+\@]+"
EXTRA_TOKENS_PATTERN = r"time|date|dated|days|months|quarters|years"
RELATIVE_PATTERN = ""
DATES_PATTERN = """
(
    (
        ## Grab any four digit years
        (?P<years>{years})
        |
        ## Numbers
        (?P<numbers>{numbers})
        ## Grab any digits
        |
        (?P<digits>{digits})(?P<digits_suffixes>{digits_suffixes})?
        |
        (?P<days>{days})
        |
        (?P<months>{months})
        |
        ## Delimiters, ie Tuesday[,] July 18 or 6[/]17[/]2008
        ## as well as whitespace
        (?P<delimiters>{delimiters})
        |
        (?P<positionnal_tokens>{positionnal_tokens})
        |
        ## These tokens could be in phrases that dateutil does not yet recognize
        ## Some are US Centric
        (?P<extra_tokens>{extra_tokens})
    ## We need at least three items to match for minimal datetime parsing
    ## ie 10pm
    ){{1,1}}
)
"""

DATES_PATTERN = DATES_PATTERN.format(
    years=YYYY_PATTERN,
    numbers=NUMBERS_PATTERN,
    digits=DIGITS_PATTERN,
    digits_suffixes=DIGITS_SUFFIXES,
    days=DAYS_PATTERN,
    months=MONTHS_PATTERN,
    delimiters=DELIMITERS_PATTERN,
    positionnal_tokens=POSITIONNAL_TOKENS,
    extra_tokens=EXTRA_TOKENS_PATTERN,
)

# Define all the group of patterns we want to match against. This builds the capture dict
ALL_GROUPS = ['time', 'years', 'numbers', 'digits', 'digits_suffixes', 'days',
              'months', 'delimiters', 'positionnal_tokens', 'extra_tokens',
              'hours', 'minutes', 'seconds', 'microseconds', 'time_periods', 'timezones']

DATE_REGEX = re.compile(
    DATES_PATTERN, re.IGNORECASE | re.MULTILINE | re.UNICODE | re.DOTALL | re.VERBOSE
)

RANGE_SPLIT_PATTERN = r'\Wto\W|\Wthrough\W'
RANGE_SPLIT_REGEX = re.compile(RANGE_SPLIT_PATTERN, re.IGNORECASE | re.MULTILINE | re.UNICODE | re.DOTALL)


class DateMatches:
    def __init__(self):
        self.match_str = ''
        self.indices = (0, 0)
        self.captures = dict()

    def __repr__(self):
        str_capt = ', '.join(['"{}": [{}]'.format(c, self.captures[c]) for c in self.captures])
        return '{} [{}, {}]\nCaptures: {}'.format(self.match_str, self.indices[0], self.indices[1], str_capt)

    def get_captures_count(self):
        # Each key has a list of values. All values will format the final text span
        return sum([len(self.captures[m]) for m in self.captures])


def split_date_range(text):
    st_matches = RANGE_SPLIT_REGEX.finditer(text)
    start = 0
    parts = []  # List[Tuple[str, Tuple[int, int]]]

    for match in st_matches:
        match_start = match.start()
        if match_start > start:
            parts.append((text[start:match_start], (start, match_start)))
        start = match.end()

    if start < len(text):
        parts.append((text[start:], (start, len(text))))

    return parts


def extract_date_from_strings(text, text_start=0):
    rng = split_date_range(text)
    if rng and len(rng) > 1:
        range_strings = []
        for range_str in rng:
            range_strings.extend(extract_date_from_strings(range_str[0], text_start=range_str[1][0]))
        for range_string in range_strings:
            yield range_string
        return

    tokens = extract_matches_of_patterns(text)
    items = merge_matched_parts(tokens)
    for match in items:
        match_str = match.match_str
        indices = (match.indices[0] + text_start, match.indices[1] + text_start)

        match_str = match_str.strip()
        start = text.find(match_str, indices[0])

        yield match_str, (start, start + len(match_str))


def extract_matches_of_patterns(text):
    """
    use regex pattern to find all groups of matched cases. year, time, number, month etc
    :param text: text to extract date
    :return: list of regex matched pieces
    """
    items = []
    last_index = 0

    for match in DATE_REGEX.finditer(text):
        match_str = match.group(0)
        indices = match.span(0)
        # capture is a dict which key is the group name we defined in our pattern.
        # value is a list of captured/matched text
        captures = match.capturesdict()
        group = get_token_group(captures)

        if indices[0] > last_index:
            items.append((text[last_index: indices[0]], "", {}))
        items.append((match_str, group, captures))
        last_index = indices[1]
    if last_index < len(text):
        items.append((text[last_index: len(text)], "", {}))
    return items


def merge_matched_parts(tokens, min_matches=1):
    """
    Merge matched text part into date spans. E.g. month, day and year could be a single date span.
    :param min_matches: minimum number of pieces to merge
    :param tokens: pieces of text matched with various patterns
    :return: chunk of text, with matching info
    """
    fragments = []
    frag = DateMatches()

    start_char, total_chars = 0, 0

    for token in tokens:
        total_chars += len(token[0])

        tok_text, group, tok_capts = token[0], token[1], token[2]

        # when current matched text not in predefined group, we merge the previous
        # matched pieces into a single span
        if not group:
            if frag.indices[1] > 0:
                if frag.get_captures_count() >= min_matches:
                    fragments.append(frag)

            frag = DateMatches()
            start_char = total_chars
            continue

        if frag.indices[1] == 0:
            frag.indices = (start_char, total_chars)
        else:
            frag.indices = (frag.indices[0], total_chars)  # -1

        frag.match_str += tok_text

        for capt in tok_capts:
            if capt in frag.captures:
                frag.captures[capt] += tok_capts[capt]
            else:
                frag.captures[capt] = tok_capts[capt]

        start_char = total_chars

    # merge the final piece
    if frag.get_captures_count() >= min_matches:
        fragments.append(frag)

    for frag in fragments:
        for gr in ALL_GROUPS:
            if gr not in frag.captures:
                frag.captures[gr] = []

    return fragments


def get_token_group(captures):
    for gr in ALL_GROUPS:
        lst = captures.get(gr)
        if lst and len(lst) > 0:
            return gr
    return ""


def extract_time_spans(text, text_start=0):
    time_spans_generator = extract_date_from_strings(text, text_start=text_start)
    results = []
    for text, span in time_spans_generator:
        if len(text) > 1:
            results.append((text, span))
    return results


if __name__ == "__main__":
    # only support time span where there is number
    s = "purchased between Jan 2020 and may 01 2020 and then it's 2020, and 31st Oct 1900"
    # s = 'purchased between 01/2020 and 05/01/2020'
    # s = "in week 14 on 31st december 2018"
    # s = "week 14 in season 2019"
    # s = 'Total student older than year 1980'
    # s = "today at 9"
    # s = "price 3 days ago"
    # s = "price last week"
    # s = "price last quarter"

    matches = extract_time_spans(s)
    print(matches)
