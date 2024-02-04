from rest_framework import serializers
from django.contrib.auth.models import User
from . import models

class MenuItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.MenuItem
        fields = "__all__"

class GroupSerializer(serializers.ModelSerializer):
        class Meta:
            model = User
            fields = ['id','username']


class CartSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Cart
        fields = "__all__"

class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Order
        fields = "__all__"

class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.OrderItem
        fields = "__all__"
