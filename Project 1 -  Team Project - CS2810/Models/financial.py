from django.db import connection
from datetime import timedelta
from django.utils import timezone
import os
from pathlib import Path
from django.db import models
from django.core.exceptions import ValidationError

date = timezone.now()
username = os.getlogin()
current_datetime = date.strftime("\'%Y-%m-%d\'")
download_save_location = "C:/Users/" + username + "/Downloads/"


def general_query(query):
    with connection.cursor() as cursor:
        cursor.execute(query)
        value = cursor.fetchall()
        return value


def search_database(column, table, query_type, where="", start="", end="", month="f.csv"):
    start = str(start)
    end = str(end)
    # a connection with the database is creates for query injection
    with connection.cursor() as cursor:
        # query used for creating a CSV in downloads folder of user
        if query_type == 0:
            cursor.execute("COPY (SELECT " + column + " FROM " + table + ") TO \'" + download_save_location + month +
                           "\' WITH CSV HEADER;")
        # query used to return a single value that is the average of that column integers
        if query_type == 1:
            cursor.execute(
                "SELECT AVG(" + column + ")::numeric(3, 1) FROM " + table + " WHERE " + where + " BETWEEN " + start +
                " AND " + end + ";")
            value = cursor.fetchall()[0]
            return value
        # query used to return the number of values in a given column
        if query_type == 2:
            cursor.execute("SELECT COUNT(" + column + ") FROM " + table + " WHERE " + where +
                           " BETWEEN " + start + " AND " + end + ";")
            value = cursor.fetchall()[0]
            return value
        if query_type == 3:
            cursor.execute("SELECT SUM(" + column + ") FROM " + table + " WHERE " + where + " BETWEEN " + start +
                           " AND " + end + ";")
            value = cursor.fetchall()[0]
            return value
        if query_type == 4:
            cursor.execute("SELECT COUNT(" + column + ") FROM " + table + " WHERE " + where + ";")
            value = cursor.fetchall()[0]
            return value


# method used to return the Start date of the previous month relative to the current date
def date_start_last(result_type):
    if date.strftime("%m") == "01":
        new_month = "12"
        new_year = str(int(date.strftime("%Y")) - 1)
        if result_type == 0:
            return "\'" + new_year + "-" + new_month + "-01\'"
        else:
            return new_year + "-" + new_month + "-01"
    else:
        new_month = str(int(date.strftime("%m")) - 1)
        if len(new_month) == 1:
            new_month = "0" + new_month
        if result_type == 0:
            return "\'" + date.strftime("%Y") + "-" + new_month + "-01\'"
        else:
            return date.strftime("%Y") + "-" + new_month + "-01"


# method used to return the first date of the current month
def date_start_current(result_type):
    if result_type == 0:
        return "\'" + date.strftime("%Y-%m") + "-01\'"
    else:
        return date.strftime("%Y-%m") + "-01"


# method used to return the last date of the previous month
def date_end_last(result_type):
    start_current = date.replace(day=1)
    # this reduces the days by one accounting for months of different lengths
    day = start_current - timedelta(days=1)
    if result_type == 0:
        return "\'" + day.strftime("%Y-%m-%d") + "\'"
    else:
        return day.strftime("%Y-%m-%d")


