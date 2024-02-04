from django.shortcuts import render,get_object_or_404
from rest_framework import viewsets,permissions,status
from . import models
from . import serializers
from rest_framework.response import Response
from django.contrib.auth.models import User,Group
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import action,api_view,authentication_classes, permission_classes
from datetime import date
from . import Permissions
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.pagination import PageNumberPagination
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle


class MenuItemView(viewsets.ModelViewSet):
    queryset = models.MenuItem.objects.all()
    serializer_class = serializers.MenuItemSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    filter_backends = [SearchFilter, OrderingFilter]
    throttle_classes = [UserRateThrottle, AnonRateThrottle]
    search_fields = ['title']
    ordering_fields = ['title']

    # Pagination
    pagination_class = PageNumberPagination
    page_size = 10
    

    def create(self, request, *args, **kwargs):
        if self.request.user.groups.filter(name='Manager').exists():
            return super().create(request, *args, **kwargs)
        
        return Response({'massage':'Denies access'},status=status.HTTP_401_UNAUTHORIZED)
    
    def update(self, request, *args, **kwargs):
        if self.request.user.groups.filter(name='Manager').exists():
            return super().update(request, *args, **kwargs)
        
        return Response({'massage':'Denies access'},status=status.HTTP_401_UNAUTHORIZED)

    def destroy(self, request, *args, **kwargs):
        if self.request.user.groups.filter(name='Manager').exists():
            return super().destroy(request, *args, **kwargs)

        return Response({'massage':'Denies access'},status=status.HTTP_401_UNAUTHORIZED)


class ManagerGroupView(viewsets.ModelViewSet):
    queryset = User.objects.filter(groups__name='Manager')
    serializer_class = serializers.GroupSerializer
    permission_classes = [Permissions.IsManager]
    authentication_classes = [TokenAuthentication]
    throttle_classes = [UserRateThrottle, AnonRateThrottle]

    def create(self, request, *args, **kwargs):
            MyUserId = request.data.get('id')

            if MyUserId == None:
                return Response({'message':'you should set UserId'},status=status.HTTP_400_BAD_REQUEST)
            
            MyUser = User.objects.get(id=MyUserId)
            if MyUser.groups.filter(name="Manager").exists():
                return Response({'message':'already exist'},status=status.HTTP_400_BAD_REQUEST)
            
            MyGroup = Group.objects.get(name="Manager")
            MyGroup.user_set.add(MyUserId)
            return Response(status=status.HTTP_201_CREATED)
    
    def destroy(self, request, *args, **kwargs):
        MyUserId = kwargs.get('pk')
        MyUser = User.objects.get(pk=MyUserId)

        if not MyUser.groups.filter(name="Manager").exists():
            return Response(status=status.HTTP_404_NOT_FOUND)

        MyGroup = Group.objects.get(name="Manager")
        MyUser.groups.remove(MyGroup)

        return Response(status=status.HTTP_200_OK)


class DeliveryCrewGroupView(viewsets.ModelViewSet):
    queryset = User.objects.filter(groups__name='Delivery crew')
    serializer_class = serializers.GroupSerializer
    permission_classes = [Permissions.IsManager]
    authentication_classes = [TokenAuthentication]
    throttle_classes = [UserRateThrottle, AnonRateThrottle]

    def create(self, request, *args, **kwargs):
            MyUserId = request.data.get('id')

            if MyUserId == None:
                return Response({'message':'you should set UserId'},status=status.HTTP_400_BAD_REQUEST)
            
            MyUser = User.objects.get(id=MyUserId)
            if MyUser.groups.filter(name="Delivery crew").exists():
                return Response({'message':'already exist'},status=status.HTTP_400_BAD_REQUEST)

            MyGroup = Group.objects.get(name="Delivery crew")
            MyGroup.user_set.add(MyUserId)
            return Response(status=status.HTTP_201_CREATED)
    
    def destroy(self, request, *args, **kwargs):
        MyUserId = kwargs.get('pk')
        MyUser = User.objects.get(pk=MyUserId)

        if not MyUser.groups.filter(name="Delivery crew").exists():
            return Response(status=status.HTTP_404_NOT_FOUND)

        MyGroup = Group.objects.get(name="Delivery crew")
        MyUser.groups.remove(MyGroup)

        return Response(status=status.HTTP_200_OK)


