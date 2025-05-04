URL_CREATE_SALES_ORDER = "create_sales_order";

$(document).ready(function () {

  $("#term_condition").prop("checked", false)

  $(".dropdown-menu.dropdown-menu-right").children().first().remove()

  const REDIRECT_INDEX = `/order/index`;

  const REDIRECT_CONFIRM = `/order/confirm`;

  shipping_method = $('#select_shipping_method').val();

  if (sessionStorage.getItem("order_id")) {

    const order_id = sessionStorage.getItem("order_id")

    redirect_link = `/order/item_formulary?order_id=${order_id}`

    redirect(redirect_link)

    sessionStorage.removeItem("order_id")
  }

  get_shipping_calendar(shipping_method)
  $("#table_content").on('keypress', ".quantity", function (event) {
    var keycode = (event.keyCode ? event.keyCode : event.which);
    if (keycode == '13') {

      document.activeElement.blur()

    }
  })


  $("#table_content").on('focus', ".quantity", function () {
    if (!$(this).val() || $(this).val() == "0") {
      $(this).val("");
    }
  })
  $("#table_content").on('blur', ".quantity", function () {
    if ($(this).val()) {
      und_factor($(this))
    } else {
      $(this).val(0)
    }
  })



  $("#select_shipping_method").change(function () {

    $('#datepicker').val("");

    get_shipping_calendar(this.value)
  })

  $("#btn_confirm_order").on("click", () => {
    if ($("#term_condition").prop("checked")) {
      addressSelect = $("#address");
      address = $("#address").val()
      sales_persons = $("#sales_persons");
      customerInput = $("#qp_phoenix_order_customer");
      customerValue = customerInput.val().trim();

      if (customerValue === "") {

        customerInput.addClass("input-error");
        frappe.throw("La orden del cliente es obligatorio")

      }

      if (sales_persons.val() === "") {

        is_vendor_required = sales_persons.data("is_vendor_required")

        if (is_vendor_required == "1") {
          sales_persons.addClass("input-error");
          frappe.throw("Vendedor es obligatorio")
        }
      }

      if (address === "" || address === "0") {
        addressSelect.addClass("input-error");
        frappe.throw("La dirección es obligatoria");
      }

      update_modal(2, 1)

    } else {
      frappe.throw("Debe aceptar las condiciones comerciales")
    }

  })

  $("#qp_phoenix_order_customer").on("blur", function () {
    $(this).removeClass("input-error");
  });

  $("#confirm_draft").on("click", () => {

    order_id = $("#order_id").val()

    if (order_id) {

      update_modal(3, 1)

    } else {

      save_order(URL_CREATE_SALES_ORDER, REDIRECT_CONFIRM, null, true, null, true)
    }
  })



  $("#save_draft").on("click", () => {

    order_id = $("#order_id").val()

    if (order_id) {
      valid_change(REDIRECT_INDEX)
    } else {

      save_order(URL_CREATE_SALES_ORDER, REDIRECT_INDEX)
    }


  })


  $("#btn_back_orders").click(() => {
    valid_change(REDIRECT_INDEX)
  })

  $("#button_yes").click(() => {

    data_type = $("#warn-modal #type").val()

    if (data_type == 0) {


      deleted_rows()

    }
    if (data_type == 1) {

      update_order(REDIRECT_INDEX, false)
    }
    if (data_type == 2) {

      update_order(false, true, action = "confirm", true)
    }
    if (data_type == 3) {

      order_id = $("#order_id").val()
      url = `${REDIRECT_CONFIRM}?order_id=${order_id}`
      update_order(url, false)
    }

    $('#warn-modal').modal("hide")
  })

  total_update()

  $(".btn-redirect").on("click", function () {

    redirect_link = $(this).data("url")

    redirect(redirect_link)

  })

  
  $("#import").on("change", function () {
    const file = this.files[0];
    if (!file) {
      frappe.throw("Debe seleccionar un archivo");
      return;
    }
  
    const formData = new FormData();
    formData.append("file", file);
  
    // Paso 1: Importar archivo
    fetch("/api/method/qp_phonix_front.www.order.index.import_file", {
      method: "POST",
      body: formData,
      headers: {
        "X-Frappe-CSRF-Token": frappe.csrf_token,
      },
    })
      .then(async (response) => {
        const data = await response.json();
  
        if (!response.ok) {
          const errorMsg = data._server_messages
            ? JSON.parse(data._server_messages)[0]
            : "Error al importar el archivo.";
          throw new Error(errorMsg);
        }
  
        // Paso 2: Validar ítems
        return fetch("/api/method/qp_phonix_front.www.order.index.validate_items_and_fetch_info", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "X-Frappe-CSRF-Token": frappe.csrf_token,
          },
          body: JSON.stringify({
            items: JSON.stringify(data.message.items), 
          }),
        });
      })
      .then(async (response) => {
        const data = await response.json();
  
        if (!response.ok) {
          const errorMsg = data._server_messages
            ? JSON.parse(data._server_messages)[0]
            : "Error al validar los productos.";
          throw new Error(errorMsg);
        }
        // Paso 3: Crear Orden de Compra
        const imported_items = data.message.items;
        sessionStorage.setItem("imported_items", JSON.stringify(imported_items));
        save_order(URL_CREATE_SALES_ORDER, "/order/confirm", null, true, null, false, false, null, null, imported_items);
        
        $("#import").val('');
      })
      .catch((error) => {
        console.error("Error:", error);
        frappe.msgprint(error.message || "Error desconocido.");
        $("#import").val('');
      });
  });
  
})

