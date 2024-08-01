[![Static Badge](https://img.shields.io/badge/Click_me-By--Typo-red?style=for-the-badge&labelColor=fedcba)](https://aulasau.github.io/by-typo/)
# By-Typo

By-Typo is a web-based typographic tool designed to enhance Belarusian text by applying various typographic rules and corrections.

It's an adaptation of [SBOLTypograph repo](https://github.com/DanilovM/SBOLTypograph) to Python and Belarusian.

## Main Features

- Manages no-break spaces along the text
- Fixes different punctuation mistakes
- Works with Belarusian language
- Fixes Ў issues

## Details

### Text Processing Rules

By-Typo applies the following rules to improve text quality:

1. **Letter Ў correction**
   - Replaces 'у' with 'ў' where appropriate
   - Corrects 'ў' to 'у' at the beginning of sentences or after consonants

2. **Quotation marks**
   - Replaces simple quotes with proper quotation marks («»)

3. **Dashes**
   - Applies appropriate dash lengths for different contexts (em dash, en dash)
   - Adds non-breaking spaces where needed

4. **Punctuation**
   - Corrects order of multiple punctuation marks
   - Replaces triple dots with ellipsis character

5. **Spaces**
   - Adds or removes spaces around punctuation marks as needed
   - Eliminates double spaces

6. **Non-breaking spaces**
   - Inserts non-breaking spaces in appropriate places (e.g., between initials and surnames)

7. **Number formatting**
   - Formats large numbers with proper spacing
   - Corrects abbreviations for thousands, millions, etc.

8. **Currency symbols**
   - Replaces currency codes (USD, EUR) with symbols ($ €)
   - Positions currency symbols correctly relative to numbers

## Contact

For bug reports or suggestions, contact: [aulasau.public@gmail.com](mailto:aulasau.public+by-typo@gmail.com)
