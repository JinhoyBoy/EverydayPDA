from datetime import datetime

# Helper-function to check if a date is valid and convert it to the format YYYY-MM-DD
def is_valid_date(date_string):
    try:
        # Checks if date is in format YYYY-MM-DD
        datetime.strptime(date_string, "%Y-%m-%d")
        return date_string

    except ValueError:
        try:
            # Checks if date is in format DD.MM.YYYY
            parsed_date = datetime.strptime(date_string, "%d.%m.%Y")
            return parsed_date.strftime("%Y-%m-%d")

        except ValueError:
            # If Year is missing, append the current year
            current_year = datetime.now().year
            date_with_year = f"{date_string}{current_year}"
            parsed_date = datetime.strptime(date_with_year, "%d.%m.%Y")
            return parsed_date.strftime("%Y-%m-%d")