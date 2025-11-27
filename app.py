from flask import Flask, render_template, request, jsonify, redirect, url_for
from core.database.database import Database

app = Flask(__name__)
db = Database()

@app.route('/', methods=['GET'])
def index():
    if request.method == 'GET':
        orders = db.get_all_orders()
        if request.args.get('warning'):
            warning = request.args.get('warning')
            return render_template('form.html', orders=orders, warning=warning)
        return render_template('form.html', orders=orders)


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5500, debug=True)



@app.route('/product', methods=['GET', 'POST', 'DELETE'])
def product():
    # 1. GET：查詢商品名稱清單或單價
    if request.method == 'GET':
        category = request.args.get('category')
        product_name = request.args.get('product')

        # /product?category=...
        if category:
            product_list = db.get_product_names_by_category(category)
            return jsonify({"product": product_list})

        # /product?product=...
        if product_name:
            price = db.get_product_price(product_name)
            return jsonify({"price": price})

        # 沒有帶需要的參數
        return jsonify({"error": "Missing query parameter"}), 400

    # 2. POST：新增訂單
    elif request.method == 'POST':
        # 前端表單欄位是用 dash（product-date），要轉成底線 key
        order_data = {
            'product_date':  request.form.get('product-date'),
            'customer_name': request.form.get('customer-name'),
            'product_name':  request.form.get('product-name'),
            'product_amount': int(request.form.get('product-amount', 0)),
            'product_total':  int(request.form.get('product-total', 0)),
            'product_status': request.form.get('product-status'),
            'product_note':   request.form.get('product-note')
        }

        db.add_order(order_data)

        # 重導回首頁並帶上 warning 訊息
        return redirect(url_for('index', warning="Order placed successfully"))

    # 3. DELETE：刪除訂單
    elif request.method == 'DELETE':
        order_id = request.args.get('order_id')
        db.delete_order(order_id)
        return jsonify({"message": "Order deleted successfully"}), 200