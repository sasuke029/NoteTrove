import datetime
import json
from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib.auth import authenticate, login, logout
from django.views import View
from django.http import HttpResponseRedirect
from django.urls import reverse
from .models import *
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import  User
from .forms import MyUserCreationForm, NoteForm, UserForm
from django.contrib.admin.views.decorators import user_passes_test # type: ignore


# Create your views here.
@login_required
@user_passes_test(lambda user: user.is_superuser)
def admin_button_view(request):
    orders = Order.objects.filter(complete=True).order_by('-date_ordered')

    context={'orders':orders}
    return render(request, 'adminonly.html',context)


def admin_order_Item(request,pk):
    # Get the specific order based on the provided pk
    order = Order.objects.get(id=pk)
    items = order.orderitem_set.all()  # type: ignore
    customer=order.customer
    shipping=ShippingAddress.objects.filter(customer=customer).last()
    cart_items = order.get_cart_items
        

    context = {
        'customer':customer,
        'order': order,
        'shipping':shipping,
        'items':items,
        'cart_items': cart_items,

    }

    return render(request,'admin_order_item.html',context)

def index(request):

    q = request.GET.get('q') if request.GET.get('q') != None else ''
    rooms = Room.objects.filter(
        Q(topic__name__icontains=q)
    )
    
    rooms_count = rooms.count
    topics = Note.objects.all()[0:4]
    context={'rooms':rooms,'topics':topics,'rooms_count':rooms_count}
    return render(request,'index.html',context)


@login_required(login_url='login')
def download_section(request,pk):
    rooms = Room.objects.get(id=pk)
    user =  rooms.host
    similarnote = Room.objects.filter(host=user)
    customer = Customer.objects.filter(user=user).first();
    if customer:
        customer_name = customer.name
    else:
        customer_name = "No customer associated with this user"

    context={'rooms':rooms,'similarnote':similarnote,'customer_name':customer_name}
    return render(request,'download_section.html',context)


def profilePage(request,pk):
    user=User.objects.get(id=pk)
    rooms = user.room_set.all() # type: ignore
    customer = Customer.objects.filter(user=user).first();
    if customer:
        customer_name = customer.name
    else:
        customer_name = "No customer associated with this user"
    
    topics=Note.objects.all()[0:4]
    rooms_count = rooms.count
    context = {'user':user,'rooms':rooms,'topics':topics,'rooms_count':rooms_count,'customer_name':customer_name}
    return render(request,'profile.html',context)

@login_required(login_url='login')
def updateUser(request):
    user = request.user.customer
    form = UserForm(instance=user)

    if request.method == 'POST':
        form = UserForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            return redirect('profile', pk=user.id)

    return render(request, 'edit-profile.html', {'form': form})


def registerPage(request):
    form = MyUserCreationForm()

    if request.method == 'POST':
        form = MyUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()

            Customer.objects.create(
                user=user,
                name=request.POST.get('name'),
                email=request.POST.get('email')
            )
            login(request, user)
            return redirect('home')

        else:
            messages.error(request, 'An error occurred during registration')

    return render(request, 'login_register.html', {'form': form})


def loginPage(request):
    page = 'login'

    if request.method == 'POST':
        username = request.POST.get('username').lower()
        password = request.POST.get('password')

        try:
            user = User.objects.get(username=username)
        except:
            messages.error(request, 'User does not exist')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            # customer, created = Customer.objects.get_or_create(user=user, email=user.email)

            return redirect('home')
        else:
            messages.error(request, 'Username OR password does not exit')

    context = {'page': page}
    return render(request, 'login_register.html', context)




def logoutUser(request):
    logout(request)
    return redirect('home')


