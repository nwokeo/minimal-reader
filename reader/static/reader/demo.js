$(document).ready(function(){
		
	// first example
	$("#navigation").treeview({
		collapsed: true,
		unique: true,
		persist: "location"
	});

	
	// second example
	//animated:"normal",
	$("#browser").treeview({
		animated:"fast",
		persist: "cookie"
	});


	// third example
	$("#red").treeview({
		animated: "fast",
		collapsed: true,
		control: "#treecontrol"
	});


});
