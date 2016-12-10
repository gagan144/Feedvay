# Copyright (C) 2017 Feedvay (Gagandeep Singh: singh.gagan144@gmail.com) - All Rights Reserved
# Content in this document can not be copied and/or distributed without the express
# permission of Gagandeep Singh.
from __future__ import unicode_literals

from django.db import models
import tinymce.models as tinymce_models
from django_mysql import models as models57
from django_fsm import FSMField, transition
from django_fsm_log.decorators import fsm_log_by

from django.core.exceptions import ValidationError
from django.utils import timezone
import shortuuid
import uuid
import os
import qrcode
import StringIO
from django.core.files.uploadedfile import InMemoryUploadedFile

from accounts.models import RegisteredUser
from brands.models import Brand
from form_builder.models import Form

class SurveyTag(models.Model):
    """
    Basic tags names for surveys.

    **Authors**: Gagandeep Singh
    """
    name        = models.CharField(max_length=255, default=None, db_index=True, unique=True, help_text='Name of the survey category.')
    description = tinymce_models.HTMLField(default=None, help_text='Description about this category.')

    created_on  = models.DateTimeField(auto_now_add=True, editable=False, db_index=True, help_text='Date on which this record was created.')
    modified_on = models.DateTimeField(null=True, blank=True, editable=False, help_text='Date on which this record was modified.')

    def __unicode__(self):
        return self.name

    def clean(self):
        """
        Method to clean & validate data fields.

        **Authors**: Gagandeep Singh
        """

        if self.pk:
            # Update modified date
            self.modified_on = timezone.now()

        super(self.__class__, self).clean()

    def save(self, update_theme=False, *args, **kwargs):
        """
        Pre-save method for this model.

        **Authors**: Gagandeep Singh
        """

        self.clean()
        super(self.__class__, self).save(*args, **kwargs)


class SurveyCategory(models.Model):
    """
    Model to store categories of the survey. This creates a first impression of the survey by identifying its type.
    This allows users to search survey of their interest. Also, it can be used to provide pre-defined templates
    before user starts creating questionnaire.

    **Authors**: Gagandeep Singh
    """
    name        = models.CharField(max_length=255, default=None, db_index=True, unique=True, help_text='Name of the survey category.')
    description = tinymce_models.HTMLField(default=None, help_text='Description about this category.')

    active      = models.BooleanField(default=True, help_text='If this category is active. On deactivation, it does not effect connected surveys.')

    created_on  = models.DateTimeField(auto_now_add=True, editable=False, db_index=True, help_text='Date on which this record was created.')
    modified_on = models.DateTimeField(null=True, blank=True, editable=False, help_text='Date on which this record was modified.')

    class Meta:
        verbose_name_plural = 'Survey categories'

    def __unicode__(self):
        return self.name

    def clean(self):
        """
        Method to clean & validate data fields.

        **Authors**: Gagandeep Singh
        """

        if self.pk:
            # Update modified date
            self.modified_on = timezone.now()

        super(self.__class__, self).clean()

    def save(self, update_theme=False, *args, **kwargs):
        """
        Pre-save method for this model.

        **Authors**: Gagandeep Singh
        """

        self.clean()
        super(self.__class__, self).save(*args, **kwargs)

def upload_survey_qrcode_to(instance, filename):
    id = str(uuid.uuid4())
    fname, ext = os.path.splitext(filename)
    new_filename = "{}.{}".format(id, ext.replace('.',''))

    return "surveys/{survey_uid}/{filename}".format(
        survey_uid = str(instance.survey_uid),
        filename = new_filename
    )
