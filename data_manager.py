import sqlite3

class DatabaseManager:
    def __init__(self, db_path='app_data'):
        self.db_path = db_path

    def _get_conn(self):
        return sqlite3.connect(self.db_path)

    def user_exists(self, username):
        '''Returns true if username is found'''
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT 1 FROM users WHERE username = ?', (username,))
            return cursor.fetchone() is not None

    def insert_user(self, username, password):
        '''Adding user to database'''
        try:
            with self._get_conn() as conn:
                conn.cursor().execute(
                    'INSERT INTO users (username, password, logged_status) VALUES (?, ?, 0)',
                    (username, password)
                )
                conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

    def get_password_by_username(self, username):
        '''Extract user password, None if not found'''
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT password FROM users WHERE username = ?', (username,))
            result = cursor.fetchone()
            return result[0] if result else None

    def get_uuid(self, username):
        '''Returns uuid for user'''
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT uuid FROM users WHERE username = ?', (username,))
            result = cursor.fetchone()
            return result[0] if result else None

    def update_status(self, uuid, status_code):
        '''Updates logged_status'''
        with self._get_conn() as conn:
            conn.cursor().execute(
                'UPDATE users SET logged_status = ? WHERE uuid = ?', 
                (status_code, uuid)
            )
            conn.commit()

class UserManager:
    def __init__(self, db_manager):
        self.db = db_manager
        self.current_uuid = None

    def validate_and_register(self, username, password, confirm_password):
        '''Ensure conditions before registeration'''

        if not username or not password:
            return False, 'All fields are required!'
        
        if password != confirm_password:
            return False, 'Passwords do not match!'

        if len(password) < 6:
            return False, 'Password must be at least 6 characters long!'

        if self.db.user_exists(username):
            return False, 'Username is already taken!'

        if self.db.insert_user(username, password):
            return True, 'Account created successfully!'
        else:
            return False, 'Database error during insertion.'

    def validate_and_login(self, username, password):
        '''Ensure conditions before login'''

        if not username or not password:
            return False, 'Please enter both username and password!'

        stored_password = self.db.get_password_by_username(username)

        if stored_password is None:
            return False, 'Username not found!'

        if password == stored_password:
            self.current_uuid = self.db.get_uuid(username)
            self.db.update_status(self.current_uuid, 1)
            return True, 'Login successful!'
        else:
            return False, 'Incorrect password!'

    def logout(self, user_uuid):
        '''Update user logged status'''
        if user_uuid:
            self.db.update_status(user_uuid, 0)