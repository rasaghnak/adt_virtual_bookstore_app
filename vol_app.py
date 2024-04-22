from urllib.parse import urlparse, urljoin
from flask import Flask, abort, render_template, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
import os

bcrypt = Bcrypt()

basedir = os.path.abspath(os.path.dirname(__file__))
secret_key = os.urandom(24)
print(secret_key)

# Create Flask app instance
vol_app = Flask(__name__)
vol_app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///' + os.path.join(basedir, 'vol_app.db')
vol_app.config['SECRET_KEY'] = secret_key

db = SQLAlchemy(vol_app)
ma = Marshmallow(vol_app)
login_manager = LoginManager(vol_app)
login_manager.login_view = 'login'


@vol_app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            next_page = request.args.get('next')  # 'next' can be used for redirection after login
            if not is_safe_url(next_page):
                return abort(400)  # Prevent redirect to malicious URLs
            return redirect(next_page or url_for('admin_home' if user.is_admin else 'user_page'))
        return 'Invalid username or password'
    return render_template('login.html')

def is_safe_url(target):
    """Checks if the redirect target is safe."""
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc


@vol_app.route('/add_user', methods=['POST'])
def api_add_user():
    username = request.json.get('username')
    password = request.json.get('password')
    is_admin = request.json.get('is_admin', False)
    add_user(username, password, is_admin)
    return jsonify({"message": "User added"}), 201

# Define Models
class User(UserMixin,db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)


# Database management functions
def add_user(username, password, is_admin=False):
    user = User(username=username)
    user.set_password(password)
    user.is_admin = is_admin
    db.session.add(user)
    db.session.commit()

def authenticate_user(username, password):
    user = User.query.filter_by(username=username).first()
    if user and user.check_password(password):
        return True
    return False


# Declare Book model
class Book(db.Model):
    __tablename__ = 'books'
    id = db.Column(db.Integer, primary_key=True)
    publishing_year = db.Column(db.Integer, nullable=False)
    title = db.Column(db.String(255), nullable=False)  # 'Book Name' in CSV, 'title' in model
    author = db.Column(db.String(100), nullable=False)
    language_code = db.Column(db.String(10), nullable=True)  # Assuming this can be null
    author_rating = db.Column(db.String(50), nullable=True)  # Assuming this can be null
    book_average_rating = db.Column(db.Float, nullable=True)  # Assuming this can be null
    book_ratings_count = db.Column(db.Integer, nullable=True)  # Assuming this can be null
    genre = db.Column(db.String(50), nullable=False)
    gross_sales = db.Column(db.Float, nullable=True)  # Assuming this can be null
    publisher_revenue = db.Column(db.Float, nullable=True)  # Assuming this can be null
    sale_price = db.Column(db.Float, nullable=True)  # Assuming this can be null
    sales_rank = db.Column(db.Integer, nullable=True)  # Assuming this can be null
    publisher = db.Column(db.String(100), nullable=True)  # Assuming this can be null
    units_sold = db.Column(db.Integer, nullable=True)  # Assuming this can be null

    def __init__(self, publishing_year, title, author, language_code, author_rating, 
                 book_average_rating, book_ratings_count, genre, gross_sales, 
                 publisher_revenue, sale_price, sales_rank, publisher, units_sold):
        self.publishing_year = publishing_year
        self.title = title
        self.author = author
        self.language_code = language_code
        self.author_rating = author_rating
        self.book_average_rating = book_average_rating
        self.book_ratings_count = book_ratings_count
        self.genre = genre
        self.gross_sales = gross_sales
        self.publisher_revenue = publisher_revenue
        self.sale_price = sale_price
        self.sales_rank = sales_rank
        self.publisher = publisher
        self.units_sold = units_sold

    def __repr__(self):
        return f'<Book {self.title}>'

# Schema for Books
class BookSchema(ma.Schema):
    class Meta:
        fields = ('id', 'publishing_year', 'title', 'author', 'language_code', 
                  'author_rating', 'book_average_rating', 'book_ratings_count', 
                  'genre', 'gross_sales', 'publisher_revenue', 'sale_price', 
                  'sales_rank', 'publisher', 'units_sold')


book_schema = BookSchema()
books_schema = BookSchema(many=True)

# Create tables/db file
with vol_app.app_context():
    db.create_all()

# Routes for Bookstore Management

@vol_app.route('/', methods=['GET'])
def home():
    return render_template('home.html')

@vol_app.route('/books', methods=['POST'])
def add_book():
    title = request.json['title']
    author = request.json['author']
    genre = request.json['genre']
    new_book = Book(title, author, genre)
    
    db.session.add(new_book)
    db.session.commit()

    return book_schema.jsonify(new_book)

@vol_app.route('/books', methods=['GET'])
def get_books():
    all_books = Book.query.all()
    result = books_schema.dump(all_books)
    return jsonify(result)

