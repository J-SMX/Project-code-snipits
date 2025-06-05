import datetime

from decimal import Decimal

from django.test import Client, TestCase

from org.models import MenuItem, ActiveTable, CurrentOrder, DiscountCode, User, HistoricalOrder, Payment
from org.models import OrderStatusChoices, ItemType, PaymentStatusChoices
from org.models.financial import generate_customers_last_month, generate_customers_current_month, \
    generate_avg_payment_last_month, generate_avg_payment_current_month, generate_average_table_size_last_month, \
    generate_average_table_size_current_month, generate_total_payment_last_month, \
    generate_total_payment_current_month, generate_number_partially_refunded, generate_number_fully_refunded, \
    generate_number_cancelled_orders, generate_customers_last_year
from org.models.search import user_search_first_name, user_search_email, active_tables_search_tabel_number, \
    menu_item_search_item_name, menu_item_search_is_available, current_order_search_order_status, \
    current_order_search_payment_status, historical_order_search_order_status, historical_order_search_payment_status, \
    discount_codes_search_is_available


class GenerateReceiptTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.menu_item = MenuItem.objects.create(item_name="Pizza", price_ex_vat=10.00, price_inc_vat=12.00)
        self.menu_item2 = MenuItem.objects.create(item_name="Burger", price_ex_vat=8.00, price_inc_vat=10.00)
        self.order = CurrentOrder.objects.create(final_price_ex_vat=10.00, final_price_inc_vat=12.00)
        self.order.items_selected.add(self.menu_item.id)
        self.order.items_selected.add(self.menu_item2.id)
        self.order.save()

    def test_setup(self):
        print(MenuItem.objects.values())
        print(CurrentOrder.objects.values())
        print(CurrentOrder.objects.get(id=self.order.id).items_selected.all())

    def test_generate_receipt(self):
        response = self.client.get(f'/api/receipt/{self.order.id}/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'receipt.html')
        self.assertContains(response, 'Pizza')
        self.assertContains(response, '10.00')
        self.assertContains(response, '12.00')


class CurrentOrderTestCase(TestCase):
    def setUp(self):
        # Create a user for testing
        self.customer = User.objects.create_user(username='customer', password='password', email='customer@example.com')
        self.waiter = User.objects.create_user(username='waiter', password='password', email='waiter@example.com')
        self.item_type = ItemType.objects.create(name='Main Course')
        self.menu_item = MenuItem.objects.create(
            item_name='MenuItem',
            item_description='Description',
            item_type=self.item_type,
            price_ex_vat=10.00,
            price_inc_vat=12.00,
            vat_percentage=20,
            allergens_numbers='1,2,3'
        )

        # Create a payment for testing
        self.payment = Payment.objects.create(verification_token=123)

        # Create a discount code for testing
        self.discount_code = DiscountCode.objects.create(active=True, discount_name="Test Discount",
                                                         discount_percentage=10)
        self.discount_code.applicable_items.set([self.menu_item])
        print(self.discount_code.applicable_items)

        # Create a current order for testing
        self.current_order = CurrentOrder.objects.create(
            final_price_ex_vat=10.00,
            final_price_inc_vat=12.00,
            order_status=OrderStatusChoices.PLACED,
            payment_status=PaymentStatusChoices.UNPAID,
            customer=self.customer,
            waiter=self.waiter,
            payment_id=self.payment,
        )
        self.current_order.items_selected.set([self.menu_item])

    def test_apply_discount(self):
        self.current_order.apply_discount(self.discount_code)

        self.assertEqual(self.current_order.final_price_ex_vat, Decimal('9.00'))
        self.assertEqual(self.current_order.final_price_inc_vat, Decimal('10.90'))

    def test_apply_discount_invalid_code(self):
        invalid_code = DiscountCode.objects.create(
            active=True,
            discount_name='Invalid Discount',
            discount_percentage=10,
            discount_value=0,
        )

        with self.assertRaises(ValueError):
            self.current_order.apply_discount(invalid_code)

    def test_apply_discount_inactive_code(self):
        inactive_code = DiscountCode.objects.create(
            active=False,
            discount_name='Inactive Discount',
            discount_percentage=10,
            discount_value=0,
        )
        inactive_code.applicable_items.add(self.menu_item)

        with self.assertRaises(ValueError):
            self.current_order.apply_discount(inactive_code)

    def test_apply_discount_no_items_applicable(self):
        no_items_code = DiscountCode.objects.create(
            active=True,
            discount_name='No Items Discount',
            discount_percentage=10,
            discount_value=0,
        )

        with self.assertRaises(ValueError):
            self.current_order.apply_discount(no_items_code)


class SearchFinancialTests(TestCase):
    def setUp(self):
        # Test data so that the functions can be tested in a thorough way
        ActiveTable.objects.create(table_number=2, no_of_seats=2, timestamp_created="2023-02-01 12:00:00")
        ActiveTable.objects.create(table_number=56, no_of_seats=6, timestamp_created="2023-03-06 20:00:00")
        ActiveTable.objects.create(table_number=23, no_of_seats=34, timestamp_created="2023-03-13 21:34:57")
        ActiveTable.objects.create(table_number=65, no_of_seats=91, timestamp_created="2023-02-14 14:45:21")
        ActiveTable.objects.create(table_number=1, no_of_seats=4, timestamp_created="2023-02-14 14:45:21")
        ActiveTable.objects.create(table_number=9, no_of_seats=10, timestamp_created="2023-03-03 14:45:21")
        ActiveTable.objects.create(table_number=9, no_of_seats=7, timestamp_created="2023-02-23 9:34:57")
        item1 = MenuItem.objects.create(item_name="Chicken", item_description="chicken", price_ex_vat=8.00,
                                        price_inc_vat=10.00, vat_percentage=25, allergens_numbers="1, 3, 6",
                                        is_available=True)
        item2 = MenuItem.objects.create(item_name="Lamb", item_description="lamb", price_ex_vat=12.00,
                                        price_inc_vat=15.00, vat_percentage=25, allergens_numbers="5, 7, 13",
                                        is_available=False)
        item3 = MenuItem.objects.create(item_name="Pork", item_description="pork", price_ex_vat=16.00,
                                        price_inc_vat=20, vat_percentage=25, allergens_numbers="2, 8, 11",
                                        is_available=True)

        ho1 = HistoricalOrder.objects.create(id=1, timestamp_ordered="2023-03-12",
                                             timestamp_completed="2023-03-12",
                                             final_price_ex_vat=9.00, final_price_inc_vat=11.00,
                                             order_status="FF",
                                             payment_status="R")
        ho1.items_selected.set([item1])
        ho2 = HistoricalOrder.objects.create(id=2, timestamp_ordered="2023-03-06",
                                             timestamp_completed="2023-01-6",
                                             final_price_ex_vat=13.00, final_price_inc_vat=16.00,
                                             order_status="FF",
                                             payment_status="P")
        ho2.items_selected.set([item2])
        ho3 = HistoricalOrder.objects.create(id=3, timestamp_ordered="2023-03-03",
                                             timestamp_completed="2023-03-03",
                                             final_price_ex_vat=17.00, final_price_inc_vat=21.00,
                                             order_status="FF",
                                             payment_status="P")
        ho3.items_selected.set([item3])
        ho4 = HistoricalOrder.objects.create(id=4, timestamp_ordered="2023-02-14",
                                             timestamp_completed="2023-02-14",
                                             final_price_ex_vat=9.00, final_price_inc_vat=11.00,
                                             order_status="FF",
                                             payment_status="R")
        ho4.items_selected.set([item1])
        ho5 = HistoricalOrder.objects.create(id=5, timestamp_ordered="2023-02-14",
                                             timestamp_completed="2023-02-14",
                                             final_price_ex_vat=9.00, final_price_inc_vat=11.00,
                                             order_status="FF",
                                             payment_status="P")
        ho5.items_selected.set([item2])
        ho6 = HistoricalOrder.objects.create(id=6, timestamp_ordered="2023-03-15",
                                             timestamp_completed="2023-03-15",
                                             final_price_ex_vat=13.00, final_price_inc_vat=16.00,
                                             order_status="FF",
                                             payment_status="PR")
        ho6.items_selected.set([item3])
        ho7 = HistoricalOrder.objects.create(id=7, timestamp_ordered="2023-02-23",
                                             timestamp_completed="2023-02-24",
                                             final_price_ex_vat=17.00, final_price_inc_vat=21.00,
                                             order_status="FF",
                                             payment_status="P")
        ho7.items_selected.set([item1])
        ho8 = HistoricalOrder.objects.create(id=8, timestamp_ordered="2022-08-15", timestamp_completed="2022-08-15",
                                             final_price_ex_vat=1.00, final_price_inc_vat=2, order_status="RD",
                                             payment_status="P")
        ho8.items_selected.set([item1])
        co1 = CurrentOrder.objects.create(id=8, timestamp_ordered="2023-02-23 16:01:00",
                                          final_price_ex_vat=9.00, final_price_inc_vat=11.00, order_status="FF",
                                          payment_status="P")
        co1.items_selected.set([item1])
        co2 = CurrentOrder.objects.create(id=9, timestamp_ordered="2023-02-23 16:34:00",
                                          final_price_ex_vat=13.00, final_price_inc_vat=16.00, order_status="CC",
                                          payment_status="UP")
        co2.items_selected.set([item2])
        co3 = CurrentOrder.objects.create(id=10, timestamp_ordered="2023-02-23 16:56:00",
                                          final_price_ex_vat=9.00, final_price_inc_vat=11.00, order_status="FF",
                                          payment_status="PR")
        co3.items_selected.set([item1])
        co4 = CurrentOrder.objects.create(id=11, timestamp_ordered="2023-02-23 17:00:30",
                                          final_price_ex_vat=17.00, final_price_inc_vat=21.00, order_status="PL",
                                          payment_status="P")
        co4.items_selected.set([item3])
        co5 = CurrentOrder.objects.create(id=12, timestamp_ordered="2023-02-23 17:20:00",
                                          final_price_ex_vat=9.00, final_price_inc_vat=11.00, order_status="PL",
                                          payment_status="UP")
        co5.items_selected.set([item1])
        co6 = CurrentOrder.objects.create(id=13, timestamp_ordered="2023-02-23 17:34:00",
                                          final_price_ex_vat=9.00, final_price_inc_vat=11.00, order_status="PL",
                                          payment_status="UP")
        co6.items_selected.set([item1])
        dc1 = DiscountCode.objects.create(active=True, discount_name="Big Chicken", discount_percentage=20)
        dc1.applicable_items.set([item1])
        dc2 = DiscountCode.objects.create(active=False, discount_name="Big Lamb", discount_percentage=17)
        dc2.applicable_items.set([item2])
        dc3 = DiscountCode.objects.create(active=True, discount_name="Big Pork", discount_percentage=90)
        dc3.applicable_items.set([item3])
        User.objects.create(username="Xx_Hamza_xX", password="kdnwlks", email="Harry.bot@gmail.com", first_name="Harry",
                            last_name="Bot", last_login="2023-08-12")
        User.objects.create(username="SIZZLE", password="KDNE20", email="sizzle.bizzle@gmail.com", first_name="Sizzle",
                            last_name="Bizzle", last_login="2023-08-27")
        User.objects.create(email="John.Doe@live.com", first_name="John", last_name="Doe", username="John23")
        User.objects.create(username="Ben", password="odbw8sjkeb", email="BenSmith23@outlook.com", first_name="Ben",
                            last_name="Smith", last_login="2022-08-12")

    def test_financials(self):
        # financial.py tests
        self.assertEqual(generate_customers_last_month()[0], 3, "3 is correct as that is that number of orders int "
                                                                "the previous month")
        self.assertEqual(generate_customers_current_month()[0], 4, "4 is correct as that is the number of orders in "
                                                                   "the current month")
        self.assertEqual(generate_avg_payment_last_month()[0], Decimal('14.3'), "14.3 is correct as that is the "
                                                                                "average price of an order in the "
                                                                                "previous month")
        self.assertEqual(generate_total_payment_last_month()[0], 43, "43 is correct as that is the total of all "
                                                                     "payments by customers in the previous month")
        self.assertEqual(generate_avg_payment_current_month()[0], Decimal('16.0'), "16 is correct as that is the "
                                                                                   "average price of an order in the "
                                                                                   "current month")
        self.assertEqual(generate_total_payment_current_month()[0], 64, "64 is correct as that is the total of all "
                                                                        "payments by customers in the current month")
        self.assertEqual(generate_average_table_size_last_month()[0], Decimal('26.0'), "26 is correct as that is the "
                                                                                       "average table size that was "
                                                                                       "used in the previous month")
        self.assertEqual(generate_average_table_size_current_month()[0], Decimal('16.7'), "16.7 is correct as that is "
                                                                                          "the average table size "
                                                                                          "that was used in the "
                                                                                          "current month")
        self.assertEqual(generate_number_cancelled_orders(), 1, "1 is correct as that is the number of orders that "
                                                                "have been cancelled in the order history")
        self.assertEqual(generate_number_partially_refunded(), 2, "2 is correct as that is the number of partially "
                                                                  "refunded orders in the order history")
        self.assertEqual(generate_number_fully_refunded(), 2, "2 is correct as that is the number of fully refunded "
                                                              "orders in the order history")
        self.assertEqual(generate_customers_last_year()[0], 3)
        self.assertEqual(generate_customers_last_year()[6], 1)

    def test_search(self):
        # created search results for the assertequal() function to use as some may be used twice
        search_result0 = user_search_first_name("John", 1)
        search_result1 = user_search_first_name("bonkers", 1)
        search_result2 = user_search_email("sizzle.bizzle@gmail.com", 1)
        search_result3 = user_search_email("BenSmith23@outlook.com", 1)
        search_result4 = user_search_email("didlskd.lksdjf@milling.com", 1)
        search_result5 = active_tables_search_tabel_number(23, 1)
        search_result6 = active_tables_search_tabel_number(2, 1)
        search_result7 = active_tables_search_tabel_number(97, 1)
        search_result8 = menu_item_search_item_name("Chicken", 1)
        search_result9 = menu_item_search_item_name("Lamb", 1)
        search_result10 = menu_item_search_item_name("Pork", 1)
        search_result11 = menu_item_search_item_name("Beef", 1)
        search_result12 = menu_item_search_is_available(False, 1)
        search_result13 = current_order_search_order_status("CC", 1)
        search_result14 = current_order_search_order_status("Dead", 1)
        search_result15 = current_order_search_payment_status("P", 2)
        search_result16 = current_order_search_payment_status("Blocked", 1)
        search_result17 = historical_order_search_order_status("FF", 7)
        search_result18 = historical_order_search_order_status("FF", 4)
        search_result19 = historical_order_search_order_status("unknown", 1)
        search_result20 = historical_order_search_payment_status("Default", 1)
        search_result21 = discount_codes_search_is_available(True, 2)
        search_result22 = discount_codes_search_is_available(False, 1)
        # Tests for methods in financial.py
        self.assertEqual(search_result0[0][4], "John23", "The user with first name \'John\' has the username \'John23\'")
        self.assertEqual(search_result1, [], "\'bonkers\' is not a first name in the database returning an empty list")
        self.assertEqual(search_result2[0][1], "KDNE20", "the user with email \'sizzle.bizzle@gmail.com\' has the "
                                                         "password \'KDNE20\'")
        self.assertEqual(search_result3[0][1], "odbw8sjkeb", "The user with email \'BenSmith23@outlook.com\' has "
                                                             "password \'odbw8sjkeb\'")
        self.assertEqual(search_result4, [], "\'didlskd.lksdjf@milling.com\'  is not an email in the database "
                                             "returning an empty list")
        self.assertEqual(search_result5[0][2], Decimal('34'), "Table no. 23 has 34 seats")
        self.assertEqual(search_result6[0][2], Decimal('2'), "Table no. 2 has 2 seats")
        self.assertEqual(search_result7, [], "97 is not a table no. in the database returning an empty list")
        self.assertEqual(search_result8[0][5], Decimal('25'), "The menu item \'Chicken\' has vat % of 25")
        self.assertEqual(search_result9[0][4], Decimal('15'), "The menu item \'Lamb\' has a final price inc. vat of 15")
        self.assertEqual(search_result10[0][2], "pork", "The menu item \'Pork\' has item description \'pork\'")
        self.assertEqual(search_result10[0][7], True, "The menu item \'Pork\' has an an availability of True")
        self.assertEqual(search_result11, [], "\'Beef\' is not a menu item returning an empty list")
        self.assertEqual(search_result12[0][1], "Lamb", "Searching for non-available item will only return \'Lamb\' "
                                                        "as it is only menu item unavailable")
        self.assertEqual(search_result13[0][2], Decimal('13'), "There is only 1 \'Canceled\' current order which has "
                                                               "a final price excl. vat of 13.00")
        self.assertEqual(search_result14, [], "\'Dead\' is not an order status on any current order so it returns an "
                                              "empty list")
        self.assertEqual(search_result15[1][3], Decimal('16'), "The 2nd current order with the payment status of "
                                                               "\'P\' has a finacl price inc. vat of 16.00")
        self.assertEqual(search_result16, [], "\'Blocked\' is not a payment status on any current order so it "
                                              "reuturns an empty list")
        self.assertEqual(search_result17[5][6], "PR", "All the historical orders have a order status of \'FF\' "
                                                      "returning the 6th ones payment status should equal \'PR\'")
        # this answer is not in original format entered because of how the Date Time Field works
        self.assertEqual(search_result18[2][1], datetime.datetime(2023, 3, 3, tzinfo=datetime.timezone.utc),
                         "All the historical orders have an order status of \'FF\' returning 3rd one entereds "
                         "timestamp ordered should give the equivalend of 23-03-03 ")
        self.assertEqual(search_result19, [], "\'unknown\' is not an order status on any historical order, this causes "
                                              "it to return an empty list")
        self.assertEqual(search_result20, [], "\'Default\' is not a payment status on any Historical order, "
                                              "this causes it to return an empty list")
        self.assertEqual(search_result21[1][3], Decimal('90'), "There are 2 Discount codes that are available the "
                                                               "secound one has a percentage of 90")
        self.assertEqual(search_result22[0][2], "Big Lamb", "There is only one Discount code that is not available "
                                                            "its discount name is \'Big lamb\'")
