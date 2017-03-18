# Copyright (C) 2017 Feedvay (Gagandeep Singh: singh.gagan144@gmail.com) - All Rights Reserved
# Content in this document can not be copied and/or distributed without the express
# permission of Gagandeep Singh.
from django.core.exceptions import ValidationError
from jsonobject import *
from jsonobject.properties import SetProperty

from datetime import datetime

# ---------- General ----------
class BspTypes:
    """
    Enum class that defines various types of business and Service points.
    These are fundamental types and not categories.

    **Add new type in the system**:

        - Create type enum in this class and add to ``choices`` keepng the order.
        - Create new BSP type class by extending :class:`market.bsp_types.BaseBspType`
        - Add mapping in ``MAPPING_BSP_CLASS``
        - Create bsp edit partial in directory and as: ``market/templates/market/partials/bsp_types/<bsp_type_code>_attributes.html``

    **Authors**: Gagandeep Singh
    """
    # ATM = 'atm'
    # BANK = 'bank'
    CAFE = 'cafe'
    # DOCTOR = 'doctor'   # <<-- category
    # TOILET = 'toilet'
    # MOBILE_APP = 'app'
    RESTAURANT = 'restaurant'
    # WEBSITE = 'website'

    # Note: Keep this in alphabetic order
    choices = (
        (CAFE, 'Cafe'),
        (RESTAURANT, 'Restaurant'),
    )

class PaymentMethods:
    """
    Enum class for payment methods.

    **Authors**: Gagandeep Singh
    """
    CASH = 'cash'
    CARDS = 'cards'
    WALLETS = 'wallets'

    choices = (
        (CASH, 'Cash'),
        (CARDS, 'Cards'),
        (WALLETS, 'Wallets')
    )

    help_text = '(Comma separated) Payment methods available.<br/>Values: '+", ".join(['<code>{}</code>'.format(pm[0]) for pm in choices])

# ---------- BSP Types ----------
class BaseBspType(JsonObject):
    """
    Base BSP type or establishment definitation.
    Always inherit this class to define any further BSP type.

    **Authors**: Gagandeep Singh
    """
    _allow_dynamic_properties = False

    class ENUMS:
        HELP_TEXT = {
            "highlights": "(Comma separated) Any highlighting points.",
            "recommendations": "Any recommendations.",
        }

    highlights  = SetProperty(unicode, exclude_if_none=True)    # Highlighting features
    recommendations = StringProperty(exclude_if_none=True)      # Any recommendations

    @classmethod
    def type_cast_value(cls, label, value):
        """
        Method to type cast value as per label property data type.

        :param label: Attribute label
        :param value: Value of the attribute
        :return: Type casted value
        """

        attr = getattr(cls, label)
        if attr is None:
            raise Exception("Invalid label '{}'.".format(label))

        if value is None:
            return None
        elif isinstance(attr, IntegerProperty):
            return int(value)
        elif isinstance(attr, FloatProperty) or isinstance(attr, DecimalProperty):
            return float(value)
        elif isinstance(attr, StringProperty):
            return str(value)
        elif isinstance(attr, BooleanProperty):
            return bool(value)
        elif isinstance(attr, DateTimeProperty):
            return datetime.strptime("%Y-%m-%d %H:%M:%s", value)
        elif isinstance(attr, DateProperty):
            return datetime.strptime("%Y-%m-%d", value)
        elif isinstance(attr, TimeProperty):
            return datetime.strptime("%H:%M:%s", value)
        elif isinstance(attr, DictProperty):
            return dict(value)
        elif isinstance(attr, ListProperty) or isinstance(attr, SetProperty):
            return value.split(',')
        else:
            raise NotImplementedError("Type cast for attribute '{}' of property '{}' not implemented".format(label, attr))

class Cafe(BaseBspType):
    """
    A cafe, or coffeehouse is a small restaurant serving coffee, beverages, and light meals.

    **Authors**: Gagandeep Singh
    """
    class ENUMS:
        HELP_TEXT = {
            "home_delivery": "Whether home delivery is available.",
            "average_cost_2": "Average cost for two people",
            "payment_methods": PaymentMethods.help_text,

            "highlights": BaseBspType.ENUMS.HELP_TEXT["highlights"],
            "recommendations": BaseBspType.ENUMS.HELP_TEXT["recommendations"]
        }

    home_delivery   = BooleanProperty(default=False, required=True) # Home delivery available or not
    average_cost_2  = IntegerProperty(default=None, exclude_if_none=True)   # Average cost for two person in native currency
    payment_methods = SetProperty(unicode, exclude_if_none=True)   # Mode of payments

