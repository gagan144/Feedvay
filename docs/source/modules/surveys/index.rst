Survey
======

App that manages all surveys.


Types of survey
---------------
There are two types of surveys:

       - **Simple survey**: It is the most simplest form of survey which consist of a questionnaire
         to be filled by a respondent for data collection. These survey has shorter lifetime and
         do not have any workflow or stages. Once the survey is filled, it ends for the respondent.
         For example: Survey for collecting demograph

       - **Complex survey:** A survey is complex when it is executed in a workflow or stages. Such
         survey consist of one or more stages each with a questionnaire attached to it. A respondent
         on participating follows the complete by completing each stage one by one, advancing to the next
         until end stage is reached. Such survey are most likely to a life cycle of days or weeks.
         For example: Survey for 'New product launch' wherein product may be handed over to participant
         and his views are then captured after a week.


Surveyor: Who can conduct a survey?
-----------------------------------
A person or an organisation that can conduct asurvey is called **surveyor**. On Feedvay platform,
a survey can be conducted by an individual or an organisation or even a brand:

       1. **An individual:** Any person who has registered with Feedvay and has completed his basic KYC
          can create a survey and invite participant without any cost or service charges.
          For example: Psychiatrist wishes to do a survey on some human behavior.

            - Individual cannot create complex surveys.
            - The person who created the survey can himself the only respondent.
              For example: A blogger who rates restaurants may respond to his own created survey after
              his visit in the restaurant.

       2. **Brand:** A survey can be published by a brand of a company on any context such as products,
          services etc. For example: Starbucks want to launch new product in the market.

          Brands can create simple and complex surveys.

       3. **Company:** A company can also create a survey on its behalf for any kind of data collection.
          For example: Some research agency wants to collect demographs for a particular area.

       Campany can also create simple or complex surveys.


Respondents: Types of target audience
-------------------------------------
There can be following types audience for a survey that user can select while creating survey:

    1. **Public**: Anyone who is interested in participating in the survey. Such survey are visible to
       the public.
       User can however, use filter to limit audience on basis of certain traits suchs as respondent age, location etc.

    2. **Private/Invited audience**: User can target set of respondents from his contacts by sharing his survey
       link via unique id, barcode scan, social media sharing or any kind of personal invitation.

    3. **Self**: The surveyor can himself be the only respondent for his survey. For example, a blogger who rates
       restaurants may respond to his own created survey after his visit in the restaurant. This allows user
       to collect data personally for thier study or research.



Contents
--------

    .. toctree::
       :maxdepth: 2
       :titlesonly:

       models
       decorators
       forms
       views
       api

