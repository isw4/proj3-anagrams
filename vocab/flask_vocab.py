"""
Simple Flask web site
"""

import flask
import logging

# Our own modules
from letterbag import LetterBag
from vocab import Vocab
from jumble import jumbled
import config

###
# Globals
###
app = flask.Flask(__name__)

CONFIG = config.configuration()
app.secret_key = CONFIG.SECRET_KEY  # Should allow using session variables

#
# One shared 'Vocab' object, read-only after initialization,
# shared by all threads and instances.  Otherwise we would have to
# store it in the browser and transmit it on each request/response cycle,
# or else read it from the file on each request/responce cycle,
# neither of which would be suitable for responding keystroke by keystroke.

#TO FIX: modify the config input
WORDS = Vocab(CONFIG.VOCAB)
#WORDS = Vocab(['chaeyoung', 'dahyun', 'nayeon', 'jihyo', 'mina', 'sana', 'tzuyu', 'momo', 'jungyeon'])
#flask.g.vocab = WORDS.as_list()

###
# Pages
###


@app.route("/")
@app.route("/index")
def index():
    """The main page of the application"""
    #global flask.g.vocab
    flask.g.vocab = WORDS.as_list()
    print(flask.g.vocab[0])
    flask.session["target_count"] = min(
        len(flask.g.vocab), CONFIG.SUCCESS_AT_COUNT)
    flask.session["jumble"] = jumbled(
        flask.g.vocab, flask.session["target_count"])
    flask.session["matches"] = []
    app.logger.debug("Session variables have been set")
    assert flask.session["matches"] == []
    assert flask.session["target_count"] > 0
    app.logger.debug("At least one seems to be set correctly")
    return flask.render_template('vocab.html')


@app.route("/success")
def success():
    return flask.render_template('success.html')

#######################
# Form handler.
# CIS 322 note:
#   You'll need to change this to a
#   a JSON request handler
#######################


@app.route("/_check", methods=["POST"])
def check():
    """
    User has submitted the form with a word ('attempt')
    that should be formed from the jumble and on the
    vocabulary list.  We respond depending on whether
    the word is on the vocab list (therefore correctly spelled),
    made only from the jumble letters, and not a word they
    already found.
    """
    app.logger.debug("Entering check")

    # The data we need, from form and from cookie
    text = flask.request.form['text']
    jumble = flask.session["jumble"]
    matches = flask.session["matches"]
    print("matches I got from the client is:")
    print(matches)
    
    # Is the attempted word good?
    in_jumble = LetterBag(jumble).contains(text)
    matched = WORDS.has(text)

    # Which of the list of vocab are ruled out? Add boolean list to rslt to be returned:
    word_is_valid = []
    for word in WORDS.as_list():
        word_is_valid.append(LetterBag(word).contains(text))
        print(word + " is valid: :" + str(LetterBag(word).contains(text)))
    rslt = { "wordisvalid": word_is_valid }

    # Respond appropriately
    if matched and in_jumble and not (text in matches):
        # Cool, they found a new word
        matches.append(text)
        flask.session["matches"] = matches
        print("matches I'm sending to the client is:")
        print(flask.session["matches"])
        assert flask.session["matches"] != None

        if len(matches) >= flask.session["target_count"]:
            # Solved: indicate to client to redirect. Unable to redirect from server
            # when using ajax. See: https://stackoverflow.com/questions/25561668/force-redirect-page-on-ajax-call
            rslt.update({ "status": "success", "redirect": flask.url_for("success")})
        else:
            # Match found but all matches found
            rslt.update({ "status": "new match" })
    
    elif text in matches:
        rslt.update({ "status": "old match" })
    elif not in_jumble:
        rslt.update({ "status": "invalid" })
    
    else:
        # No match found but letters still in jumble
        pass

    return flask.jsonify(result=rslt)


###############
# AJAX request handlers
#   These return JSON, rather than rendering pages.
###############


@app.route("/_example")
def example():
    """
    Example ajax request handler
    """
    app.logger.debug("Got a JSON request")
    rslt = {"key": "value"}
    return jsonify(result=rslt)


#################
# Functions used within the templates
#################


@app.template_filter('filt')
def format_filt(something):
    """
    Example of a filter that can be used within
    the Jinja2 code
    """
    return "Not what you asked for"


###################
#   Error handlers
###################


@app.errorhandler(404)
def error_404(e):
    app.logger.warning("++ 404 error: {}".format(e))
    return flask.render_template('404.html'), 404


@app.errorhandler(500)
def error_500(e):
    app.logger.warning("++ 500 error: {}".format(e))
    assert not True  # I want to invoke the debugger
    return flask.render_template('500.html'), 500


@app.errorhandler(403)
def error_403(e):
    app.logger.warning("++ 403 error: {}".format(e))
    return flask.render_template('403.html'), 403


####

if __name__ == "__main__":
    if CONFIG.DEBUG:
        app.debug = True
        app.logger.setLevel(logging.DEBUG)
        app.logger.info(
            "Opening for global access on port {}".format(CONFIG.PORT))
        app.run(port=CONFIG.PORT, host="0.0.0.0")
