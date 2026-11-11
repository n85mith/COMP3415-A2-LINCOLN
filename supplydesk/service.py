"""Operations used by the command-line order desk."""

from supplydesk.storage import JsonStore

MIN_ITEM_QUANTITY = 1
MAX_ITEM_QUANTITY = 99

STUDENT_DISCOUNT_THRESHOLD_CENTS = 5000
STUDENT_DISCOUNT_PERCENT = 10
STUDENT_DIVISOR = 100
DISCOUNT_ROUNDING = 50

FREE_DELIVERY_THRESHOLD_CENTS = 10000
DELIVERY_FEE = 600
EXPRESS_DELIVERY_FEE_CENTS = 1200

class OrderService:
    def __init__(self, state_path=".supplydesk/state.json"):
        self.store = JsonStore(state_path)

    def catalog(self):
        return self.store.load()["catalog"]

    def reduce_stock(self, state, items):
        for line in items:
            for product in state["catalog"]:
                if product["product_id"] == line["product_id"]:
                    product["stock"] -= line["quantity"]


    def prepare_order(self, state, customer_type, items, fulfillment):
        if customer_type not in ("regular", "student"):
            raise ValueError("Customer type must be regular or student.")
        if fulfillment not in ("pickup", "delivery", "express"):
            raise ValueError("Fulfillment must be pickup, delivery, or express.")

        if not isinstance(items, list) or not items:
            raise ValueError("An order must contain at least one item.")

        lines = []
        subtotal = 0

        for item in items:
            if not isinstance(item, dict):
                raise ValueError("Each item must contain a product_id and quantity.")
            product = None
            for candidate in state["catalog"]:
                if candidate["product_id"] == item.get("product_id"):
                    product = candidate
                    break

            if product is None:
                raise ValueError("Unknown product.")
            
            quantity = item.get("quantity")
            if type(quantity) is not int or quantity < MIN_ITEM_QUANTITY or quantity > MAX_ITEM_QUANTITY:
                raise ValueError(f"Quantity must be an integer from {MIN_ITEM_QUANTITY} to {MAX_ITEM_QUANTITY}.")
            
            if quantity > product["stock"]:
                raise ValueError("Not enough stock for " + product["product_id"] + ".")
            
            line_total = product["unit_price_cents"] * quantity
            subtotal += line_total
            lines.append({
                "product_id": product["product_id"],
                "name": product["name"],
                "unit_price_cents": product["unit_price_cents"],
                "quantity": quantity,
                "line_total_cents": line_total,
            })
        discount = 0
        if customer_type == "student" and subtotal > STUDENT_DISCOUNT_THRESHOLD_CENTS:
            discount = (subtotal * 10 + 50) // 100
        delivery = 0
        if fulfillment == "delivery" and subtotal - discount < FREE_DELIVERY_THRESHOLD_CENTS:
            delivery = DELIVERY_FEE
        elif fulfillment == "express":
            delivery = EXPRESS_DELIVERY_FEE_CENTS
            
        return {
                "lines": lines,
                "subtotal": subtotal,
                "discount": discount,
                "delivery": delivery
            }
    
    def quote(self, customer_type, items, fulfillment="pickup"):
        state = self.store.load()
        details = self.prepare_order(state, customer_type, items, fulfillment)
        
        return {
            "customer_type": customer_type,
            "fulfillment": fulfillment,
            "items": details["lines"],
            "subtotal_cents": details["subtotal"],
            "discount_cents": details["discount"],
            "delivery_cents": details["delivery"],
            "total_cents": details["subtotal"] - details["discount"] + details["delivery"],
        }

    def place_order(self, customer_type, items, fulfillment="pickup"):
        state = self.store.load()
        details = self.prepare_order(state, customer_type, items, fulfillment)

        order = {
            "order_id": "ORD-" + str(state["next_order_number"]).zfill(4),
            "status": "placed",
            "customer_type": customer_type,
            "fulfillment": fulfillment,
            "items": details["lines"],
            "subtotal_cents": details["subtotal"],
            "discount_cents": details["discount"],
            "delivery_cents": details["delivery"],
            "total_cents": details["subtotal"] - details["discount"] + details["delivery"],
        }

        self.reduce_stock(state, order["items"])


        state["next_order_number"] += 1
        state["orders"].append(order)
        self.store.save(state)
        return order

    def list_orders(self):
        return self.store.load()["orders"]

    def get_order(self, order_id):
        state = self.store.load()
        for order in state["orders"]:
            if order["order_id"] == order_id:
                return order
        raise ValueError("Unknown order: " + order_id)

    def cancel_order(self, order_id):
        state = self.store.load()
        order = None
        for candidate in state["orders"]:
            if candidate["order_id"] == order_id:
                order = candidate
                break
        if order is None:
            raise ValueError("Unknown order: " + order_id)
        for line in order["items"]:
            for product in state["catalog"]:
                if product["product_id"] == line["product_id"]:
                    product["stock"] += line["quantity"]
        order["status"] = "cancelled"
        self.store.save(state)
        return order
