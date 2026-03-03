"""
Database Manager Module
Handles SQLite database operations for the banking application.
"""

import sqlite3
import hashlib
import os
import random
import string
from datetime import datetime
from enum import Enum


class UserRole(Enum):
    ADMIN = "admin"
    CUSTOMER = "customer"


class DatabaseManager:
    """Manages SQLite database connections and operations."""
    
    def __init__(self, db_path=None):
        """Initialize database manager with database path."""
        if db_path is None:
            # Store database in project root
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            db_path = os.path.join(base_dir, "banking.db")
        self.db_path = db_path
        self.init_database()
    
    def get_connection(self):
        """Get a database connection with row factory."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def init_database(self):
        """Initialize database tables and create default admin account."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Create users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                full_name TEXT NOT NULL,
                role TEXT NOT NULL CHECK(role IN ('admin', 'customer')),
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP
            )
        """)
        
        # Create accounts table for customers with IBAN
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS accounts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                iban TEXT UNIQUE,
                balance REAL DEFAULT 0.0,
                account_type TEXT DEFAULT 'savings',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)
        
        # Create transactions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                account_id INTEGER NOT NULL,
                transaction_type TEXT NOT NULL,
                amount REAL NOT NULL,
                description TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (account_id) REFERENCES accounts(id)
            )
        """)
        
        conn.commit()
        conn.close()
        
        # Migrate old database: Add IBAN column if it doesn't exist
        # This must be done after tables are committed
        self._migrate_add_iban_column()
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Create default admin account if it doesn't exist
        self._create_default_admin(cursor)
        
        conn.commit()
        conn.close()
    
    def _migrate_add_iban_column(self):
        """Migrate database to add IBAN column if it doesn't exist."""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            # Check if iban column exists
            cursor.execute("PRAGMA table_info(accounts)")
            columns = [column[1] for column in cursor.fetchall()]
            
            if 'iban' not in columns:
                # SQLite doesn't allow adding UNIQUE column with existing data
                # Add column without UNIQUE constraint first
                cursor.execute("ALTER TABLE accounts ADD COLUMN iban TEXT")
                conn.commit()
                
                # Generate IBANs for existing accounts that don't have one
                cursor.execute("SELECT id FROM accounts WHERE iban IS NULL")
                accounts = cursor.fetchall()
                
                for account in accounts:
                    iban = self._generate_iban_internal(cursor)
                    cursor.execute("UPDATE accounts SET iban = ? WHERE id = ?", (iban, account[0]))
                
                conn.commit()
                print(f"Migration complete: Added IBAN column and generated {len(accounts)} IBANs")
        except sqlite3.Error as e:
            print(f"Migration warning: {e}")
            pass  # Column might already exist or other migration issue
        finally:
            conn.close()
    
    def _generate_iban_internal(self, cursor):
        """Generate a unique IBAN number (internal use with existing connection)."""
        while True:
            # Country code (2 letters)
            country = "GB"
            # Check digits (2 digits)
            check_digits = f"{random.randint(10, 99)}"
            # Bank code (4 letters)
            bank_code = ''.join(random.choices(string.ascii_uppercase, k=4))
            # Account number (14 digits)
            account_number = ''.join(random.choices(string.digits, k=14))
            
            # Combine without spaces for storage
            iban = f"{country}{check_digits}{bank_code}{account_number}"
            
            # Check uniqueness
            cursor.execute("SELECT id FROM accounts WHERE iban = ?", (iban,))
            if not cursor.fetchone():
                return iban
    
    def _create_default_admin(self, cursor):
        """Create the default admin account if it doesn't exist."""
        cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'admin'")
        admin_count = cursor.fetchone()[0]
        
        if admin_count == 0:
            # Default admin credentials
            admin_username = "admin"
            admin_password = "admin123"  # Should be changed on first login
            admin_email = "admin@bank.com"
            admin_full_name = "System Administrator"
            
            password_hash = self._hash_password(admin_password)
            
            cursor.execute("""
                INSERT INTO users (username, password_hash, email, full_name, role)
                VALUES (?, ?, ?, ?, ?)
            """, (admin_username, password_hash, admin_email, admin_full_name, UserRole.ADMIN.value))
    
    def _hash_password(self, password):
        """Hash a password using SHA-256."""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def verify_password(self, password, password_hash):
        """Verify a password against its hash."""
        return self._hash_password(password) == password_hash
    
    def _generate_iban(self):
        """Generate a unique IBAN number.
        Format: XX00 0000 0000 0000 0000 00 (24 characters total)
        Example: GB82 WEST 1234 5698 7654 32
        """
        while True:
            # Country code (2 letters)
            country = "GB"
            # Check digits (2 digits)
            check_digits = f"{random.randint(10, 99)}"
            # Bank code (4 letters)
            bank_code = ''.join(random.choices(string.ascii_uppercase, k=4))
            # Account number (14 digits)
            account_number = ''.join(random.choices(string.digits, k=14))
            
            # Combine without spaces for storage
            iban = f"{country}{check_digits}{bank_code}{account_number}"
            
            # Check uniqueness
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM accounts WHERE iban = ?", (iban,))
            if not cursor.fetchone():
                conn.close()
                return iban
            conn.close()
    
    def format_iban(self, iban):
        """Format IBAN with spaces for display."""
        if not iban:
            return ""
        # Format: XX00 0000 0000 0000 0000 00
        parts = [iban[i:i+4] for i in range(0, len(iban), 4)]
        return ' '.join(parts)
    
    def authenticate_user(self, username, password):
        """
        Authenticate a user with username and password.
        Returns user dict if successful, None otherwise.
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, username, password_hash, email, full_name, role, is_active
            FROM users WHERE username = ? AND is_active = 1
        """, (username,))
        
        user = cursor.fetchone()
        conn.close()
        
        if user and self.verify_password(password, user['password_hash']):
            return {
                'id': user['id'],
                'username': user['username'],
                'email': user['email'],
                'full_name': user['full_name'],
                'role': user['role']
            }
        return None
    
    def register_customer(self, username, password, email, full_name):
        """
        Register a new customer user.
        Returns (success: bool, message: str)
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Check if username already exists
        cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
        if cursor.fetchone():
            conn.close()
            return False, "Username already exists"
        
        # Check if email already exists
        cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
        if cursor.fetchone():
            conn.close()
            return False, "Email already registered"
        
        try:
            password_hash = self._hash_password(password)
            
            cursor.execute("""
                INSERT INTO users (username, password_hash, email, full_name, role)
                VALUES (?, ?, ?, ?, ?)
            """, (username, password_hash, email, full_name, UserRole.CUSTOMER.value))
            
            user_id = cursor.lastrowid
            
            # Create a default account for the customer with IBAN
            iban = self._generate_iban()
            cursor.execute("""
                INSERT INTO accounts (user_id, iban, balance, account_type)
                VALUES (?, ?, 0.0, 'savings')
            """, (user_id, iban))
            
            conn.commit()
            conn.close()
            return True, "Registration successful"
            
        except sqlite3.Error as e:
            conn.close()
            return False, f"Database error: {str(e)}"
    
    def get_user_by_id(self, user_id):
        """Get user details by ID."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, username, email, full_name, role, is_active, created_at
            FROM users WHERE id = ?
        """, (user_id,))
        
        user = cursor.fetchone()
        conn.close()
        
        if user:
            return dict(user)
        return None
    
    def get_user_account(self, user_id):
        """Get user's account with IBAN and balance."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT a.id, a.user_id, a.iban, a.balance, a.account_type, a.created_at
            FROM accounts a
            WHERE a.user_id = ?
        """, (user_id,))
        
        account = cursor.fetchone()
        conn.close()
        
        if account:
            return dict(account)
        return None
    
    def get_all_customers_with_accounts(self):
        """Get all customer users with their account info (for admin use)."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT u.id, u.username, u.email, u.full_name, u.is_active, u.created_at,
                   a.iban, a.balance
            FROM users u
            LEFT JOIN accounts a ON u.id = a.user_id
            WHERE u.role = 'customer'
            ORDER BY u.created_at DESC
        """)
        
        customers = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return customers
    
    def get_all_customers(self):
        """Get all customer users (for admin use)."""
        return self.get_all_customers_with_accounts()
    
    def update_last_login(self, user_id):
        """Update the last login timestamp for a user."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?
        """, (user_id,))
        
        conn.commit()
        conn.close()
    
    def get_account_by_iban(self, iban):
        """Get account by IBAN number."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Remove spaces from IBAN if present
        iban = iban.replace(" ", "").upper()
        
        cursor.execute("""
            SELECT a.id, a.user_id, a.iban, a.balance, a.account_type,
                   u.username, u.full_name, u.email
            FROM accounts a
            JOIN users u ON a.user_id = u.id
            WHERE a.iban = ?
        """, (iban,))
        
        account = cursor.fetchone()
        conn.close()
        
        if account:
            return dict(account)
        return None
    
    def transfer_money(self, from_user_id, to_iban, amount, description="Transfer"):
        """
        Transfer money from one account to another using IBAN.
        Returns (success: bool, message: str)
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Remove spaces from IBAN
            to_iban = to_iban.replace(" ", "").upper()
            
            # Get source account
            cursor.execute("""
                SELECT id, balance FROM accounts WHERE user_id = ?
            """, (from_user_id,))
            from_account = cursor.fetchone()
            
            if not from_account:
                conn.close()
                return False, "Source account not found"
            
            # Get destination account by IBAN
            cursor.execute("""
                SELECT id, user_id, balance FROM accounts WHERE iban = ?
            """, (to_iban,))
            to_account = cursor.fetchone()
            
            if not to_account:
                conn.close()
                return False, "Destination IBAN not found"
            
            if from_account['id'] == to_account['id']:
                conn.close()
                return False, "Cannot transfer to the same account"
            
            if from_account['balance'] < amount:
                conn.close()
                return False, "Insufficient balance"
            
            # Deduct from source
            cursor.execute("""
                UPDATE accounts SET balance = balance - ? WHERE id = ?
            """, (amount, from_account['id']))
            
            # Add transaction record for source (debit)
            cursor.execute("""
                INSERT INTO transactions (account_id, transaction_type, amount, description)
                VALUES (?, 'debit', ?, ?)
            """, (from_account['id'], amount, f"Transfer to {to_iban}: {description}"))
            
            # Add to destination
            cursor.execute("""
                UPDATE accounts SET balance = balance + ? WHERE id = ?
            """, (amount, to_account['id']))
            
            # Add transaction record for destination (credit)
            cursor.execute("""
                INSERT INTO transactions (account_id, transaction_type, amount, description)
                VALUES (?, 'credit', ?, ?)
            """, (to_account['id'], amount, f"Transfer from account: {description}"))
            
            conn.commit()
            conn.close()
            return True, "Transfer successful"
            
        except sqlite3.Error as e:
            conn.close()
            return False, f"Database error: {str(e)}"
    
    def deposit(self, user_id, amount, description="Deposit"):
        """Deposit money to user's account."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                UPDATE accounts SET balance = balance + ? WHERE user_id = ?
            """, (amount, user_id))
            
            # Get account id for transaction record
            cursor.execute("SELECT id FROM accounts WHERE user_id = ?", (user_id,))
            account = cursor.fetchone()
            
            if account:
                cursor.execute("""
                    INSERT INTO transactions (account_id, transaction_type, amount, description)
                    VALUES (?, 'credit', ?, ?)
                """, (account['id'], amount, description))
            
            conn.commit()
            conn.close()
            return True, "Deposit successful"
            
        except sqlite3.Error as e:
            conn.close()
            return False, f"Database error: {str(e)}"
    
    def withdraw(self, user_id, amount, description="Withdrawal"):
        """Withdraw money from user's account."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Check balance
            cursor.execute("SELECT id, balance FROM accounts WHERE user_id = ?", (user_id,))
            account = cursor.fetchone()
            
            if not account:
                conn.close()
                return False, "Account not found"
            
            if account['balance'] < amount:
                conn.close()
                return False, "Insufficient balance"
            
            cursor.execute("""
                UPDATE accounts SET balance = balance - ? WHERE user_id = ?
            """, (amount, user_id))
            
            cursor.execute("""
                INSERT INTO transactions (account_id, transaction_type, amount, description)
                VALUES (?, 'debit', ?, ?)
            """, (account['id'], amount, description))
            
            conn.commit()
            conn.close()
            return True, "Withdrawal successful"
            
        except sqlite3.Error as e:
            conn.close()
            return False, f"Database error: {str(e)}"
    
    def get_transactions(self, user_id, limit=50):
        """Get transaction history for a user."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT t.id, t.transaction_type, t.amount, t.description, t.timestamp
            FROM transactions t
            JOIN accounts a ON t.account_id = a.id
            WHERE a.user_id = ?
            ORDER BY t.timestamp DESC
            LIMIT ?
        """, (user_id, limit))
        
        transactions = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return transactions
    
    def delete_customer(self, user_id):
        """Delete a customer and their account."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Check if user exists and is a customer
            cursor.execute("SELECT role FROM users WHERE id = ?", (user_id,))
            user = cursor.fetchone()
            
            if not user:
                conn.close()
                return False, "User not found"
            
            if user['role'] == 'admin':
                conn.close()
                return False, "Cannot delete admin account"
            
            # Delete transactions first
            cursor.execute("""
                DELETE FROM transactions WHERE account_id IN 
                (SELECT id FROM accounts WHERE user_id = ?)
            """, (user_id,))
            
            # Delete account
            cursor.execute("DELETE FROM accounts WHERE user_id = ?", (user_id,))
            
            # Delete user
            cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
            
            conn.commit()
            conn.close()
            return True, "Customer deleted successfully"
            
        except sqlite3.Error as e:
            conn.close()
            return False, f"Database error: {str(e)}"
    
    def update_customer(self, user_id, full_name=None, email=None):
        """Update customer information."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            updates = []
            params = []
            
            if full_name:
                updates.append("full_name = ?")
                params.append(full_name)
            
            if email:
                # Check if email is already used by another user
                cursor.execute("SELECT id FROM users WHERE email = ? AND id != ?", (email, user_id))
                if cursor.fetchone():
                    conn.close()
                    return False, "Email already in use"
                updates.append("email = ?")
                params.append(email)
            
            if not updates:
                conn.close()
                return True, "No changes to update"
            
            params.append(user_id)
            query = f"UPDATE users SET {', '.join(updates)} WHERE id = ?"
            cursor.execute(query, params)
            
            conn.commit()
            conn.close()
            return True, "Customer updated successfully"
            
        except sqlite3.Error as e:
            conn.close()
            return False, f"Database error: {str(e)}"


# Singleton instance for global use
db_manager = DatabaseManager()