function und_factor($quantity) {

  let row = $quantity.data("select")
  let value = parseInt($quantity.val())
  let quantity_format = $quantity.data("quantity_format")
  let max_value = parseInt($quantity.data("quantity"))
  let transit_value = parseInt($quantity.data("quantity_dis"))
  let item_name = $quantity.data("select")
  let qp_box_no_sku = parseInt($("#qp_box_no_sku").val())
  let qp_box_sku = parseInt($("#qp_box_sku").val())
  let qp_buy_no_sku = parseInt($("#qp_buy_no_sku").val())
  let sku = $quantity.data("sku")
  let qp_prioritize_unit_package = $quantity.data("qp_prioritize_unit_package")
  let incomplete_boxes = parseInt($("#incomplete_boxes").val())
  let calc_incomplete_boxes = true;


  if (value && value > 0) {
    $(`tr.${row} td`).addClass("item_select")
    $(`tr.${row}`).addClass("row_select")
  } else {
    $(`tr.${row} td`).removeClass("item_select")
    $(`tr.${row}`).removeClass("row_select")

  }

  is_factor = !(sku == "SI" ? qp_box_sku : qp_box_no_sku)

  if (incomplete_boxes) {
    $.each(["BH34", "BG21", "BG81"], function (index, value) {
      if ($(`tr.${row}`).attr("data-phonix-class") == value) {
        is_factor = 1;
        calc_incomplete_boxes = false;
      }
    });
  }

  if (is_factor && value > 0 || qp_prioritize_unit_package == "1") {

    factor = parseInt($quantity.data("factor"))

    let buy_no_sku = false;

    if (qp_buy_no_sku && sku == "NO" || qp_prioritize_unit_package == "1") {

      base_result = Number((max_value / factor).toFixed(10));
      base_decimal = Number((base_result - parseInt(base_result)).toFixed(10));
      base_mult_ue = Number((base_decimal * factor).toFixed(10));
      result = Number((value / factor).toFixed(10));
      decimal_value = Number((result - parseInt(result)).toFixed(10));
      mult_ue = Number((decimal_value * factor).toFixed(10));
      down_value = Number((parseInt(result) * factor).toFixed(10));
      up_value = Number((down_value + base_mult_ue).toFixed(10));

      buy_no_sku = (up_value - down_value) >= mult_ue ? true : false;

    }

    if (((value % factor != 0) && (!(buy_no_sku) && calc_incomplete_boxes))) {

      result = parseInt(value / factor) + 1;

      value = result * factor;

      $quantity.val(value)

    }


  }
  $inventory_quantity = $(`#table_content #inventory_quantity-${item_name}`);

  control_value = transit_value + max_value;

  if (quantity_format == "False" && control_value > 0) {


    if (parseInt(value) > parseInt(max_value)) {

      if (control_value >= value)

        $inventory_quantity.html("En tránsito");
      else

        $inventory_quantity.html("No");
    }
    else {
      $inventory_quantity.html("Si");
    }
  }

  $line = $quantity.parents(".line")

  price = parseFloat($line.data("price"))

  sub = value * price;

  $subtotal = $line.find(".subtotal")

  $subtotal.val(sub)

  total_update()
}

