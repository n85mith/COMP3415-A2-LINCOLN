# Task 5 — CR-01: Express Delivery

## Part A — Before Implementation

### 1. What behaviour will change?

I will add express delivery as a third fulfillment option alongside
pickup and standard delivery.

Express delivery will always cost 1,200 cents ($12 CAD), even when
standard delivery would be free.

Student discount eligibility and rounding will remain unchanged.
The discount will apply to merchandise, not the delivery fee.

Pickup and standard delivery behaviour will remain unchanged, along
with stock handling, order numbering, history, and cancellation rules.

### 2. Which files and methods do I expect to modify?

- supplydesk/service.py:
  Update prepare_order to accept express and calculate its fixed fee.
  Add a named constant for the express delivery fee.

- supplydesk/menu.py:
  Add express to the fulfillment prompt and keep pickup as the default.

- supplydesk/cli.py:
  Check and update the fulfillment options and command help.

- README.md and relevant specification documentation:
  Explain express delivery and show how to use it.

- Automated tests:
  Add express delivery tests and check that existing behaviour is preserved.

### 3. Which tests do I expect to need?

- A regular customer ordering two notebooks with express:
  expected total of 2,200 cents.

- A student ordering two hoodies with express:
  expected total of 8,400 cents.

- A regular customer ordering three hoodies:
  standard delivery total of 12,000 cents;
  express delivery total of 13,200 cents.

- Quotes and placed orders agree on items, fulfillment, discount,
  delivery fee, and total.

- Express order details remain correct when retrieved, reopened from
  a saved file, and cancelled.

- Pickup, standard delivery, student discount boundaries, invalid
  fulfillment values, stock, order numbering, history, and existing
  cancellation rules still behave as before.

- Express works through individual commands and the interactive menu,
  while regular customer and pickup defaults remain unchanged.