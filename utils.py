"""Project Utils."""

import dateutil.parser
import babel


def format_datetime(value, date_format: str='medium'):
    """Formats date based on the supplied input.
        Args:
            value (str): The supplied value
            date_format (str): The reqruired format
        Returns:
            str: The formatted date
        """
    if isinstance(value, str):
        date = dateutil.parser.parse(value)
    else:
        date = value

    if date_format == 'full':
        date_format = "EEEE MMMM, d, y 'at' h:mma"
    elif date_format == 'medium':
        date_format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, date_format, locale='en')
