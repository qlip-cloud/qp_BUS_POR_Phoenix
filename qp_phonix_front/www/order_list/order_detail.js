$(document).ready(function() {

    const REDIRECT_TO_ORDERS = `/order_list/orders_list`;

    sessionStorage.removeItem("order_id")

    $(".quantity").bind('blur mouseup', function () {
        
        value = $(this).val()

        if (value == 0){

            $line = $(this).parents(".line")

            delete_line_modal($line.attr("id"))
            
        }
    })

    $("#btn_back_orders").click( ()=>{

        redirect(REDIRECT_TO_ORDERS)
    })

})

