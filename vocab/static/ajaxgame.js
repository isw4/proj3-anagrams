/***
* Javascript to request and handle the AJAX post requests
* 
* Whenever a key is pressed, will send a post request to check if the word is correct.
* Displays incorrect words or letters as appropriate, and also automatically matches
* a correct word. If all words are successfully matched, directs to a success page automatically.
**/

// Suppress normal form submission (supposedly)
$("#entry").submit(function(event){
  event.preventDefault();
  event.stopPropagation();
});

//submits an ajax post when a letter key or the backspace is pressed
$("#attempt").keyup(function(event){
  var txt = $("#attempt").val();  // Current content of the input field
  var keycode = event.which;      // The key that just went up
  
  // Does nothing if the key entered is not a letter or backspace. Prevents unnecessary AJAX calls
  if (keycode!=8 && !(keycode>=65 || keycode<=90)) { return }

  //clearing old flash messages
  $("#message").text("");

  //AJAX post request
  $.post("/_check", { text: txt }, function(data) {
    status = data.result.status;
    
    //matched a new word, adding it to results display
    if (status === "new match") {
      $("#results h2").text("You found:");
      $("#results *:last").after($("<p></p>").text(txt));
    }

    //letters are either not in jumble or proper word typed is incorrect
    //adds to message display
    else if (status === "old match") {
      $("#message").text("You already found " + txt);
    }
    else if (status === "invalid") {
      $("#message").text(txt + " can't be made from the letters in the jumble");
    }

    //if successful, redirects to success page
    else if (status === "success") {
      return window.location = data.result.redirect;
    }

    return false;
  }, "json");
})