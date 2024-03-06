
API_ROOT = "qp_phonix_front.resources"

async function send_petition(payload, module_root, method, callresponse = null){

    //console.log(payload, module_root, method)

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

                if (response.status == 500) {

                    if (callresponse) {

                        callresponse(response)

                    }
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
