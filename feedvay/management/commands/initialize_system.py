# Copyright (C) 2017 Feedvay (Gagandeep Singh: singh.gagan144@gmail.com) - All Rights Reserved
# Content in this document can not be copied and/or distributed without the express
# permission of Gagandeep Singh.
from optparse import make_option
from django.core.management.base import BaseCommand, CommandError
import codecs
import json
import os
import StringIO
from django.core.files.uploadedfile import InMemoryUploadedFile

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DIR_DB = os.path.join(BASE_DIR, "db")

class Command(BaseCommand):
    """
    Django admin command to initialize newely configured Feedvay project.
    This must be run after the ssytem has been perfectly configured. This
    command mostly includes database data initialization.

    **Authors**: Gagandeep Singh
    """
    help = 'Initialises system and creates all necessary database entries. ' \
           'Use this command only after all database syncs have been done.'
    requires_system_checks = True

    def db_languages(self):
        """
        Initializes 'Language' table and 'Translations' collection that contains
        commonly used text and their translations.

        **Authors**: Gagandeep Singh
        """
        self.stdout.write('* Creating database entries for languages & translations (App:languages)...')
        from languages.models import Language, Translation

        # (a) Set 'Language' database
        self.stdout.write("\tLanguages: preparing data...")
        # Read json database
        with codecs.open(os.path.join(DIR_DB, "db_languages.json"), 'r', encoding="utf-8") as file_db:
            data_langs = json.load(file_db)

        # Loop & make entries
        counter = 0
        for row in data_langs:
            list_new_langs = []
            if not Language.objects.filter(code=row['code']).exists():
                list_new_langs.append(
                    Language(
                        code        = row['code'],
                        name        = row['name'],
                        name_native = row['name_native'],
                        description = row['description'],
                        active      = row['active'],
                    )
                )
                counter += 1

            if len(list_new_langs):
                Language.objects.bulk_create(list_new_langs)

        self.stdout.write("\tLanguages: {} languages inserted.".format(counter))

        # (b) Set 'Translations' database
        self.stdout.write("\tTranslations: Inserting translations...")
        # Read json database
        with codecs.open(os.path.join(DIR_DB, "db_translations.json"), 'r', encoding="utf-8") as file_db:
            data_trans = json.load(file_db)

        # Loop & make entries
        counter = 0
        for row in data_trans:
            if not Translation.objects.filter(unique_id=row['unique_id']).count():
                trans = Translation(**row)
                trans.save()

                counter += 1

        self.stdout.write("\tTranslations: {} translations inserted.".format(counter))


    def db_themes(self):
        """
        Initializes theme tables such as Theme, ThemeSkin.

        **Authors**: Gagandeep Singh
        """
        self.stdout.write('* Creating database entries for Theme,ThemeSkin (App:form_builder)...')
        from form_builder.models import Theme, ThemeSkin

        self.stdout.write("\tTheme: preparing data...")

        # Read json database
        f = open(os.path.join(DIR_DB, "db_themes.json"), 'r')
        data = json.loads(f.read())
        f.close()

        # loop data & make entries if not present
        count = 0
        for thm_data in data:
            if not Theme.objects.filter(code=thm_data['code']).exists():

                # Get icon file and create an InMemory object
                f = file(os.path.join(BASE_DIR, thm_data['icon_path']),'rb')
                f_io = StringIO.StringIO(f.read())
                mem_file_icon = InMemoryUploadedFile(
                    f_io,
                    u'file',
                    os.path.basename(thm_data['icon_path']),
                    u'image/jpeg',
                    f_io.len,
                    None
                )
                f.close()

                # Create 'Theme' entry
                theme = Theme.objects.create(
                    code = thm_data['code'],
                    name = thm_data['name'],
                    description = thm_data['description'],
                    icon = mem_file_icon,
                    active = thm_data['active']
                )

                # Create 'ThemeSkin' for this theme
                for skn_data in thm_data['skins']:
                    skin = ThemeSkin.objects.create(
                        theme = theme,
                        code = skn_data['code'],
                        name = skn_data['name'],
                        description = skn_data['description'],
                        color = skn_data['color'],
                        active = skn_data['active']
                    )

                count += 1
        self.stdout.write('\tThemes: {} themes inserted.'.format(count))

    def db_market(self):
        """
        Initializes all tables in market app

        **Authors**: Gagandeep Singh
        """
        self.stdout.write("* Creating database entries for 'market' app...")
        from market.models import RestaurantCuisine, BspTag

        # --- (a) Restaurants Cuisines ---
        self.stdout.write("\tRestaurant Cuisine: preparing data...")

        # Read json database
        f = open(os.path.join(DIR_DB, "db_market_restaurant_cuisines.json"), 'r')
        data_cuisines = json.loads(f.read())
        f.close()

        count = 0
        for row in data_cuisines:
            cus, is_new = RestaurantCuisine.objects.get_or_create(
                name = row['name'],
                defaults = {
                    "active": row["active"]
                }
            )

            if is_new:
                count +=1

        self.stdout.write("\tRestaurant Cuisine: {} cuisies inserted.".format(count))

        # --- (b) BSP Tags ---
        self.stdout.write("\n\tBSP Tags: preparing data...")

        # Read json database
        f = open(os.path.join(DIR_DB, "db_market_bsptags.json"), 'r')
        data_tags = json.loads(f.read())
        f.close()

        count = 0
        for row in data_tags:
            BspTag.objects(
                name = row['name']
            ).update_one(
                set__list_bsp_types = row["list_bsp_types"],
                set__active = row["active"],
                upsert = True
            )

            count +=1

        self.stdout.write("\tBSP Tags: {} tags upserted.".format(count))

    def handle(self, *args, **options):
        self.stdout.write('Initializing Feedvay system, please wait...')

        # (1) Create database entries for language & translations
        self.db_languages()

        # (2) Create database entries for themes
        self.db_themes()

        # (3) Market
        self.db_market()

        # Completed!
        self.stdout.write("Done! All initialization completed. You are now good to go.")


