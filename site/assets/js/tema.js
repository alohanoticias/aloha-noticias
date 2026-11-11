try{var t=localStorage.getItem("aloha-tema");if(t==="dark"||t==="light")document.documentElement.setAttribute("data-theme",t)}catch(e){}
// Fontes do Google sem bloquear a primeira pintura: o <link id="fontes"> chega com media="print" e vira "all" ao carregar
(function(){var f=document.getElementById("fontes");if(!f)return;function on(){f.media="all"}if(f.sheet){on()}else{f.addEventListener("load",on)}})();
