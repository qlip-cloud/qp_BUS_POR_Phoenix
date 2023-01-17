$(function () {
        $('[data-toggle="tooltip"]').tooltip()
      })
$(document).ready(function() {
        
        sessionStorage.removeItem("order_id")

        $('#select_shipping_method').prop('selectedIndex',0);

        $('#datepicker').val("");

        $('.card-item-group').on('click',()=>{

                item_type = $(this).data("item_group")


                console.log($(this))
                //shipping_type = $('#select_shipping_method').val();
                //shipping_date = $('#datepicker').val();
                //window.location.href = `/order/item_formulary?item_group=${item_type}`;
        });

});

function openmodal(item_type){
        window.location.href = `/order/item_formulary?item_group=${item_type}`;

}