# this generate the last date of each month to be used to query the database for individual months
def dates_last_twelve_months():
    month_one = date.replace(day=1)
    month_one = month_one - timedelta(days=1)
    month_two = month_one - timedelta(days=day_calc(month_one.strftime("%m"), month_one.strftime("%Y")))
    month_three = month_two - timedelta(days=day_calc(month_two.strftime("%m"), month_two.strftime("%Y")))
    month_four = month_three - timedelta(days=day_calc(month_three.strftime("%m"), month_three.strftime("%Y")))
    month_five = month_four - timedelta(days=day_calc(month_four.strftime("%m"), month_four.strftime("%Y")))
    month_six = month_five - timedelta(days=day_calc(month_five.strftime("%m"), month_five.strftime("%Y")))
    month_seven = month_six - timedelta(days=day_calc(month_six.strftime("%m"), month_six.strftime("%Y")))
    month_eight = month_seven - timedelta(days=day_calc(month_seven.strftime("%m"), month_seven.strftime("%Y")))
    month_nine = month_eight - timedelta(days=day_calc(month_eight.strftime("%m"), month_eight.strftime("%Y")))
    month_ten = month_nine - timedelta(days=day_calc(month_nine.strftime("%m"), month_nine.strftime("%Y")))
    month_eleven = month_ten - timedelta(days=day_calc(month_ten.strftime("%m"), month_ten.strftime("%Y")))
    month_twelve = month_eleven - timedelta(days=day_calc(month_eleven.strftime("%m"), month_eleven.strftime("%Y")))
    month_thirteen = month_twelve - timedelta(days=day_calc(month_twelve.strftime("%m"), month_twelve.strftime("%Y")))
    months = [month_one, month_two, month_three, month_four, month_five, month_six, month_seven, month_eight,
              month_nine, month_ten, month_eleven, month_twelve, month_thirteen]

    return months


# this works out how many days are in the entered month accounting for leap years
def day_calc(month, year):
    month = int(month)
    year = int(year)
    if month == 2 and year % 4 == 0:
        day = 28
        return day
    if month == 2:
        day = 29
        return day
    if month == 4 or month == 6 or month == 9 or month == 10:
        day = 30
        return day
    if month == 1 or month == 3 or month == 5 or month == 7 or month == 8 or month == 11 or month == 12:
        day = 31
        return day
    else:
        raise ValidationError("incorrect date calculation")


# generates the total of the payments made in the previous month
def generate_total_payment_last_month():
    total_price = search_database("final_price_inc_vat", "org_historicalorder", 3, "timestamp_ordered",
                                  date_start_last(0), date_end_last(0))
    return total_price


# generates the total of the payments made in the current months starting on the first up to the current datetime
def generate_total_payment_current_month():
    total_price = search_database("final_price_inc_vat", "org_historicalorder", 3, "timestamp_ordered",
                                  date_start_current(0), current_datetime)
    return total_price


# generates the total of all payments made each month over the past year to be used for graphing
def generate_total_payment_last_year():
    months = dates_last_twelve_months()
    payments_per_month = []
    i = 1
    while i <= 12:
        selected_month_datetime = months[i]
        selected_month_datetime = selected_month_datetime.strftime("\'%Y-%m-%d\'")
        previous_month_datetime = months[i - 1]
        previous_month_datetime = previous_month_datetime.strftime("\'%Y-%m-%d\'")
        total_price = search_database("final_price_inc_vat", "org_historicalorder", 3, "timestamp_ordered",
                                      selected_month_datetime, previous_month_datetime)
        payments_per_month.append(total_price[0])
        i += 1
    return payments_per_month


# generates the average of all payments made from the fist of the current month up until the current datetime
def generate_avg_payment_current_month():
    avg_price = search_database("final_price_inc_vat", "org_historicalorder", 1, "timestamp_ordered",
                                date_start_current(0), current_datetime)
    return avg_price


# generates the average of all payments made in the previous month
def generate_avg_payment_last_month():
    # average order price inc vat
    avg_price = search_database("final_price_inc_vat", "org_historicalorder", 1, "timestamp_ordered",
                                date_start_last(0),
                                date_end_last(0))
    return avg_price


# generates the average payments for each month for the last 12 months for graphing purposes
def generate_avg_payment_last_year():
    months = dates_last_twelve_months()
    avg_payment_per_month = []
    i = 1
    while i <= 12:
        selected_month_datetime = months[i]
        selected_month_datetime = selected_month_datetime.strftime("\'%Y-%m-%d\'")
        previous_month_datetime = months[i - 1]
        previous_month_datetime = previous_month_datetime.strftime("\'%Y-%m-%d\'")
        total_price = search_database("final_price_inc_vat", "org_historicalorder", 3, "timestamp_ordered",
                                      selected_month_datetime, previous_month_datetime)
        avg_payment_per_month.append(total_price[0])
        i += 1
    return avg_payment_per_month


