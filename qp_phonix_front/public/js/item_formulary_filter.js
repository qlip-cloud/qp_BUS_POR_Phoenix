var mouseX;
var mouseY;
$(document).mousemove( function(e) {
   mouseX = e.pageX; 
   mouseY = e.pageY;
});  

$(document).ready(function() {
    
    $("#with_inventary").prop("checked", false);

    $("#sku_true").prop("checked", false);

    $("#tool-tip-container").on("mouseover", ".dropdown-item", function(e){

        title_new = $(this).children('.text').text().replace(/\s/g, '');
    
        text = $(`.tooltip-data[data-name="${title_new}"]`).val()

        $('#tool-tip-div').css({'top':mouseY + 10,'left':mouseX})
        $("#tool-tip-div").show()
        $("#tool-tip-div div").html(text);

        
    });

    $("#tool-tip-container").on("mouseout", ".dropdown-item", function(){

        $("#tool-tip-div").hide()
    
    })

    /*$("#filter_clear").on("click", function(){
        reset_filter()
        $(".selectpicker").selectpicker("deselectAll")
        $(".selectpicker").selectpicker("refresh")
        active_item()

    })*/

    $("#filter_text").on("keyup", function(){
           
            get_filter_text()
    })

    
    item_group_active = $("#item_group_active").val()

    $(`.select-principal.${item_group_active}`).show()

    $(`.select-secundary.${item_group_active}`).show()

    item_group_filter_toggle(item_group_active)

    $(".item_group").on("click", function(){

        item_group_default = $(this).data("item-group")

        item_group_filter_toggle(item_group_default)

        $(".item_group").addClass("inactive")

        $(this).removeClass("inactive")

        get_rows()
    
        $(`.select-principal`).hide()
        $(`.select-secundary`).hide()

        $(`.select-principal.${item_group_default}`).show()
        $(`.select-secundary.${item_group_default}`).show()


    })

    $("#sku_true").on("change", function(){

        //edicion with_inventary
        //$("#with_inventary").prop("checked", false);

        group_filter = get_group_filter();

        $item = group_filter ? $(`.item-row.filter`).filter(group_filter) : $(`.item-row.filter`);
        console.log($item)
        if ($(this).is(':checked')){
            
            $(`.item-row.filter`).not(".row_select").hide()

            $item.filter(".SI").show()

            //$(".row-inventary").show()
            
            get_rows()

        }
        else{
            $item.show()

            //$(".row-inventary").hide()
        }

        //setup_filter(class_filter)

        if (!group_filter){

            visible_filter_select($(this).is(":checked"))
        }
    })

    /*$('#select-Categoria').on('changed.bs.select', function (e, clickedIndex, isSelected, previousValue) {

        if ((clickedIndex === 0) || (clickedIndex > 0)){    

            setup_select_multiple(".option.select-Categoria", 0, previousValue)              

            select = e.target.options[clickedIndex].value
            
            select_Categoria = $(this).val()


            if (select_Categoria && select_Categoria.includes("SI")){
                $("#with_inventary").prop("checked", false);

                $(".row-inventary").show()
            }else{
                $(".row-inventary").hide()
                $("#with_inventary").prop("checked", false);

            }
            
            $select_option = $(`.select-option.filter`)

            if (!(isSelected)){
               
                if (!$(this).val()){

                    
                    reset_filter()

                }else{

                    visible_filter_select($select_option, select_Categoria)

                }

                $(`.select-option.filter.${select}`).removeAttr("selected")

                $("#select-SubCategoria").selectpicker("refresh")

            }else{
                
                visible_filter_select($select_option, select_Categoria)

            }
            
            active_item()

            get_rows()

            if (!(isSelected) && (!$(this).val())){

                get_class($('.item-row.filter:visible'))

            }

        }
        else{

            $(".row-inventary").hide()

            $("#with_inventary").prop("checked", false);
        }
    })*/

    $('#select-SubCategoria').on('changed.bs.select', function (e, clickedIndex, isSelected, previousValue) {

        setup_select_multiple(".select-option", 1, previousValue)              

        active_item()
        
        if (isSelected)
            
            get_rows(false, false, true)
    })
    $("#filter_text").val("")
});

