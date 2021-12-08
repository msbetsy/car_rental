var formErrors = {% if form.errors %}true{% else %}false{% endif %};

$(document).ready(function() {
    if (formErrors) {
        $('#emailModal').modal('show');
    }
});