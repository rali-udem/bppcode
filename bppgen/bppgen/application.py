#!/usr/bin/env python
# coding=utf-8
from flask import Flask, request, send_from_directory, url_for
from json import dumps, loads
import bppconf, os
from bppgen.api.profile_api import BPPAPI
import bppgen.letter.letter as letter
from gentext.syntax import print_jsrealb
from gentext.realizer import new_vocab
import sys

ADMISSIBLE_FILETYPES = ['json', 'css', 'js', 'htm', 'html',
                        'map', 'woff', 'svg', 'ttf', 'woff2']
app = Flask(__name__, static_folder='static/')
api = BPPAPI()
DEFAULT_GENERATION_DATA = {"lang" : "en",
                            "formality" : letter.FORMALITY_INFORMAL,
                            "psy" : "D"}


### UTILS ###
def get_best(curr_id, get_fn, query_fn, query):
    res = get_fn(curr_id)
    if not res :
        res = query_fn(query.format(curr_id))
        if res :
            this_id = res[0].id
            res = get_fn(this_id)
            res['id'] = this_id
    if not res :
        res = {}
    try :
        return dumps(res)
    except :
        return res

### THESE ROUTES ARE JUST A WORKAROUND TO AVOID CONFIGURING APACHE. ###
@app.route('/')
def root():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/bootstrap/<subdir>/<filename>.<extension>')
def serve_bootstrap(filename, subdir, extension):
    if extension in ADMISSIBLE_FILETYPES:
        return send_from_directory(app.static_folder + '/bootstrap/' + subdir, filename + '.' + extension)

@app.route('/<filename>.<extension>')
def serve_static(filename, extension):
    if extension in ADMISSIBLE_FILETYPES:
        return send_from_directory(app.static_folder, filename + '.' + extension)


### CALLS TO THE API. ###

@app.route('/api/offer/<string:offer_id>')
def get_offer(offer_id):
    return get_best(offer_id,
                    api.get_offer,
                    api.query_offers,
                    'title:"{0}" OR description:"{0}" OR coname:"{0}"')

@app.route('/api/profile/<string:profile_id>')
def get_profile(profile_id):
    return get_best(profile_id, api.get_profile, api.query_profiles, 'expfunc:"{0}" OR claim:"{0}" OR skillname:"{0}"')
    
@app.route('/letter_only', methods=['POST'])
def generate_letter_pure():
    all_data = loads(request.data)
    generation_data = all_data['other']
    if not generation_data or not generation_data.has_key('lang') :
        generation_data = DEFAULT_GENERATION_DATA
    else :
        generation_data["formality"] = int(generation_data["formality"])
    generated = letter.generate_letter(all_data['offer'], all_data['profile'], generation_data)
    stringed = map(print_jsrealb, generated)
    return dumps(stringed)


@app.route('/letter', methods=['POST'])
def generate_letter():
    all_data = loads(request.data)
    generation_data = all_data['other']
    if not generation_data or not 'lang' in generation_data :
        generation_data = DEFAULT_GENERATION_DATA
    else :
        generation_data["formality"] = int(generation_data["formality"])
    generated = letter.generate_and_realize_letter(all_data['offer'], all_data['profile'], generation_data)
    return generated

if __name__ == '__main__' :
    if len(sys.argv) > 1 and sys.argv[1] == 'prod':
        app.run(host='0.0.0.0', port=80)
    else:
        app.debug = True
        app.run()