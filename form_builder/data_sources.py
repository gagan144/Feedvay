# Copyright (C) 2017 Feedvay (Gagandeep Singh: singh.gagan144@gmail.com) - All Rights Reserved
# Content in this document can not be copied and/or distributed without the express
# permission of Gagandeep Singh.
"""
This files defines various data sources for multiple choice fields.
All data source must inherit 'BasicFieldDataSource' and must be a static class.
That means no object is create for these data source and all methods are static
which can be directly accessed from class.

* To add new data source:
    - Inherit 'BasicFieldDataSource'
    - Add the new data source to 'FIELD_DATA_SOURCES' as tuple of ('<class name>','<name>')
"""

from datetime import datetime

class BasicFieldDataSource(object):
    """
    An abstract class to define field data source. All data sources must
    derive this class and must provide implementation of all methods.
    This class is static i.e. no object is created will using this class.
    """

    name = None

    def __init__(self):
        raise Exception("Field data source '{}' must not be initiated. Use static methods directly.".format(self.__class__.__name__))

    @staticmethod
    def get():
        """
        This method returns choice data for the data source. The data is a list of dictionary
        having keys text & value
        Format:
            [
                { "value": "<value>", "text":"<text>"},
                ...
            ]
        """
        pass

# ---------- Actual field data sources ----------
class YearDataSource(BasicFieldDataSource):
    """
    Field data source for year choice.
    The choices ranges from 1900 to current year
    """

    name = 'Year'

    @staticmethod
    def get():
        now = datetime.now()

        choices = []
        for y in range(1900, now.year+1):
            choices.append({
                "value": y,
                "text": y
            })

        return choices

# ---------- Data source lookup ----------
FIELD_DATA_SOURCES = (
    (YearDataSource.__name__, YearDataSource.name)
)


print FIELD_DATA_SOURCES