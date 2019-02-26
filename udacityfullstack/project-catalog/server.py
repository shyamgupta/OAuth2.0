from flask import Flask, render_template,request,redirect, flash,jsonify,make_response
import httplib2,json,requests
from flask import session as login_session
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import random, string
app = Flask(__name__)
app.secret_key = "This_is_a-Secret_Key"
# Connect to catalog database
from db_setup import Base, Category, Item, User
# Connect to the database
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.pool import StaticPool
engine = create_engine('sqlite:///catalog.db',connect_args={'check_same_thread':False},poolclass=StaticPool)
Base.metadata.bind = engine
DBSession = sessionmaker(bind = engine)
dbsession = DBSession()


# Route: Homepage
@app.route('/')
def index():
    categories = dbsession.query(Category).all()
    items = dbsession.query(Item).all()
    if 'username' in login_session:
        return render_template('index.html',categories=categories,items=items,username=login_session['username'])
    else:
        return render_template('index.html',categories=categories,items=items,username=None)

#Login Page
@app.route('/login')
def login():
    # Anti Forgery State Token
    state = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html',STATE=state)

# Logout
@app.route('/logout')
def logout():
    if login_session.get('access_token') is None:
        response = make_response(json.dumps('User is not logged in.'),401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token='+ login_session['access_token']
    h = httplib2.Http()
    result = h.request(url,'GET')[0]
    print result['status']
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        return redirect('/')

# Google Plus Sign in - Handling response from client
@app.route('/gconnect',methods=['POST'])
def gconnect():
    print 'Executing gconnect'
    with open('client_secrets.json','r') as file:
        CLIENT_ID = json.load(file)['web']['client_id']
    # Verify Anti Forgery State Token received from client
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Store authorization code received from client
    code = request.data
    # Exchange authorization code with Google for a credentials object
    try:
    # Create a Flow object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        # Exchange authorization code for a credentials token
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Verify if access token is valid/working
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s' % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url,'GET')[1])
    # Handle error if access token is not valid
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Verify if access token is for the right user
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
        json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Verify if access token is for the right application
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
        json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response
    # Verify if user is already logged in
    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.'),200)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Store access token for later use
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id
    # Get user details (name and email) from Google API
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)
    data = answer.json()
    login_session['username'] = data['name']
    login_session['email'] = data['email']
    # Check if the user already exists in the database
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id
    # Send Response back to the client
    output = ''
    output += '<h1>Welcome '
    output += login_session['username']
    output += '</h1>'
    return output


# Route: List all items within a category
@app.route('/catalog/<string:category>/items/')
def listitems(category):
    itemcount=0
    cat = dbsession.query(Category).filter_by(name=category).first()
    print cat.name
    items = dbsession.query(Item).filter_by(category=cat).all()
    if items:
        for item in items:
            itemcount +=1
    else:
        itemcount=0
    categories = dbsession.query(Category).all()
    if 'username' in login_session:
        return render_template('listitems.html',category=cat,categories=categories,items=items,itemcount=itemcount,username=login_session['username'])
    else:
        return render_template('protectedlistitems.html',category=cat,categories=categories,items=items,itemcount=itemcount,username=None)

# Route: List information about an item
@app.route('/catalog/<string:category>/<string:item>/')
def iteminfo(category,item):
    category = dbsession.query(Category).filter_by(name=category).one()
    item = dbsession.query(Item).filter_by(name=item).one()
    categories = dbsession.query(Category).all()
    if 'username' in login_session:
        return render_template('iteminfo.html',categories=categories,item=item,username=login_session['username'])
    else:
        return render_template('protectediteminfo.html',categories=categories,item=item,username=None)

# Create an item
@app.route('/catalog/createItem',methods=['POST','GET'])
def createItem():
    categories = dbsession.query(Category).all()
    if request.method == 'GET':
        categories = dbsession.query(Category).all()
        if 'username' in login_session:
            return render_template('createitem.html',categories=categories,username=login_session['username'])
        else:
            return redirect('/login')
    if request.method=='POST':
        category = dbsession.query(Category).filter_by(name=request.form['category']).one()
        newItem = Item(name=request.form['name'],description=request.form['description'],category_id=category.id,user_id=login_session['user_id'])
        dbsession.add(newItem)
        dbsession.commit()
        flash('Item added successfully')
        return redirect('/')

# Route to edit an item's informatiom
@app.route('/catalog/<string:item>/edit/',methods=['GET','POST'])
def edititem(item):
    if request.method=='GET':
        item = dbsession.query(Item).filter_by(name=item).one()
        categories = dbsession.query(Category).all()
        if 'username' in login_session:
            if login_session['user_id'] == item.user_id:
                return render_template('edititem.html',item=item,categories=categories,username=login_session['username'])
            else:
                flash("You cannot edit items created by others.")
                return redirect('/')
        else:
            return redirect('/login')
    if request.method=='POST':
        item = dbsession.query(Item).filter_by(name=item).one()
        category = dbsession.query(Category).filter_by(name=request.form['category']).one()
        item.name = request.form['title']
        item.description = request.form['description']
        item.category_id = category.id
        dbsession.add(item)
        dbsession.commit()
        flash('Item was successfully updated.')
        return redirect('/')

# Delete Item
@app.route('/catalog/<string:item>/delete/',methods=['POST','GET'])
def deleteitem(item):
    if request.method=='POST':
        item = dbsession.query(Item).filter_by(name=item).one()
        dbsession.delete(item)
        dbsession.commit()
        return redirect('/')
    if request.method=='GET':
        categories = dbsession.query(Category).all()
        item = dbsession.query(Item).filter_by(name=item).one()
        if 'username' in login_session:
            if login_session['user_id'] == item.user_id:
                return render_template('deleteitem.html',categories=categories,item=item,username=login_session['username'])
            else:
                flash("You cannot delete items created by others.")
                return redirect('/')
        else:
            return redirect('/login')

# JSON endpoint
@app.route('/catalog.json')
def catalogJSON():
    categories = dbsession.query(Category).all()
    items = dbsession.query(Item).all()
    categories_array = []
    for category in categories:
        categories_array.append({'id':category.id,'name':category.name,'items':[]})
    for category in categories_array:
        items = dbsession.query(Item).filter_by(category_id=category['id']).all()
        for item in items:
            category['items'].append({'item_id':item.id,'name':item.name,'description':item.description,'category':item.category.name})
    return jsonify(categories_array)

# Create new user
def createUser(login_session):
    newUser = User(name=login_session['username'],email=login_session['email'])
    dbsession.add(newUser)
    dbsession.commit()
    user = dbsession.query(User).filter_by(email=login_session['email']).one()
    return user

# Get user information
def gerUserInfo(user_id):
    user = dbsession.query(User).filter_by(id=user_id).one()
    return user

# Get User ID
def getUserID(email):
    try:
        user = dbsession.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0',port=5000)