function updateIndicator() {

  $visible_area = $(".connection-alert")
  $disabled_inpuut = $("#confirm_draft, #save_draft, #filter_text, #datepicker, select")

  if (window.navigator.onLine) {
    $visible_area.toggle()
    $disabled_inpuut.prop("disabled", false)
    if (get_change_count()) {
      save_or_update()
    }

  }
  else {
    $visible_area.toggle()
    $disabled_inpuut.prop("disabled", true)

  }
  //$('.selectpicker').selectpicker('refresh');


}


window.addEventListener('online', updateIndicator);
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

function delay_save_or_update() {


  if (window.navigator.onLine && $("#save_control").val() == "0") {


    $("#save_control").val("1")

    setTimeout(() => {

      save_or_update()


    }, control);

  }

}
function save_or_update() {

  order_id = $("#order_id").val()

  if (order_id) {

    update_order(null, false, null, false, true)

    //-- tienes q verificar si tienes q actualizar algo en la linea q identifica si la linea tuvo cambios--

  } else {

    save_order(URL_CREATE_SALES_ORDER, null, null, true, null, false, true)

    //-- tienes q verificar si tienes q actualizar algo en la linea q identifica si la linea tuvo cambios--

  }
  $("#save_control").val("0")
}


function valid_change(redirect_url) {

  if (get_change_count()) {

    update_modal(1, 1)

  } else {
    redirect(redirect_url)
  }
}

function total_update() {


  let total = 0
  let discount = 0
  let total_discount = 0

  $(".row_select .subtotal").each(function () {

    total += parseFloat($(this).val());

  })

  //total_str = formato.format(total)

  $(".price_total").html(currency_format(total, 0))


  $(".row_select .subtotal_discount").each(function () {

    discount += parseFloat($(this).val());
  })

  if (discount > 0) {

    total_discount = total - discount;


    $(".price_discount").html(currency_format(total_discount, 0))
    $("#green-discount").show()
  }
}
function update_modal(type, data_no = 0) {

  $("#button_no").attr("data-no", data_no)

  $("#button_yes").removeClass("trash_SubCategoria")

  $("#warn-modal #type").val(type)

  $('#warn-modal').modal("show")
}

function get_change_count() {

  count = $(".is_removed").length

  $(".quantity, .shipping_data").each(function () {

    value = $(this).val()

    base_value = $(this).data("value")

    type_val = $(this).attr('type')

    if (type_val == "number") {
      if (parseFloat(base_value) != parseFloat(value)) {
        count++

      }
    } else {
      if (base_value != value) {

        count++
      }
    }
  })

  return count
}
function update_order(redirect_link = null, valid_empty = false, action = "update", is_return = false, is_async = false) {

  url = "sales_order_update";

  order_id = $("#order_id").val()

  sales_persons = $("#sales_persons").val()

  address = $("#address").val()

  save_order(url, redirect_link, action, valid_empty, order_id, is_return, is_async, sales_persons, address)
}

