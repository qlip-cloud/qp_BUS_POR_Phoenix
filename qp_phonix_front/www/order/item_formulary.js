API_ROOT = "qp_phonix_front.resources"

$(document).ready(function () {

    $("#reconcile").on("click", function () {

        const grouped = {};

        // Agrupar inputs por data-select
        $('.quantity').each(function () {
            const selectValue = $(this).data('select');
            if (!grouped[selectValue]) {
                grouped[selectValue] = [];
            }
            grouped[selectValue].push($(this));
        });

        // Sumar valores y dejar solo uno
        $.each(grouped, function (selectValue, inputs) {
            let total = 0;

            inputs.forEach(function (input) {
                total += parseFloat(input.val());
            });

            // Dejar solo el primer input y actualizar su valor
            inputs[0].val(total);

            // Eliminar los demás inputs
            for (let i = 1; i < inputs.length; i++) {
                const tr = inputs[i].closest('tr');
                const nextTr = tr.next('tr');
                tr.remove();
                nextTr.remove();
            }
        });
        const uniqueSelects = Object.keys(grouped);
        $('#filter_text').val(uniqueSelects.join(' '));
    });

})

function deleteRows() {

    $('#table_item_list tbody tr.item-row').not('.row_select').remove();

}

function view_info_filter(isHasActiveFilters) {
    
    if ($('#table_item_list tbody tr.item-row').length == 0 && !isHasActiveFilters)
        $("#info_filter").show() 
    else
        $("#info_filter").hide();
    

}   


$(window).on('scroll', function() {
    // 1. Cuánto ha bajado el usuario
    var scrollActual = $(window).scrollTop(); 
    // 2. El alto de la ventana del navegador
    var altoVentana = $(window).height();
    // 3. El alto total de toda tu página
    var altoDocumento = $(document).height();

    // Ajuste: 100 píxeles antes de llegar al final para que la carga sea fluida
    var margenDiferencia = 150;

    if (scrollActual + altoVentana >= altoDocumento - margenDiferencia) {
        // Ejecuta tu función de carga aquí
        getRows(is_delete_rows = false, is_blockscreen = false);
        
    }
});
//$(window).scroll(function () {
//
//    
//    if ((($(window).scrollTop() * 2) + $(window).height()) >= $(document).height()) {
//
//        getByPaginator()
//    }
//    
//});

function getFilterPayload() {

    let filters = {};

    $('.filter-items').each(function() {
        const el = $(this);
        const id = el.attr('id');


        if (!id) return;

        if (el.is(':checkbox')) {

            filters[id] = el.prop('checked') ? 1 : 0;
        } 
        else if (el.is('select')) {

            const val = el.val();

            filters[id] = val ? (Array.isArray(val) ? val : [val]) : [];
        } 
        else if (el.is('input[type="text"]') || el.is('textarea')) {

            const rawVal = el.val() || "";
            const trimmed = rawVal.trim();

            filters[id] = trimmed !== "" ? trimmed.split(/\s+/) : [];
        }
    });

    filters["item_code_list"] = [];

    $(`.item-row-base`).each(function () {
        filters["item_code_list"].push($(this).data("id").toString())
    })

    return filters;
}

function hasActiveFilters(filters) {
    for (let key in filters) {
        if (key === 'item_code_list') continue;

        const val = filters[key];

        if (Array.isArray(val)) {
            if (val.length > 0) return true;
        } 

        else if (typeof val === 'number') {
            if (val !== 0) return true;
        } 

        else if (typeof val === 'string') {
            if (val.trim() !== "") return true;
        }
    }


    return false;
}

const getRows = debounce(function(is_delete_rows = true, is_blockscreen = true) {
    
    if (is_delete_rows) {
        
        deleteRows();
    }

    $("#no_results").hide();
    
    const payload = getFilterPayload();

    const isHasActiveFilters = hasActiveFilters(payload)

    if (isHasActiveFilters) {

        get_rows(payload, is_blockscreen = is_blockscreen);

    }

    view_info_filter(isHasActiveFilters)
       
}, 150); 


$(document).on('change', '.filter-items', getRows);

function debounce(func, wait) {
    let timeout;
    return function() {
        const context = this, args = arguments;
        clearTimeout(timeout);
        timeout = setTimeout(() => func.apply(context, args), wait);
    };
}

function get_rows(payload, is_blockscreen = true, is_class = false) {
 
    if (window.navigator.onLine) {

        $pagination_control = $("#pagination_control")

        $petition_control = $("#petition_control")

        $pagination_control.val(0)
        

        if ($pagination_control.val() == 0 && $petition_control.val() == 0) {

            $petition_control.val(1)
            $("#loader").show()

            if (is_blockscreen) {
                $('#blockscreen-modal').modal("show")
            }
            
            //$("#loading").show()

            payload.order_id = $("#order_id").val()

            module_root = "render.item_formulary.item_formulary_render"

            method = "get_rows"

            callresponse = (response) => {
                
                if (!response.data) {
                    $pagination_control.val(1)
                }
                
                $("#table_item_list tbody").append(response.data);
                
                $("#loader").hide()

                if (is_blockscreen) {
                    $('#blockscreen-modal').modal("hide")
                }

                if (!response.data) {
                    $("#no_results").show()
                }

                $petition_control.val(0)
    
            }

            send_petition(payload, module_root, method, callresponse)
        }
    }

}

async function send_petition(payload, module_root, method, callresponse = null) {

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

                        console.log(response)
                        callresponse(response)

                    }
                    frappe.msgprint(__(`error: ${response.msg}`))
                }


            }
        })
    })

}

function setup_method(api_root, module_root, method) {

    result = `${api_root}.${module_root}.${method}`;

    return result

}