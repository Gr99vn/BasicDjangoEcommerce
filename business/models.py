from django.db import models
from django.contrib.auth.models import User
from django.db.models.fields.files import ImageField

ORDER_STATUS = (
  ("NEW", "NEW"),
  ("ACCEPTED", "ACCEPTED"),
  ("CANCELED", "CANCELED"),
  ("DELIVERING", "DELIVERING"),
  ("COMPLETED", "COMPLETED"),
)

SIZE = (
  ("M", "M"),
  ("L", "L"),
  ("XL", "XL"),
)

PAYMENT_METHOD = (
  ("ON DELIVER", "ON DELIVER"),
  ("BANKING", "BANKING"),
)

class Shop(models.Model):
  name = models.CharField(max_length=100)
  phone = models.CharField(max_length=20)
  mail = models.CharField(max_length=100)
  des = models.CharField(max_length=500)
  def __str__(self):
    return f"Shop {self.name}"

class Staff(models.Model):
  user = models.OneToOneField(User, related_name="staff_info", on_delete=models.CASCADE)
  staff_position = models.CharField(max_length=100)
  def __str__(self):
    return f"Staff {self.user}"

class Customer(models.Model):
  user = models.OneToOneField(User, related_name="customer_info", on_delete=models.CASCADE)
  phone = models.CharField(max_length=15, blank=True, null=True)
  def __str__(self):
    return f"Customer {self.user}"

class Address(models.Model):
  address_type = models.CharField(max_length=100)
  apartment_number = models.CharField(max_length=100, null=True)
  street = models.CharField(max_length=100, null=True)
  distric = models.CharField(max_length=100, null=True)
  city_or_province = models.CharField(max_length=100, null=True)
  phone = models.CharField(max_length=15, null=True)
  customer = models.ForeignKey(Customer, related_name="address", on_delete=models.CASCADE)
  def __str__(self):
    return f"{self.customer} {self.address_type}"
  @property
  def get_detailed_address(self):
    return f"{self.apartment_number}, {self.street}, {self.distric}, {self.city_or_province}"

class Category(models.Model):
  name = models.CharField(max_length=100)
  def __str__(self):
    return self.name

class SubCategory(models.Model):
  name = models.CharField(max_length=100)
  category = models.ForeignKey(Category, related_name="sub_categorys", on_delete=models.CASCADE)
  def __str__(self):
    return f"{self.category} {self.name}"

class Item(models.Model):
  name = models.CharField(max_length=100)
  brand = models.CharField(max_length=50)
  cost = models.FloatField() 
  remaining_quantity = models.PositiveIntegerField()
  des = models.TextField()
  category = models.ForeignKey(Category, related_name="category_items", on_delete=models.CASCADE)
  image = models.ImageField(null=True)
  def __str__(self):
    return f"Item {self.name}"

class Book(models.Model):
  item = models.OneToOneField(Item, on_delete=models.CASCADE, related_name="book")
  author = models.CharField(max_length=100)
  publishing_company = models.CharField(max_length=100)
  publishcation_date = models.DateField()
  number_of_page = models.PositiveIntegerField()
  sub_category = models.ManyToManyField(SubCategory, related_name="book_sub_category")
  def __str__(self):
    return f"Book item - {self.item}"
  @property
  def get_book_sub_category(self):
    return ",".join([s.name for s in self.sub_category.all()])

class Clothes(models.Model):
  item = models.OneToOneField(Item, on_delete=models.CASCADE, related_name="clothes")
  material = models.CharField(max_length=200)
  size = models.CharField(choices=SIZE, max_length=5, null=True, blank=True)
  sub_category = models.ForeignKey(SubCategory, related_name="clothes_sub_category", on_delete=models.CASCADE)
  def __str__(self):
    return f"Clothes item - {self.item}"

