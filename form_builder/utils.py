# Copyright (C) 2017 Feedvay (Gagandeep Singh: singh.gagan144@gmail.com) - All Rights Reserved
# Content in this document can not be copied and/or distributed without the express
# permission of Gagandeep Singh.
import re

class JsCompilerTool(object):
    """
    Class for compiler analysis of javascript code.

    **Authors**: Gagandeep Singh
    """

    def __init__(self, code):
        self.code = code

    def extract_variables(self):
        pattern = re.compile(r'[$a-z_][a-z0-9_.]+', re.IGNORECASE+re.DOTALL)
        matches = pattern.findall(self.code)
        return matches

class GeoLocation:
    """
    A class to define gps options available in the form.

    **Authors**: Gagandeep Singh
    """

    # GPS options enums
    PRECISE = 'precise'
    HIGH = 'high'
    FINE = 'fine'
    COARSE = 'coarse'
    PASSABLE = 'passable'

    choices = (
        (PRECISE, 'Precise'),
        (HIGH, 'High'),
        (FINE, 'Fine'),
        (COARSE, 'Coarse'),
        (PASSABLE, 'Passable')
    )

    choice_order = [PRECISE, HIGH, FINE, COARSE, PASSABLE]

    # Config Parameters for each option
    # max_radius: In meters, allowed accuracy of retrieved of gps location
    # max_age Age: In milliseconds, max age of previously obtained gps that is acceptable as current location
    # high_accuracy: Retrieving method; True=satellite based methods, False=Network based methods
    # default: marked selected by default
    config = {
        PRECISE: {
            "name": "Precise",
            "description": "Pin-point location",
            "max_radius": 25,
            "max_age": 5000,    # 5 sec
            "high_accuracy": True,
            "remarks": "Ideal for areas with very high network coverage."
        },
        HIGH: {
            "name": "High",
            "description": "High accuracy",
            "max_radius": 50,
            "max_age": 10000,   # 10 sec
            "high_accuracy": True,
            "default": True,
            "remarks": "Ideal for urban areas with high network coverage."
        },
        FINE: {
            "name": "Fine",
            "description": "Acceptable accuracy",
            "max_radius": 100,
            "max_age": 15000,   # 15 sec
            "high_accuracy": True,
            "remarks": "Ideal for wide range of areas having variable network coverage."
        },
        COARSE: {
            "name": "Coarse",
            "description": "Approximate accuracy",
            "max_radius": 500,
            "max_age": 30000,   # 30 sec
            "high_accuracy": False,
            "remarks": "Ideal for rural or remote areas."
        },
        PASSABLE: {
            "name": "Passable",
            "description": "Just get the location",
            "max_radius": None,
            "max_age": 60000,   # 60 sec
            "high_accuracy": False,
            "remarks": "Ideal for remote areas with constrained network conditions."
        }
    }

    @staticmethod
    def get_choices():
        choices = []
        for key in GeoLocation.choice_order:
            conf = GeoLocation.config[key]
            conf["id"] = key
            choices.append(conf)
        return choices