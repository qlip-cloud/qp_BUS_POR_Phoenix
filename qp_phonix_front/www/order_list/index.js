GLOBAL_PARAM_ROOT = "qp_phonix_front.qp_phonix_front.ball_integration.uses_cases.global_parameters.set_global_default";

$(document).ready(function() {

    redirect_to_orders()

});

function assign_settings(){

    company_default = $('#select_company').val();

    customer_default = $('#customer_id').val();

    customer_name_default = $('#customer_name').val();

    if ((company_default) && (customer_default.length != 0) && (customer_name_default.length != 0)){

        frappe.call(GLOBAL_PARAM_ROOT, {
            "ball_company": company_default,
            "ball_customer_id": customer_default,
            "ball_customer_name": customer_name_default
        }).then(() => {
            window.location.href = `/order_list/orders_list`;
        });

    }else{
        $(".alert").removeClass("hide");
        $('#select_defaults').prop('disabled',false);
    }

};

function hide_alert(){

    $(".alert").addClass("hide");

};

function set_customer(cust_id, cust_name){

    document.getElementById("customer_id").value = cust_id;

    document.getElementById("customer_name").value = cust_name;

};


function redirect_to_orders(){

    frm_updt = $('#updt').val();

    if (frm_updt == 0) {

        var ball_company = frappe.get_cookie("ball_company");
        var ball_customer_id = frappe.get_cookie("ball_customer_id");
        var ball_customer_name = frappe.get_cookie("ball_customer_name");

        if (ball_company.length !== 0 && ball_customer_id.length !== 0 && ball_customer_name !== 0){

            window.location.href = `/order_list/orders_list`;

        }

    }

};


function myFunction() {
    // Declare variables
    var input, filter, ul, li, a, i, txtValue;
    input = document.getElementById('myInput');
    filter = input.value.toUpperCase();
    ul = document.getElementById("myUL");
    li = ul.getElementsByTagName('li');

    // Loop through all list items, and hide those who don't match the search query
    for (i = 0; i < li.length; i++) {
      a = li[i].getElementsByTagName("a")[0];
      txtValue = a.textContent || a.innerText;
      if (txtValue.toUpperCase().indexOf(filter) > -1) {
        li[i].style.display = "";
      } else {
        li[i].style.display = "none";
      }
    }
};
