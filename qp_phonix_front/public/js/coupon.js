$(document).ready(function() {
    $("#send_coupon").on("click", function(){

        $(this).prop("disabled", true)

        $(".coupon_error").html("Canjeando..")

        payload = {
            coupon: $("#coupon").val(),
            order_id: $("#order_id").val()
        }

        callresponse = (data) =>{

            $("#send_coupon").prop("disabled", false)

            switch (data.status) {

                case 200:

                    order = data.order
                    coupon = data.coupon
                    items = order.items

                    coupon_log = data.coupon_log

                    coupon_items = coupon_log.coupon_items

                    description = `${coupon.percentage}% `

                    if (coupon_items.length > 0){

                        items.forEach((item) => {

                            coupon_item = coupon_items.find(coupon_item => coupon_item.item_code == item.item_code);
                            console.log(coupon_item)

                            if (coupon_item){
                                item_code = item.item_code.replace(":","-")
                                update_list_price(item_code, item)
                            }
                            description += "Descuento aplicado al precio de cada productos de la promoción"
                        
                        });
                    }else{
                        description += "Descuento aplicado al subtotal de la factura"
                    }

                    $(".coupon_legend").html(description)
                    $(".coupon_name").append(`<li>${coupon.title}</li>`)
                    $(".section-coupon").hide()
                    $(".section-redeem").show()
                    $(".price_total").html(new Intl.NumberFormat('es-CO').format(order.net_total))
                    
                    break;


                case 500:
                    $(".coupon_error").html(data.msg)
                    $(".coupon_error").show()
                    break;
                default:
                  console.log(`Sorry, we are out of ${expr}.`);
              }
        }

        send_petition(payload, "api.coupon", "redeem", callresponse = callresponse)
    })
})

function update_list_price(item_code, item){

    $(`#row-${item_code}`).attr('data-price', item.net_rate);
    $(`#row-${item_code}`).attr('data-subtotal', item.net_amount);
    $(`#row-${item_code} > .subtotal`).val(item.net_amount)
    $(`#price-${item_code}`).html(item.net_rate);
    $(`#total-${item_code}`).html(item.net_amount);
    $(`#label-${item_code}`).show();
}