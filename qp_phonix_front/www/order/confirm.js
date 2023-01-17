$(document).ready(function() {
    sessionStorage.removeItem("order_id")

    $(".quantity").bind('blur mouseup', function () {
        
        value = $(this).val()

        if (value == 0){

            $line = $(this).parents(".line")

            delete_line_modal($line.attr("id"))
            
        }
    })

    $("#btn_edit_order").click(function(){

        order_id = $("#order_id").val()

        window.location.href = `/order/item_formulary?order_id=${order_id}`
    })

    $(".trash").click( function(){

        $line = $(this).parents(".line")

        delete_line_modal($line.attr("id"))
    })

    
})


function delete_line_modal(line_id){

    $("#button_yes").addClass("trash_SubCategoria")
    $("#warn-modal #type").val(0)
    $("#warn-modal #line").val(line_id)
    $('#warn-modal').modal("show")
}
