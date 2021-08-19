function replybutton(btn) {
  btn.nextElementSibling.style.display = "block";
  btn.style.display = "none"
  }

var formErrors = {% if form.errors %}true{% else %}false{% endif %};

$(document).ready(function() {
    if (formErrors) {
        $('#emailModal').modal('show');
    }
});