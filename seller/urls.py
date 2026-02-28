from django.urls import path
from . import views
urlpatterns = [
          path("usersellerbridge/",views.user_seller_bridge,name="user_seller"),
          path("sellerregistration/",views.seller_registration,name="seller_registration"),
          path("sellerdashboard/",views.seller_dashboard,name="seller_dashboard"),
          path("sellerproducts/",views.seller_products,name="seller_product"),
          path("addproduct/",views.add_products,name="add_product"),
          path("inventory/",views.seller_inventory,name="seller_inventory"),
          path("sellerorder/",views.seller_order,name="seller_order"),
          path("sellerearnings/",views.seller_earnings,name="seller_earnings"),
          path("offerdiscount/",views.offer_discount,name="offer_discount"),
          path("sellerreviews/",views.seller_reviews,name="seller_reviews"),
          path("sellerprofile/",views.seller_profile,name="seller_profile"),
          path("sellersettings/",views.seller_settings,name="seller_settings"),


]