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
        # 這裡的欄位名稱對應 form.html 裡的 name
        # form 的 name 應該是：
        # order_date, customer_name, category, product, price, quantity, subtotal, status, note
        qty_str = request.form.get('quantity', '0') or '0'
        subtotal_str = request.form.get('subtotal', '0') or '0'

        try:
            quantity = int(qty_str)
        except ValueError:
            quantity = 0

        try:
            # '60.00' 先轉 float 再轉 int -> 60
            total = int(float(subtotal_str))
        except ValueError:
            total = 0

        order_data = {
            'product_date':  request.form.get('order_date'),   # 日期 → order_list.date
            'customer_name': request.form.get('customer_name'),
            'product_name':  request.form.get('product'),      # 商品名稱 → order_list.product
            'product_amount': quantity,                        # 數量 → order_list.amount
            'product_total':  total,                           # 小計 → order_list.total
            'product_status': request.form.get('status'),
            'product_note':   request.form.get('note', "")
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

