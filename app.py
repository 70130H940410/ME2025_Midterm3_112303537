from flask import Flask, render_template, request, jsonify, redirect, url_for
from core.database.database import Database

app = Flask(__name__)
db = Database()


@app.route('/', methods=['GET'])
def index():
    orders = db.get_all_orders()
    warning = request.args.get('warning')
    return render_template('form.html', orders=orders, warning=warning)


# --------------------- /product 路由 ---------------------
@app.route('/product', methods=['GET', 'POST', 'DELETE'])
def product():
    # 1. GET：查詢商品名稱清單或單價
    if request.method == 'GET':
        category = request.args.get('category')
        product_name = request.args.get('product')

        # /product?category=飲料  → 回傳該類別商品名稱
        if category:
            rows = db.get_product_names_by_category(category)  # [('咖哩飯',), ('蛋包飯',)...]
            names = [r[0] for r in rows]                      # ['咖哩飯','蛋包飯',...]
            return jsonify({"product": names})

        # /product?product=咖哩飯 → 回傳單價
        if product_name:
            price = db.get_product_price(product_name)
            return jsonify({"price": price})

        # 兩個都沒帶
        return jsonify({"error": "Missing query parameter"}), 400

    # 2. POST：新增訂單
    elif request.method == 'POST':
        # 同時支援底線命名（單元測試）與 dash 命名（前端 form）
        product_date = (
            request.form.get('product_date')
            or request.form.get('order_date')
            or request.form.get('product-date')
        )
        customer_name = (
            request.form.get('customer_name')
            or request.form.get('customer-name')
        )
        product_name = (
            request.form.get('product_name')
            or request.form.get('product')
            or request.form.get('product-name')
        )

        amount_raw = (
            request.form.get('product_amount')
            or request.form.get('product-amount')
            or request.form.get('quantity')
            or '0'
        )
        total_raw = (
            request.form.get('product_total')
            or request.form.get('product-total')
            or request.form.get('subtotal')
            or '0'
        )

        status = (
            request.form.get('product_status')
            or request.form.get('status')
            or request.form.get('product-status')
        )
        note = (
            request.form.get('product_note')
            or request.form.get('note')
            or request.form.get('product-note')
            or ""
        )

        def to_int(value):
            """安全地把表單字串轉成整數，支援 '60' / '60.0' / '60.00'。"""
            try:
                return int(value)
            except (TypeError, ValueError):
                try:
                    return int(float(value))
                except (TypeError, ValueError):
                    return 0

        order_data = {
            'product_date': product_date,
            'customer_name': customer_name,
            'product_name': product_name,
            'product_amount': to_int(amount_raw),
            'product_total': to_int(total_raw),
            'product_status': status,
            'product_note': note,
        }

        db.add_order(order_data)
        # 重導回首頁並帶上 warning 訊息
        return redirect(url_for('index', warning="Order placed successfully"))

    # 3. DELETE：刪除訂單
    elif request.method == 'DELETE':
        order_id = request.args.get('order_id')
        if not order_id:
            return jsonify({"error": "order_id is required"}), 400

        ok = db.delete_order(order_id)
        if ok:
            return jsonify({"message": "Order deleted successfully"}), 200
        else:
            return jsonify({"message": "Order not found"}), 404


# --------------------- 程式入口 ---------------------
if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5500, debug=True)

