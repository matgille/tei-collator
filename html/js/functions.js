// TODO: ajouter une fonction de désactivation du défilement quand <= ou => est enclenché. 

$(document).ready(function () {
    var pause = document.getElementById("pause");
    pause.setAttribute("true", "false");
    tournezMenages();
});

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



function scrollTo(id, shift) {
    if (shift < 0) {
        var n = 1;
    }
    else {
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