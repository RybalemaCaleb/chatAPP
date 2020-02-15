document.addEventListener('DOMContentLoaded', function() {
    var elems = document.querySelectorAll('select');
    var instances = M.FormSelect.init(elems, option);
});

// Or with jQuery

$(document).ready(function(){
    $('select').formSelect();
});