class Survey(models.Model):
    """
    Model to define a survey.

    **Points**:

        - Simple survey will not allow multiple survey phases.
        - Survey unique id is always attached with survey that can be shared to respondents. But only
          ``public`` and ``private`` survey are allowed to be answers.
        - Surveyor type:
            - **Company**: Field ``company`` is mandatory.
            - **Brand**: Field ``brand`` is mandatory.
            - **Individual**: ``created_by`` is used as surveyor.
        - Survey with audience as ``public`` is only visible to the public, rest are hidden.
        - Audience filer to automatically set to {} if audience type is ``self``.
        - Survey with status ``draft`` & ``paused`` are not visible to the public.

    **State chart diagram for brand status**:

        .. image:: ../../_static/surveys/survey_statechart.jpg


    **Authors**: Gagandeep Singh
    """

    # --- Enums ---
    SURVEY_UID_LEN = 8

    TYPE_SIMPLE = 'simple'
    TYPE_COMPLEX = 'complex'
    CH_TYPE = (
        (TYPE_SIMPLE, 'Simple'),
        (TYPE_COMPLEX, 'Complex')
    )

    SURVYR_COMPANY = 'company'
    SURVYR_BRAND = 'brand'
    SURVYR_INDIVIDUAL = 'individual'
    CH_SURVEYOR = (
        (SURVYR_COMPANY, 'Company'),
        (SURVYR_BRAND, 'Brand'),
        (SURVYR_INDIVIDUAL, 'Individual')
    )

    AUD_PUBLIC = 'public'
    AUD_INVITED = 'invited'
    AUD_SELF = 'self'
    CH_AUDIENCE = (
        (AUD_PUBLIC, 'Public'),
        (AUD_INVITED, 'Invited'),
        (AUD_SELF, 'Self')
    )

    ST_DRAFT = 'draft'
    ST_PUBLISHED = 'published'
    ST_PAUSED = 'paused'
    ST_STOPPED = 'stopped'
    CH_STATUS = (
        (ST_DRAFT, 'Draft'),
        (ST_PUBLISHED, 'Published'),
        (ST_PAUSED, 'Paused'),
        (ST_STOPPED, 'Stopped')
    )

    # --- Fields ---
    type        = models.CharField(max_length=10, default=None, choices=CH_TYPE, db_index=True, help_text='Type of survey - simple or complex.')
    category    = models.ForeignKey(SurveyCategory, help_text='Category of this survey.')

    # Basic
    survey_uid  = models.CharField(max_length=SURVEY_UID_LEN, default=None, blank=True, editable=False, unique=True, db_index=True, help_text='Eight letter survey unique id that can be shared user users.')
    title       = models.CharField(max_length=512, default=None, db_index=True, help_text='Title of the survey. This is visible to the public')
    description = tinymce_models.HTMLField(default=None, help_text='Detailed description about the survey. This tells what the survey is all about.')

    tags        = models.ManyToManyField(SurveyTag, default=None, blank=True, help_text='Tag survey with keywords.')
    start_date  = models.DateField(help_text='Start date of this survey (Included).')
    end_date    = models.DateField(help_text='End date of this survey (Included).')

    # Surveyor
    surveyor_type = models.CharField(max_length=16, default=None, choices=CH_SURVEYOR, help_text='Who is conducting this survey?')
    # TODO: company     = models.ForeignKey(Company, null=True, blank=True, help_text='Company reference if the surveyor is a company.')
    brand       = models.ForeignKey(Brand, null=True, blank=True, help_text='Brand reference if the surveyor is a brand.')

    # Audience
    audience_type    = models.CharField(max_length=16, default=None, choices=CH_AUDIENCE, help_text='Type of the target audience.')
    audience_filters = models57.JSONField(default=None, blank=True, null=True, help_text='Expression to filter the audience. (Only for public & invited)')
    audience_cease   = models.BooleanField(verbose_name='Cease further audience', default=False, help_text='Switch to stop new audience that is, if checked will not allow new user to open survey.')

    # Status
    status      = FSMField(default=ST_DRAFT, choices=CH_STATUS, protected=True, help_text='Status of the survey')

    # Misc
    qrcode      = models.ImageField(upload_to=upload_survey_qrcode_to, blank=True, editable=False, help_text='Qrcode image file for this survey.')
    created_by  = models.ForeignKey(RegisteredUser, editable=False, help_text='User that created this survey.')
    created_on  = models.DateTimeField(auto_now_add=True, editable=False, db_index=True, help_text='Date on which this record was created.')
    modified_on = models.DateTimeField(null=True, blank=True, editable=False, help_text='Date on which this record was modified.')

    @property
    def phases(self):
        return self.surveyphase_set.all().order_by('order')

    def __unicode__(self):
        return self.title

    # --- Transitions ---
    @fsm_log_by
    @transition(field=status, source=ST_DRAFT, target=ST_PUBLISHED)
    def trans_publish(self):
        """
        Transition edge to publish a survey. On publishing, survey is active & will automatically start
        as per ``start_date`` & ``end_date``.

        **Authors**: Gagandeep Singh
        """
        pass

    @fsm_log_by
    @transition(field=status, source=ST_PUBLISHED, target=ST_PAUSED)
    def trans_pause(self):
        """
        Transition edge to pause a survey after it has been published. Puases survey are not executable.
        This is used when user wants to halt a survey for sometime.

        **Authors**: Gagandeep Singh
        """
        pass

    @fsm_log_by
    @transition(field=status, source=ST_PAUSED, target=ST_PUBLISHED)
    def trans_resume(self):
        """
        Transition edge to resume a paused survey. After resuming, it will be visible to public.

        **Authors**: Gagandeep Singh
        """
        pass

    @fsm_log_by
    @transition(field=status, source=[ST_PUBLISHED,ST_PAUSED], target=ST_STOPPED)
    def trans_stop(self):
        """
        Transition edge to stop a survey. A survey after stop cannot be restarted.

        **Authors**: Gagandeep Singh
        """
        pass

    # --- /Transitions ---

    def update_qrcode(self, auto_save=True):
        """
        Method to update survey qrcode.

        **Authors**: Gagandeep Singh
        """
        survey_uid = self.survey_uid
        if self.survey_uid is None:
            raise ValidationError("Survey uid is not set yet.")

        # Prepare data
        data = {
            "type": "survey",
            "survey_uid": survey_uid,
            "title": self.title
        }

        # Create qrcode image
        qr = qrcode.QRCode(
            version=3,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=2,
        )

        qr.add_data(data)
        qr.make(fit=True)

        img = qr.make_image()

        # Create image file
        img_io = StringIO.StringIO()
        img.save(img_io, format='JPEG')

        img_file = InMemoryUploadedFile(
            img_io,
            None,
            'qrcode_{}.jpg'.format(survey_uid),
            'image/jpeg',
            img_io.len,
            None
        )

        # Set file
        self.qrcode = img_file

        if auto_save:
            self.save()


    def clean(self):
        """
        Method to clean & validate data fields.

        **Authors**: Gagandeep Singh
        """

        if not self.pk:
            # Set, check & correct survey_uid
            self.survey_uid = Survey.generate_uid()

            # Set qrcode
            self.update_qrcode(auto_save=False)

        # Check surveyor type
        if self.surveyor_type == Survey.SURVYR_COMPANY:
            raise NotImplementedError("Surveyor as company is not implemented yet.")
        elif self.surveyor_type == Survey.SURVYR_BRAND:
            if self.brand is None:
                raise ValidationError("Please select brand surveyor.")
        elif self.surveyor_type == Survey.SURVYR_INDIVIDUAL:
            pass
        else:
            ValidationError("Invalid surveyor type '{}'.".format(self.surveyor_types))

        # Check & correct audience type
        if self.audience_type == Survey.AUD_SELF:
            self.audience_filters = {}

        if self.pk:
            # Update modified date
            self.modified_on = timezone.now()

        super(self.__class__, self).clean()

    def save(self, *args, **kwargs):
        """
        Pre-save method for this model.

        **Authors**: Gagandeep Singh
        """

        self.clean()
        super(self.__class__, self).save(*args, **kwargs)

    @staticmethod
    def generate_uid():
        """
        Method to generate a unique survey id.

        :return:  ``Survey.SURVEY_UID_LEN`` letters long unique id.
        """
        survey_uid = shortuuid.ShortUUID().random(length=Survey.SURVEY_UID_LEN).lower()
        while Survey.objects.filter(survey_uid=survey_uid).exists():
            survey_uid = shortuuid.ShortUUID().random(length=Survey.SURVEY_UID_LEN).lower()

        return survey_uid



