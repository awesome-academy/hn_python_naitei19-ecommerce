function remove_item(slug) {
    $.ajax({
        url: location.origin + "/remove-from-cart/" + slug + "/",
        method: "POST",
        success: function (data) {
            $('.' + slug).remove()
            var formattedTotalPrice = formatCurrency(data.cart_total)
            $('#cart_total').text(formattedTotalPrice);
            return
        },
        error: function (error) {
            console.log(error);
        }
    })
}

function remove_single_item(slug) {
    $.ajax({
        url: location.origin + "/remove-single-item-from-cart/" + slug + "/",
        method: "POST",
        success: function (data) {
            if (data.quantity == 0) {
                $('.' + slug).remove()
            }
            $('#item_quantity_' + slug).html(data.quantity)
            var formattedTotalPrice = formatCurrency(data.cart_total)
            $('#cart_total').text(formattedTotalPrice);
            var formattedTotalItemPrice = formatCurrency(data.item_total)
            $('#total_item_price_' + slug).text(formattedTotalItemPrice)
        },
        error: function (error) {
            console.log(error);
        }
    })
}

function add_item(slug) {
    $.ajax({
        url: location.origin + "/add-to-cart/" + slug + "/",
        method: "POST",
        success: function (data) {
            $('#item_quantity_' + slug).html(data.quantity)
            var formattedTotalPrice = formatCurrency(data.cart_total)
            $('#cart_total').text(formattedTotalPrice);
            var formattedTotalItemPrice = formatCurrency(data.item_total)
            $('#total_item_price_' + slug).text(formattedTotalItemPrice)
        },
        error: function (error) {
            console.log(error);
        }
    })
}

function formatCurrency(amount, currency = 'USD') {
    return new Intl.NumberFormat('en-US', { style: 'currency', currency: currency }).format(amount);
}
