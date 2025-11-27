import datetime
import os
import random
import sqlite3  # 一定要記得匯入


class Database:
    def __init__(self, db_filename: str = "order_management.db"):
        """
        db_filename 預設是 order_management.db
        檔案位置會被放在 core/database/ 底下
        """
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.db_path = os.path.join(base_dir, db_filename)

    @staticmethod
    def generate_order_id() -> str:
        """產生訂單編號（照老師原本給的寫法）"""
        now = datetime.datetime.now()
        timestamp = now.strftime("%Y%m%d%H%M%S")
        random_num = random.randint(1000, 9999)
        return f"OD{timestamp}{random_num}"

    # ------------------------------------------------------------------
    # 1. 根據 category 取得商品名稱列表
    # ------------------------------------------------------------------
    def get_product_names_by_category(self, category: str):
        """
        從 commodity 表中找出特定 category 的所有 product 名稱。
        回傳形式：list of tuple，例如 [('咖哩飯',), ('蛋包飯',), ...]
        """
        sql = "SELECT product FROM commodity WHERE category = ?"

        with sqlite3.connect(self.db_path) as conn:
            cur = conn.cursor()
            cur.execute(sql, (category,))
            rows = cur.fetchall()

        return rows

    # ------------------------------------------------------------------
    # 2. 根據 product 名稱取得單價
    # ------------------------------------------------------------------
    def get_product_price(self, product: str):
        """
        從 commodity 表中查詢指定 product 的 price。
        找不到時回傳 None。
        """
        sql = "SELECT price FROM commodity WHERE product = ?"

        with sqlite3.connect(self.db_path) as conn:
            cur = conn.cursor()
            cur.execute(sql, (product,))
            row = cur.fetchone()

        return row[0] if row is not None else None

    # ------------------------------------------------------------------
    # 3. 新增訂單
    # ------------------------------------------------------------------
    def add_order(self, order_data: dict) -> bool:
        """
        將訂單寫入 order_list。

        order_data 的 key 依照題目／後端規格：
        - product_date   -> 對應資料表欄位 date
        - customer_name  -> customer_name
        - product_name   -> product
        - product_amount -> amount
        - product_total  -> total
        - product_status -> status
        - product_note   -> note
        """
        order_id = self.generate_order_id()

        sql = """
        INSERT INTO order_list (
            order_id,
            date,
            customer_name,
            product,
            amount,
            total,
            status,
            note
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """

        params = (
            order_id,
            order_data.get("product_date"),
            order_data.get("customer_name"),
            order_data.get("product_name"),
            order_data.get("product_amount"),
            order_data.get("product_total"),
            order_data.get("product_status"),
            order_data.get("product_note", ""),
        )

        with sqlite3.connect(self.db_path) as conn:
            cur = conn.cursor()
            cur.execute(sql, params)
            conn.commit()

        return True

    # ------------------------------------------------------------------
    # 4. 取得所有訂單（JOIN commodity 把 price 一起查出來）
    # ------------------------------------------------------------------
    def get_all_orders(self):
        """
        回傳所有訂單，並附上對應商品的 price。

        回傳欄位順序：
        0: order_id
        1: date
        2: customer_name
        3: product
        4: price   (commodity.price)
        5: amount
        6: total
        7: status
        8: note
        """
        sql = """
        SELECT
            o.order_id,
            o.date,
            o.customer_name,
            o.product,
            c.price,
            o.amount,
            o.total,
            o.status,
            o.note
        FROM order_list AS o
        LEFT JOIN commodity AS c
            ON o.product = c.product
        ORDER BY o.order_id
        """

        with sqlite3.connect(self.db_path) as conn:
            cur = conn.cursor()
            cur.execute(sql)
            rows = cur.fetchall()

        return rows

    # ------------------------------------------------------------------
    # 5. 刪除訂單
    # ------------------------------------------------------------------
    def delete_order(self, order_id: str) -> bool:
        """
        根據 order_id 刪除訂單。
        有刪到至少 1 筆則回傳 True。
        """
        sql = "DELETE FROM order_list WHERE order_id = ?"

        with sqlite3.connect(self.db_path) as conn:
            cur = conn.cursor()
            cur.execute(sql, (order_id,))
            conn.commit()
            affected = cur.rowcount

        return affected > 0
"""
class Database():
    def __init__(self, db_filename="order_management.db"):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.db_path = os.path.join(base_dir, db_filename)

    @staticmethod
    def generate_order_id() -> str:
        now = datetime.datetime.now()
        timestamp = now.strftime("%Y%m%d%H%M%S")
        random_num = random.randint(1000, 9999)
        return f"OD{timestamp}{random_num}"

    def get_product_names_by_category(self, cur, category):

    def get_product_price(self, cur, product):

    def add_order(self, cur, order_data):

    def get_all_orders(self, cur):

    def delete_order(self, cur, order_id):
"""
