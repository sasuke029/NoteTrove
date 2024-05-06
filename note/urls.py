from django.urls import path
from . import views
urlpatterns = [
    path('',views.index,name="home"),
    path('download_section/<str:pk>/',views.download_section,name="download_section"),
    path('login',views.loginPage,name="login"),
    path('register',views.registerPage,name="register"),
    path('logout',views.logoutUser,name="logout"),
    path('createNote',views.createNote,name="create-note"),
    path('logout',views.logoutUser,name="logout"),
    path('profile/<str:pk>/',views.profilePage,name="profile"),
    path('catagories',views.Catagories,name="catagories"),
    path('semester/<str:pk>/',views.semester,name="semester"),
    path('update_room/<int:pk>/', views.updateRoom, name='update_room'),
    path('delete_room/<int:pk>/', views.delete_room, name='delete_room'),
    path('cart',views.Cart,name="cart"),
    path('checkout',views.checkout,name="checkout"),
    path('update_profile/', views.updateUser, name="update_profile"),
    path('update_item/', views.updateItem, name="update_item"), 
    path('esewarequest/',views.esewa_request_view,name='esewarequest'),
    path('process_order/',views.processOrder,name="process_order"),
    path('my_profile/',views.my_profile,name="my_profile"),
    path('adminonly/',views.admin_button_view,name="adminonly"),
    path('customerorderdetail/<str:pk>',views.CustomerOrderDetail,name="customerorderdetail"),
    path('admin_orderitem/<str:pk>',views.admin_order_Item,name="admin_orderitem"),
    path('topics/',views.topics_page,name="topics")

      

]