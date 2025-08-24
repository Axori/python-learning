import abc
import model
from sqlalchemy import text


class AbstractRepository(abc.ABC):

    @abc.abstractmethod
    def add(self, batch: model.Batch):
        raise NotImplementedError

    @abc.abstractmethod
    def get(self, reference) -> model.Batch:
        raise NotImplementedError


class SqlRepository(AbstractRepository):

    def __init__(self, session):
        self.session = session

    def add(self, batch):
        with self.session.begin():
            self.session.execute(
                text(
                    "INSERT INTO batches (reference, sku, _purchased_quantity, eta)VALUES (:reference, :sku, :_purchased_quantity, :eta)"
                ),
                {
                    "reference": batch.reference,
                    "sku": batch.sku,
                    "eta": batch.eta,
                    "_purchased_quantity": batch._purchased_quantity,
                },
            )
            batch_id = self.session.execute(text("SELECT last_insert_rowid()")).scalar()
            for order_line in batch._allocations:
                self.session.execute(
                    text(
                        "INSERT INTO order_lines (sku, qty, orderid) VALUES (:sku, :qty, :orderid)"
                    ),
                    {
                        "sku": order_line.sku,
                        "qty": order_line.qty,
                        "orderid": order_line.orderid,
                    },
                )
                order_line_id = self.session.execute(text("SELECT last_insert_rowid()")).scalar()
                self.session.execute(
                    text(
                        "INSERT INTO allocations (orderline_id, batch_id) VALUES (:orderline_id, :batch_id)"
                    ),
                    {
                        "orderline_id": order_line_id,
                        "batch_id": batch_id,
                    },
                )


    def get(self, reference) -> model.Batch:
        [[id, reference, sku, qty, eta]] = self.session.execute(
            text(
                "SELECT id, reference, sku, _purchased_quantity, eta FROM batches  WHERE reference = :reference"
            ),
            {"reference": reference},
        )

        results = self.session.execute(
            text(
                "Select o.orderid, o.sku, o.qty FROM allocations a JOIN order_lines o ON o.id=a.orderline_id WHERE batch_id=:batch_id"
            ),
            {"batch_id": id},
        )
        batch = model.Batch(reference, sku, qty, eta)
        batch._allocations = {
            model.OrderLine(row[0], row[1], row[2]) for row in results
        }
        return batch
