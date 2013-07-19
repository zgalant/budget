var PARENTS = {};

PARENTS["lunch"] = ["food"];
PARENTS["dinner"] = ["food"];
PARENTS["groceries"] = ["food"];
PARENTS["subway"] = ["sandwiches"];
PARENTS["sandwiches"] = ["food"];

PARENTS["coffee"] = ["drinks"];
PARENTS["beer"] = ["alcohol"];
PARENTS["alcohol"] = ["drinks"];

PARENTS["bart"] = ["transportation"];
PARENTS["caltrain"] = ["transportation"];
PARENTS["gas"] = ["car"];
PARENTS["muni"] = ["transportation"];
PARENTS["car maintenance"] = ["car"];
PARENTS["car"] = ["transportation"];

var Tagger = (function(){
	var tags = [];
	var getTags = function(){
		return tags;
	}
	var add = function(tag){
		if(tags.indexOf(tag) == -1){
			tags.push(tag);
		}
		var parents = PARENTS[tag];
		if(parents == undefined){
			return;
		}
		for(var i = 0; i < parents.length; i++){
			parent = parents[i];
			add(parent);
		}
	}

	return {
		add: add,
		getTags: getTags
	}
}());

var TagUI = (function(){
	var add_tag_box = "";
	var tag_list = "";

	var tagMarkdown = function(tag){
		var md = '<span class="tag">' + tag + '</span>';
		return md;
	}

	var displayTags = function(){
		var tags = Tagger.getTags();
		var md = "";
		for(var i=0; i < tags.length; i++){
			md += tagMarkdown(tags[i]);
		}
		console.log(md);
		$(tag_list).html(md);
	}

	var setup = function(){
		add_tag_box = "#id_tags";
		tag_list = "#tag-list";

		$(add_tag_box).keydown(function(event){
			if(event.which == 188 || event.which == 13){
				var tag = $(this).val();
				$(this).val("");
				Tagger.add(tag);
				displayTags();
				event.preventDefault();
			}
		});
	}

	return {
		setup: setup
	}
}());

$(document).ready(function(){
	TagUI.setup();

	$("#add-purchase-button").click(function(){
		$form = $("form");
		$("#id_tags").val(Tagger.getTags().join(","));
	});
});