function save_order(url, redirect_link, action = null, valid_empty = true, order_id = null, is_return = false, is_async = false, sales_person = null, address = null, imported_items = null) {

  let base_url = "qp_phonix_front.qp_phonix_front.uses_cases.sales_order.sales_order"

  let method = `${base_url}.${url}`

  //let delivery_date = $("#datepicker").val()

  //let shipping_type = $("#select_shipping_method").val()

  let items = []

  let len = 0;

  if (!imported_items){
    $(".row_select").each(function () {
  
      let qty = parseInt($(this).find("#quantity").val())
      let quantity = parseInt($(this).find("#quantity").attr("data-quantity"))
      let quantity_dis = parseInt($(this).find("#quantity").attr("data-quantity_dis"))
      let description = $(this).attr("data-description")
      let code = $(this).attr("data-code")
      let rate = $(this).find("#item_price").val()
      let discount_percentage = $(this).find("#item_discount").val()
      let item_code = $(this).find("#item_id").val()
      if (qty > 0) {
  
        /*if(action != "confirm"){
                if(qty > quantity_dis && quantity_dis > 0){
   
                        qty -= quantity_dis;
   
                        items.push({
                                qty: quantity_dis,
                                item_code: $(this).find("#item_id").val(),
                                description: $(this).find("#item_id").val() + "_" + len,
                                rate: $(this).find("#item_price").val(),
                                discount_percentage: $(this).find("#item_discount").val()
                        });
                            
                        len ++;
                }
   
                if(qty > quantity && quantity > 0){
   
                        qty -= quantity;
   
                        items.push({
                                qty: quantity,
                                item_code: $(this).find("#item_id").val(),
                                description: $(this).find("#item_id").val() + "_" + len,
                                rate: $(this).find("#item_price").val(),
                                discount_percentage: $(this).find("#item_discount").val()
                        });
                            
                        len ++;
                }
        }*/
  
        obj = {
          qty,
          code,
          item_code,
          description,
          //description: action == "confirm" ? $(this).data("description") : $(this).find("#item_id").val() + "_" + len,
          rate,
          discount_percentage,
  
  
          //,delivery_date
        }
        items.push(obj);
        console.log(obj)
        len++;
      }
  
    });
  } else {
    imported_items.forEach((item) => {
      let item_code = item.name;
      let description = item.description;
      let qty = parseInt(item.cantidad);
      let rate = parseFloat(item.rate);
      let discount_percentage = parseFloat(item.discountpercentage);

      items.push({
        qty,
        item_code,
        description,
        rate,
        discount_percentage,
      });
      len++;
    }
    )
  }



  args = {
    'order_json': {
      "qp_phoenix_order_customer": action == "confirm" ? $("#qp_phoenix_order_customer").val() : ""
      , items
      , order_id
      , action
      , sales_person
      , address
      , "qp_phoenix_order_comment": $("#qp_phoenix_order_comment").val()
    }
  }

  if (len) {
    if (!is_async) active_block();

    let order_id = $("#order_id").val();

    uploadOrderFile(order_id, function (file_name) {
      if (file_name) {
        args.order_json.qp_phoenix_order_file = file_name;
      }

      frappe.call({
        method,
        args,
        callback: function (r) {
          if (!r.exc) {
            let response = r.message;

            if (response.result == 400) {
              frappe.msgprint(response.msg);
              disabled_block();
            } else if (!is_async) {
              if (is_return) {
                if (!redirect_link) {
                  disabled_block();
                  $("#confirm-modal").modal("show");
                } else {
                  redirect(`${redirect_link}?order_id=${response.name}`);
                }
              } else {
                redirect(redirect_link);
              }
            } else {
              if (url == URL_CREATE_SALES_ORDER) {
                if (!sessionStorage.getItem("order_id")) {
                  sessionStorage.setItem('order_id', response.name);
                }
                $("#order_id").val(response.name);
              }
            }
          }
        },
        freeze: true
      });
    });
  }
  else if (valid_empty) {
    frappe.msgprint("You have not selected any product")
  }
  else {
    redirect(redirect_link)
  }
}


