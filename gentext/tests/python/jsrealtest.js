var jsrealb=require('./jsreal/JSrealB-EnFr.js');

//charger les exports (Constructeurs pour terminaux et non-terminaux) dans le contexte courant
//pour pouvoir les utiliser directement
for (var v in jsrealb){
 eval("var "+v+"=jsrealb."+v);
}
//test en français
loadFr();
addToLexicon("JSrealB", {"N":{"g":"m", "pe":3, "tab":["nI"]}});
for (var i=0;i<2;i++)
 console.log(S(NP(N("JSrealB")),
        VP(V("réaliser").t("pc"),
           NP(D("ce"),N("phrase")))).typ({pas:i%2==1}));
console.log("---");
//test en anglais
loadEn(true); // paramètre pour avoir un message lors du chargement
addToLexicon("JSrealB",{"N":{"tab":["n1"]}});
//étrangement this est comme Adv et Pro mais non D dans le lexique...
addToLexicon("this",{"D":{ "tab": ["d3"] }, "Pro": { "tab": ["pn8"]}}); // mais problème avec la table d3
for (var i=0;i<2;i++)
	console.log(S(NP(N("JSrealB")),
        VP(V("realize"),
           NP(D("that"),N("sentence")))).typ({pas:i%2==1}));