@login_required(login_url='login')
def createNote(request):
    form = NoteForm()
    topics = Note.objects.all()
    semesters= Semester.objects.all()
    department=Departments.objects.all()

    if request.method == "POST":
        topic_name = request.POST.get('topic')
        topic ,created = Note.objects.get_or_create(name=topic_name)

        semester_name = request.POST.get('semester')
        semester ,created = Semester.objects.get_or_create(name=semester_name)

        department_name = request.POST.get('department')
        department ,created = Departments.objects.get_or_create(name=department_name)

        Room.objects.get_or_create(
            topic=topic,
            host=request.user,
            description= request.POST.get('description'),
            department=department,
            semester=semester,
            avatar=request.POST.get('avatar'),
            rate=request.POST.get('rate')
            )

        return redirect('home')

    context={'topics':topics,'form':form,'semesters':semesters,'department':department}
    return render(request, 'create_note.html', context)


def Catagories(request):
    departments = Departments.objects.all()[0:5]
    q = request.GET.get('q') if request.GET.get('q') != None else ''

    rooms = Room.objects.filter(
        Q(department__name__icontains=q)
    )
    rooms_count = rooms.count
    context = {'departments':departments,'rooms_count':rooms_count,'rooms':rooms}
    return render(request,'catagories.html',context)

def semester(request,pk):
    department = Departments.objects.get(id=pk)
    semesters = department.semester_set.all() # type: ignore
    context = {'semesters':semesters}
    return render(request,'semester.html',context)


@login_required(login_url='login')
def updateRoom(request, pk):
    room = Room.objects.get(id=pk)
    form = NoteForm(instance=room)
    topics = Note.objects.all()
    semesters=Semester.objects.all()
    department=Departments.objects.all()
    if request.user != room.host:
        return HttpResponse('Your are not allowed here!!')

    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic ,created = Note.objects.get_or_create(name=topic_name)

        semester_name = request.POST.get('semester')
        semester ,created = Semester.objects.get_or_create(name=semester_name)

        department_name = request.POST.get('department')
        department ,created = Departments.objects.get_or_create(name=department_name)

        room.topic = topic
        room.department=department
        room.semester=semester
        room.description = request.POST.get('description')
        room.avatar=request.POST.get('avatar')
        room.rate=request.POST.get('rate')
        room.save()
        return redirect('home')

    context = {'form': form, 'topics': topics, 'room': room,'semesters':semesters,'department':department}
    return render(request, 'create_note.html', context)


@login_required
def delete_room(request, pk):
    room = Room.objects.get(id=pk)
    
    # Check if the user is the owner of the room
    if room.host == request.user:
        # Delete the room
        room.delete()
        messages.success(request, 'Room deleted successfully.')
    else:
        # Handle the case where the user is not the owner of the room
        # You can redirect or display an error message here
        pass

    # Redirect back to the previous page or a suitable URL
    return HttpResponseRedirect(reverse('home'))  # Adjust the URL as needed


