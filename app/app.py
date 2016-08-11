from flask import Flask, Response, request, redirect, abort, session, url_for
from threading import Lock
import datetime, socket, urllib, os, time, json, bcrypt, cgi

# Load pages:
f = open('profile_template.html', 'r')
profile_template = f.read().decode('UTF-8')
f.close()

f = open('project_template.html', 'r')
project_template = f.read().decode('UTF-8')
f.close()

f = open('signup.html', 'r')
signup_html = f.read().decode('UTF-8')
f.close()

f = open('login.html', 'r')
login_html = f.read().decode('UTF-8')
f.close()

# Incase we switch to a database.
def putdata(k, v):
    with open(k.replace('.', '/').replace(' ', '-'), 'w') as f:
        f.write(v.encode('UTF-8'))

def getdata(k):
    try:
        f = open(k.replace('.', '/').replace(' ', '-'), 'r')
        c = f.read().decode('UTF-8')
        f.close()
        return c
    except:
        return None 

# EMOJIIIIIIIII :) :) :) :) :)
EMOJI = {
    ':)':                   '<img src="http://emojione.com/wp-content/uploads/assets/emojis/1f642.svg" class=emoji>',
    ':(':                   '<img src="http://emojione.com/wp-content/uploads/assets/emojis/2639.svg" class=emoji>',
    ':trump:':              '<img src="//pbs.twimg.com/profile_images/694213196899430400/qm64QeyO.jpg" class=emoji>',
    ':octocat:':            '<img src="/static/octocat.svg" class=emoji>',
    ':pizza:':              '<img src="http://emojione.com/wp-content/uploads/assets/emojis/1f355.svg" class=emoji>',
    ':watch:':              '<img src="http://emojione.com/wp-content/uploads/assets/emojis/231a.svg" class=emoji>',
    ':phone:':              '<img src="http://emojione.com/wp-content/uploads/assets/emojis/1f4f1.svg" class=emoji>',
    ':laptop:':             '<img src="http://emojione.com/wp-content/uploads/assets/emojis/1f4bb.svg" class=emoji>',
    ':PC:':                 '<img src="http://emojione.com/wp-content/uploads/assets/emojis/1f5a5.svg" class=emoji>',
    '(c)':                  '&copy;',
    '(r)':                  '&reg;',
    ':radioactive:':        '<img src="http://emojione.com/wp-content/uploads/assets/emojis/2622.svg" class=emoji>',
    ':blobfish:':           '<img src="/static/blobfish_icon.jpg" class=emoji>',
    '(tm)':                 '&trade;',
    ':keyboard:':           '<img src="http://emojione.com/wp-content/uploads/assets/emojis/2328.svg" class=emoji>',
    ':mouse:':              '<img src="http://emojione.com/wp-content/uploads/assets/emojis/1f5b1.svg" class=emoji>',
    ':plug:':               '<img src="http://emojione.com/wp-content/uploads/assets/emojis/1f50c.svg" class=emoji>',
    ':camera:':             '<img src="http://emojione.com/wp-content/uploads/assets/emojis/1f4f7.svg" class=emoji>',
    ':money:':              '<img src="http://emojione.com/wp-content/uploads/assets/emojis/1f4b0.svg" class=emoji>',
    ':$$$:':                '<img src="http://emojione.com/wp-content/uploads/assets/emojis/1f911.svg" class=emoji>',
    ':error:':              '<img src="" class=emoji>',
}

# Not really markdown, but...
def md2html(md):
    html = ''
    i = 0
    while i < len(md):
        if md[i] == '>':
            html += '&gt;'
        elif md[i] == '<':
            html += '&lt;'
        elif md[i] == '&':
            html += '&amp;'
        elif md[i] == '\n':
            html += '<br>'
        else:
            f = False
            for emoji in EMOJI.keys():
                if md[i:].startswith(emoji):
                    html += EMOJI[emoji]
                    i += len(emoji)
                    f = True
                    break
            if f: continue
            html += md[i]
        i+=1
    return html

# Create app.
app = Flask(__name__)

# Super awesome key:
app.secret_key = ':secret::secret::secret::secret:'

# No index yet:
@app.route('/')
def index():
    return 'hello'

