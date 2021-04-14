// TODO: ajouter une fonction de désactivation du défilement quand <= ou => est enclenché.

$(document).ready(function () {
    var pause = document.getElementById("pause");
    pause.setAttribute("true", "false");
    tournezMenages();
    var show_lemma = true;
});

var show_lemma = true

/*$(function () {
 $("td").click(function () {
 var rect = this.getBoundingClientRect();
 var id = this.id
 console.log(id)
 var rect_left = rect.left
 console.log(rect.left);
 var middle_of_the_screen = (screen.width / 2) - 100
 console.log(middle_of_the_screen);
 var shift = Math.floor(rect_left - middle_of_the_screen)
 console.log("shift: " + shift);
 scrollTo(id, shift)
 });
 });

 */ 3
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