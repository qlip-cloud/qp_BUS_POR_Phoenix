URL_CREATE_SALES_ORDER = "create_sales_order";

$(document).ready(function() {

        const REDIRECT_INDEX = `/order/index`;

        const REDIRECT_CONFIRM = `/order/confirm`;

        shipping_method = $('#select_shipping_method').val();

        if (sessionStorage.getItem("order_id")){

                const order_id = sessionStorage.getItem("order_id")

                window.location.href = `/order/item_formulary?order_id=${order_id}`

                sessionStorage.removeItem("order_id")
        }
    
        get_shipping_calendar(shipping_method)

        $("#table_content").on('keyup blur mouseup', ".quantity",function () {
                
                let value = parseInt($(this).val())
                let quantity_format = $(this).data("quantity_format")
                let max_value = parseInt($(this).data("quantity"))
                let transit_value = parseInt($(this).data("quantity_dis"))
                let item_name = $(this).data("select")
                let sku = $(this).data("sku")


                if (sku != "SI" && value > 0){
               
                    factor = parseInt($(this).data("factor"))
                            
                    if (value % factor != 0){
        
                        result = parseInt(value / factor) + 1;
            
                        value = result * factor;
                        
                        $(this).val(value)
                        
                    }
                    
                        
                }
                $inventory_quantity = $(`#table_content #inventory_quantity-${item_name}`);
                
                if (quantity_format == "False" && max_value > 0) {
                        
                        if ( parseInt(value) > parseInt(max_value) ){
                                if ((transit_value + max_value) >= value)
                                        
                                        $inventory_quantity.html("En tránsito");
                                else
                                        
                                        $inventory_quantity.html("No");
                        }
                        else{
                                $inventory_quantity.html("Si");
                        }
                }

                $line = $(this).parents(".line")

                price = parseFloat($line.data("price"))
                
                sub = value * price;
                
                $subtotal = $line.find(".subtotal")
                
                $subtotal.val(sub)

                total_update()

                //delay_save_or_update()

            })

        
        $("#select_shipping_method").change(function(){

                $('#datepicker').val("");
        
                get_shipping_calendar(this.value)
        })

        $("#btn_confirm_order").on("click", ()=>{

                //update_modal(2, 1)

        })

        $("#confirm_draft").on("click", ()=>{
                
                order_id = $("#order_id").val()

                if (order_id){
                        
                        update_modal(3, 1)

                }else{

                        save_order(URL_CREATE_SALES_ORDER, REDIRECT_CONFIRM,null,true,null, true)
                }
        })



        $("#save_draft").on("click", ()=>{

                order_id = $("#order_id").val()

                if (order_id){
                        valid_change(REDIRECT_INDEX)
                }else{
        
                        save_order(URL_CREATE_SALES_ORDER, REDIRECT_INDEX)
                }
                
                
        })

        
        $("#btn_back_orders").click( ()=>{
                valid_change(REDIRECT_INDEX)                
        })

        $("#button_yes").click(()=>{

                data_type = $("#warn-modal #type").val()

                if (data_type == 0){

                        line_id = $("#warn-modal #line").val()

                        delete_line(line_id)

                }
                if (data_type == 1){

                        update_order(REDIRECT_INDEX, false)
                }
                if (data_type == 2){

                        update_order(false, true, action = "confirm", true)
                }
                if (data_type == 3){

                        order_id = $("#order_id").val()
                        url = `${REDIRECT_CONFIRM}?order_id=${order_id}`
                        update_order(url, false)
                }

                $('#warn-modal').modal("hide")
        })

        total_update()



})


function updateIndicator() {

        $visible_area = $(".connection-alert")
        $disabled_inpuut = $("#confirm_draft, #save_draft, #filter_text, #datepicker, select")

        if(window.navigator.onLine){
                $visible_area.toggle()
                $disabled_inpuut.prop("disabled", false)
                if (get_change_count()){
                        save_or_update()
                }

        }
        else{
                $visible_area.toggle()
                $disabled_inpuut.prop("disabled", true)
                
        }
        //$('.selectpicker').selectpicker('refresh');


}


window.addEventListener('online',  updateIndicator);
window.addEventListener('offline', updateIndicator);



/*

$(document.body).on("keyup", this, function (event) {

        if (event.keyCode == 116) {

                order_id = $("#order_id").val()

                if (order_id){
                        window.location.href = `/order/item_formulary?order_id=${order_id}`
                }
                else{
                        location.reload()
                }
        }
});*/

const control = parseInt($("#save_control").data("time"))

function delay_save_or_update(){

       
        if(window.navigator.onLine && $("#save_control").val() == "0"){

               
                $("#save_control").val("1")

                setTimeout(() => { 

                        save_or_update()

                        
                }, control);
                        
        }

}
function save_or_update(){

        order_id = $("#order_id").val()

        if (order_id){

                update_order(null, false, null, false, true)

                //-- tienes q verificar si tienes q actualizar algo en la linea q identifica si la linea tuvo cambios--
                
        }else{

                save_order(URL_CREATE_SALES_ORDER,null, null, true, null, false, true)

                //-- tienes q verificar si tienes q actualizar algo en la linea q identifica si la linea tuvo cambios--

        }
        $("#save_control").val("0")
}


function valid_change(redirect_url){
        
        if (get_change_count()){

                update_modal(1, 1)

        }else{
                redirect(redirect_url)
        }
}

function total_update(){

        const formato = new Intl.NumberFormat('en-US', {
                maximumFractionDigits: 0,
              });
        
        let total = 0

        $(".row_select .subtotal").each(function(){
                
                subtotal = parseFloat($(this).val());

                total += subtotal;
        })

        $("#price_total").html(String(formato.format(total)).replace(",","."))
}
function update_modal(type, data_no = 0){

        $("#button_no").attr("data-no",data_no)

        $("#button_yes").removeClass("trash_SubCategoria")

        $("#warn-modal #type").val(type)

        $('#warn-modal').modal("show")
    }

