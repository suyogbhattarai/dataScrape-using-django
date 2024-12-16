from rest_framework import serializers
from .models import *

class companySerializer(serializers.ModelSerializer):
    class Meta:
        model=Company
        fields='__all__'


class priceHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model=priceHistory
        fields='__all__'