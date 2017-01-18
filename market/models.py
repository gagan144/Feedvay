# Copyright (C) 2017 Feedvay (Gagandeep Singh: singh.gagan144@gmail.com) - All Rights Reserved
# Content in this document can not be copied and/or distributed without the express
# permission of Gagandeep Singh.
from __future__ import unicode_literals

from django.db import models
from django_mysql import models as models57
from django.utils import timezone
from django.template.defaultfilters import slugify
from django.core.exceptions import ValidationError

from django.contrib.auth.models import User

from accounts.models import RegisteredUser

# ---------- Business or Service Point ----------
class BusinessServicePoint(models57.Model):
    """
    Business or Service Point (BSP) is a generic term that refers to place where consumer
    can consume a product or can be offered with a service. Such a place can be a business point
    where a person sells a product or conducts operations or runs his business. This can
    also be a place that is offered a service.

    Examples:
        Local business shop such as restaurants, clothing, repair shop, grocery shop etc,
        Government office, post boxes, ATMs, Company office, pan wala shop, chemist, hospital,
        Tutor, Coaching center, mobile app/website lets say to order food or buy products and so on.

    **Points**:

        - BSP can be physical (Place/Person) or virtual (Website/App).
        - Each BSP has its unique id.
        - Each BSP is associated with one type that defines its attributes.
          Type cannot be changed once selected.
        - Attributes are not kept in this table. Instead are placed in mongodb collection.
        - This model only includes basic fields that are mostly used for entity relationships.

    **Authors**: Gagandeep Singh
    """

    bsp_code    = models.CharField(max_length=255, unique=True, db_index=True, help_text='Unique id of the BSP. This will be shared with public.')
    name        = models.CharField(max_length=255, db_index=True, help_text='Name of the BSP. This can be duplicate.')
    slug        = models.SlugField(unique=True, blank=True, db_index=True, help_text='Slug of the name used for url referencing.')

    description = models.TextField(max_length=512, help_text='Description about the BSP. Include keywords for better SEO and keep characters between 150-160.')

    # type        = models
    # organisation    =
    # brand         =
    members      = models.ManyToManyField(RegisteredUser, help_text='People who manages this BSP. These can be owners or compant employee.')

    # Controls
    active      = models.BooleanField(default=True, db_index=True, help_text='Control to temporarly hide BSP if set false.')

    # Misc
    created_by  = models.ForeignKey(User, editable=False, help_text='User that created this BSP. This can be registered user or staff user.')
    created_on  = models.DateTimeField(auto_now_add=True, editable=False, db_index=True, help_text='Date on which this record was created.')
    modified_on = models.DateTimeField(null=True, blank=True, editable=False, help_text='Date on which this record was modified.')

    class Meta:
        ordering = ('name', )


    def clean(self):
        """
        Method to clean & validate data fields.

        **Authors**: Gagandeep Singh
        """

        if self.pk:
            # Update modified date
            self.modified_on = timezone.now()

        # Name slug
        if not self.slug:
            self.slug = slugify(self.name)

        super(self.__class__, self).clean()

    def save(self, update_theme=False, *args, **kwargs):
        """
        Pre-save method for this model.

        **Authors**: Gagandeep Singh
        """

        self.clean()
        super(self.__class__, self).save(*args, **kwargs)

    def delete(self, using=None, keep_parents=False):
        raise ValidationError("You cannot delete a BSP. Mark it inactive instead.")