function get_change_count(){

        count = $(".is_removed").length

        $(".quantity, .shipping_data").each(function() {

                value = $(this).val()

                base_value = $(this).data("value")
                
                type_val = $(this).attr('type')

                if(type_val == "number"){
                        if (parseFloat(base_value) != parseFloat(value)){
                                count ++ 

                        }
                }else {
                        if (base_value != value){

                                count ++ 
                        }
                }
        })

        return count
}
function update_order(redirect_link = null, valid_empty = false, action = "update", is_return = false, is_async = false ){

        url = "sales_order_update";

        order_id = $("#order_id").val()

        save_order(url, redirect_link, action, valid_empty, order_id, is_return, is_async)
}

function save_order(url, redirect_link, action = null, valid_empty = true, order_id = null, is_return = false, is_async = false){

        let base_url = "qp_phonix_front.qp_phonix_front.uses_cases.sales_order.sales_order"

        let method = `${base_url}.${url}`
        
        //let delivery_date = $("#datepicker").val()
        
        //let shipping_type = $("#select_shipping_method").val()

        let items = []

        let len = 0

        

        $(".row_select").each(function() {

            let qty = $(this).find("#quantity").val()

            if (qty > 0){
                obj = {
                    qty: $(this).find("#quantity").val(),
                    item_code: $(this).find("#item_id").val(),
                    description: $(this).find("#item_id").val(),
                    rate: $(this).find("#item_price").val(),
                    discount_percentage: $(this).find("#item_discount").val()

                    //,delivery_date
                }
                items.push(obj)
                len ++
            }
            
        });
        
        args = {
                'order_json': {
                        items
                        //, shipping_type
                        , order_id
                        , action}
        }

        if(len){
            if (!is_async)
                
                active_block()
            frappe.call({
                method,
                args,
                callback: function(r) {
                    if (!r.exc) {

                        let response = r.message

                        if (response.result == 400){

                                frappe.msgprint(response.msg)

                                disabled_block()
                        }
                        else if (!is_async){

                                if (is_return){
                                        if (!redirect_link){
                                                disabled_block()
                                                $("#confirm-modal").modal("show")

 
                                        }else{
                                                redirect(`${redirect_link}?order_id=${response.name}`)
                                        }
                                        
                                }else{
                                                                                    
                                        redirect(redirect_link)
                                }
                        }else{
                                
                                if (url == URL_CREATE_SALES_ORDER){

                                        if (!sessionStorage.getItem("order_id")){
                                                
                                                
                                                sessionStorage.setItem('order_id', response.name)

                                        }

                                        $("#order_id").val(response.name)
                                }

                        } 
                    }
                },
                freeze:true
            })

        }else if (valid_empty){
            frappe.msgprint("You have not selected any product")
        }
        else{
                redirect(redirect_link)
        }
}


function delete_line(line_id){

        $line = $(`#${line_id}`)

        $line.addClass("is_removed")

        $line.removeClass("row_select")

        $line.hide()

        remove_count = $(".is_removed").length

        msg = `Deshacer ${remove_count} producto eliminado`

        $("#undo").text(msg)

        $("#undo").show()
    
        $(".btn-primary").removeClass("trash_SubCategoria")

        total_update()

}

$("#undo").click(()=>{

        $removed_lines = $(".is_removed")
        
        $removed_lines.show()

        $removed_lines.removeClass("is_removed")

        $removed_lines.addClass("row_select")

        $removed_lines.each(function(){

                $line = $(this)

                $quantity = $line.find("#quantity")

                if ($quantity.val() <= 0){

                        subtotal = parseInt($line.data("subtotal"))
                        $subtotal = $line.find(".subtotal")
                        $subtotal.val(subtotal)
        
                        quantity =  parseInt($quantity.data("value"))
                        $quantity.val(quantity)
        
                }

        })

        $("#undo").hide()
        
        $("#undo").text("")

        total_update()

    })

function redirect(redirect_link){
        
        window.location.href = redirect_link
}

function get_shipping_calendar(shipping_method){

        if(shipping_method){
                frappe.call({
                        method: 'qp_phonix_front.qp_phonix_front.uses_cases.shipping_method.shipping_method_list.vf_shipping_date_list',
                        args: {
                                'shipping_method': shipping_method
                        },
                        callback: function(r) {
                                if (!r.exc) {
                                let message = ""
                                let response = r.message
                                let weekday_list = response.weekdaysenabled
                                let mindate = response.mindate
                                let maxdate = response.maxdate
                
                                init_datepicker(weekday_list, mindate, maxdate)
                
                                }
                        }
                })
        }

        }
        
function init_datepicker(weekday_list, mindate, maxdate){
        
        $("#datepicker").removeClass("hasDatepicker")
        
        $("#ui-datepicker-trigger").remove()
        
        $("#datepicker").datepicker({
                dateFormat: "yy-mm-dd",
                minDate: mindate,
                maxDate: maxdate,
                beforeShowDay: function( date ) {
        
                        response = weekday_list.filter(element => {
                                return date.getDay() == element
                        });
                        
                        if(response.length ) {
                                return [true, '', ''];
                        } else {
                                return [false, '', ''];
                        }
                                
                }
        });
        }

function active_block(){

        $("#blockscreen").addClass("modal-backdrop" )
        $("#blockscreen").addClass("fade" )
        $("#blockscreen").addClass("show" )
        $("#loader").show()
}
function disabled_block(){
        $("#blockscreen").removeClass("modal-backdrop fade show" )
        $("#loader").hide()

}