$(document).ready(function() {
    $(".tab-draft").show()

    $(".tab-items").click(function(){

        if (!$(this).hasClass("active")){

            $(".tab-items").toggleClass("active")

            $(".tab-section").toggle()

        }
    })
});
