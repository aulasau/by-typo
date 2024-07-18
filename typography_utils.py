"""
Adaptation of https://github.com/DanilovM/SBOLTypograph to Python and Belarusian.
https://claude.ai was used to rewrite js into python, so this is why all functions aren't written in the same style
"""

from typing import Match
import re
import regex  # more powerful package for lookbehinds with variable length
from itertools import product


def generate_combinations(text, symbols):
    """Need this func for word sets like "для таго каб" (look at nbsp_multiple_words.txt)
    and for all their combinations with usual space symbol and NBSP-symbol.
    generate_combinations('для таго каб', [' ', '_NBSP_']) =>
     ['для таго каб',
     'для таго_NBSP_каб',
     'для_NBSP_таго каб',
     'для_NBSP_таго_NBSP_каб']
    """
    words = text.split()
    spaces = len(words) - 1
    # Generate all possible combinations of symbols
    symbol_combinations = product(symbols, repeat=spaces)
    result = []
    for combination in symbol_combinations:
        new_text = words[0]
        for i, symbol in enumerate(combination):
            new_text += symbol + words[i + 1]
        result.append(new_text)
    return result


class ByTypograph:
    def __init__(self, calendar_file_path, nbsp_before_file, nbsp_after_file, nbsp_multiple_words_file):
        words = self.extract_data_from_files(calendar_file_path, nbsp_before_file, nbsp_after_file, nbsp_multiple_words_file)
        for key, value in words.items():
            self.__setattr__(key, value)

    @staticmethod
    def extract_data_from_files(calendar_file_path, nbsp_before_file, nbsp_after_file, nbsp_multiple_words_file):
        month = ""
        month_short = ""
        weekday = ""
        weekday_short = ""
        before_nbsp = ""
        after_nbsp = ""
        multiple_words_nbsp = ""

        # Read calendar file
        with open(calendar_file_path, 'r', encoding='utf-8') as file:
            for line in file:
                line = line.strip()
                if line.startswith("month ="):
                    month = line.split("=", 1)[1].strip()
                elif line.startswith("month_short ="):
                    month_short = line.split("=", 1)[1].strip()
                elif line.startswith("weekday ="):
                    weekday = line.split("=", 1)[1].strip()
                elif line.startswith("weekday_short ="):
                    weekday_short = line.split("=", 1)[1].strip()

        # Read NBSP files
        nbsp_words = []
        for nbsp_file_path in [nbsp_before_file, nbsp_after_file, nbsp_multiple_words_file]:
            with open(nbsp_file_path, 'r', encoding='utf-8') as file:
                nbsp_words.append('|'.join(file.readlines()).replace("\n", ""))
        before_nbsp, after_nbsp, multiple_words_nbsp = nbsp_words

        multiples = []
        for m in multiple_words_nbsp.split('|'):
            multiples.extend(generate_combinations(m, [' ', '\u00A0']))
        multiple_words_nbsp = "|".join(multiples)

        return {
            "month": month,
            "month_short": month_short,
            "weekday": weekday,
            "weekday_short": weekday_short,
            "before_nbsp": before_nbsp,
            "after_nbsp": after_nbsp,
            "multiple_words_nbsp": multiple_words_nbsp
        }

    @staticmethod
    def punctuation(string_to_parse):
        # Replace ...? → ?‥ and ...! → !‥
        string_to_parse = re.sub(r'(\.{2,}|…)([!?])', lambda m: m.group(2) + '\u2025', string_to_parse)

        # Replace ?... → ?‥ and !... → !‥
        string_to_parse = re.sub(r'([!?])(\.{3,}|…)', lambda m: m.group(1) + '\u2025', string_to_parse)

        # Replace ... with ellipsis … U+2026
        string_to_parse = re.sub(r'\.{3,}', '\u2026', string_to_parse)

        # Replace multiple ? with one
        string_to_parse = re.sub(r'(\?){2,}', r'?', string_to_parse)

        # Replace multiple ! with one
        string_to_parse = re.sub(r'(!){2,}', r'!', string_to_parse)

        # Replace multiple . with one
        string_to_parse = re.sub(r'(\.){2,}', r'.', string_to_parse)

        # Replace multiple , with one
        string_to_parse = re.sub(r'(,){2,}', r',', string_to_parse)

        # Replace multiple ; with one
        string_to_parse = re.sub(r'(;){2,}', r';', string_to_parse)

        # Replace multiple : with one
        string_to_parse = re.sub(r'(:){2,}', r':', string_to_parse)

        # Replace multiple - with one
        string_to_parse = re.sub(r'(-){2,}', r'-', string_to_parse)

        # Replace !? → ?!
        string_to_parse = re.sub(r'(!\?)', '?!', string_to_parse)

        # Move the period inside the quotation mark to the outside
        string_to_parse = re.sub(r'([^.])(\.)(["»“)])(\.)?', r'\1\3\2', string_to_parse)

        return string_to_parse

    @staticmethod
    def replace_quote_marks(string_to_parse):
        # Replace opening quotes
        string_to_parse = re.sub(r"""(^|\s)["'„“]""", r'\1«', string_to_parse)
        string_to_parse = re.sub(r"""(«)["'„“]""", r'\1«', string_to_parse)

        # Replace closing quotes
        string_to_parse = re.sub(r"""(\S)["'”]([\W"'»,.…:;!?})\]]|$)""", r'\1»\2',
                                 string_to_parse)
        string_to_parse = re.sub(r"""(»)["'”]""", r'\1»', string_to_parse)

        # Replace nested quotes
        new_string = []
        previous_quote = ''

        for char in string_to_parse:
            if char == "«":
                if previous_quote in ("«", "“"):
                    new_string.append("„")
                    previous_quote = "„"
                else:
                    new_string.append(char)
                    previous_quote = "«"
            elif char == "»":
                if previous_quote == "„":
                    new_string.append("“")
                    previous_quote = "“"
                else:
                    new_string.append(char)
                    previous_quote = "»"
            else:
                new_string.append(char)

        return ''.join(new_string)

    @staticmethod
    def delete_spaces(string_to_parse):
        # Remove spaces AFTER « „ " ' ( [
        string_to_parse = re.sub(r"""([«„"'(\[])\s+""", r'\1', string_to_parse)

        # Remove spaces BEFORE . … : , ; ? ! » “ " ' ) ]
        string_to_parse = re.sub(r"""\s+([.…:,;?!»”"')\]])""", r'\1', string_to_parse)

        # Remove spaces between a number and %
        string_to_parse = re.sub(r'(\d)\s+(%)', r'\1\2', string_to_parse)

        # Remove spaces at the beginning and end of the string
        # If the string contains only whitespace characters, don't change it
        if re.search(r'\S', string_to_parse):
            string_to_parse = string_to_parse.strip()

        # Remove double spaces
        string_to_parse = re.sub(r'[\u0020\u00A0]{2,}', ' ', string_to_parse)

        return string_to_parse

    @staticmethod
    def remove_end_dot_in_single_string(string_to_parse):
        # Search for . ! ? followed by a space or end of string
        search_result = re.findall(r'[.!?][\s$]', string_to_parse)

        # If there's 0 or 1 match, it's a single sentence
        if len(search_result) <= 1:
            # Remove the period at the end of the string
            string_to_parse = re.sub(r'\.$', '', string_to_parse)

        return string_to_parse

    def add_no_break_space(self, string_to_parse, nbsp='\u00A0'):
        # Non-breaking space between initials and surname
        # Initials together, non-breaking space, surname
        string_to_parse = re.sub(
            r"""(^|[\u0020«„"(\[])([A-ZА-ЯЁІЎЄҐЇ]\.)\u0020?([A-ZА-ЯЁІЎЄҐЇ]\.)?\u0020?([A-ZА-ЯЁІЎЄҐЇ][а-яёіўєґї']+)([\s.,;:?!"»“‘)\]]|$)""",
            lambda m: f"{m.group(1)}{m.group(2)}{m.group(3) or ''}{nbsp}{m.group(4)}{m.group(5)}",
            string_to_parse, flags=re.MULTILINE
        )

        # Surname, non-breaking space, initials together
        string_to_parse = re.sub(
            r"""(^|[\u0020«„"(\[])([A-ZА-ЯЁІЎЄҐЇ][а-яёіўєґї']+)\u0020?([A-ZА-ЯЁІЎЄҐЇ]\.)\u0020?([A-ZА-ЯЁІЎЄҐЇ]\.)?([.,;:?!"»“‘)\]]|$)""",
            lambda m: f"{m.group(1)}{m.group(2)}{nbsp}{m.group(3)}{m.group(4) or ''}{m.group(5)}",
            string_to_parse, flags=re.MULTILINE
        )

        # Non-breaking spaces between word and "и т.д.", "и т.п.", "и др."
        string_to_parse = re.sub(
            r'(.)\u0020+(и)\u0020+((т\.д\.)|(т\.п\.)|(др\.))',
            lambda m: f"{m.group(1)}{nbsp}{m.group(2)}{nbsp}{m.group(3)}",
            string_to_parse
        )

        # Non-breaking space BEFORE words
        string_to_parse = re.sub(
            rf"[\u0020\u00A0]({self.before_nbsp})([^a-zа-яёіўєґїґ'])",
            lambda m: f"{nbsp}{m.group(1)}{m.group(2)}",
            string_to_parse
        )

        # Non-breaking space AFTER certain words
        # string_to_parse = re.sub(
        #     rf'(^|[\u0020\u00A0«„"(\[])({self.after_nbsp})\u0020',
        #     lambda m: f"{m.group(1)}{m.group(2)}{nbsp}",
        #     string_to_parse, flags=re.IGNORECASE | re.MULTILINE
        # )
        """this version is smarter, it has lookbehind 
        and it helps in cases like `Ну а калі так здарыцца`
        (commented version above does not work properly)"""
        string_to_parse = regex.sub(
            rf"""(?<=(^|[\n\u0020\u00A0«„"([])({self.after_nbsp}))\u0020""",
            lambda m: f"{nbsp}",
            string_to_parse, flags=re.IGNORECASE
        )


        # Non-breaking space AFTER "стр.", "гл.", "рис.", "илл.", "ст.", "п.", "c."
        string_to_parse = re.sub(
            r'(^|[\u0020«„"(\[])(стр|гл|рис|илл?|ст|п|c)\.\u0020',
            lambda m: f"{m.group(1)}{m.group(2)}.{nbsp}",
            string_to_parse, flags=re.IGNORECASE | re.MULTILINE
        )

        # Non-breaking space AFTER "№"
        string_to_parse = re.sub(
            r'№(\S)',
            lambda m: f"№{nbsp}{m.group(1)}",
            string_to_parse, flags=re.MULTILINE
        )

        # Non-breaking space between number and following word
        string_to_parse = re.sub(
            r"(\d)\u0020+([a-zа-яёіўєґї'])",
            lambda m: f"{m.group(1)}{nbsp}{m.group(2)}",
            string_to_parse, flags=re.IGNORECASE
        )

        # Non-breaking space AFTER abbreviations for city, region, street, etc.
        string_to_parse = re.sub(
            r"""(^|,[\u0020\u00A0])(г|обл|кр|ст|пос|с|д|ул|пер|пр|пр-т|просп|пл|бул|б-р|наб|ш|туп|оф|кв|комн?|под|мкр|уч|вл|влад|стр|корп?|эт|пгт)\.\u0020?(-?[A-ZА-ЯЁІЎЄҐЇ\d])""",
            lambda m: f"{m.group(1)}{m.group(2)}.{nbsp}{m.group(3)}",
            string_to_parse, flags=re.MULTILINE
        )

        # Non-breaking space AFTER "дом"
        string_to_parse = re.sub(
            r'(^|,[\u0020\u00A0])(дом)\u0020(\d)',
            lambda m: f"{m.group(1)}{m.group(2)}{nbsp}{m.group(3)}",
            string_to_parse, flags=re.MULTILINE
        )

        # Non-breaking space AFTER short word
        # string_to_parse = re.sub(
        #     r"""(^|[\u0020\u00A0«„"(\[])([а-яёіўєґї']{1,3})\u0020""",
        #     lambda m: f"{m.group(1)}{m.group(2)}{nbsp}",
        #     string_to_parse, flags=re.IGNORECASE
        # )
        """this version is smarter, it has lookbehind 
        and it helps in cases like `І з гэтага гаю яна выйшла`
        (commented version above does not work properly)"""
        string_to_parse = regex.sub(
            r"""(?<=(^|[\n\u0020\u00A0«„([])([а-яёіўєґї']{1,3}))\u0020""",
            lambda m: f"{nbsp}",
            string_to_parse, flags=re.IGNORECASE
        )

        # Non-breaking space BEFORE last short word in sentence or single line
        string_to_parse = re.sub(
            r"\u0020([а-яёіўєґї']{1,3}[!?…»]?$)",
            lambda m: f"{nbsp}{m.group(1)}",
            string_to_parse, flags=re.IGNORECASE | re.MULTILINE
        )

        # put NBSP between any words from nbsp_multiple_words.txt
        string_to_parse = re.sub(
            rf"([^a-zа-яёіўєґїґ'])({self.multiple_words_nbsp})([^a-zа-яёіўєґїґ']|$)",
            lambda
                m: f"{m.group(1)}{m.group(2).replace('\u0020', nbsp)}{nbsp if m.group(3) == '\u0020' else m.group(3)}",
            string_to_parse,
            flags=re.IGNORECASE
        )

        for pattern in [
            r"""\u0020([а-яёіўєґї']{1,3}[\.!?…](\u0020.|$))""",
            r"""\u0020([а-яёіўєґї']{1,3}[\.!?…][\)\]](\u0020.|$))""",
            r"""\u0020([а-яёіўєґї']{1,3}[\)\]][\.!?…](\u0020.|$))""",
            r"""\u0020([а-яёіўєґї']{1,3}[!?…]["»](\u0020.|$))""",
            r"""\u0020([а-яёіўєґї']{1,3}[!?…]?["»][\.!?…](\u0020.|$))"""
        ]:
            string_to_parse = re.sub(
                pattern,
                lambda m: f"{nbsp}{m.group(1)}",
                string_to_parse, flags=re.IGNORECASE | re.MULTILINE
            )

        # ADDITIONAL STEP TO REMOVE Non-breaking space after words from before_nbsp list words
        # 'Каманда_NBSP_б_NBSP_убачыла' => 'Каманда_NBSP_б убачыла'
        string_to_parse = re.sub(
            rf"[\u0020\u00A0]({self.before_nbsp})(\u00A0)",
            lambda m: f"{nbsp}{m.group(1)} ",
            string_to_parse
        )

        return string_to_parse

    @staticmethod
    def replace_y_with_short_u(string_to_parse):
        # Define Belarusian vowels
        vowels = 'аеёіоуыэюяАЕЁІОУЫЭЮЯ'

        # Pattern to match 'у' or 'У' preceded by a vowel,
        # including across word boundaries
        pattern = rf'([{vowels}])(\s*)([уУ])'

        # Replace function
        def replace(match):
            vowel, space, y = match.groups()
            return vowel + (space if space in match.group(0) else '') + ('ў' if y == 'у' else 'Ў')

        # Perform the replacement
        return re.sub(pattern, replace, string_to_parse,
                      flags=re.MULTILINE
                      )

    @staticmethod
    def replace_short_u_with_y(string_to_parse):
        # Define Belarusian vowels
        vowels = 'аеёіоуыэюяАЕЁІОУЫЭЮЯ'

        # Pattern to match 'у' or 'У' preceded by a vowel,
        # including across word boundaries
        pattern = rf'(^|[^\s{vowels}])(\s*)([ўЎ])'

        # Replace function
        def replace(match):
            not_vowel, space, y = match.groups()
            return not_vowel + (space if space in match.group(0) else '') + ('у' if y == 'ў' else 'У')

        # Perform the replacement
        return re.sub(pattern, replace, string_to_parse, flags=re.MULTILINE)

    @staticmethod
    def yo(string_to_parse, yo_dict):
        """
        Not really need it for Belarusian, but as legacy let it be here.
        """

        def replace_word(match):
            word = match.group(1)
            word_lower = word.lower()

            if word_lower in yo_dict:
                yo_dict_word = yo_dict[word_lower]
                word_all_case = ''

                for i, char in enumerate(word):
                    if char.lower() == yo_dict_word[i]:
                        # The letter from the word is equal to the letter from the dictionary word
                        word_all_case += char
                    else:
                        # The letters don't match. Either it's a different case or 'е' vs 'ё'
                        if char.isupper():
                            # uppercase
                            if char.upper() == yo_dict_word[i].upper():
                                # Compare the uppercase letter of the main word with the uppercase letter of the dictionary word
                                # If they match, append
                                word_all_case += char
                            else:
                                # They don't match, so it's a replacement of 'е' with 'ё'
                                word_all_case += yo_dict_word[i].upper()
                        else:
                            # lowercase
                            # They don't match, so it's a replacement of 'е' with 'ё'
                            word_all_case += yo_dict_word[i]

                return word_all_case

            return word

        # Split the text into words and replace them
        return re.sub(r"""([а-яёіўєґї']+)""", replace_word, string_to_parse, flags=re.IGNORECASE)

    @staticmethod
    def phone_number(string_to_parse, phone_code_ru, nbsp='\u00A0'):
        """
        Not sure that this functionality is in the scope, but let bring it here as legacy.
        Haven't tested it.
        """
        # Space or non-breaking space
        space_tmpl = r'[\u0020\u00A0]?'
        # Any dash
        dash_tmpl = r'[\u002D\u2012\u2013\u2014]?'
        # Space or non-breaking space or any dash
        space_dash_tmpl = r'[\u0020\u00A0\u002D\u2012\u2013\u2014]?'

        # Special symbol for dash in phone numbers
        special_dash = '<phoneDash>'

        # Federal number 8 800
        re_federal = re.compile(
            rf'[\+\(]*?{space_tmpl}(8){space_tmpl}{dash_tmpl}\(?'
            rf'(800){space_tmpl}{dash_tmpl}[\)]?{space_dash_tmpl}'
            rf'(\d){space_dash_tmpl}(\d){space_dash_tmpl}(\d){space_dash_tmpl}'
            rf'(\d){space_dash_tmpl}(\d){space_dash_tmpl}(\d){space_dash_tmpl}(\d)'
        )

        def format_federal(match):
            groups = match.groups()
            formatted = f"{groups[0]}{nbsp}({groups[1]}){nbsp}{''.join(groups[2:5])}{special_dash}{''.join(groups[5:7])}{special_dash}{''.join(groups[7:])}"
            return formatted

        string_to_parse = re_federal.sub(format_federal, string_to_parse)

        # Russian numbers +7 (333) 333-22-22
        re_ru = re.compile(
            rf'[\+\(]*?{space_tmpl}(7|8){space_tmpl}{dash_tmpl}\(?'
            rf'({phone_code_ru}){space_tmpl}{dash_tmpl}[\)]?{space_dash_tmpl}'
            rf'(\d){space_dash_tmpl}(\d){space_dash_tmpl}(\d){space_dash_tmpl}'
            rf'(\d){space_dash_tmpl}(\d){space_dash_tmpl}(\d)?{space_dash_tmpl}(\d)?'
        )

        def format_ru(match):
            groups = match.groups()
            area_code = groups[1]
            if len(area_code) == 3:
                formatted = f"+7{nbsp}({area_code}){nbsp}{''.join(groups[2:5])}{special_dash}{''.join(groups[5:7])}{special_dash}{''.join(groups[7:])}"
            elif len(area_code) == 4:
                formatted = f"+7{nbsp}({area_code}){nbsp}{''.join(groups[2:4])}{special_dash}{''.join(groups[4:6])}{special_dash}{''.join(groups[6:8])}"
            return formatted

        string_to_parse = re_ru.sub(format_ru, string_to_parse)

        # Short number 900
        string_to_parse = re.sub(
            r'(^|\D)(\+900|\#900|\@900)(\D|$)',
            r'\1900\3',
            string_to_parse, flags=re.MULTILINE
        )

        return string_to_parse

    def dash(self, string_to_parse, nbsp='\u00A0'):
        # All types of dashes
        dash_all = r'[\u002D\u2012\u2013\u2014]'

        # At the beginning of a string or sentence, long dash + non-breaking space
        string_to_parse = re.sub(
            rf'(^|[.!?][\u0020\u00A0])({dash_all})(.)?',
            lambda m: f"{m.group(1)}\u2014{nbsp if m.group(3) != nbsp else ''}{m.group(3) if m.group(3) else nbsp}",
            string_to_parse,
            flags=re.MULTILINE
        )

        def month_weekday(params):
            nonlocal string_to_parse
            pattern = rf'(({params})\.?)[\u0020\u00A0]?({dash_all})[\u0020\u00A0]?(({params})\.?)'
            string_to_parse = re.sub(
                pattern,
                lambda m: f"{m.group(1)}\u2013{m.group(5)}",
                string_to_parse,
                flags=re.IGNORECASE | re.MULTILINE
            )
            return string_to_parse

        # Apply month_weekday function for different date formats
        for date_format in [self.month, self.month_short, self.weekday, self.weekday_short]:
            string_to_parse = month_weekday(date_format)

        # Within text, use non-breaking space + long dash
        string_to_parse = re.sub(
            rf'([^.!?\dXIV])[\u0020\u00A0]({dash_all})[\u0020\u00A0]?([^\dXIV])',
            lambda m: f"{m.group(1)}{nbsp}\u2014 {m.group(3)}",
            string_to_parse
        )

        # For number ranges, use en dash without spaces: 2002–2009 + centuries XI–XII
        string_to_parse = re.sub(
            rf'(\d|[XIV])[\u0020\u00A0]?({dash_all})[\u0020\u00A0]?(\d|[XIV])',
            '\\1\u2013\\3',
            string_to_parse
        )

        # Replace <phoneDash> from phoneNumber() function with hyphen
        string_to_parse = re.sub(r'<phoneDash>', '\u002D', string_to_parse)

        return string_to_parse

    @staticmethod
    def numbers(string_to_parse: str) -> str:
        """
        Format numbers in the given string according to specific rules.

        This function applies various formatting rules to numbers, including:
        - Splitting large numbers into groups of three digits
        - Handling decimal points and currency symbols
        - Formatting dates and special number sequences (like account numbers)

        Args:
            string_to_parse (str): The input string to be formatted.

        Returns:
            str: The formatted string.
        """
        non_breaking_space = '\u00A0'

        def format_large_numbers_and_currency(match: Match) -> str:
            groups = match.groups()
            integer_part, _, _, fractional_part, currency_part = groups[:5]
            if len(integer_part) >= 5 or currency_part is not None:
                integer_part = re.sub(r'(\d)(?=(\d{3})+(?!\d))',
                                      lambda m: m.group(1) + non_breaking_space,
                                      integer_part)

            fractional_part = f',{fractional_part}' if fractional_part else ''

            currency_part = currency_part or ''
            return f'{integer_part}{fractional_part}{currency_part}'

        def format_dates(match: Match) -> str:
            groups = match.groups()
            prefix, day, month, _, _, year, suffix = groups
            year_part = f'.{year}' if year else ''
            return f'{prefix}{day}.{month}{year_part}{suffix}'

        def format_postal_codes(match: Match) -> str:
            groups = match.groups()
            return f'{groups[0]}{groups[1]}{groups[2]}{groups[3]}'

        def format_phone_numbers(match: Match) -> str:
            groups = match.groups()
            return f'{groups[0]}{groups[1]}{groups[2]}{groups[3]}'

        def format_account_numbers(match: Match) -> str:
            groups = match.groups()
            return ''.join(groups[1:-1])

        # Apply formatting rules
        string_to_parse = re.sub(
            r'(\d+)(([.,])(\d+))?(\u00A0(тыс|млн|млрд|трлн|₽|\$|€|£|¥))?',
            format_large_numbers_and_currency,
            string_to_parse
        )

        string_to_parse = re.sub(
            r'(^|\D)(\d{2}),(\d{2})(?!\u00A0(тыс|млн|млрд|трлн|₽|\$|€|£|¥))(,(\d{4}))?($|\D)',
            format_dates,
            string_to_parse,
            flags=re.MULTILINE
        )

        string_to_parse = re.sub(
            r'(^|\D)(\d{3})\u00A0(\d{3})(,\s)',
            format_postal_codes,
            string_to_parse,
            flags=re.MULTILINE
        )

        string_to_parse = re.sub(
            r'(\d\u00A0\()(\d)\u00A0(\d{3})(\)\u00A0\d)',
            format_phone_numbers,
            string_to_parse,
            flags=re.MULTILINE
        )

        string_to_parse = re.sub(
            r'(^|\D)(\d{2})\u00A0(\d{3})\u00A0(\d{3})\u00A0(\d{3})\u00A0(\d{3})\u00A0(\d{3})\u00A0(\d{3})($|\D)',
            format_account_numbers,
            string_to_parse,
            flags=re.MULTILINE
        )

        return string_to_parse

    @staticmethod
    def currency(string_to_parse):
        nbsp = '\u00A0'

        # Replace 'тыс' with 'тыс.'
        string_to_parse = re.sub(r'(тыс)([!?,:;\u00A0\u0020\n]|$)', r'\1.\2', string_to_parse,
                                 flags=re.IGNORECASE | re.MULTILINE)

        # Remove dot after 'млн', 'млрд', 'трлн'
        string_to_parse = re.sub(r'(млн|млрд|трлн)\.', r'\1', string_to_parse, flags=re.IGNORECASE | re.MULTILINE)

        # Add dot after 'млн', 'млрд', 'трлн' at the end of a sentence
        string_to_parse = re.sub(r'(млн|млрд|трлн)(\u0020|\u00A0)((«|—(\u0020|\u00A0))?[A-ZА-ЯЁІЎЄҐЇ])', r'\1.\2\3',
                                 string_to_parse, flags=re.MULTILINE)

        # Convert USD to $
        string_to_parse = re.sub(r'(\d|тыс\.|млн|млрд|трлн)(\u0020|\u00A0)?(USD)\.?([!?,:;\u00A0\u0020\n]|$)',
                                 rf'\1{nbsp}$\4', string_to_parse, flags=re.IGNORECASE | re.MULTILINE)

        # Convert EUR to €
        string_to_parse = re.sub(r'(\d|тыс\.|млн|млрд|трлн)(\u0020|\u00A0)?(EUR)\.?([!?,:;\u00A0\u0020\n]|$)',
                                 rf'\1{nbsp}€\4', string_to_parse, flags=re.IGNORECASE | re.MULTILINE)

        # Convert Р, р., руб. RUR RUB to ₽
        string_to_parse = re.sub(r'(\d|тыс\.|млн|млрд|трлн)(\u0020|\u00A0)?(р|руб|RUR|RUB)\.?([!?,:;\u00A0\u0020\n]|$)',
                                 rf'\1{nbsp}₽\4', string_to_parse, flags=re.IGNORECASE | re.MULTILINE)

        # Incorporate kopeks into the main amount
        string_to_parse = re.sub(
            r'(\d)(\u00A0₽)(\u0020|\u00A0)(\d{1,2})(\u0020|\u00A0)?(к|коп)\.?([!?,:;\u00A0\u0020\n]|$)',
            lambda m: f"{m.group(1)},{m.group(4).zfill(2)}{m.group(2)}{m.group(7)}", string_to_parse,
            flags=re.IGNORECASE | re.MULTILINE)

        # Add dot after ₽ at the end of a sentence
        string_to_parse = re.sub(r'(\d\u00A0₽)(\u0020|\u00A0)((«|—(\u0020|\u00A0))?[A-ZА-ЯЁІЎЄҐЇ])', r'\1.\2\3',
                                 string_to_parse,
                                 flags=re.MULTILINE)

        # Move currency sign after digits and separate with non-breaking space
        string_to_parse = re.sub(
            r'(^|[\D]{2})(₽|\$|€|£|¥)[\u0020\u00A0]?(\d+([\u0020\u00A0]\d{3})*([.,]\d+)?)([\u0020\u00A0]?(тыс\.|млн|млрд|трлн))?',
            lambda m: f"{m.group(1)}{m.group(3)}{nbsp + m.group(7) if m.group(7) else ''}{nbsp}{m.group(2)}",
            string_to_parse, flags=re.MULTILINE)

        # Separate currency sign from number with non-breaking space
        string_to_parse = re.sub(r'(\d)(₽|\$|€|£|¥)', rf'\1{nbsp}\2', string_to_parse, flags=re.MULTILINE)

        return string_to_parse

    def run_typographical_enhancement(self, text):
        from time import sleep
        # sleep(2)
        functions = [
            self.punctuation,
            self.replace_quote_marks,
            self.delete_spaces,
            # self.remove_end_dot_in_single_string,
            self.add_no_break_space,
            self.replace_y_with_short_u,
            self.replace_short_u_with_y,
            # yo,
            # phone_number,
            self.dash,
            self.currency,
            self.numbers
        ]
        result = text
        for f in functions:
            result = f(result)
        return result


default_typo = ByTypograph(r'resources/month_weekdays.txt',
                          r'resources/nbsp_before_words.txt',
                          'resources/nbsp_after_words.txt',
                          'resources/nbsp_multiple_words.txt')

if __name__ == "__main__":
    with open('resources/test_text.txt') as f:
        test_text = f.read()

    by_typo = ByTypograph(r'resources/month_weekdays.txt',
                          r'resources/nbsp_before_words.txt',
                          'resources/nbsp_after_words.txt',
                          'resources/nbsp_multiple_words.txt')

    # print(by_typo.before_nbsp, by_typo.after_nbsp, by_typo.multiple_words_nbsp, sep='\n\n')
    result = by_typo.run_typographical_enhancement(test_text)

    # print(result)
    # print(result.replace("\u00A0", "_NBSP_"))


    print(result.replace("\u00A0", "_nbsp_"))