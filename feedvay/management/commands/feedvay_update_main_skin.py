# Copyright (C) 2017 Feedvay (Gagandeep Singh: singh.gagan144@gmail.com) - All Rights Reserved
# Content in this document can not be copied and/or distributed without the express
# permission of Gagandeep Singh.

from django.core.management.base import BaseCommand, CommandError
import os

from utilities.theme import render_theme

class Command(BaseCommand):
    """
    Django management command to create or update default 'Feedvay' theme.
    This takes ``THEME_DEFAULT`` parameters in ``settings.py`` and renders project theme
    using '/template/theme/inspinia-style-template.css' css file and finally
    create/overrides '/static/ui/css/style-default.css'

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

        user_input = raw_input("This will override '{}' file. Are you sure (y/n)?".format(PATH))
        if user_input in ['Y', 'y']:
            self.stdout.write(self.style.SUCCESS('Rendering default project theme...'))
            content = render_theme(
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

            self.stdout.write(self.style.SUCCESS('Success! Default theme for Feedvay updated.'))
        else:
            self.stdout.write(self.style.SUCCESS('Cancelled!'))
