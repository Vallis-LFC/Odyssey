from database import engine, Base
import models  


def main():
    print("Creating tables (if they don't already exist)...")
    Base.metadata.create_all(bind=engine)
    print("Tables created:")
    for i in Base.metadata.sorted_tables: #i is the table
        print(f"  - {i.name}")


if __name__ == "__main__":
    main()