# this will show the average table size in the previous month
def generate_average_table_size_last_month():
    value = search_database("no_of_seats", "org_activetable", 1, "timestamp_created", date_start_last(0),
                            date_end_last(0))
    return value


# this will show the average tabel size form the first of the current month up until the current datetime
def generate_average_table_size_current_month():
    value = search_database("no_of_seats", "org_activetable", 1, "timestamp_created", date_start_current(0),
                            current_datetime)
    return value


# this will generate the average table size for each month over the last year for graphing purposes
def generate_avg_table_size_last_year():
    months = dates_last_twelve_months()
    avg_table_size_per_month = []
    i = 1
    while i <= 12:
        selected_month_datetime = months[i]
        selected_month_datetime = selected_month_datetime.strftime("\'%Y-%m-%d\'")
        previous_month_datetime = months[i - 1]
        previous_month_datetime = previous_month_datetime.strftime("\'%Y-%m-%d\'")
        table_size = search_database("no_of_seats", "org_activetable", 1, "timestamp_created", selected_month_datetime,
                                     previous_month_datetime)
        avg_table_size_per_month.append(table_size[0])
        i += 1
    return avg_table_size_per_month


# this will show the number of customers in the previous month
def generate_customers_last_month():
    value = search_database("*", "org_historicalorder", 2, "timestamp_ordered", date_start_last(0),
                            date_end_last(0))
    return value


# this will show the number of customers from the first of the current month to the current datetime
def generate_customers_current_month():
    value = search_database("*", "org_historicalorder", 2, "timestamp_ordered", date_start_current(0),
                            current_datetime)
    return value


# this generates the number of customers each month over the last year for graphing purposes
def generate_customers_last_year():
    months = dates_last_twelve_months()
    customer_per_month = []
    i = 1
    while i <= 12:
        selected_month_datetime = months[i]
        selected_month_datetime = selected_month_datetime.strftime("\'%Y-%m-%d\'")
        previous_month_datetime = months[i - 1]
        previous_month_datetime = previous_month_datetime.strftime("\'%Y-%m-%d\'")
        table_size = search_database("*", "org_historicalorder", 2, "timestamp_ordered", selected_month_datetime,
                                     previous_month_datetime)
        customer_per_month.append(table_size[0])
        i += 1
    return customer_per_month


# this generates the number of cancelled order there have been in org_historicalorder table
def generate_number_cancelled_orders():
    value0 = search_database("*", "org_historicalorder", 4, "order_status = 'CC'")
    value1 = search_database("*", "org_currentorder", 4, "order_status = 'CC'")
    value = value0[0] + value1[0]
    return value


# this generates the number of partially refunded orders in the org_historicalorder table
def generate_number_partially_refunded():
    value0 = search_database("*", "org_historicalorder", 4, "payment_status = 'PR'")
    value1 = search_database("*", "org_currentorder", 4, "payment_status = 'PR'")
    value = value0[0] + value1[0]
    return value


# this generates the number of fully refunded orders in the org_historicalorder table
def generate_number_fully_refunded():
    value0 = search_database("*", "org_historicalorder", 4, "payment_status = 'R'")
    value1 = search_database("*", "org_currentorder", 4, "payment_status = 'R'")
    value = value0[0] + value1[0]
    return value


class Financial(models.Model):
    timestamp_generated = models.DateTimeField(editable=False, default=timezone.datetime.now)
    search_query = models.CharField(default="", editable=False, max_length=4096)
    returned_value = models.CharField(default="", editable=False, max_length=4096)