function delete_line(line_id) {

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

$("#undo").click(() => {

  $removed_lines = $(".is_removed")

  $removed_lines.show()

  $removed_lines.removeClass("is_removed")

  $removed_lines.addClass("row_select")

  $removed_lines.each(function () {

    $line = $(this)

    $quantity = $line.find("#quantity")

    if ($quantity.val() <= 0) {

      subtotal = parseInt($line.data("subtotal"))
      $subtotal = $line.find(".subtotal")
      $subtotal.val(subtotal)

      quantity = parseInt($quantity.data("value"))
      $quantity.val(quantity)

    }

  })

  $("#undo").hide()

  $("#undo").text("")

  total_update()
  show_deleted_button()

})

function redirect(redirect_link) {

  division = redirect_link.includes('?') ? "&" : "?";

  const uniqueTimestamp = new Date().getTime();

  window.location.href = `${redirect_link}${division}control=${uniqueTimestamp}`;
}

function get_shipping_calendar(shipping_method) {

  if (shipping_method) {
    frappe.call({
      method: 'qp_phonix_front.qp_phonix_front.uses_cases.shipping_method.shipping_method_list.vf_shipping_date_list',
      args: {
        'shipping_method': shipping_method
      },
      callback: function (r) {
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

function init_datepicker(weekday_list, mindate, maxdate) {

  $("#datepicker").removeClass("hasDatepicker")

  $("#ui-datepicker-trigger").remove()

  $("#datepicker").datepicker({
    dateFormat: "yy-mm-dd",
    minDate: mindate,
    maxDate: maxdate,
    beforeShowDay: function (date) {

      response = weekday_list.filter(element => {
        return date.getDay() == element
      });

      if (response.length) {
        return [true, '', ''];
      } else {
        return [false, '', ''];
      }

    }
  });
}

function active_block() {

  $("#blockscreen").addClass("modal-backdrop")
  $("#blockscreen").addClass("fade")
  $("#blockscreen").addClass("show")
  $("#loader").show()
}
function disabled_block() {
  $("#blockscreen").removeClass("modal-backdrop fade show")
  $("#loader").hide()

}

function currency_format(value, decimal = 2) {

  currency = $("#currency").val()

  formatoMoneda = {
    "COP": "es-CO",
    "USD": "en-US",
    "EUR": "es-ES"

  }

  formatoMoneda = value.toLocaleString(formatoMoneda[currency], { style: 'currency', currency: 'COP', minimumFractionDigits: decimal, maximumFractionDigits: decimal });

  return formatoMoneda.replace(/[^\d.,]/g, ''); // Elimina cualquier símbolo no numérico
}

function uploadOrderFile(orderName, callback) {
  let fileInput = document.querySelector("#qp_phoenix_order_file");

  if (!fileInput || !fileInput.files.length) {
    callback(null);
    return;
  }

  let file = fileInput.files[0];

  let formData = new FormData();
  formData.append("file", file);
  formData.append("is_private", 0); 
  formData.append("doctype", "Sales Order");
  formData.append("docname", order_id);

  fetch("/api/method/upload_file", {
    method: "POST",
    body: formData,
    headers: {
      "X-Frappe-CSRF-Token": frappe.csrf_token,
    },
  })
    .then((r) => r.json())
    .then((data) => {
      if (data.message && data.message.file_url) {
        frappe.call({
          method: "frappe.client.set_value",
          args: {
            doctype: "Sales Order",
            name: order_id,
            fieldname: {
              qp_phoenix_order_file: data.message.file_url,
            },
          },
          callback: function () {
            callback(file.name);
          },
        });
      } else {
        callback(null);
      }
    })
    .catch((err) => {
      console.error(err);
      callback(null);
    });
}

