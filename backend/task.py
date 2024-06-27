from workers import celery
from models import *
from mailer import send_email
from datetime import datetime, timedelta
from flask import render_template
from celery.schedules import crontab

@celery.on_after_finalize.connect
def setup_periodic_tasks(sender, **kwargs):
    #sender.add_periodic_task(crontab(minute="*/1"), daily_reminder.s(), name="every day reminder (every minute)")
    #sender.add_periodic_task(crontab(hour=10, minute=0), daily_reminder.s(), name="every day reminder (every day at 10 AM)")
    sender.add_periodic_task(crontab(minute="*/1"), monthly_report.s(), name="monthly report (every min)")
    #sender.add_periodic_task(crontab(hour=0, minute=0, day_of_month="1"), monthly_report.s(), name="monthly report (every month)")
    

@celery.task
def daily_reminder():
    twenty_four_hours_ago = datetime.now() - timedelta(hours=24)
    inactive_users = User.query.filter(User.last_loggedin < twenty_four_hours_ago).filter(User.role == "user").all()
    message = "You are getting this mail, because you haven't logged in for 24 hours. Please login again."
    for user in inactive_users:
        subject = "You are missing out on a big Sale today!"
        to = user.email
        html = render_template('daily.html', user=user, message=message)
        send_email(subject, to, html)
        print("Reminder email Sent to ", user.name)

    return "success"

@celery.task
def order_successful_mail(order_id):
    order = Order.query.get(order_id)
    subject = "Order Successful"
    to = order.user_email
    html = render_template('order_mail.html', order=order)

    send_email(subject, to, html)

    return f"Sent Email to {order.user.name}"

@celery.task
def monthly_report():
    users = User.query.filter_by(role="user").all()

    for user in users:
        one_month_ago = datetime.now() - timedelta(days=30)
        user_orders = Order.query.filter_by(user_email=user.email).filter(Order.order_date > one_month_ago).all()

        order_details = []
        total_amount_spent = 0

        for order in user_orders:
            order_items = order.items
            total_order_value = sum(item.product.rateperunit * item.quantity for item in order_items)
            total_amount_spent += total_order_value
            product_names = [item.product.name for item in order_items]

            order_details.append({
                'order_date': order.order_date.strftime('%Y-%m-%d %H:%M'),
                'total_order_value': total_order_value,
                'product_names': product_names
            })

        html = render_template('monthly_report.html', user=user, order_details=order_details, total_amount_spent=total_amount_spent)
        send_email(subject = "Monthly Report", to = user.email, html = html)

    return "success"