function validate_has_filter(){
    //if ($('#select-SubCategoria').val() || $('#sku_true').prop("checked") || $('#filter_text').val())
    if ($('#select-SubCategoria').val() || $('#sku_true').prop("checked") || $('#filter_text').val() || $('#with_inventary').prop("checked"))
        return true
    return false
}
function get_group_filter(){

    select_value = $('#select-SubCategoria').selectpicker('val')
        
    let group_filter = ""

    let count = 0

    if (select_value){
        select_value.forEach(element => {
            if (count > 0){
                group_filter += ","
            }
            
            group_filter += ` .${element}`
    
            count ++;
    
        });
        group_filter += ","
    }
    
    group_filter += $("#sku_true").is(":checked") ? " .SI" : ".SI, .NO";

    group_filter += $("#with_inventary").is(':checked') ? ".inventary-SI" : ""
    
    let value = $("#filter_text").val()

    if (value){
        
        value = value.split(" ")

        value.forEach(element => {
            element = element.replace(":","-")

            group_filter += `.${element}`
        })
    }

    return group_filter
}
function get_filter_text(){

    $('.item-row.filter').not(".row_select").hide()

    $(".link_abc").removeClass("selected")

    if ($("#filter_text").val()){
        
        get_rows()

        setup_filter_text()

        get_class($('.item-row.filter:visible'))
    }
}
function setup_filter_text(){
    
    let value = $("#filter_text").val()

    if (value){
        
        value = value.split(" ")

        value.forEach(element => {
            element = element.replace(":","-")

            $('.item-row.filter').filter(`.${element}`).show()
        })
    }
    else{
        group_filter = get_group_filter();

        $item = group_filter ? $(`.item-row.filter`).filter(group_filter) : $(`.item-row.filter`);
    
        $item.show()
    } 
}

function visible_filter_select(select_sku = false){

    $select_option = $(`.select-option.filter`)
    
    $select_option.hide()

    $("#select-SubCategoria").selectpicker("deselectAll")
    
    if (select_sku){

        $select_option.filter(`.SI`).show()

    }else{

        $select_option.show()

    }


    $("#select-SubCategoria").selectpicker("refresh")
}

/*function visible_filter_select($select_option, select_Categoria){
    
    $select_option.hide()

    $("#select-SubCategoria").selectpicker("deselectAll")

    $item = $(".item-row.filter:visible") 
    
    /*$select_option1 = $select_option.filter(function(option){
        console.log($item.hasClass($(this).val()),$item.prop("class"),  $(this).val())
        if ($item.hasClass($(this).val())){
            return true
        }
    })
    //$select_option.filter(`.${select_Categoria[i]}`).show()
    for(i = 0; i < select_Categoria.length; i++){

        $select_option.filter(`.${select_Categoria[i]}`).show()
    }
    $("#select-SubCategoria").selectpicker("refresh")
}*/
function reorganization_subcategory(){

    $("#select-SubCategoria").selectpicker("deselectAll")

    $select_option = $(".select-option")

    $select_option.hide()

    $item_filter = $(".item-row.filter:visible") 

    $item_filter.each(function(){

        array_class = $(this).attr("class").split(" ")

        $(`#select-SubCategoria option[value='${array_class[2]}']`).show()

    })
    
    $(".selectpicker").selectpicker("refresh")

}
function setup_select_multiple(option, select_type, previousValue){
    
    $item_group = $(".item_group").not(".inactive")
    
    item_group_active = $item_group.data("item-group")

    //if ($(`${select}.${item_group_active}`).data("select-type") == 0){
    if (select_type == 0){
        
        if (previousValue.length > 0){

            $(`${option}[value=${previousValue}]`).removeAttr("selected")

            $(".selectpicker").selectpicker("refresh")
        }

    }
}

function reset_filter(){
    $(`.select-option.filter`).show()
    $(`.select-Categoria.filter`).show()
    $(".link_abc.selected").removeClass("selected")
    $("#filter_text").val("")
}

function active_item(){

    letter_filter = $(".link_abc.selected").data("value")

    text_filter = $("#filter_text").val().toUpperCase()

    $item = $(".item-row.filter")

    $item.hide()

    if (letter_filter){
        $item = $item.filter(`.${letter_filter}`)
    }

    if (text_filter){

        $item = setup_filter_text()
    }

    select_Categoria =  format_class($("#sku_true").is(':checked') ? ["SI"] : ["SI", "NO"]);
    
    select_SubCategoria = format_class($("#select-SubCategoria").val());

    if ((select_Categoria) || (select_SubCategoria)){

        if ((select_Categoria) && (select_SubCategoria)){

            result = select_Categoria.map((Categoria) => {
    
                format = select_SubCategoria.map((SubCategoria)=>{
                    return Categoria + SubCategoria
                })
                
                return format.join(",")
            });
    
        }else{
    
            result = select_Categoria ? select_Categoria : select_SubCategoria
        }
        
        result = result.join(",")
    
        $item.filter(result).show()

    }else{

        $item.show()

    }

}


function format_class(list_id){

    if (list_id){
        return list_id.map((id)=>{
    
            inventory = $("#with_inventary").is(':checked') ? ".inventary-SI" : ""

            return `.${id}${inventory}`
        })
    }
    
    return null

}

