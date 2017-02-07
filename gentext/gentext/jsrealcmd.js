var jsrealb=require(process.argv[2]);

//charger les exports (Constructeurs pour terminaux et non-terminaux) dans le contexte courant
//pour pouvoir les utiliser directement
for (var v in jsrealb){
 eval("var "+v+"=jsrealb."+v);
}

if (process.argv[5] === 'fr') {
	loadFr();
}
else if (process.argv[5] === 'en') {
	loadEn();
}
else {
	loadEn();
}

var new_lexicon = JSON.parse(process.argv[3]);
var lexicon = JSrealB.Config.get("lexicon");

for (var unit_name in new_lexicon){
	var unit_detail = new_lexicon[unit_name];
	if (lexicon.hasOwnProperty(unit_name)) {
		var current_entry = lexicon[unit_name];
		for (var syntagmType in unit_detail) {
			if (!current_entry.hasOwnProperty(syntagmType)) {
				current_entry[syntagmType] = unit_detail[syntagmType]
			}
		}
	}
	else {
		lexicon[unit_name] = unit_detail;
	}
}

var codes = eval(process.argv[4])
var paragraphs = [];
var current_paragraph = [];
codes.forEach(function(val, index, array){
	if (val === '"#NEWLINE"' || val === '#NEWLINE') {
		paragraphs.push(current_paragraph);
		current_paragraph = [];
	}
	else {
		current_paragraph.push(eval(val) + "");
	}
});

if (current_paragraph) {
	paragraphs.push(current_paragraph);
	current_paragraph = [];
}
var textual_paragraphs = [];
paragraphs.forEach(function(current_paragraph, index, array){
	textual_paragraphs.push(current_paragraph.join(' '));
});
console.log(textual_paragraphs.join('\n'));


