from business.forms import AddressForm
from django.http.response import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from .models import *
from django.urls.base import reverse
from django.contrib.auth.decorators import login_required, user_passes_test
import random
from datetime import datetime

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
  reviews = Review.objects.filter(item=item).all()
  star_average, review_count = 0, len(reviews)
  for r in reviews:
    star_average += r.star
  star_average = 0 if len(reviews) == 0 else round(star_average / review_count, 1)
  suggests = []
  if item.category.name == "Sách":
    books = list(Book.objects.all())
    books.remove(item.book)
    item_sub_categorys = item.book.sub_category.all()
    for book in books:
      check = False
      for sub_c in item_sub_categorys:
        if sub_c in book.sub_category.all():
          check = True
      if check:
        suggests.append(book)
    if not suggests:
      suggests = books if len(books) <= 4 else books[0:4]
  elif item.category.name == "Quần áo":
    clothes = list(Clothes.objects.all())
    clothes.remove(item.clothes)
    for cloth in clothes:
      check = False
      if item.clothes.sub_category == cloth.sub_category:
        check = True
      if check:
        suggests.append(cloth)
    if not suggests:
      suggests = clothes if len(clothes) <= 4 else clothes[0:4]
  elif item.category.name == "Đồ điện tử":
    electric = list(Electric.objects.all())
    electric.remove(item.electric)
    for elect in electric:
      check = False
      if item.electric.sub_category == elect.sub_category:
        check = True
      if check:
        suggests.append(elect)
    if not suggests:
      suggests = electric if len(electric) <= 4 else electric[0:4]
  if len(suggests) > 4:
    random.shuffle(suggests)
    suggests = suggests[0:4]
  if request.method == "GET":
    context = {
      "item": item,
      "suggests": suggests,
      "star_average": star_average,
      "review_count": review_count,
      "reviews": reviews,
      "dstars": [1,2,3,4,5],
    }
    return render(request, "item.html", context)

@login_required
def review(request):
  if request.method == "POST":
    review = Review()
    review.customer = request.user.customer_info
    review.star = request.POST.get("rating")
    review.content = request.POST.get("content")
    item = int(request.POST.get("item"))
    review.item = Item.objects.get(pk=item)
    review.save()
    return redirect(reverse('item', args=[item]))

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
    itemms = Item.objects.all()
    items = []
    for item in itemms:
      if searchData.strip().lower() in item.name.lower():
        items.append(item) 
    if not items:
      categorys = Category.objects.all()
      for category in categorys:
        if searchData.lower() in category.name.lower():
          items.extend(list(category.category_items.all()))
    if not items:
      sub_categorys = SubCategory.objects.all()
      for sub_category in sub_categorys:
        if searchData.lower() in sub_category.name.lower():
          items.extend(list(book.item for book in sub_category.book_sub_category.all()))
          items.extend(list(clothes.item for clothes in sub_category.clothes_sub_category.all()))
          items.extend(list(electric.item for electric in sub_category.electric_sub_category.all()))
    context = {
      "items": items,
      "search_data": searchData,
    }
    return render(request, "search_result.html", context)

@user_passes_test(lambda user : user.is_staff)
def staff_home(request):
  return render(request, "staff_home.html")

@user_passes_test(lambda user : user.is_staff)
def order_management(request, status):
  if request.method == "GET": 
    orders = []
    status = status.upper()
    orders = Order.objects.filter(order_status=status)
    context = {
      "orders": orders,
      "status": status
    }
    return render(request, "order_management.html", context)
  elif request.method == "POST":
    order_id = int(request.POST.get("order_id"))
    order_status = request.POST.get("order_status")
    order = Order.objects.get(pk=order_id)
    order.order_status = order_status
    order.save()
    now = datetime.now()
    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
    message = Message()
    message.staff = request.user.staff_info
    message.customer = order.customer
    rev_status = order_status.lower()
    message.content = f"Your order code OD{order.pk} is {rev_status} at {dt_string}."
    message.save()
    return redirect(reverse("order_management", args=[rev_status]))

@user_passes_test(lambda user : user.is_staff)
def order_detail(request, pk):
  order = Order.objects.get(pk=pk)
  cartItems = []
  for cartItem in CartItem.objects.filter(order=order):
    cartItems.append(cartItem)
  context = {
    "order": order,
    "cartItems": cartItems,
  }
  return render(request, "order_detail.html", context)

@login_required
def get_notifycation(request):
  messages = Message.objects.filter(customer=request.user.customer_info).all()
  context = {
    "messages": messages,
  }
  return render(request, "notification.html", context)

@user_passes_test(lambda user : user.is_staff)
def feedback(request):
  if request.method == "GET":
    reviews = Review.objects.all()
    context = {
      "reviews": reviews,
      "dstars": [1,2,3,4,5],
    }
    return render(request, "feedback.html", context)
  elif request.method == "POST":
    feedback = ShopFeedback()
    feedback.review = Review.objects.get(pk=int(request.POST.get("review_id")))
    feedback.content = request.POST.get("content")
    feedback.save()
    return redirect(reverse("feedback"))