class SurveyPhase(models.Model):
    """
    Model to define survey phase. Each survey must has a phase whether it is simple or complex.
    Since, for complex survey with multiple phases that has its own separate form, it is the phase
    to which form is attached and not the survey itself.

    **Points**:
        - Form is attached to the survey phase and not the survey.
        - For **Simple** survey there can only be one phase whereas for **comples** survey there is no
          limitation in the phases.
        - Order of the phase is determined by the field ``order``. Phase with lowest order
          is conducted first follwed by second least and so on.
        - All child phases must belong to same survey.

    **Authors**: Gagandeep Singh
    """

    survey      = models.ForeignKey(Survey, db_index=True, help_text='Survey to which this phase belongs.')
    form        = models.ForeignKey(Form, db_index=True, help_text='Questionnaire form for this phase.')
    order       = models.SmallIntegerField(db_index=True, help_text='Order of this phase in the survey. Phase with lower order is conducted first.')

    # Misc
    created_on  = models.DateTimeField(auto_now_add=True, editable=False, db_index=True, help_text='Date on which this record was created.')
    modified_on = models.DateTimeField(null=True, blank=True, editable=False, help_text='Date on which this record was modified.')

    class Meta:
        ordering = ('survey', 'order')

    def __unicode__(self):
        return "{} - {}".format(self.survey.survey_uid, self.id)

    def clean(self):
        """
        Method to clean & validate data fields.

        **Authors**: Gagandeep Singh
        """

        # Check survey type
        if self.survey.type == Survey.TYPE_SIMPLE:
            if SurveyPhase.objects.filter(survey_id=self.survey_id).exists():
                raise ValidationError("You cannot add more than one phase for simple survey.")

        if self.pk:
            # Update modified date
            self.modified_on = timezone.now()

        super(self.__class__, self).clean()

    def save(self, update_theme=False, *args, **kwargs):
        """
        Pre-save method for this model.

        **Authors**: Gagandeep Singh
        """

        self.clean()
        super(self.__class__, self).save(*args, **kwargs)


