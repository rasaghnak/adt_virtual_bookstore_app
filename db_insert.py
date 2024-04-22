from vol_app import vol_app, db, Book  # Replace with the actual module name
import pandas as pd

def insert_books_from_csv(csv_path):
    books_df = pd.read_csv(csv_path)

    # Ensuring all necessary columns are present and non-null where required
    required_columns = ['index','Publishing Year','Book Name','Author','language_code','Author_Rating','Book_average_rating','Book_ratings_count','genre','gross sales','publisher revenue','sale price','sales rank','Publisher ','units sold']
    
    # Drop rows where any required columns are NaN (adjust according to your CSV structure)
    books_df = books_df.dropna(subset=required_columns, how='any')

    with vol_app.app_context():
        for index, row in books_df.iterrows():
            # Create a new Book instance for each row in the DataFrame
            new_book = Book(
                publishing_year=int(row['Publishing Year']) if not pd.isna(row['Publishing Year']) else None,
                title=row['Book Name'],
                author=row['Author'],
                language_code=row['language_code'] if 'language_code' in row and not pd.isna(row['language_code']) else None,
                author_rating=row['author_rating'] if 'author_rating' in row and not pd.isna(row['Author_rating']) else None,
                book_average_rating=float(row['Book_average_rating']) if not pd.isna(row['Book_average_rating']) else None,
                book_ratings_count=int(row['Book_ratings_count']) if not pd.isna(row['Book_ratings_count']) else None,
                genre=row['genre'],
                gross_sales=float(row['gross sales']) if not pd.isna(row['gross sales']) else None,
                publisher_revenue=float(row['publisher revenue']) if not pd.isna(row['publisher revenue']) else None,
                sale_price=float(row['sale price']) if not pd.isna(row['sale price']) else None,
                sales_rank=int(row['sales rank']) if not pd.isna(row['sales rank']) else None,
                publisher=row['Publisher'] if 'publisher' in row and not pd.isna(row['Publisher']) else None,
                units_sold=int(row['units sold']) if not pd.isna(row['units sold']) else None,
            )
            # Add the new Book instance to the session
            db.session.add(new_book)
        # Commit the session to insert the records into the database
        db.session.commit()

csv_file_path = "Books_Data_Clean.csv"  # Make sure this is the correct path to your CSV file
insert_books_from_csv(csv_file_path)
