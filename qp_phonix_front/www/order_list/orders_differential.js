SEND_GP_ROOT = "api.file_api"
$(document).ready(function() {

    const REDIRECT_TO_ORDERS = `/order_list/orders_list`;

    let element = document.getElementById("btn_confirm_gp_orders");

    process_name = $("#process_id").val();

    if ($("#show_buttom").val() === "1") {

        element.removeAttribute("hidden");

    } else {

        element.setAttribute("hidden", "hidden");

    }

    $("#btn_back_orders").click( ()=>{

        redirect(REDIRECT_TO_ORDERS);
    })

    $("#btn_confirm_gp_orders").on("click", ()=>{

        $('#confirm-gp-modal').modal("show");
    
    })

    $("#button_send_gp_yes").click(()=>{

        $('#btn_confirm_gp_orders').hide();

        $("#modal_notify_so").show();

        $("#confirm-gp-modal").hide();

        callback = (response)=>{

            if (response) {

                refresh_after_n_seconds(1, process_name);

            } else {

                frappe.throw(__('Error in send sales orders to GP...'));

            }

        }

        payload = {
            "adv_int_name": process_name
        }

        send_petition(payload, SEND_GP_ROOT,"sent_so2gp", callback);

    })


    if ($("#so_import_finish").val() === "0") {

        $("#modal_notify_so").show();

        refresh_after_n_seconds(10, process_name);

    } else {

        if ($("#so_notify_finish").val() === "0" && $("#end_process").val() === "0") {

            $("#modal_notify_so").show();

            refresh_after_n_seconds(10, process_name);
        }

    }

});

function refresh_after_n_seconds(n_seconds, process_name) {
	// cache invalidation after 10 seconds
	const timeout = n_seconds * 1000;

	setTimeout(() => {
        actualizar(process_name);
	}, timeout);
};

function actualizar(process_name){

    console.log("entra a limpiar cache", process_name);

    clear_cache_diff(process_name);

};

function clear_cache_diff(process_name){

    payload= {}

    callresponse = (response)=>{

        if (response.data) {

            window.location.href =  `/order_list/orders_differential?process_name=${process_name}`;

            console.log("redirige despues de limpiar cache");

        } else {

            frappe.throw(__('Error in clear cache...'));

        }

    }

    send_petition(payload, SEND_GP_ROOT, "update_diff", callresponse)

}