class Restaurant(BaseBspType):
    """
    Eatery is any point offering food or drink service in any form and type.

    **Authors**: Gagandeep Singh
    """
    _allow_dynamic_properties = False


    class ENUMS:
        # --- Cuisines ---
        # From market.models.RestaurantCuisine

        # --- Categories ---
        CTG_BAKERIES = 'bakeries'
        CTG_BEVERAGE_SHOPS = 'beverage shops'
        CTG_BUFFETS = 'buffets'
        # CTG_CAFES = 'cafes'
        CTG_CASUAL_DINING = 'casual dining'
        CTG_DESSERT_PARLOR = 'dessert parlor'
        CTG_FOOD_COURTS = 'food courts'
        CTG_FOOD_TRUCKS = 'food trucks'
        CTG_FOOD_STALLS = 'food stalls'
        CTG_KIOSKS = 'kiosks'
        CTG_LUXURY_DINING = 'luxury dining'
        CTG_ROOFTOPS = 'rooftops'
        CTG_TAKE_AWAY = 'take away'
        CTG_MICROBREWERIES = 'microbreweries'
        CTG_SHEESHA_LOUNGES = 'sheesha lounges'
        CTG_SWEET_SHOPS = 'sweet shops'
        CTG_QUICK_BITES = 'quick bites'
        CH_CATEGORIES = (
            (CTG_BAKERIES,CTG_BAKERIES),
            (CTG_BEVERAGE_SHOPS,CTG_BEVERAGE_SHOPS),
            (CTG_BUFFETS,CTG_BUFFETS),
            # (CTG_CAFES,CTG_CAFES),
            (CTG_CASUAL_DINING,CTG_CASUAL_DINING),
            (CTG_DESSERT_PARLOR,CTG_DESSERT_PARLOR),
            (CTG_FOOD_COURTS,CTG_FOOD_COURTS),
            (CTG_FOOD_TRUCKS,CTG_FOOD_TRUCKS),
            (CTG_FOOD_STALLS,CTG_FOOD_STALLS),
            (CTG_KIOSKS,CTG_KIOSKS),
            (CTG_LUXURY_DINING,CTG_LUXURY_DINING),
            (CTG_ROOFTOPS,CTG_ROOFTOPS),
            (CTG_TAKE_AWAY,CTG_TAKE_AWAY),
            (CTG_MICROBREWERIES,CTG_MICROBREWERIES),
            (CTG_SHEESHA_LOUNGES,CTG_SHEESHA_LOUNGES),
            (CTG_SWEET_SHOPS,CTG_SWEET_SHOPS),
            (CTG_QUICK_BITES,CTG_QUICK_BITES),
        )

        @staticmethod
        def get_category_list():
            return [c[0] for c in Restaurant.ENUMS.CH_CATEGORIES]


        # --- Food type ---
        FOOD_VEG = 'veg'
        FOOD_NON_VEG = 'non_veg'
        FOOD_EGG    = 'egg'
        CH_FOOD_TYPE = (
            (FOOD_VEG, 'Veg'),
            (FOOD_NON_VEG, 'Non-Veg'),
            (FOOD_EGG, 'Egg')
        )

        @staticmethod
        def get_food_type_list():
            return [f[0] for f in Restaurant.ENUMS.CH_FOOD_TYPE]

        HELP_TEXT = {
            "category": '(Comma separated) Category of the restaurant.<br/>Values: ' + ', '.join(['<code>{}</code>'.format(catg[0]) for catg in CH_CATEGORIES]),
            "food_type": '(Comma separated) Type of food served.<br/>Values: ' + ', '.join(['<code>{}</code>'.format(ft[0]) for ft in CH_FOOD_TYPE]),
            "cuisines": "(Comma separated) Cuisines served in the restaurant",
            "home_delivery": "Whether home delivery is available.",
            "average_cost_2": "Average cost for two people",
            "payment_methods": PaymentMethods.help_text,

            "highlights": BaseBspType.ENUMS.HELP_TEXT["highlights"],
            "recommendations": BaseBspType.ENUMS.HELP_TEXT["recommendations"]
        }

    # --- Fields ---
    category    = SetProperty(unicode, required=True)   # Category of eatery

    food_type   = SetProperty(unicode, required=True) # Type of food; veg, non-veg, egg
    cuisines    = SetProperty(unicode)

    home_delivery   = BooleanProperty(default=False, required=True) # Home delivery available or not
    average_cost_2  = IntegerProperty(default=None, exclude_if_none=True)   # Average cost for two person in native currency
    payment_methods = SetProperty(unicode)   # Mode of payments

    # def __init__(self, _obj=None, **kwargs):
    #     super(Restaurants, self).__init__(_obj=_obj, **kwargs)


MAPPING_BSP_CLASS = {
    BspTypes.CAFE: Cafe,
    BspTypes.RESTAURANT: Restaurant,
}