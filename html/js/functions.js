// TODO: ajouter une fonction de désactivation du défilement quand <= ou => est enclenché.

$(document).ready(function () {
    var pause = document.getElementById("pause");
    pause.setAttribute("true", "false");
    tournezMenages();
    var show_lemma = true;
});

var show_lemma = true

$(function () {
    $(".forme").click(function () {
        $(this).css("background-color", "grey")
    });
});


/*Fonction qui permet de copier dans le presse-papier la valeur de l'analyse pour faciliter la correction*/
$(function () {
    $(".annotation").click(function () {
        var annotation = this.childNodes[0].nodeValue;
        console.log(annotation);
        navigator.clipboard.writeText(annotation);
    });
});
/*Fonction qui permet de copier dans le presse-papier la valeur de l'analyse pour faciliter la correction*/



/*
 $(function () {
 $(".texte").mouseover(function () {
 console.log("Texte cliqué");
 var ide = this.id;
 console.log(ide);
 var cible = "#ann_" + ide;
 console.log(cible);
 $(cible).css("visibility", "visible");
 });
 });


 $(function () {
 $(".texte").mouseout(function () {
 $(".annotation").css("visibility", "hidden");
 });
 });
 */


$(function () {
    $("#pause").click(function () {
        var pause = document.getElementById("pause");
        if (pause.getAttribute('true') === 'true') {
            pause.firstChild.data = "Défile";
            pause.setAttribute("true", "false");
        } else {
            pause.firstChild.data = "Défile pas";
            pause.setAttribute("true", "true");
        }
    });
});

$(document).keydown(function (e) {
    switch (e.keyCode) {
        case 80:
        // check if the key is registered
        console.log("p is pressed, pauses/resumes the game!");
        $("#pause").click();
    }
});

/*Ajouter une fonction pour faire apparaître les lemmes*/
$(document).keydown(function (e) {
    switch (e.keyCode) {
        case 76:
        // check if the key is registered
        console.log("L is pressed!");
        if (show_lemma == true) {
            $(".annotation").css("visibility", "visible");
            show_lemma = false;
        } else {
            $(".annotation").css("visibility", "hidden");
            show_lemma = true;
        }
    }
});


function scrollTo(id, shift) {
    if (shift < 0) {
        var n = 1;
    } else {
        var n = -1;
    }
    if (document.getElementById(id).getBoundingClientRect().left === (screen.width / 2) - 100) {
        console.log("True")
        scrolldelay = setTimeout(scrollTo(id, shift), 10000);
    } else {
        window.scrollBy(n, 0);
        scrolldelay = setTimeout(scrollTo(id, shift), 10000);
    }
}

$(document).scroll(function () {
    var scroll_left = $(this).scrollLeft();
    var client_width = document.body.clientWidth;
    var scroll_width = document.body.scrollWidth;
    var scrollPercentage = 100 * scroll_left / scroll_width /(1 - client_width / scroll_width);
    $('#log').html(scrollPercentage.toFixed(2) + '%');
    console.log(scrollPercentage.toFixed(2) + '%');
});

function tournezMenages() {
    var pause = document.getElementById("pause");
    if (pause.getAttribute('true') === 'true') {
        window.scrollBy(30, 0);
        scrolldelay = setTimeout(tournezMenages, 450);
    } else {
        console.log("Paused pageScrolling")
        scrolldelay = setTimeout(tournezMenages, 450);
    }
}