UPDATE_FILE_ROOT = "api.file_api";
$(document).ready(function() {

    redirect_to_index()

    $(".tab-draft").show();

    $(".tab-items").click(function(){

        if (!$(this).hasClass("active")){

            $(".tab-items").toggleClass("active");

            $(".tab-section").toggle();

        }
    })

    $('#load_file').on('click',()=>{

        $('#load_file').prop('disabled',true);

        $("#modal_loading_files").show();

        fileToUpload = $('#fileToUpload').prop('files');
           
        if (fileToUpload.length!=0){

                import_order(fileToUpload);

        }else{
                $(".alert").removeClass("hide");
                $('#load_file').prop('disabled',false);
                $("#modal_loading_files").hide();
        }
    });

});

function openmodal(){
    $("#fileToUpload").val("");
    $('#load_file').prop('disabled',false);
    $("#modal_loading_files").hide();
    $('#load_option_modal').modal('show');
};

function import_order(fileToUpload){

    let method = `qp_phonix_front.www.order_list.orders_list.import_template`;

    let param_company = $('#param_company').val();
    let param_customer = $('#param_customer').val();

    frappe.call({
        async: false,
        method,
        callback: function(r) {
            if (!r.exc) {

                let response = r.message;

                if (response.result === 200) {

                    var formData = new FormData();

                    url = "/api/method/upload_file";

                    formData.append("file", fileToUpload[0], fileToUpload[0].name);
                    formData.append("is_private", 0);
                    formData.append("doctype", "qp_Advanced_Integration");
                    formData.append("docname", response.name);
                    formData.append("fieldname", "import_file");

                    callback = (data)=>{

                        console.log("data-->", data)

                        if (data) {

                            callback_end = (res_data)=>{

                                if (res_data) {

                                    console.log("redirecciona --------->")

                                    window.location.href =  `/order_list/orders_differential?process_name=${response.name}`;

                                } else {

                                    $("#modal_loading_files").hide();

                                    frappe.throw(__('Error in create sale ordes...'));

                                }
                            }

                            payload = {
                                "adv_int_name": response.name,
                                "url_file": data.file_url,
                                "param_company": param_company,
                                "param_customer": param_customer,
                            }
                
                            send_petition(payload, UPDATE_FILE_ROOT,"update", callback_end);

                            $('#load_option_modal').modal('hide');

                        } else {

                            $("#modal_loading_files").hide();

                            frappe.throw(__('Error in upload file...'));

                        }
                    }

                    send_petition_upload("", "", formData, callback, url);

                } else {

                    frappe.throw(__(response.msg));

                }
            }
        },
        freeze:true
    })
};

function send_petition_upload(module_root, method, formData, callback, url = null){

    return new Promise((resolve, reject) => {
        let xhr = new XMLHttpRequest();

        xhr.onreadystatechange = () => {
            if (xhr.readyState == XMLHttpRequest.DONE) {

                response = JSON.parse(xhr.responseText);

                if (xhr.status === 200) {
                    
                    callback(response.message);

                } else {

                    callback(response.message);
                           
                    frappe.msgprint(__(`Error: ${response.message.msg}`));

                }
            }
        }

        endpoint = url ? url : setup_api_method(API_ROOT, module_root, method, true);
        
        xhr.open('POST',endpoint , true);
        xhr.setRequestHeader('Accept', 'application/json');
        xhr.setRequestHeader('X-Frappe-CSRF-Token', frappe.csrf_token);
        xhr.send(formData);

    })
}

function setup_api_method(api_root, module_root, method, has_base_root = false){

    base_root = has_base_root ? "/api/method/" : "";

    result = `${ base_root }${api_root}.${module_root}.${method}`;

    return result;

}

function redirect_to_index(){
    
    var ball_company = frappe.get_cookie("ball_company");
    var ball_customer_id = frappe.get_cookie("ball_customer_id");
    var ball_customer_name = frappe.get_cookie("ball_customer_name");

    if (ball_company.length == 0 || ball_customer_id.length == 0 || ball_customer_name == 0){

        window.location.href = `/order_list/index`;

    }

};

function change_params(){

    window.location.href =  `/order_list/index?updt=${1}`;

};