class CartItemView(viewsets.ModelViewSet):
    queryset = models.Cart.objects.all()
    serializer_class = serializers.CartSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    throttle_classes = [UserRateThrottle, AnonRateThrottle]

    def get_queryset(self):
        UserId = self.request.user.id
        return models.Cart.objects.filter(user=UserId)
    
    @action(detail=False, methods=['delete'])
    def DeleteAllMenuItems(self, request):
        try:
            MenuItemsToDelete = self.get_queryset()
            MenuItemsToDelete.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class OrderView(viewsets.ModelViewSet):
    queryset = models.Order.objects.all()
    serializer_class = serializers.OrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['user', 'delivery_crew']
    ordering_fields = ['user', 'delivery_crew']

    # Pagination
    pagination_class = PageNumberPagination
    page_size = 10

    def get_queryset(self):
        if self.request.user.groups.filter(name = 'Manager').exists():
            return models.Order.objects.all()

        elif self.request.user.groups.filter(name = 'Delivery crew').exists():
            DeliveryId = self.request.user.id
            return models.Order.objects.filter(delivery_crew_id = DeliveryId)
        
        else:
            UserId = self.request.user.id
            return models.Order.objects.filter(user_id = UserId)
    
    def create(self, request, *args, **kwargs):
        UserId = self.request.user.id
        CurrentUser = User.objects.get(id=UserId)
        GetAllCartItems = models.Cart.objects.filter(user = UserId)

        Order = models.Order()
        Order.user = CurrentUser
        Order.status = False
        Order.date = date.today()
        Order.total=0
        
        for i in GetAllCartItems:
            Order.total += i.price
        
        Order.save()
        
        for i in GetAllCartItems:
            OrderItem = models.OrderItem()
            OrderItem.order = Order
            OrderItem.menuitem = i.menuitem
            OrderItem.price = i.price
            OrderItem.quantity = i.quantity
            OrderItem.save()
        
        GetAllCartItems.delete()

        return Response(status=status.HTTP_201_CREATED)
    
    def retrieve(self, request, *args, **kwargs):
        UserId = self.request.user.id
        OrderId = kwargs.get('pk')
        CurrentOrder = models.Order.objects.get(id=OrderId)
        CurrentUser = User.objects.get(id=UserId)

        if CurrentOrder.user != CurrentUser:
            return Response({'message':'this Order does not belongs to you'},status=status.HTTP_400_BAD_REQUEST)

        try:
            AllOrderItems = models.OrderItem.objects.filter(order=CurrentOrder)
            serializer = serializers.OrderItemSerializer(AllOrderItems, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except:
            return Response({'message': 'Order not found.'}, status=status.HTTP_404_NOT_FOUND)
    
    def update(self, request, *args, **kwargs):
        if self.request.user.is_staff:
            OrderId = kwargs.get('pk')
            CurrentOrder = models.Order.objects.get(id=OrderId)

            if self.request.user.groups.filter(name="Manager").exists():
                DeliveryId = request.data.get('id')
                if DeliveryId == None:
                    return Response({'message':'you should pass a Delivery crew id'},status=status.HTTP_400_BAD_REQUEST)
                
                MyDelivery = User.objects.get(id=DeliveryId)
                if not MyDelivery.groups.filter(name="Delivery crew"):
                    return Response({'message':'this is not Delivery crew'},status=status.HTTP_400_BAD_REQUEST)
                
                CurrentOrder.delivery_crew = MyDelivery
                CurrentOrder.status = False
                CurrentOrder.save()
            
            else:
                if CurrentOrder.status:
                    return Response({'message':'the order has already delivered'})
                
                CurrentOrder.status = True

                CurrentOrder.save()


            return Response(status=status.HTTP_200_OK)

        else:
            return Response({'message':'you do not have permission'})
        
    def destroy(self, request, *args, **kwargs):
        if self.request.user.groups.filter(name="Manager").exists():
            OrderId = kwargs.get('pk')

            try:
                CurrentOrder = models.Order.objects.get(id=OrderId)
                
                CurrentOrder.delete()

                return Response(status=status.HTTP_204_NO_CONTENT)
            
            except:
                return Response(status=status.HTTP_404_NOT_FOUND)

        else:
            return Response({'message':'you do not have permission'})
