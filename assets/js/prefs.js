/* Préférences d'accessibilité appliquées avant l'affichage (évite un flash) */
try{var a=JSON.parse(localStorage.getItem("yf-a11y")||"{}");for(var k in a)if(a[k])document.documentElement.classList.add("a11y-"+k);}catch(e){}
try{if(localStorage.getItem("yf-tb")==="1")document.documentElement.classList.add("tb-hidden");}catch(e){}
