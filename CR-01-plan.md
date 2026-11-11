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




## Part C — Review

### 1. What actually changed?

- service.py: Added an express delivery fee constant, accepted express
  during fulfillment validation, and applied its fixed 1,200 cent fee.
- cli.py: Added express to the fulfillment choices and command help.
- menu.py: Updated the fulfillment prompt to include express.
- tests/test_smoke.py: Added three express pricing tests and one
  express order lifecycle test.
- README.md and FUNCTIONAL_SPEC.md: Updated the documentation to
  describe express delivery and its fixed fee.

### 2. Was my prediction correct?

My prediction was largely correct. The changes were concentrated in
the shared pricing helper, interface options, tests, and documentation.
I did not need to change the storage format or add express-specific
logic to get_order or cancel_order, because the existing order
record already stores fulfillment and pricing details.

### 3. What tests and checks were completed?

The automated suite increased from four tests to eight, and all eight
passed.

The new tests check:
- Regular-customer express pricing.
- Student express pricing.
- Express delivery remaining chargeable when standard delivery is free.
- Quote/order agreement and preservation of express details through
  retrieval, reopening, and cancellation.

I also manually checked express in command help, an express quote
through the command line, and a placed express order through the
interactive menu. The student order for two hoodies showed an
800-cent discount, a 1,200 cent delivery fee, and an 8,400 cent total.

### 4. Did the earlier refactoring help?

The shared prepare_order helper made the change easier because the
express validation and fee calculation only needed to be added once
for both quotes and placed orders.

Named constants gave the express fee a clear location and descriptive
name. The stock-update helper had little direct effect on this change,
because express did not require different stock handling.