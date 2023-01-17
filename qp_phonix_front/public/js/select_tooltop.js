
$(document).ready(function() {

    $("#select_shipping_method option").tooltip({
        placement: 'right',
        trigger: 'hover',
        container: 'body'
    });
  
  $("#dropdown").change(function(event) {
    $.each($(this).find('option'), function(key, value) {
      $(value).removeClass('active');
    })
    $('option:selected').addClass('active');
  
  });

  alert("asd")
});