function active_filter_abc(item_group = null){

    if (!(item_group)){

        item_group = $("#item_group_active").val()

    }

    is_filter_abc = $(`#item_group_${item_group}`).val()
    
    $(".link_abc.selected").removeClass("selected")

    if (is_filter_abc != "0"){
        $(".filter-abc").show()
    }
    else{
        $(".filter-abc").hide()

    }
}

function item_group_filter_toggle(item_group_default){
    
    active_filter_abc(item_group_default)

    $(".selectpicker option").hide()

    $(".selectpicker option").removeAttr("selected")

    remove_class_filter()   

    $SubCategoria_option = $(`.select-option`)

    
    if ($("#sku_true").is(":checked")){
        $SubCategoria_option = $SubCategoria_option.hasClass("SI");

    }

    add_class_filter($SubCategoria_option)

    /*$Categoria_item = $(`.select-Categoria`)

    //$Categoria_item = $(`.select-Categoria.${item_group_default}`)

    $Categoria_item.each(function(){

        Categoria_id = $(this).val()

        if (Categoria_id){
           

            add_class_filter($SubCategoria_option)
        }
    })*/

    //add_class_filter($Categoria_item)

    add_class_filter($(`.item-row.${item_group_default}`))

    filter_show()

    $(".selectpicker").selectpicker("refresh")
}

function add_class_filter($objs){

    $objs.addClass("filter")
}

function remove_class_filter(){

    $(".filter").hide()
    $(".filter").removeClass("filter")
}

function filter_show(){
    $(".filter").show()
}




$(window).scroll(function() {

    if (validate_has_filter()){
        if((($(window).scrollTop() * 2) + $(window).height()) >= $(document).height()){

            get_rows(true)
        }
    }
});	



function get_rows(is_valid = false, is_letter = false, is_class = false){

    if(window.navigator.onLine){

        $pagination_control = $("#pagination_control")

        $petition_control = $("#petition_control")

        if (!is_valid){

            $pagination_control.val(0)
        }
        
        if ( $pagination_control.val() == 0 && $petition_control.val() == 0){

            $petition_control.val(1)

            filter_text = $("#filter_text").val()

            is_filter_text = filter_text ? true : false;

            if (!is_filter_text && !is_valid){
                
                $('#blockscreen-modal').modal("show")
            }

            $("#loading").show()

            $item_group_active = $(".item_group").not(".inactive")

            group_active = $item_group_active.data("item-group")

            row_active_len = $(`.item-row.${group_active}.filter`).length

            Categoria_selected = $("#sku_true").is(":checked") ? ["SI"] : ["SI", "NO"];

            SubCategoria_selected = $("#select-SubCategoria").val()

            letter_filter = $(".link_abc.selected").data("value")

            
            idlevel = $("#idlevel").val()

            has_inventary = $("#with_inventary").is(':checked');
            
            let item_code_list = []

            order_id = $("#order_id").val()

            $(`.item-row`).each(function(){
                item_code_list.push($(this).data("id"))
            })

            
            payload= {
                order_id,
                item_code_list,
                item_group: group_active,
                item_Categoria: Categoria_selected,
                item_SubCategoria: SubCategoria_selected,
                letter_filter,
                filter_text,
                idlevel,
                has_inventary
            }

            module_root = "render.item_formulary.item_formulary_render"

            method = "paginator"

            callresponse = (response)=>{

                if(!response.data){
                    $pagination_control.val(1)
                }

                $("#table_item_list tbody").append(response.data); 

                if (!is_filter_text && !is_valid){
                    $('#blockscreen-modal').modal("hide")
                }

                $("#loading").hide()

                $petition_control.val(0)

                if (filter_text != $("#filter_text").val()){
                    get_filter_text()
                }

                if (is_letter){

                    setup_filter(letter_filter)

                }
                if (has_inventary && !is_class){
                    
                    group_filter = get_group_filter();

                    if (!group_filter){
                        reorganization_subcategory()
                    }

                }
                //get_class()
            }
            
            send_petition(payload, module_root, method, callresponse)
        }
    }
    
}

API_ROOT = "qp_phonix_front.resources"

async function send_petition(payload, module_root, method, callresponse = null){

    return new Promise(() => {
        frappe.call({
            method: setup_method(API_ROOT, module_root, method),
            args: payload,
            async: false,
            callback: function (r_1) {

                response = r_1.message

                if (response.status == 200) {

                    if (callresponse) {

                        callresponse(response)

                    }
                }
                if (response.status == 400) {

                    if (callresponse) {

                        callresponse(response.data)

                    }
                    frappe.msgprint(__(`error: ${response.msg}`))
                }


            }
        })
    })
    
}

function setup_method(api_root, module_root, method){

    result =  `${api_root}.${module_root}.${method}`;

    //console.log(result)

    return result

}
