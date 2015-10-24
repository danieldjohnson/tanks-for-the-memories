$(function(){
	var editor = CodeMirror.fromTextArea($("#editor")[0],
					{mode: 'python', theme: "neo", lineNumbers: true});
	editor.on("change",function(){
		$("#save").removeClass("btn-default disabled").addClass("btn-info").text("Save");
	});
	$("#save").click(function(){
		$.post("/edit", {value: editor.getValue()}, function(data){
			$("#save").addClass("btn-default disabled").removeClass("btn-info").text("Saved");
			$("#compile-output").text(data);
		});
	});
})


// editor.setTheme("ace/theme/monokai");
// editor.getSession().setMode("ace/mode/python");