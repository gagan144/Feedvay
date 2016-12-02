# Copyright (C) 2017 Feedvay (Gagandeep Singh: singh.gagan144@gmail.com) - All Rights Reserved
# Content in this document can not be copied and/or distributed without the express
# permission of Gagandeep Singh.
from rest_framework import serializers
# from fcm.models import Device
from accounts.models import UserDevice

class UserDeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserDevice # Device
        fields = ('user', 'dev_id', 'reg_id', 'name', 'is_active')