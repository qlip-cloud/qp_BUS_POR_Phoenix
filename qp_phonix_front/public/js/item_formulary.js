
$(document).ready(function() {

    $('#select_shipping_method').selectpicker();

    $(".quantity").each(function(){
        $(this).val($(this).data("value"))
    })

    $('.disabled').show();

    $(".link_abc").click(function(){
        
        if(window.navigator.onLine){

            if($(this).hasClass("selected")){

                $(this).removeClass("selected")

                $(`.filter`).show()

                $(`.selectpicker`).selectpicker("deselectAll")

                $(".selectpicker").selectpicker("refresh")

            }else{
                
                $("#filter_text").val("")

                $(".link_abc.selected").removeClass("selected")

                $(this).addClass("selected")

                link_abc = $(this).data("value")
                
                setup_filter(link_abc)

                get_rows(false, true)
                    
            }
        }
    })

    $("#table_content").on('keyup mouseup', ".quantity",function () {
        
        value = $(this).val()
        
        row = $(this).data("select")

        if (value && value > 0){
            $(`tr.${row} td`).addClass("item_select")
            $(`tr.${row}`).addClass("row_select")
        }else{
            $(`tr.${row} td`).removeClass("item_select")
            $(`tr.${row}`).removeClass("row_select")

        }
        
    })

});

function setup_filter(link_abc){
    
    $('.item-row.filter').not(`.${link_abc}`).hide()

    $(`.item-row.filter.${link_abc}`).show()

    get_class($('.item-row.filter:visible'))
}
function get_class($item_filter){

    SubCategoria_list = []

    $(".selectpicker").selectpicker("deselectAll")

    $select_option = $(".option, .select-option")

    $select_option.hide()
    
    $item_filter.each(function(){

        array_class = $(this).attr("class").split(" ")
     
        $item_group_active = $(".item_group").not(".inactive")

        group_active = $item_group_active.data("item-group")

        //$select_option.filter(`.${group_active}.${array_class[0]}`).show()
        $select_option.filter(`.${array_class[0]}`).show()

        $(`#select-SubCategoria option[value='${array_class[1]}']`).show()

    })

    // $('#select-SubCategoria').selectpicker('val', SubCategoria_list);

    $(".selectpicker").selectpicker("refresh")

    // $("#select-SubCategoria").selectpicker("refresh")


}