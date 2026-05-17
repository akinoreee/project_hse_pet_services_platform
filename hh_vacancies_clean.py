import re
import pandas as pd


INPUT_FILE = "hh_pet_vacancies_raw_cards.csv"
OUTPUT_FILE = "hh_pet_vacancies_clean_salary.csv"


def normalize_spaces(text):
    if pd.isna(text):
        return ""

    text = str(text)
    text = text.replace("\xa0", " ")
    text = text.replace("\u202f", " ")
    text = text.replace("\u2009", " ")
    text = re.sub(r"[ \t]+", " ", text)

    return text.strip()


def money_to_rub(number, unit=None):
    number = normalize_spaces(number)
    number = number.replace(" ", "")

    if re.fullmatch(r"\d{1,3}(?:\.\d{3})+", number):
        number = number.replace(".", "")

    value = float(number.replace(",", "."))

    if unit:
        unit = unit.lower()

        if "тыс" in unit or "тысяч" in unit or unit in ["к", "k"]:
            value *= 1000

    return int(value)


def extract_salary_line(row):
    salary_text = row.get("salary_text")

    if pd.notna(salary_text) and str(salary_text).strip():
        return normalize_spaces(salary_text)

    raw_text = row.get("raw_card_text")

    if pd.isna(raw_text):
        return None

    lines = [normalize_spaces(line) for line in str(raw_text).split("\n") if normalize_spaces(line)]

    salary_pattern = re.compile(r"₽|руб|р\.|з/п|зарплат|оклад|доход", re.IGNORECASE)

    for line in lines:
        if salary_pattern.search(line):
            return line

    return None


def parse_salary_line(salary_line):
    result = {"salary_min_rub": None, "salary_max_rub": None}

    if not salary_line:
        return result

    text = normalize_spaces(salary_line)

    number = r"\d{1,3}(?:[\s.]?\d{3})+|\d+(?:[,.]\d+)?"
    unit = r"тыс\.?|тысяч|к|k"

    range_pattern = re.compile(
        rf"(?:от\s*)?"
        rf"(?P<num1>{number})\s*"
        rf"(?P<unit1>{unit})?\s*"
        rf"(?:₽|руб\.?|рублей|рубля|р\.?)?\s*"
        rf"(?:[-–—]|\s+до\s+)\s*"
        rf"(?P<num2>{number})\s*"
        rf"(?P<unit2>{unit})?\s*"
        rf"(?:₽|руб\.?|рублей|рубля|р\.?)?",
        re.IGNORECASE
    )

    range_match = range_pattern.search(text)

    if range_match:
        unit1 = range_match.group("unit1") or range_match.group("unit2")
        unit2 = range_match.group("unit2") or range_match.group("unit1")

        value1 = money_to_rub(range_match.group("num1"), unit1)
        value2 = money_to_rub(range_match.group("num2"), unit2)

        if max(value1, value2) >= 1000:
            result["salary_min_rub"] = min(value1, value2)
            result["salary_max_rub"] = max(value1, value2)

        return result

    single_pattern = re.compile(
        rf"(?P<prefix>от|до)?\s*"
        rf"(?P<num>{number})\s*"
        rf"(?P<unit>{unit})?\s*"
        rf"(?:₽|руб\.?|рублей|рубля|р\.?)?",
        re.IGNORECASE
    )

    single_match = single_pattern.search(text)

    if single_match:
        value = money_to_rub(single_match.group("num"), single_match.group("unit"))

        if value < 1000:
            return result

        prefix = single_match.group("prefix")

        if prefix and prefix.lower() == "от":
            result["salary_min_rub"] = value

        elif prefix and prefix.lower() == "до":
            result["salary_max_rub"] = value

        else:
            result["salary_min_rub"] = value
            result["salary_max_rub"] = value

    return result


df = pd.read_csv(INPUT_FILE, encoding="utf-8-sig")

df = df[df["position_group"] != "Другое"].copy()

df["salary_line_extracted"] = df.apply(extract_salary_line, axis=1)

salary_parsed = df["salary_line_extracted"].apply(parse_salary_line)
salary_df = pd.DataFrame(list(salary_parsed), index=df.index)

df = pd.concat([df, salary_df], axis=1)

result_df = df[["title", "position_group", "company", "salary_line_extracted", "salary_min_rub", "salary_max_rub"]].copy()

result_df = result_df.dropna(subset=["salary_min_rub", "salary_max_rub"], how="all").reset_index(drop=True)

result_df.to_csv(OUTPUT_FILE, index=False, encoding="utf-8-sig")
