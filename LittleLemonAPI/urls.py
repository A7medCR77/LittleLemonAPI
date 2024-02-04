from django.urls import path,include
from . import views
from rest_framework import routers

router = routers.DefaultRouter()
router.register("menu-items",views.MenuItemView)
router.register("groups/manager/users",views.ManagerGroupView)
router.register("groups/delivery-crew/users",views.DeliveryCrewGroupView)
router.register("cart/menu-items",views.CartItemView)
router.register("orders",views.OrderView)

urlpatterns = [
    path('', include(router.urls)),
]