# Sets the variable un to the username of the users session:
@app.route('/me.js')
def me_js():
    return Response('var un = %s;' % repr(session['un'])[1:], mimetype='text/javascript')   # This is incredibly hacky sanatization.
                                                                                            # But this is a hackathon, after all.
# Sigup form:
@app.route('/signup', methods=('GET', 'POST'))
def signup():
    err = ''
    if request.method == 'POST':                                                # POST request means data has been submitted.
        un = request.form.get('un')
        pw = request.form.get('pw')
        em = request.form.get('em')
        if un and pw and em:                                                    # Ensure all fields filled out.
            if '>' in un or '<' in un or '&' in un or '=' in un or '?' in un:   # NO XSS! BAD!
                err = 'Usernames may not contain <b>&lt;</b>, <b>&gt;</b>, <b>&amp;</b>, <b>=</b> or <b>?</b> characters.'
            else:
                data = {                                                        
                    'name':         un,
                    'image':        '/static/default-avatar.png',
                    'desc':         'Hello.',
                    'project arr':  [],
                    'hashword':     bcrypt.hashpw(pw.encode('UTF-8'), bcrypt.gensalt())
                }
                putdata('profiles.' + un, json.dumps(data))
                session['un'] = un
                return redirect(url_for('profile', p=un))

    return signup_html.replace('<>', err)                                       # Shows error message.

# Login form:
@app.route('/login', methods=('GET', 'POST'))
def login():
    err = ''
    if request.method == 'POST':                                                # POST request means data has been submitted.
        un = request.form.get('un')
        pw = request.form.get('pw')
        if un and pw:                                                           # Ensure data submitted.
            profile_str = getdata('profiles.' + un)                             # Get profile.
            if profile_str:                                                     # Ensure user exists.
                profile = json.loads(profile_str)
                if bcrypt.hashpw(pw.encode('UTF-8'), profile['hashword'].encode('UTF-8')) == profile['hashword']:       # Authentication
                    session['un'] = un
                    return redirect(url_for('profile', p=un))                   # Send to own profile.
                else:
                    err = 'Your password is incorrect.'
            else:
                err = 'User %s does not exist.' % cgi.escape(un)
            
    return login_html.replace('<>', err)

# Shows a profile's page:
@app.route('/profile')
def profile():
    name = request.args.get('p')
    if name:                                                                    # If no profile specified, redirect to index.
        profile_str = getdata('profiles.' + name)                               # Get profile.
        if not profile_str:
            abort(404)                                                          # 404 if profile doesn't exist.
        
        profile = json.loads(profile_str)
        profile['desc esc'] = md2html(profile['desc'])
        profile['desc rep'] = repr(profile['desc'])[1:]
        profile['projects'] = ('\n'+(' '*16)).join(['<div><img src="{0[logo]}">{0[name]}</div>'                 # Horray for
                                .format(json.loads(getdata('projects.'+i))) for i in profile['project arr']])   # Inline for
                                                                                                                # LOOPS!
        page = profile_template.format(profile)
        
        return page
    else:
        return redirect(url_for('index'))

# Update a users profile:
@app.route('/update_profile/desc', methods=('POST',))
def update_profile_desc():
    p = json.loads(getdata('profiles.' + session['un']))                        # Get
    p['desc'] = request.get_json(force=True)['text']                            # Set
    putdata('profiles.' + session['un'], json.dumps(p))                         # Put
    return ''

# Shows a project's page:
@app.route('/project')
def project():
    name = request.args.get('p')
    if name:                                                                    # This is basically the same as profiles.
        project_str = getdata('projects.' + name)
        if not project_str:
            abort(404)
        
        project = json.loads(project_str)
        project['desc esc'] = md2html(project['desc'])
        page = project_template.format(project)
        
        return page
    else:
        return redirect(url_for('index'))

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)                            # Get the external IP
s.connect(("8.8.8.8",80))                                                       # By connecting to GOOGLE
hostip=s.getsockname()[0]                                                       # And using getsockname.
s.close()                                                                       # Best code EVA!

app.run(port=64646, host=hostip, debug=True, ssl_context=('domain.crt','domain.key'))   # Run the app!
