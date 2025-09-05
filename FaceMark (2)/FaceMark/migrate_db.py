#!/usr/bin/env python3
"""
Database migration script to add new columns for email notifications and social login
"""

import sqlite3
import os

def migrate_database():
    """Add new columns to existing database"""
    db_path = 'instance/attendance.db'
    
    if not os.path.exists(db_path):
        print("Database doesn't exist yet. It will be created with the new schema.")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Add email column to users table
        try:
            cursor.execute("ALTER TABLE users ADD COLUMN email TEXT")
            print("Added email column to users table")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e):
                print("Email column already exists in users table")
            else:
                raise
        
        # Add provider column to users table
        try:
            cursor.execute("ALTER TABLE users ADD COLUMN provider TEXT DEFAULT 'local'")
            print("Added provider column to users table")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e):
                print("Provider column already exists in users table")
            else:
                raise
        
        # Add provider_id column to users table
        try:
            cursor.execute("ALTER TABLE users ADD COLUMN provider_id TEXT")
            print("Added provider_id column to users table")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e):
                print("Provider_id column already exists in users table")
            else:
                raise
        
        # Add user_id column to attendance table
        try:
            cursor.execute("ALTER TABLE attendance ADD COLUMN user_id TEXT")
            print("Added user_id column to attendance table")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e):
                print("User_id column already exists in attendance table")
            else:
                raise
        
        # Add email_sent column to attendance table
        try:
            cursor.execute("ALTER TABLE attendance ADD COLUMN email_sent INTEGER DEFAULT 0")
            print("Added email_sent column to attendance table")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e):
                print("Email_sent column already exists in attendance table")
            else:
                raise
        
        # Create notification_settings table
        try:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS notification_settings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    attendance_confirmations INTEGER DEFAULT 1,
                    absence_alerts INTEGER DEFAULT 1,
                    cutoff_time TEXT DEFAULT '10:00',
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            print("Created notification_settings table")
            
            # Insert default settings if table is empty
            cursor.execute("SELECT COUNT(*) FROM notification_settings")
            if cursor.fetchone()[0] == 0:
                cursor.execute("""
                    INSERT INTO notification_settings 
                    (attendance_confirmations, absence_alerts, cutoff_time) 
                    VALUES (1, 1, '10:00')
                """)
                print("Inserted default notification settings")
        
        except sqlite3.OperationalError as e:
            print(f"Error creating notification_settings table: {e}")
        
        conn.commit()
        print("Database migration completed successfully!")
        
    except Exception as e:
        print(f"Migration error: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    migrate_database()