@vol_app.route('/books/<book_id>', methods=['PUT'])
def update_book(book_id):
    book = Book.query.get(book_id)
    title = request.json['title']
    author = request.json['author']
    genre = request.json['genre']

    book.title = title
    book.author = author
    book.genre = genre

    db.session.commit()
    return book_schema.jsonify(book)

@vol_app.route('/books/<book_id>', methods=['DELETE'])
def delete_book(book_id):
    book = Book.query.get(book_id)
    db.session.delete(book)
    db.session.commit()

    return book_schema.jsonify(book)


# 'id', 'publishing_year', 'title', 'author', 'language_code', 
# 'author_rating', 'book_average_rating', 'book_ratings_count', 
#                   'genre', 'gross_sales', 'publisher_revenue', 'sale_price', 
#                   'sales_rank', 'publisher', 'units_sold'

from flask import request, jsonify, redirect, url_for

@vol_app.route('/admin/db-management', methods=['GET', 'POST', 'PUT', 'DELETE'])
def admin_db_management():
    # Authentication should ideally be handled by @login_required and check for is_admin

    if request.method == 'GET':
        book_id = request.args.get('bookId')
        if book_id:
            # Fetching a single book's details
            book = Book.query.get(book_id)
            if book:
                book_data = book_schema.dump(book)
                return jsonify(book_data)
            else:
                return jsonify({"message": "Book not found"}), 404
        else:
            # Return all books
            books = Book.query.all()
            books_data = books_schema.dump(books)
            return jsonify(books_data)

    if request.method == 'POST':
        data = request.form if request.form else request.json
        try:
            new_book = Book(
                publishing_year=int(data['publishing_year']),
                title=data['title'],
                author=data['author'],
                language_code=data.get('language_code', None),
                author_rating=data.get('author_rating', None),
                book_average_rating=float(data.get('book_average_rating', 0)),
                book_ratings_count=int(data.get('book_ratings_count', 0)),
                genre=data['genre'],
                gross_sales=float(data.get('gross_sales', 0)),
                publisher_revenue=float(data.get('publisher_revenue', 0)),
                sale_price=float(data.get('sale_price', 0)),
                sales_rank=int(data.get('sales_rank', 0)),
                publisher=data.get('publisher', None),
                units_sold=int(data.get('units_sold', 0))
            )
            db.session.add(new_book)
            db.session.commit()
            return jsonify({"message": "New book added"}), 201
        except Exception as e:
            return jsonify({"message": str(e)}), 400

    elif request.method == 'PUT':
        data = request.json
        book = Book.query.get(data['id'])
        if not book:
            return jsonify({"message": "Book not found"}), 404
        try:
            for key, value in data.items():
                setattr(book, key, value)
            db.session.commit()
            return jsonify({"message": "Book updated"}), 200
        except Exception as e:
            return jsonify({"message": str(e)}), 400

    elif request.method == 'DELETE':
        book_id = request.args.get('id')  # use query parameter for deletion
        book = Book.query.get(book_id)
        if not book:
            return jsonify({"message": "Book not found"}), 404
        db.session.delete(book)
        db.session.commit()
        return jsonify({"message": "Book deleted"}), 200

def authenticate_admin(token):
    # Check if the user is an admin
    user = User.query.filter_by(auth_token=token).first()
    if user and user.is_admin:
        return user
    return None



## USER PAGES

# Flask-Login loader
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes

@vol_app.route('/admin_home')
@login_required
def admin_home():
    if not current_user.is_admin:
        return 'Access Denied', 403
    return render_template('admin_home.html')


@vol_app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        is_admin = request.form.get('is_admin', 'false').lower() in ['true', '1', 't']
        
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            return 'Username already exists', 400
        
        new_user = User(username=username, is_admin=is_admin)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    
    return render_template('register.html')


@vol_app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('/login'))


@vol_app.route('/user_page')
@login_required
def user_page():
    books = Book.query.all()
    if current_user.is_admin:
        result = books_schema.dump(books)
    else:
        result = [{'title': book.title, 'author': book.author, 'genre': book.genre} for book in books]

    return render_template('user_page.html', books=result)



@vol_app.route('/admin/books', methods=['GET', 'POST'])
@login_required
def admin_books():
    if not current_user.is_admin:
        return jsonify({"message": "Access Denied"}), 403

    if request.method == 'POST':
        # Assuming the addition of books is done here, redirect to avoid form resubmission issues
        return redirect(url_for('admin_books'))

    books = Book.query.all()
    return render_template('admin_books.html', books=books)


# Marshmallow schema
# Schema for Books
class BookSchema(ma.Schema):
    class Meta:
        fields = ('book_id', 'title', 'author', 'genre')

book_schema = BookSchema()
books_schema = BookSchema(many=True)

if __name__ == '__main__':
    vol_app.run(debug=True)
