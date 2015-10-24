$(function(){
	$('#idnum_form').submit(function(event){
		var idnum_field = $('#idnum');
		var idnum = idnum_field.val();
		var verifyRegexp = /^\d{8}$/g;
		if(!verifyRegexp.test(idnum)) {
			$('#idnum_group').addClass('has-error');
			$('#idnum_help').text("Invalid ID. Your ID should be an 8-digit number.")
			event.preventDefault();
		}
	});

	$('#idnum').focus(function(){
		$('#idnum_group').removeClass('has-error');
	});
})