class ClothesDetail(models.Model):
  color = models.CharField(max_length=20)
  image = models.ImageField()
  clothes = models.ForeignKey(Clothes, related_name="details", on_delete=models.CASCADE)
  def __str__(self):
    return f"{self.clothes} {self.color}"

class Electric(models.Model):
  item = models.OneToOneField(Item, on_delete=models.CASCADE, related_name="electric")
  guarantee = models.IntegerField()
  sub_category = models.ForeignKey(SubCategory, related_name="electric_sub_category", on_delete=models.CASCADE)
  def __str__(self):
    return f"Electric item - {self.item}"

class Cart(models.Model):
  customer = models.ForeignKey(Customer, related_name="cart", on_delete=models.CASCADE)
  def __str__(self):
    return f"Cart - {self.customer}"

class Order(models.Model):
  customer = models.ForeignKey(Customer, related_name="order", on_delete=models.CASCADE)
  order_time = models.DateTimeField(auto_now_add=True)
  order_status = models.CharField(choices=ORDER_STATUS, default="NEW", max_length=10)
  total = models.FloatField()
  def __str__(self):
    return f"Order - {self.customer}"

class Shipment(models.Model):
  order = models.OneToOneField(Order, related_name="shipment", on_delete=models.CASCADE)
  ship_provider = models.CharField(max_length=100)
  ship_fee = models.FloatField()
  pickup_date = models.DateField(blank=True, null=True)
  expected_ship_date = models.DateField(blank=True, null=True)
  ship_address = models.ForeignKey(Address, on_delete=models.CASCADE, null=True)
  def __str__(self):
    return f"Shipment - {self.order}"

class Payment(models.Model):
  order = models.OneToOneField(Order, related_name="payment", on_delete=models.CASCADE)
  payment_method = models.CharField(choices=PAYMENT_METHOD, default="ON DELIVER", max_length=10)
  total_pay = models.FloatField()
  def __str__(self):
    return f"Payment - {self.order}"

class CartItem(models.Model):
  item = models.ForeignKey(Item, on_delete=models.CASCADE)
  quantity = models.PositiveIntegerField()
  cart = models.ForeignKey(Cart, related_name="bookItems", on_delete=models.CASCADE)
  order = models.ForeignKey(Order, related_name="orderItems", on_delete=models.CASCADE, blank=True, null=True)
  def __str__(self):
    return f"Cart item - {self.order} - {self.item}"

class Review(models.Model):
  star = models.PositiveIntegerField()
  content = models.CharField(max_length=200)
  created_time = models.DateTimeField(auto_now_add=True)
  item = models.ForeignKey(Item, related_name="item_reviews", on_delete=models.CASCADE)
  customer = models.ForeignKey(Customer, related_name="customer_reviews", on_delete=models.CASCADE)
  def __str__(self):
    return f"Review - {self.customer} - {self.item} - {self.created_time} "

class ShopFeedback(models.Model):
  review = models.ForeignKey(Review, related_name="shop_feedback", on_delete=models.CASCADE)
  content = models.CharField(max_length=200)
  created_time = models.DateTimeField(auto_now_add=True)
  def __str__(self):
    return f"Shop feedback - {self.review}"
  
class Message(models.Model):
  staff = models.ForeignKey(Staff, related_name="sent_messages", on_delete=models.CASCADE)
  customer = models.ForeignKey(Customer, related_name="sent_messages", on_delete=models.CASCADE)
  content = models.CharField(max_length=300)
  created_time = models.DateTimeField(auto_now_add=True)
  def __str__(self):
    return f"Message - {self.staff} - {self.customer} - {self.created_time}"

class Voucher(models.Model):
  value = models.FloatField()
  expired = models.DateField()
  code = models.CharField(max_length=10)
  def __str__(self):
    return f"Voucher - {self.code} - {self.value}"
 
class ProductVoucher(Voucher):
  item = models.ForeignKey(Item, related_name="item_vouchers", on_delete=models.CASCADE)
