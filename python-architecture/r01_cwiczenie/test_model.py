from datetime import date, timedelta
import pytest

from model import Batch, OrderLine, allocate

today = date.today()
tomorrow = today + timedelta(days=1)
later = tomorrow + timedelta(days=10)


def make_batch_and_order_line(
    sku: str, batch_qty: int, line_qty: int
) -> tuple[Batch, OrderLine]:
    return Batch("batch-ref", sku, batch_qty, today), OrderLine(
        "order-id", sku, line_qty
    )


def test_allocating_to_a_batch_reduces_the_available_quantity():
    batch, order_line = make_batch_and_order_line("SKU", 10, 2)
    batch.allocate(order_line)
    assert batch.available_quantity == 8


def test_can_allocate_if_available_greater_than_required():
    batch, order_line = make_batch_and_order_line("SKU", 10, 2)
    assert batch.can_allocate(order_line) == True


def test_cannot_allocate_if_available_smaller_than_required():
    batch, order_line = make_batch_and_order_line("SKU", 2, 3)
    assert batch.can_allocate(order_line) == False


def test_can_allocate_if_available_equal_to_required():
    batch, order_line = make_batch_and_order_line("SKU", 2, 2)
    assert batch.can_allocate(order_line) == True

def test_prefers_earlier_batches():
    earlier_batch, order_line = make_batch_and_order_line("Chair", 10, 3) 
    later_batch = Batch("later", "Chair", 10, eta=tomorrow)
    allocate(order_line, [later_batch, earlier_batch])

    assert earlier_batch.available_quantity == 7
    assert later_batch.available_quantity == 10
