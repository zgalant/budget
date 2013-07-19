var Tagger = (function(){
	var tags = [];
	var PARENTS = {};
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

	var removeTag = function(tag){
		var index = tags.indexOf(tag);
		tags.splice(index, 1);
	}

	var setParents = function(parents){
		PARENTS = JSON.parse(parents);
	}

	return {
		add: add,
		getTags: getTags,
		removeTag: removeTag,
		setParents: setParents
	}
}());

var TagUI = (function(){
	var add_tag_box = "";
	var tag_list = "";

	var tagMarkdown = function(tag){
		var md = '<span class="tag label label-info" data-val="' + tag + 
				'">' + tag + '<span class="close">&times;</span></span>';
		return md;
	}

	var displayTags = function(){
		var tags = Tagger.getTags();
		var md = "";
		for(var i=0; i < tags.length; i++){
			md += tagMarkdown(tags[i]);
		}
		$(tag_list).html(md);
	}

	var removeTag = function(tag){
		Tagger.removeTag(tag);
	}

	var setup = function(){
		add_tag_box = "#id_tags";
		tag_list = "#tag-list";

		function setupRemove(){
			$(".close").click(function(){
				var tag = $(this).parent();
				var val = tag.attr("data-val");
				Tagger.removeTag(val);
				$(tag).remove();
			});
		}

		$(add_tag_box).keydown(function(event){
			if(event.which == 188 || event.which == 13){
				var tag = $(this).val();
				$(this).val("");
				Tagger.add(tag);
				displayTags();
				setupRemove();
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