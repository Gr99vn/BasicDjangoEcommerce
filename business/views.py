from business.forms import AddressForm
from django.http.response import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from .models import *
from django.urls.base import reverse
from django.contrib.auth.decorators import login_required

# Create your views here.
def myAccount(request):
  customer = Customer.objects.filter(user=request.user).first()
  form = AddressForm()
  context = {
    "customer": customer,
    "form": form,
}
  return render(request, "account.html", context)


def customerAddress(request):
  if request.method == "POST":
    form = AddressForm(request.POST)
    if form.is_valid():
      address = Address()
      address.address_type = form.cleaned_data["address_type"]
      address.apartment_number = form.cleaned_data["apartment_number"]
      address.street = form.cleaned_data["street"]
      address.distric = form.cleaned_data["distric"]
      address.city_or_province = form.cleaned_data["city_or_province"]
      address.phone = form.cleaned_data["phone"]
      address.customer = request.user.customer_info
      address.save()
  return redirect(reverse("myAccount"))

def home(request):
  books = Book.objects.all()
  clothes = Clothes.objects.all()
  electrics = Electric.objects.all()
  context = {
    "books": books,
    "clothes": clothes,
    "electrics": electrics,
  }
  return render(request, "home.html", context)

def item(request, pk):
  item = Item.objects.get(pk=pk)

  if request.method == "GET":
    context = {
      "item": item
    }
    return render(request, "item.html", context)

@login_required
def bookItem(request):
  if request.method == "POST":
    pk = int(request.POST.get("pk"))
    item = Item.objects.get(pk=pk)
    customer = Customer.objects.filter(user=request.user).first()
    if not Cart.objects.filter(customer=customer):
      cart = Cart()
      cart.customer=customer
      cart.save()
    else:
      cart = Cart.objects.filter(customer=customer).first()
    quantity = int(request.POST.get("quantity"))
    cartItem = CartItem()
    cartItem.item = item
    cartItem.cart = cart
    cartItem.quantity = quantity
    cartItem.save()
    return redirect(reverse("cart"))
  else:
    return redirect(reverse("home"))

@login_required
def cart(request):
  customer = Customer.objects.filter(user=request.user).first()
  cart = Cart.objects.filter(customer=customer).first()
  if cart is None:
    cartItems = []
  else :
    cartItems = cart.bookItems.all().filter(order__isnull=True)
  context = {
    "cart": cart,
    "cartItems": cartItems,
  }
  return render(request, "cart.html", context)
  
@login_required
def deleteCartItem(request):
  if request.is_ajax and request.method == "POST":
    pk = int(request.POST.get("cartItemId"))
    cartItem = get_object_or_404(CartItem, pk=pk)
    if cartItem:
      cartItem.delete()
      return JsonResponse({"msg": "Delete succeed!", "pk": pk})

@login_required
def modifyCartItem(request):
  if request.is_ajax and request.method == "POST":
    pk = int(request.POST.get("cartItemId"))
    cartItem = get_object_or_404(CartItem, pk=pk)
    if cartItem:
      quantity = int(request.POST.get("quantity"))
      cartItem.quantity = quantity
      cartItem.save()
      return JsonResponse({"msg": "Save changes succeed!"})

SHIPS = [
  {
    "ship_provider": "GHN",
    "ship_fee": 30000,
  },
  {
    "ship_provider": "GHTK",
    "ship_fee": 25000,
  },
  {
    "ship_provider": "NINJA",
    "ship_fee": 35000,
  },
]

@login_required
def payment(request):
  if request.method == "POST":
    customer = Customer.objects.filter(user=request.user).first()
    cartItemIds = request.POST.getlist("cartItemIds[]", [])
    request.session["cartItemIds"] = cartItemIds
    cartItems = list()
    for pk in cartItemIds:
      cartItem = get_object_or_404(CartItem, pk=pk)
      cartItems.append(cartItem)
    context = {
      "customer": customer,
      "cartItems": cartItems,
      "ships": SHIPS,
    }
    return render(request, "payment.html", context)
  
@login_required
def createOrder(request):
  if request.method == "POST":
    customer = Customer.objects.filter(user=request.user).first()
    order = Order()
    order.total = request.POST.get("total")
    order.customer = customer
    order.save()
    shipment = Shipment()
    shipment.order = order
    shipment.ship_address = Address.objects.get(pk=int(request.POST.get("ship_address")))
    ship_index = int(request.POST.get("shipment"))
    shipment.ship_provider = SHIPS[ship_index]["ship_provider"]
    shipment.ship_fee = SHIPS[ship_index]["ship_fee"]
    shipment.save()
    payment = Payment()
    payment.order = order
    payment.payment_method = request.POST.get("payment")
    payment.total_pay = order.total
    payment.save()
    cartItemIds = request.session.get("cartItemIds", [])
    for pk in cartItemIds:
      cartItem = get_object_or_404(CartItem, pk=pk)
      if cartItem:
        cartItem.order = order
        cartItem.save()
  return redirect(reverse("orderView"))

@login_required
def orderView(request):
  customer = Customer.objects.filter(user=request.user).first()
  orders = Order.objects.filter(customer=customer)
  orderItems = []
  for order in orders:
    orderItem = {}
    orderItem["order"] = order
    cartItems = []
    for cartItem in CartItem.objects.filter(order=order):
      cartItems.append(cartItem)
    orderItem["cartItems"] = cartItems
    orderItems.append(orderItem)
  context = {
    "orderItems": orderItems,
  }
  return render(request, "order.html", context)

def search(request):
  if request.method == "GET":
    searchData = request.GET.get("search_data")
    items = Item.objects.filter(name__contains=searchData)
    context = {
      "items": items,
    }
    return render(request, "search_result.html", context)