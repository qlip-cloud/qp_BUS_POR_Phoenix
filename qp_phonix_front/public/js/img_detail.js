// Get the modal
/*var modal = document.getElementById("myModal");

// Get the image and insert it inside the modal - use its "alt" text as a caption
var img = document.getElementById("myImg");
var modalImg = document.getElementById("img01");
var captionText = document.getElementById("caption");



img.onclick = function(){
  modal.style.display = "block";
  modalImg.src = this.src;
  captionText.innerHTML = this.alt;
}

// Get the <span> element that closes the modal
var span = document.getElementsByClassName("close")[0];

// When the user clicks on <span> (x), close the modal
span.onclick = function() {
  modal.style.display = "none";
} 
*/
$(document).ready(function() {
    $("#table_item_list").on("click", ".item_img", function(){
        $("#myModal").css("display", "block")
        $("#img01").attr("src", $(this).attr("src"))
        
    })

    $(".close_mymodal").on("click", function(){
        $("#myModal").css("display", "none")
    })
})
