from workers import celery
from models import *
from mailer import send_email

@celery.task
def add():
    x = 1
    y = 2
    return x + y


@celery.task
def multiply(x, y):
    return x * y

@celery.task
def order_successful_mail(order_id):
    order = Order.query.get(order_id)
    subject = "Order Successful"
    to = order.user_email
    body = f"Your order has been successfully placed. Total bill amount is {order.total_amount}"

    send_email(subject, to, body)

    return f"Sent Email to {order.user.name}"

