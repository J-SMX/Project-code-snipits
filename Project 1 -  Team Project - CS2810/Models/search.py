from django.db import models
from django.db import connection
from django.utils import timezone


def search_database(table, column, list_length, query_type, search_query=""):
    # a connection with the database is creates for query injection

    with connection.cursor() as cursor:
        if query_type == 0:
            cursor.execute("SELECT * FROM " + table + " WHERE " + column + " LIKE \'%" + search_query + "%\' LIMIT " +
                           str(list_length) + ";")
        else:
            cursor.execute("SELECT * FROM " + table + " WHERE " + column + " LIMIT " + str(list_length) + ";")

        try:
            rows = cursor.fetchall()
        except IndexError:
            rows = None
        return rows


# Function to search for users by first_name
def user_search_first_name(search_query, list_length):
    rows = search_database("org_user", "first_name", list_length, 0, search_query)
    return rows


def user_search_email(search_query, list_length):
    rows = search_database("org_user", "email", list_length, 0, search_query)
    return rows


# active tables search by table no. and waiterID
def active_tables_search_tabel_number(search_query, list_length):
    str_search_query = "table_number = \'" + str(search_query) + "\'"
    rows = search_database("org_activetable", str_search_query, list_length, 1)
    return rows


# menu item search by name allergens and if it is available
def menu_item_search_item_name(search_query, list_length):
    rows = search_database("org_menuitem", "item_name", list_length, 0, search_query)
    return rows


def menu_item_search_is_available(search_query, list_length):
    str_search_query = "is_available = \'" + str(search_query) + "\'"
    rows = search_database("org_menuitem", str_search_query, list_length, 1)
    return rows


# current order search by item selected, order status or payment status
def current_order_search_items_selected(search_query, list_length):
    rows = search_database("org_currentorder", "items_selected", list_length, 0, search_query)
    return rows


def current_order_search_order_status(search_query, list_length):
    rows = search_database("org_currentorder", "order_status", list_length, 0, search_query)
    return rows


def current_order_search_payment_status(search_query, list_length):
    rows = search_database("org_currentorder", "payment_status", list_length, 0, search_query)
    return rows


def historical_order_search_order_status(search_query, list_length):
    rows = search_database("org_historicalorder", "order_status", list_length, 0, search_query)
    return rows


def historical_order_search_payment_status(search_query, list_length):
    rows = search_database("org_historicalorder", "payment_status", list_length, 0, search_query)
    return rows


def discount_codes_search_is_available(search_query, list_length):
    str_search_query = "active = \'" + str(search_query) + "\'"
    rows = search_database("org_discountcode", str_search_query, list_length, 1)
    return rows


class Search(models.Model):
    timestamp_searched = models.DateTimeField(editable=False, default=timezone.datetime.now)
    searched = models.CharField(max_length=255)
    # can attach ID of person searching here
