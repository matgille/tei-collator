$(document).ready(function () {
    var arrows = document.querySelectorAll('.current_arrow');
    var first_arrow = arrows[0];
    $(first_arrow).show();
});
/*
 $(function () {
 $('.switch').click(function (e) {
 e.preventDefault();
 }).click();
 });
 */

$(function () {
    $(".switch").click(function () {
        console.log("Switch cliqué");
        var grandparent_node = this.parentNode.parentNode
        console.log(grandparent_node.getAttribute("semblable"))
        if (grandparent_node.getAttribute("semblable") == "False") {
            grandparent_node.setAttribute("semblable", "True");
            this.setAttribute("clické", "True");
        } else {
            grandparent_node.setAttribute("semblable", "False");
            this.setAttribute("clické", "False");
        }
    });
});


$(function () {
    $(".dissemblable").click(function () {
        var sibling_switch = this.parentNode.nextElementSibling.childNodes[1];
        $(sibling_switch).click();
    });
});



var myGlobalVar = 0;

$(document).keydown(function (e) {
    switch (e.keyCode) {
        case 65:
        console.log("Gauche cliqué");
        console.log(myGlobalVar)
        var rows = document.querySelectorAll('.switch');
        var first_semblable = rows[myGlobalVar];
        var grandparent_node = first_semblable.parentNode.parentNode;
        var all_arrows = document.querySelectorAll('.current_arrow');
        var first_arrow = all_arrows[myGlobalVar + 1];
        var current_activation = $(grandparent_node).attr("semblable")
        if (current_activation == "True") {
            $(first_semblable).click();
        } else {
        };
        $(all_arrows).fadeOut();
        $(first_arrow).fadeIn(1000);
        var next_grandparent_node = rows[myGlobalVar + 1].parentNode.parentNode;
        var grandparent_node = rows[myGlobalVar].parentNode.parentNode;
        grandparent_node.setAttribute("class", "");
        next_grandparent_node.setAttribute("class", "active");
        myGlobalVar = myGlobalVar + 1;
    }
});


$(document).keydown(function (e) {
    switch (e.keyCode) {
        case 68:
        console.log("Droite cliqué");
        console.log(myGlobalVar)
        var rows = document.querySelectorAll('.switch');
        var first_semblable = rows[myGlobalVar]
        $(first_semblable).click();
        var all_arrows = document.querySelectorAll('.current_arrow');
        var first_arrow = all_arrows[myGlobalVar + 1];
        $(all_arrows).fadeOut();
        $(first_arrow).fadeIn();
        var next_grandparent_node = rows[myGlobalVar + 1].parentNode.parentNode;
        var grandparent_node = rows[myGlobalVar].parentNode.parentNode;
        grandparent_node.setAttribute("class", "");
        next_grandparent_node.setAttribute("class", "active");
        myGlobalVar = myGlobalVar + 1
    }
});


$(document).keydown(function (e) {
    switch (e.keyCode) {
        case 83:
        console.log("Bas cliqué");
        console.log(myGlobalVar)
        var rows = document.querySelectorAll('.switch');
        var first_semblable = rows[myGlobalVar]
        var all_arrows = document.querySelectorAll('.current_arrow');
        var first_arrow = all_arrows[myGlobalVar + 1];
        $(all_arrows).fadeOut();
        $(first_arrow).fadeIn();
        var next_grandparent_node = rows[myGlobalVar + 1].parentNode.parentNode;
        var grandparent_node = rows[myGlobalVar].parentNode.parentNode;
        grandparent_node.setAttribute("class", "");
        next_grandparent_node.setAttribute("class", "active");
        myGlobalVar = myGlobalVar + 1
    }
});

$(document).keydown(function (e) {
    switch (e.keyCode) {
        case 87:
        console.log("Haut cliqué");
        console.log(myGlobalVar)
        var rows = document.querySelectorAll('.switch');
        var first_semblable = rows[myGlobalVar]
        var all_arrows = document.querySelectorAll('.current_arrow');
        var first_arrow = all_arrows[myGlobalVar - 1];
        $(all_arrows).fadeOut();
        $(first_arrow).fadeIn();
        var next_grandparent_node = rows[myGlobalVar - 1].parentNode.parentNode;
        var grandparent_node = rows[myGlobalVar].parentNode.parentNode;
        grandparent_node.setAttribute("class", "");
        next_grandparent_node.setAttribute("class", "active");
        myGlobalVar = myGlobalVar - 1
    }
});



/*Il faut aller chercher dans le DOM le premier élément de la classe semblable / dissemblable*/

$(function () {
    $("#enregistrer").click(function () {
        console.log("Enregistrer cliqué.")
        var rows = document.querySelectorAll('.lemmes');
        
        var linksArray =[];
        // Loop through all rows
        for (var i = 0; i < rows.length; i++) {
            
            // Store rows in variable
            
            var text_node = rows[i].childNodes[0].data
            var current_node = rows[i].childNodes[0]
            var text_node = current_node.data
            var semblable = rows[i].parentNode.getAttribute("semblable")
            var final_text = text_node + "\t" + semblable
            linksArray.push(final_text);
            
            // Works fine in console
            console.log(final_text);
        }
        
        
        // Create text document — only saves 1st link in text doc
        var textDoc = document.createElement('a');
        textDoc.href = 'data:attachment/text,' + encodeURI(linksArray.join('\n'));
        textDoc.target = '_blank';
        textDoc.download = 'myFile.txt';
        textDoc.click();
    });
});