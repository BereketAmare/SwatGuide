import os
from flask import Flask, render_template, request, redirect, url_for, make_response, jsonify, session, flash
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from models import db, Guide, Comment, Reply, User, Report, Notification
from datetime import datetime
from functools import wraps

# Initialize Flask application

app = Flask(__name__)

app.secret_key = os.environ.get("SECRET_KEY", "dev-please-change")

db_uri = os.environ["DATABASE_URL"].replace("postgres://", "postgresql://")
app.config["SQLALCHEMY_DATABASE_URI"] = db_uri
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

from models import Guide, Comment, Reply, User, Report, Notification

with app.app_context():
    db.create_all()

# Admin Required Decorator
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login'))
        user = User.query.get(session['user_id'])
        if not user or not user.is_admin:
            flash('You do not have permission to access this page.', 'danger')
            return redirect(url_for('home'))
        return f(*args, **kwargs)
    return decorated_function

# HOME 
@app.route("/")
def home():
    """Render the home page with guides and user information."""
    if 'user_id' not in session:
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
                    'username': guide.user.username if guide.user else 'Unknown User'
                }
            })
        return render_template('home.html', guides=guide_data, user=user)
    except Exception as e:
        app.logger.error(f"Error in home route: {str(e)}") # Log the specific error
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
@app.route("/profile/<int:user_id>")
@app.route("/profile")
def profile_page(user_id=None):
    if user_id is None:
        user_id = session.get('user_id')

    profile_user = User.query.get_or_404(user_id)
    logged_in_user = User.query.get(session.get('user_id'))
    user_guides = Guide.query.filter_by(user_id=profile_user.id).all()

    return render_template("profile_page.html",
                           profile_user=profile_user,
                           user=logged_in_user,
                           guides=user_guides,
                           is_own_profile=profile_user.id == session.get('user_id'))

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
        
        # Create notification for guide owner
        if guide.user_id != user.id: # Don't notify if user comments on their own guide
            notification = Notification(
                user_id=guide.user_id,
                content=f"{user.username} commented on your guide: \"{guide.title}\"",
                type='comment',
                link=url_for('view_guide', guide_id=guide.id, _external=True) # _external=True for full URLs if needed
            )
            db.session.add(notification)
        
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
    
    isLiked = False # Initialize isLiked
    if user in guide.liked_by:
        guide.liked_by.remove(user)
        guide.num_likes = max(0, guide.num_likes - 1)
        isLiked = False
    else:
        guide.liked_by.append(user)
        guide.num_likes += 1
        isLiked = True
        
        # Create notification for guide owner
        if guide.user_id != user.id: # Don't notify if user likes their own guide
            notification = Notification(
                user_id=guide.user_id,
                content=f"{user.username} liked your guide: \"{guide.title}\"",
                type='like',
                link=url_for('view_guide', guide_id=guide.id, _external=True) # _external=True for full URLs
            )
            db.session.add(notification)
        
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

@app.route('/notifications')
def notifications():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user = User.query.get(session['user_id'])
    if not user: # Good practice to check if user exists
        session.clear()
        return redirect(url_for('login'))
    
    # Assuming 'notifications_received' is the backref from the Notification model to User
    user_notifications = Notification.query.filter_by(user_id=user.id).order_by(Notification.created_at.desc()).all()
    return render_template('notifications.html', notifications=user_notifications, user=user)

@app.route('/mark_notification_read/<int:notification_id>')
def mark_notification_read(notification_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401 # Return JSON for fetch requests if appropriate
        
    notification = Notification.query.get_or_404(notification_id)
    
    # Ensure the notification belongs to the logged-in user
    if notification.user_id != session['user_id']:
        return jsonify({'error': 'Unauthorized'}), 403

    notification.is_read = True
    db.session.commit()
    # Redirect to the link associated with the notification
    # Or return a success response if it's an AJAX call
    return redirect(notification.link if notification.link else url_for('notifications'))

@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    guides = Guide.query.order_by(Guide.created_at.desc()).all()
    # For a more complete dashboard, you might fetch comments and reports separately
    # or rely on relationships when displaying details. For simplicity here, we fetch all.
    # comments = Comment.query.order_by(Comment.created_at.desc()).all()
    # reports = Report.query.order_by(Report.created_at.desc()).all()
    return render_template('admin_dashboard.html', guides=guides, user=User.query.get(session['user_id']))

@app.route('/admin/delete_guide/<int:guide_id>', methods=['POST'])
@admin_required
def admin_delete_guide(guide_id):
    guide = Guide.query.get_or_404(guide_id)
    try:
        # Need to delete associated comments, replies, reports, and likes first 
        # or set up cascade delete in your SQLAlchemy models if not already done.
        
        # Example: Delete comments associated with the guide
        Comment.query.filter_by(guide_id=guide.id).delete()
        # Example: Delete reports associated with the guide
        Report.query.filter_by(guide_id=guide.id).delete()
        # (Add similar for replies and handle likes table if you have a direct association table)

        db.session.delete(guide)
        db.session.commit()
        flash(f'Guide "{guide.title}" has been deleted.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting guide: {str(e)}', 'danger')
    return redirect(url_for('admin_dashboard'))

if __name__ == '__main__':
    app.run(debug=True)