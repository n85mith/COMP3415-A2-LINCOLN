"""A small starting test suite for the order desk."""

from pathlib import Path
import tempfile
import unittest

from supplydesk.service import OrderService


class OrderSmokeTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.path = Path(self.directory.name) / "state.json"
        self.service = OrderService(self.path)

    def test_regular_pickup_quote(self):
        quote = self.service.quote("regular", [{"product_id": "notebook", "quantity": 2}])
        self.assertEqual(quote["subtotal_cents"], 1000)
        self.assertEqual(quote["discount_cents"], 0)
        self.assertEqual(quote["delivery_cents"], 0)
        self.assertEqual(quote["total_cents"], 1000)

    def test_student_delivery_quote(self):
        quote = self.service.quote("student", [{"product_id": "hoodie", "quantity": 2}], "delivery")
        self.assertEqual(quote["discount_cents"], 800)
        self.assertEqual(quote["delivery_cents"], 600)
        self.assertEqual(quote["total_cents"], 7800)

    def test_order_can_be_reopened(self):
        order = self.service.place_order("regular", [{"product_id": "mug", "quantity": 1}])
        self.assertEqual(order["order_id"], "ORD-0001")
        self.assertEqual(order["status"], "placed")
        self.assertEqual(OrderService(self.path).get_order(order["order_id"]), order)

    def test_cancel_order_restores_stock(self):
        before = self.service.catalog()
        order = self.service.place_order("regular", [{"product_id": "pen-pack", "quantity": 2}])
        cancelled = self.service.cancel_order(order["order_id"])
        self.assertEqual(cancelled["status"], "cancelled")
        self.assertEqual(self.service.catalog(), before)

        
    def test_regular_express_quote(self):
        quote = self.service.quote(
            "regular",
            [{"product_id": "notebook", "quantity": 2}],
            "express",
        )

        self.assertEqual(quote["fulfillment"], "express")
        self.assertEqual(quote["subtotal_cents"], 1000)
        self.assertEqual(quote["discount_cents"], 0)
        self.assertEqual(quote["delivery_cents"], 1200)
        self.assertEqual(quote["total_cents"], 2200)


    def test_student_express_quote(self):
        quote = self.service.quote(
            "student",
            [{"product_id": "hoodie", "quantity": 2}],
            "express",
        )

        self.assertEqual(quote["subtotal_cents"], 8000)
        self.assertEqual(quote["discount_cents"], 800)
        self.assertEqual(quote["delivery_cents"], 1200)
        self.assertEqual(quote["total_cents"], 8400)


    def test_express_fee_is_not_waived(self):
        items = [{"product_id": "hoodie", "quantity": 3}]

        standard = self.service.quote("regular", items, "delivery")
        express = self.service.quote("regular", items, "express")

        self.assertEqual(standard["delivery_cents"], 0)
        self.assertEqual(standard["total_cents"], 12000)
        self.assertEqual(express["delivery_cents"], 1200)
        self.assertEqual(express["total_cents"], 13200)

    def test_express_order_details_are_preserved(self):
        items = [{"product_id": "hoodie", "quantity": 2}]
        stock_before = self.service.catalog()

        quote = self.service.quote("student", items, "express")
        order = self.service.place_order("student", items, "express")

        # Placing the order must preserve every quoted field.
        for key, value in quote.items():
            self.assertEqual(order[key], value)

        self.assertEqual(order["order_id"], "ORD-0001")
        self.assertEqual(order["status"], "placed")

        # Retrieving and reopening must preserve the complete order.
        self.assertEqual(
            self.service.get_order(order["order_id"]),
            order,
        )

        reopened = OrderService(self.path)
        self.assertEqual(reopened.get_order(order["order_id"]), order)
        self.assertEqual(reopened.list_orders(), [order])

        # Cancellation changes status, not the recorded order details.
        cancelled = reopened.cancel_order(order["order_id"])
        self.assertEqual(cancelled["status"], "cancelled")

        for key, value in quote.items():
            self.assertEqual(cancelled[key], value)

        self.assertEqual(cancelled["order_id"], order["order_id"])
        self.assertEqual(reopened.catalog(), stock_before)

        # The cancellation must also be saved.
        saved = OrderService(self.path)
        self.assertEqual(saved.get_order(order["order_id"]), cancelled)


if __name__ == "__main__":
    unittest.main()
