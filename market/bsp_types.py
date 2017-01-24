# Copyright (C) 2017 Feedvay (Gagandeep Singh: singh.gagan144@gmail.com) - All Rights Reserved
# Content in this document can not be copied and/or distributed without the express
# permission of Gagandeep Singh.
from django.core.exceptions import ValidationError
from jsonobject import *
from jsonobject.properties import SetProperty


class BspTypes:
    """
    Enum class that defines various types of business and Service points.
    These are fundamental types and not categories.

    **Authors**: Gagandeep Singh
    """
    # ATM = 'atm'
    # BANK = 'bank'
    # DOCTOR = 'doctor'   # <<-- category
    # TOILET = 'toilet'
    # MOBILE_APP = 'app'
    RESTAURANT = 'restaurant'
    # WEBSITE = 'website'

    choices = (
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


class Restaurant(JsonObject):
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
        CTG_CAFES = 'cafes'
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
            (CTG_CAFES,CTG_CAFES),
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

    # --- Fields ---
    category    = SetProperty(unicode, required=True)   # Category of eatery

    food_type   = SetProperty(unicode, required=True) # Type of food; veg, non-veg, egg
    cuisines    = SetProperty(unicode, required=True)
    highlights  = SetProperty(unicode, exclude_if_none=True)    # Highlighting features
    recommendations = StringProperty(exclude_if_none=True) # Any recommendations

    home_delivery   = BooleanProperty(default=False, required=True) # Home delivery available or not
    average_cost_2  = IntegerProperty(default=None, exclude_if_none=True)   # Average cost for two person in native currency
    payment_methods = SetProperty(unicode, required=True)   # Mode of payments

    # def __init__(self, _obj=None, **kwargs):
    #     super(Restaurants, self).__init__(_obj=_obj, **kwargs)



"""
# ---------- Delete -----------

r = Restaurant(
    category = set([Restaurant.ENUMS.CTG_FOOD_STALLS]),
    food_type = set([Restaurant.ENUMS.FOOD_NON_VEG, Restaurant.ENUMS.FOOD_VEG]),
    cuisines = set(['chines', 'north']),
    home_delivery = True,
    average_cost_2 = 500,
    payment_methods = set([PaymentMethods.CARDS, PaymentMethods.WALLETS, PaymentMethods.CASH])
)
print r
print "\n"
print r.to_json()

print r.ENUMS.CH_FOOD_TYPE

# new_r = Eatery(r.to_json())
# print new_r.payment_methods
"""