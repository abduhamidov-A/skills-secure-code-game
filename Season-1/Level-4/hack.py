import unittest

import code as c


class TestDatabase(unittest.TestCase):

    def test_injected_update_does_not_change_stock_price(self):
        operations = c.DB_CRUD_ops()
        before = operations.get_stock_price('MSFT')
        payload = "MSFT'; UPDATE stocks SET price = '525' WHERE symbol = 'MSFT'--"
        self.assertNotIn("[RESULT]", operations.get_stock_price(payload))
        self.assertEqual(operations.get_stock_price('MSFT'), before)

    def test_reporting_methods_reject_sql_writes(self):
        operations = c.DB_CRUD_ops()
        before = operations.get_stock_price('MSFT')
        payload = "UPDATE stocks SET price = 525 WHERE symbol = 'MSFT'"
        with self.assertRaises(ValueError):
            operations.exec_multi_query(payload)
        with self.assertRaises(ValueError):
            operations.exec_user_script(payload)
        self.assertEqual(operations.get_stock_price('MSFT'), before)


if __name__ == '__main__':
    unittest.main()
