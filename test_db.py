from sqlalchemy import create_engine, MetaData, Table
import os


def reflect_table_schema():
    
    basedir = os.path.abspath(os.path.dirname(__file__))
    engine = create_engine('sqlite:///' + os.path.join(basedir, 'vol_app.db'))  # Use your actual database connection string
    metadata = MetaData()
    metadata.reflect(bind=engine)
    table = Table('books', metadata, autoload=True, autoload_with=engine)
    for column in table.columns:
        print(f"Column: {column.name} | Type: {column.type}")

reflect_table_schema()
