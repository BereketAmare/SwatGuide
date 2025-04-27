from flask import Flask, render_template, request, redirect, url_for, make_response, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from models import db, Guide, Comment, Reply, User, Report
from datetime import datetime

# Initialize Flask application

app = Flask(__name__)


# pull DATABASE_URL that Render injects
db_uri = os.environ.get("DATABASE_URL")
if db_uri is None:
    raise RuntimeError("DATABASE_URL is not set — check Render env-vars")

# make it SQLAlchemy-friendly
db_uri = db_uri.replace("postgres://", "postgresql://")

# configure Flask-SQLAlchemy
app.config["SQLALCHEMY_DATABASE_URI"] = db_uri
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

# Initialize db to be used with current Flask app
with app.app_context():
    db.init_app(app)
    db.create_all()

# HOME 
@app.route("/")
def home():
    """Render the home page with guides and user information."""
    # Clear any expired sessions
    if 'user_id' not in session:
        session.clear()
        return redirect(url_for('login'))
    
    try:
        user = User.query.get(session['user_id'])
        if not user:
            session.clear()
            return redirect(url_for('login'))
            
        guides = Guide.query.order_by(Guide.num_likes.desc()).all()
        guide_data = []
        for guide in guides:
            guide_data.append({
                'id': guide.id,
                'user_id': guide.user_id,
                'content': guide.content,
                'created_at': guide.created_at,
                'num_likes': guide.num_likes,
                'comments': guide.comments,
                'title': guide.title,
                'user': {
                    'username': guide.user.username
                }
            })
        return render_template('home.html', guides=guide_data, user=user)
    except Exception as e:
        session.clear()
        return redirect(url_for('login'))

def generate_password(a):
    # return generate_password_hash(password, method='sha256')
    return a

# LOGIN
@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('home'))
        
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        
        if not user:
            error = "No account found. Please register first."
            return render_template('error.html', error=error)
        elif not check_password(user.password, password):
            error = "Incorrect password."
            return render_template('error.html', error=error)
        
        session['user_id'] = user.id
        session['username'] = user.username
        session.permanent = True
        return redirect(url_for('home'))
        
    return render_template('login.html')

def check_password(a,b):
    if a == b:
        return True
    else: 
        return False

# LOGOUT
@app.route('/logout')
def logout():
    if 'user_id' in session:
        session.pop('user_id', None)  # Remove the user ID from the session
    return redirect(url_for('login'))  # Redirect to the login page

# REGISTER
@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_id' not in session:
        if request.method == 'POST':  # If the form is submitted
            username = request.form['username']  # Get the username from the form
            
            # Check if username already exists
            existing_user = User.query.filter_by(username=username).first()
            if existing_user:
                error = "An account with this username already exists. Please login instead."
                return render_template('error.html', error=error)
                
            password = request.form['password']  # Get the password from the form
            description = None
            new_password = generate_password(password) 
            new_user = User(username=username, password=new_password, description=description)  # Create a new user object
            db.session.add(new_user)  # Add the new user to the session
            db.session.commit()  # Commit the session to the database
            return redirect(url_for('login'))  # Redirect to the login page
        else:
            return render_template('register.html')  # Render the register template
    else:
        return redirect(url_for('home'))  # Redirect to the login page

# SEARCH RESULTS
@app.route('/search_results', methods=['GET', 'POST'])
def search_results():
    if 'user_id' not in session:
        return redirect(url_for('login'))
        
    user = User.query.get(session['user_id'])
    query = request.args.get('search', '').strip()

    if not query:
        return render_template("search_results.html", results=[], search_query=query, user=user)

    # Perform case-insensitive search on Guide titles and content
    results = Guide.query.filter(
        db.or_(
            Guide.title.ilike(f"%{query}%"),
            Guide.content.ilike(f"%{query}%")
        )
    ).all()

    return render_template("search_results.html", results=results, search_query=query, user=user)

# POST GUIDE
@app.route("/post_guide")
def post_guide():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user = User.query.get(session['user_id'])
    return render_template("post_guide.html", user=user)

# PROFILE
@app.route("/profile")
def profile_page():
    user = User.query.get(session['user_id'])
    user_guides = Guide.query.filter_by(user_id=user.id).all()
    return render_template("profile_page.html", user=user, guides=user_guides)

