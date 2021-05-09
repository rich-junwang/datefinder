# from finder import extract_time_spans
# string_with_dates = '''
# Total amazon shares purchased between Jan. 1 2020 and may 01 2020
# '''
#
# string_with_dates = 'Total student old than Jan 1980'
# string_with_dates = 'Total student old than year 1980'
# string_with_dates = 'purchased between Jan. 1 2020 to may 01 2020'
#
# matches = extract_time_spans(string_with_dates, strict=False)
# for match in matches:
#     print(match[:2])


import re

YYYY_PATTERN = r"19\d\d|20\d\d"

pattern = re.compile(YYYY_PATTERN)

s = "in the year 2120"

matches = re.findall(pattern, s)
for match in matches:
    print(match)
