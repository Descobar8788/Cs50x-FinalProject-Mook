function hide(clas, contrary, buttonid, contrarybuttonid) {
    var cards = document.getElementsByClassName(clas);
    var card1 = document.getElementsByClassName(clas)[0];
    var contrary = document.getElementsByClassName(contrary);
    var thisbutton = document.getElementById(buttonid);
    var contrarybutton = document.getElementById(contrarybuttonid);
    var card;
    if (card1.style.display === "none") {
        
        Array.from(cards).forEach((x) => {
            x.style.display = "flex";
        });
        thisbutton.style.border = "none";
    }
    else if (contrary[0].style.display === "none") {
        Array.from(contrary).forEach((x) => {
            x.style.display = "flex";
        });
        
        Array.from(cards).forEach((x) => {
            x.style.display = "none";
        });
        
        thisbutton.style.border = "3px solid black";
        contrarybutton.style.border = "none";
    }
    else {
        Array.from(cards).forEach((x) => {
            x.style.display = "none";
        });
        thisbutton.style.border = "3px solid black";
    }
}