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