# Copyright (C) 2017 Feedvay (Gagandeep Singh: singh.gagan144@gmail.com) - All Rights Reserved
# Content in this document can not be copied and/or distributed without the express
# permission of Gagandeep Singh.

from django.core.management.base import BaseCommand, CommandError
import os

from utilities.theme import render_skin

class Command(BaseCommand):
    """
    Django management command to create or update theme. This command updates all skin
    files for brand as well as for Feedvay project.

    For Feedvay, it takes ``THEME_DEFAULT`` parameters in ``settings.py`` and for brands, reads
    paramters from the model and create/updates all skin files using '/template/theme/inspinia-style-template.css'
    into their respective directories.

    **Authors**: Gagandeep Singh
    """
    help = "Command to create/update Feedvay theme css."
    # requires_system_checks = True
    can_import_settings = True

    # ----- Main executor -----
    def handle(self, *args, **options):
        # Import django settings
        from django.conf import settings

        PATH = os.path.join(settings.BASE_DIR, "static/ui/css/style-default.css")

        user_input = raw_input("This will override '{}' and all brand skin files. Are you sure (y/n)?".format(PATH))
        if user_input in ['Y', 'y']:
            # (1) Feedvay signature theme skin.
            self.stdout.write(self.style.SUCCESS('Rendering default project theme...'))
            content = render_skin(
                custom = False,
                clr_primary = settings.THEME_DEFAULT['primary'],
                clr_prim_hover = settings.THEME_DEFAULT['primary_dark'],
                clr_prim_disabled= settings.THEME_DEFAULT['primary_disabled']
            )
            # print content[:300]

            self.stdout.write(self.style.SUCCESS("Creating/overriding '{}' ...".format(PATH)))
            with open(PATH, 'w') as f:
                f.write(content)
                f.close()

            # (2) Brand skins
            # For every brand
            #   get parameters from model instance
            #   content = render_skin()
            #   save css file

            self.stdout.write(self.style.SUCCESS('Success! All skins updated.'))
        else:
            self.stdout.write(self.style.SUCCESS('Cancelled!'))
