$(document).ready(function() {

    $("#enable_sales_persons").on("click", function(){
        
        $("#sales_persons").prop("disabled", !$(this).is(":checked"))
        
    })
    
    sessionStorage.removeItem("order_id")

    $(".delecte_group").prop('checked', false);
    
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
    
    $("#selected_delete").click( function(){
        
        delete_line_modal(1)

    })
    $(".trash").click( function(){

        $line = $(this).parents(".line")

        delete_line_modal($line.attr("id"))
    })

    
})
$(".delecte_group").on("click", function(){
    show_deleted_button()
})
$(".select_all").on("click", function(){
    
    action = $(this).data("action")

    checked = action == "1" ? true : false;

    $(".delecte_group").prop("checked", checked)
    show_deleted_button()
})



function show_deleted_button(){
    select = false;
    visible = false

    $(".delecte_group").each(function(){
        if ($(this).prop("checked")){
            select = true

        }
        if ($(this).is(":visible")){
            visible = true

        }

    })

    if (select){
        $("#selected_delete").show()
        $("#select_all").hide()
        $("#deselect_all").show()
    }
    else{
        $("#selected_delete").hide()
        if (visible){
            $("#select_all").show()
        }
        $("#deselect_all").hide()

    }
}

function deleted_rows(){

    $(".delecte_group").each(function(){
        if ($(this).prop("checked")){

            $line = $(this).parents(".line")

            delete_line($line.attr("id"))

            $(this).prop("checked", false)
        }
    })

    show_deleted_button()

}


function delete_line_modal(line_id){

    $("#button_yes").addClass("trash_SubCategoria")
    $("#warn-modal #type").val(0)
    $("#warn-modal #line").val(line_id)
    $('#warn-modal').modal("show")
}
{

}