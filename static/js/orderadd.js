// 開啟與關閉Modal
function open_input_table() {
    document.getElementById("addModal").style.display = "block";
}
function close_input_table() {
    document.getElementById("addModal").style.display = "none";
}

// 刪除訂單
function delete_data(value) {
    fetch(`/product?order_id=${value}`, {
        method: "DELETE",
    })
        .then(response => {
            if (!response.ok) {
                throw new Error("伺服器回傳錯誤");
            }
            return response.json();
        })
        .then(result => {
            console.log(result);
            close_input_table();
            location.assign('/');   // 重新整理頁面
        })
        .catch(error => {
            console.error("發生錯誤：", error);
        });
}

/* 1. 選取商品種類後的連動選單 (Fetch API) */
function selectCategory() {
    const categorySelect = document.getElementById("category");
    const productSelect  = document.getElementById("product");
    const priceInput     = document.getElementById("price");
    const subtotalEl     = document.getElementById("subtotal");

    const category = categorySelect.value;

    // 先清空商品、單價、小計
    productSelect.innerHTML = '<option value="">請選擇商品</option>';
    if (priceInput) priceInput.value = "";
    if (subtotalEl) {
        if ("value" in subtotalEl) subtotalEl.value = "";
        else subtotalEl.textContent = "";
    }

    if (!category) return;   // 沒選類別就不打 API

    // ★這裡假設後端提供 /product?category=飲料 之類的 API
    fetch(`/product?category=${encodeURIComponent(category)}`)
        .then(res => {
            if (!res.ok) throw new Error("取得商品列表失敗");
            return res.json();
        })
        .then(data => {
            // data 可能是 ["可樂","雪碧"] 或 [{name:"可樂"},...]
            data.forEach(item => {
                const name = (typeof item === "string") ? item : item.name;
                const opt = document.createElement("option");
                opt.value = name;
                opt.textContent = name;
                productSelect.appendChild(opt);
            });
        })
        .catch(err => {
            console.error(err);
            alert("載入商品列表失敗，請稍後再試。");
        });
}

/* 2. 選取商品後，抓單價並更新畫面 (Fetch API) */
function selectProduct() {
    const productSelect = document.getElementById("product");
    const priceInput    = document.getElementById("price");

    const productName = productSelect.value;

    if (!productName) {
        if (priceInput) priceInput.value = "";
        countTotal();
        return;
    }

    // ★這裡假設後端提供 /product?name=可樂 之類的 API 回傳 {price: 35}
    fetch(`/product?name=${encodeURIComponent(productName)}`)
        .then(res => {
            if (!res.ok) throw new Error("取得單價失敗");
            return res.json();
        })
        .then(data => {
            const price = (typeof data === "number") ? data : data.price;
            if (priceInput) priceInput.value = price;
            countTotal(); // 有單價後立刻重新算小計
        })
        .catch(err => {
            console.error(err);
            alert("載入商品價格失敗，請稍後再試。");
        });
}

/* 3. 計算小計欄位：單價 × 數量 */
function countTotal() {
    const priceInput    = document.getElementById("price");
    const quantityInput = document.getElementById("quantity");
    const subtotalEl    = document.getElementById("subtotal");

    if (!priceInput || !quantityInput || !subtotalEl) return;

    const price = parseFloat(priceInput.value) || 0;
    let qty     = parseInt(quantityInput.value, 10);

    if (isNaN(qty) || qty < 0) qty = 0;

    const total = price * qty;

    if ("value" in subtotalEl) {
        subtotalEl.value = total.toFixed(2);
    } else {
        subtotalEl.textContent = total.toFixed(2);
    }
}

/* 4. 預設值與事件綁定 */
document.addEventListener("DOMContentLoaded", () => {
    // 日期預設今天
    const dateInput = document.getElementById("order_date");
    if (dateInput && !dateInput.value) {
        const today = new Date().toISOString().split("T")[0];
        dateInput.value = today;
    }

    const categorySelect = document.getElementById("category");
    if (categorySelect) {
        categorySelect.addEventListener("change", selectCategory);
    }

    const productSelect = document.getElementById("product");
    if (productSelect) {
        productSelect.addEventListener("change", selectProduct);
    }

    const quantityInput = document.getElementById("quantity");
    if (quantityInput) {
        quantityInput.addEventListener("input", countTotal);
    }

    const priceInput = document.getElementById("price");
    if (priceInput) {
        priceInput.addEventListener("input", countTotal);
    }
});