def checkout(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all() # type: ignore
        
        cart_Items = order.get_cart_items
    else:
        items = []
        order = {'get_cart_items': 0, 'get_cart_total': 0, 'shipping': False}
        cart_Items = order['get_cart_items']

    METHOD =(
    ("Cash On Delivery","Cash On Delivery"),
    ("Esewa","Esewa"),
    )
    ORDER_STATUS=(    ("Order Recieved","Order Received"),
        ("Pending","Pending"),
        ("Processing","Processing"),
        ("Order Completed","Order Completed")
    )
    payment_options = METHOD  # Assuming METHOD is defined in your models.py
    order_status= ORDER_STATUS

    context = {
        'items': items,
        'order': order,
        'cart_Items': cart_Items,
        'payment_options': payment_options,  # Pass payment options to the template
        'order_status': order_status
    }
   
 
    return render(request, 'checkout.html', context)



def Cart(request):
    if request.user.is_authenticated:
        customer =request.user.customer
        order , created = Order.objects.get_or_create(customer=customer,complete=False)
        items = order.orderitem_set.all() # type: ignore
        cart_Items = order.get_cart_items
    else:
        items=[]
        order= {'get_cart_items':0,'get_cart_total':0,'shipping':False}
        cart_Items = order['get_cart_items']

    context = {'items':items,'order':order,'cart_Items':cart_Items}
    return render(request,'my_cart.html',context)


def my_profile(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        shipping = ShippingAddress.objects.filter(customer=customer).last()
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        previous_orders = Order.objects.filter(customer=customer, complete=True).order_by('-date_ordered')
        items = order.orderitem_set.all() # type: ignore
        cart_items = order.get_cart_items
    else:
        customer = None
        shipping = None
        items = []
        previous_orders=[]
        cart_items = 0
        order = {'get_cart_items': 0, 'get_cart_total': 0, 'shipping': False}

    context = {'shipping': shipping, 'customer': customer, 'items': items, 'order': order, 'cart_items': cart_items,'previous_orders': previous_orders}
    return render(request, 'my_profile.html', context)



def CustomerOrderDetail(request, pk):
    customer = None
    shipping = None
    items = []
    cart_items = 0
    previous_orders = []

    # Get the specific order based on the provided pk
    order = get_object_or_404(Order, id=pk)

    # Check if the authenticated user is the owner of the order
    if request.user.is_authenticated and request.user.customer == order.customer:
        customer = request.user.customer
        shipping = ShippingAddress.objects.filter(customer=customer).last()
        previous_orders = Order.objects.filter(customer=customer, complete=True)
        items = order.orderitem_set.all() # type: ignore
        cart_items = order.get_cart_items

    context = {
        'shipping': shipping,
        'customer': customer,
        'items': items,
        'order': order,
        'cart_items': cart_items,
        'previous_orders': previous_orders
    }
    return render(request, 'customerorderdetail.html', context)


def updateItem(request):

    data = json.loads(request.body)
    print(data)
    productId = data['productId']
    action = data['action']
    print('Action:',action)
    print('Product', productId)

    customer=request.user.customer
    product = Room.objects.get(id=productId)
    order , created = Order.objects.get_or_create(customer=customer, complete=False)

    quantity = 1  # Set a default quantity, which could be updated based on 'action'

    if action == 'add':
    # Increase the quantity by 1 for adding an item to the cart
        quantity = +1

    
    
    elif action == 'remove':
    # Decrease the quantity by 1 for removing an item from the cart
        quantity = -1




    orderItem, created = OrderItem.objects.get_or_create(order=order, product=product, defaults={'quantity': quantity})
    if not created:
    # If the OrderItem already exists, update the quantity accordingly
        orderItem.quantity += quantity
        orderItem.save()

# Additional logic to remove the OrderItem if the quantity becomes zero or less
    # if orderItem.quantity >=10:


    if orderItem.quantity <= 0:
        orderItem.delete()

    return JsonResponse('Item added' ,safe=False)


def processOrder(request):
    transaction_id = datetime.datetime.now().timestamp()
    data = json.loads(request.body)

    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        total = float(data['form']['total'])
        order.transaction_id = transaction_id # type: ignore

        if total == order.get_cart_total:
            order.complete = True
        order.save()
        
        # if order.complete:
        #     for item in order.orderitem_set.all(): # type: ignore
        #         # Assuming each order item corresponds to a room
        #         room_to_delete = item.product
        #         room_to_delete.delete()
              

        if order.shipping == True:
            ShippingAddress.objects.create(
                customer=customer,
                order=order,
                address=data['shipping']['address'],
                city=data['shipping']['city'],
                state=data['shipping']['state'],
            )
        
        response_data = {
            'message': 'Payment done',
            'order_id': order.id
        }
        return JsonResponse(response_data)

    else:
        print("User must logged in")

    print('Data:',request.body)

    

    return JsonResponse("Payment done",safe=False)


def esewa_request_view(request):
    if request.method == 'GET':
        o_id = request.GET.get('o_id')
        try:
            order = Order.objects.get(id=o_id)
            context = {
                "order": order
            }
            return render(request, 'esewarequest.html', context)
        except Order.DoesNotExist:
            return HttpResponse("Order not found", status=404)
    else:
        return HttpResponse("Method not allowed", status=405)


def topics_page(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''

    topics = Note.objects.filter(name__icontains=q)[0:3]
    context={'topics':topics}
    return render (request,'notes.html',context)