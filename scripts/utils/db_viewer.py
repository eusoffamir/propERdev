#!/usr/bin/env python3
"""
Simple Database Viewer CLI Tool
Run this script to easily view your database tables and data
"""

import os
import sys
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.orm import sessionmaker
import pandas as pd
from tabulate import tabulate

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.config import get_config_by_name

def get_database_connection():
    """Get database connection"""
    config = get_config_by_name('development')
    if not config.SQLALCHEMY_DATABASE_URI:
        raise ValueError("Database URL not configured")
    engine = create_engine(config.SQLALCHEMY_DATABASE_URI)
    return engine

def list_tables(engine):
    """List all tables in the database"""
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    
    print("\n" + "="*60)
    print("DATABASE TABLES")
    print("="*60)
    
    for i, table in enumerate(tables, 1):
        # Get row count for each table
        with engine.connect() as conn:
            result = conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
            count = result.scalar()
        
        print(f"{i:2d}. {table:<30} ({count:,} records)")
    
    return tables

def view_table(engine, table_name, limit=50):
    """View data from a specific table"""
    try:
        # Get table structure
        inspector = inspect(engine)
        columns = inspector.get_columns(table_name)
        
        print(f"\n" + "="*80)
        print(f"TABLE: {table_name.upper()}")
        print("="*80)
        
        # Show table structure
        print("\nTABLE STRUCTURE:")
        print("-" * 80)
        structure_data = []
        for col in columns:
            structure_data.append([
                col['name'],
                str(col['type']),
                'Yes' if col['nullable'] else 'No',
                col.get('default', '-')
            ])
        
        print(tabulate(structure_data, 
                      headers=['Column', 'Type', 'Nullable', 'Default'],
                      tablefmt='grid'))
        
        # Get data
        query = text(f"SELECT * FROM {table_name} LIMIT {limit}")
        with engine.connect() as conn:
            result = conn.execute(query)
            rows = result.fetchall()
            columns = result.keys()
        
        if not rows:
            print(f"\nNo data found in table '{table_name}'")
            return
        
        # Convert to DataFrame for better display
        df = pd.DataFrame(rows, columns=columns)
        
        print(f"\nTABLE DATA (showing first {len(rows)} records):")
        print("-" * 80)
        
        # Display data in chunks if too wide
        if len(columns) > 10:
            print("Table has many columns. Showing first 10 columns...")
            df_display = df.iloc[:, :10]
        else:
            df_display = df
        
        print(tabulate(df_display, headers='keys', tablefmt='grid', showindex=False))
        
        # Show total count
        with engine.connect() as conn:
            result = conn.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
            total_count = result.scalar()
        
        print(f"\nTotal records in {table_name}: {total_count:,}")
        
    except Exception as e:
        print(f"Error viewing table '{table_name}': {str(e)}")

def export_table(engine, table_name, filename=None):
    """Export table to CSV"""
    try:
        query = text(f"SELECT * FROM {table_name}")
        with engine.connect() as conn:
            result = conn.execute(query)
            rows = result.fetchall()
            columns = result.keys()
        
        df = pd.DataFrame(rows, columns=columns)
        
        if not filename:
            filename = f"{table_name}_export.csv"
        
        df.to_csv(filename, index=False)
        print(f"\nTable '{table_name}' exported to '{filename}'")
        print(f"Records exported: {len(df):,}")
        
    except Exception as e:
        print(f"Error exporting table '{table_name}': {str(e)}")

def main():
    """Main function"""
    print("🚀 propER Database Viewer")
    print("=" * 40)
    
    try:
        engine = get_database_connection()
        print("✅ Connected to database successfully!")
        
        while True:
            tables = list_tables(engine)
            
            print("\n" + "="*60)
            print("OPTIONS:")
            print("="*60)
            print("1. View table data")
            print("2. Export table to CSV")
            print("3. List tables again")
            print("4. Exit")
            
            choice = input("\nEnter your choice (1-4): ").strip()
            
            if choice == '1':
                table_num = input("Enter table number to view: ").strip()
                try:
                    table_num = int(table_num) - 1
                    if 0 <= table_num < len(tables):
                        limit = input("Enter number of records to show (default 50): ").strip()
                        limit = int(limit) if limit.isdigit() else 50
                        view_table(engine, tables[table_num], limit)
                    else:
                        print("Invalid table number!")
                except ValueError:
                    print("Please enter a valid number!")
                    
            elif choice == '2':
                table_num = input("Enter table number to export: ").strip()
                try:
                    table_num = int(table_num) - 1
                    if 0 <= table_num < len(tables):
                        filename = input("Enter filename (or press Enter for default): ").strip()
                        if not filename:
                            filename = None
                        export_table(engine, tables[table_num], filename)
                    else:
                        print("Invalid table number!")
                except ValueError:
                    print("Please enter a valid number!")
                    
            elif choice == '3':
                continue
                
            elif choice == '4':
                print("\n👋 Goodbye!")
                break
                
            else:
                print("Invalid choice! Please enter 1-4.")
            
            input("\nPress Enter to continue...")
    
    except Exception as e:
        print(f"❌ Error connecting to database: {str(e)}")
        print("Make sure your database is running and the connection string is correct.")

if __name__ == "__main__":
    main() 