@app.route("/update_description", methods=['POST'])
def update_description():
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401
        
    user = User.query.get(session['user_id'])
    data = request.get_json()
    description = data.get('description')
    
    if description is not None:
        user.description = description
        db.session.commit()
        return jsonify({'success': True})
    
    return jsonify({'error': 'No description provided'}), 400

# VIEW GUIDE
@app.route('/view_guide/<int:guide_id>', methods=['GET', 'POST'])
def view_guide(guide_id):
    # Get the guide based on its ID
    guide = Guide.query.get_or_404(guide_id)
    
    # If you're passing individual comments to the template
    comments = Comment.query.filter_by(guide_id=guide_id).all()

    user_id = session.get('user_id')
    user = User.query.get(user_id)

    return render_template("view_guide.html", guide=guide, comments=comments, user=user)

# CREATE GUIDE
@app.route('/create_guide', methods=['POST'])
def create_guide():
    if 'user_id' not in session:
        return jsonify({"success": False, "message": "User not logged in"}), 401

    user = User.query.get(session['user_id'])

    # Get the data from the request
    data = request.get_json()

    title = data.get('title')
    content = data.get('content')

    # Make sure there is a title and content
    if not title or not content:
        return jsonify({"success": False, "message": "Missing title or content"}), 400

    # Create the guide
    guide = Guide(title=title, content=content, user_id=user.id)
    db.session.add(guide)
    db.session.commit()

    # Return a response
    return jsonify({
        "success": True,
        "guide": guide.serialize()
    })

# COMMENT
@app.route('/comment/<int:guide_id>', methods=['POST'])
def comment(guide_id):
    guide = Guide.query.get_or_404(guide_id)
    content = request.form.get('content')

    user = User.query.get(session['user_id'])

    if not content:
        return jsonify({"error": "Content is required"}), 400

    if content and user:
        new_comment = Comment(guide_id=guide.id, content=content, user=user)
        db.session.add(new_comment)
        db.session.commit()
        return make_response(jsonify({"success": True, "comment": new_comment.serialize()}), 200)
    
    return jsonify({"success": False, "message": "Missing fields"}), 400

# REPLY
@app.route('/reply/<int:comment_id>', methods=['POST'])
def reply(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    content = request.form.get('content')
    user = User.query.get(session['user_id'])

    if not content:
        return jsonify({"success": False, "message": "Content required"}), 400

    new_reply = Reply(comment_id=comment.id, content=content, user_id=user.id)
    db.session.add(new_reply)
    db.session.commit()

    return jsonify({"success": True, "reply": new_reply.serialize()}), 200

# LIKE
@app.route('/like_guide/<int:guide_id>', methods=['POST'])
def like_guide(guide_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401
        
    user = User.query.get(session['user_id'])
    guide = Guide.query.get_or_404(guide_id)
    
    if user in guide.liked_by:
        guide.liked_by.remove(user)
        guide.num_likes = max(0, guide.num_likes - 1)
        isLiked = False
    else:
        guide.liked_by.append(user)
        guide.num_likes += 1
        isLiked = True
        
    db.session.commit()
    return jsonify({'likes': guide.num_likes, 'isLiked': isLiked})

@app.route('/report_guide/<int:guide_id>', methods=['POST'])
def report_guide(guide_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401
        
    guide = Guide.query.get_or_404(guide_id)
    data = request.get_json()
    report_type = data.get('report_type')
    
    if not report_type:
        return jsonify({'error': 'Report type required'}), 400
        
    new_report = Report(guide_id=guide.id, user_id=session['user_id'], report_type=report_type)
    db.session.add(new_report)
    db.session.commit()
    
    return jsonify({'success': True, 'report_count': len(guide.reports)})

@app.route('/update_guide/<int:guide_id>', methods=['POST'])
def update_guide(guide_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401
        
    guide = Guide.query.get_or_404(guide_id)
    
    # Verify the logged-in user is the guide's author
    if guide.user_id != session['user_id']:
        return jsonify({'error': 'Unauthorized'}), 403
        
    data = request.get_json()
    content = data.get('content')
    
    if content is not None:
        guide.content = content
        db.session.commit()
        return jsonify({'success': True})
    
    return jsonify({'error': 'No content provided'}), 400

if __name__ == '__main__':
    app.run(debug=True)