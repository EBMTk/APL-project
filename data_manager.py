import sqlite3

class DatabaseManager:
    def __init__(self, db_path='appdata/app_data'):
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

    def update_user_money(self, uuid, money):
        with self._get_conn() as conn:
            conn.cursor().execute('UPDATE users SET money = ? WHERE uuid = ?', (money, uuid))
            conn.commit()

    def query_user_money(self, uuid):
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT money FROM users WHERE uuid = ?', (uuid,))
            result = cursor.fetchone()

        return result[0]
    
    def add_user_inv_furniture(self, uuid, inv_dict):
        with self._get_conn() as conn:
            conn.cursor().execute('DELETE FROM inventory WHERE uuid = ? AND item_type = ?', (uuid, 'furn'))
            conn.commit()

        for item, quantity in inv_dict.items():
            with self._get_conn() as conn:
                conn.cursor().execute(
                    'INSERT INTO inventory (uuid, item_name, item_type, quantity) VALUES (?, ?, ?, ?)',
                    (uuid, item, 'furn',quantity)
                )
                conn.commit()
    
    def add_user_eqp_furniture(self, uuid, placed_furniture):
        with self._get_conn() as conn:
            conn.cursor().execute('DELETE FROM placed_furniture WHERE uuid = ?', (uuid,))
            conn.commit()

        for item in placed_furniture:
            with self._get_conn() as conn:
                conn.cursor().execute(
                    'INSERT INTO placed_furniture (uuid, name, angle_index, x, y, z) VALUES (?, ?, ?, ?, ? , ?)',
                    (uuid, item['name'], item['angle_index'], item['x'], item['y'], item['z'])
                    )
                conn.commit()
        
        return

    def query_user_inv_furniture(self, uuid):
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT item_name, quantity FROM inventory WHERE uuid = ? AND item_type = ?', (uuid, 'furn'))
            result = cursor.fetchall()
        
        inv_furn_list = []
        for item in result:
            item_name, quantity = item
            for _ in range(quantity):
                inv_furn_list.append(item_name)
        
        return inv_furn_list


    def query_user_eqp_furniture(self, uuid):
        with self._get_conn() as conn:
            conn.row_factory = sqlite3.Row 
            cursor = conn.cursor()
            cursor.execute(f"SELECT name, angle_index, x, y, z FROM placed_furniture WHERE uuid = (?)", (uuid,))
            rows = cursor.fetchall()
            
        row_list = []
        for row in rows:
            row_data = dict(row)
            row_list.append(row_data)
        
        return row_list
    
    def add_user_eqp_clothes(self, uuid):
        with self._get_conn() as conn:
            conn.cursor().execute(
                'INSERT INTO equipped_clothes (uuid, Head, Torso, Legs, Feet) VALUES (?, ?, ?, ?, ?)',
                (uuid, None, None, None, None)
                )
            conn.commit()

    def update_user_eqp_clothes(self, uuid, equipped_clothes):
        with self._get_conn() as conn:
            conn.cursor().execute(
                'UPDATE equipped_clothes SET Head = ?, Torso = ?, Legs = ?, Feet = ? WHERE uuid = ?', 
                (equipped_clothes['Head'], equipped_clothes['Torso'], equipped_clothes['Legs'], equipped_clothes['Feet'], uuid)
            )
            conn.commit()

    def add_user_inv_clothes(self, uuid, item_list):
        with self._get_conn() as conn:
            conn.cursor().execute('DELETE FROM inventory WHERE uuid = ? AND item_type = ?', (uuid, 'clothe'))
            conn.commit()

        for item in item_list:
            with self._get_conn() as conn:
                conn.cursor().execute(
                    'INSERT INTO inventory (uuid, item_name, item_type) VALUES (?, ?, ?)',
                    (uuid, item, 'clothe')
                    )
                conn.commit()
        
        return
    
    def query_user_eqp_clothes(self, uuid):
        with self._get_conn() as conn:
            conn.row_factory = sqlite3.Row 
            cursor = conn.cursor()
            cursor.execute(f"SELECT Head, Torso, Legs, Feet FROM equipped_clothes WHERE uuid = (?)", (uuid,))
            row = cursor.fetchone()
        
        if not row:
            return {}
        else:
            return dict(row)
    
    def query_user_inv_clothes(self, uuid):
        inv = []

        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT item_name FROM inventory WHERE uuid = ? AND item_type = ?', (uuid, 'clothe'))
            result = cursor.fetchall()

        for i in range(len(result)):
            inv.append(result[i][0])
        
        if not inv:
            return []
        else:
            return inv

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
            self.current_uuid = self.db.get_uuid(username)
            default_space = [   {'name': 'Floor Blank', 'angle_index': 0, 'x': 555, 'y': 172, 'z': 0}, 
                                {'name': 'Wall1', 'angle_index': 0, 'x': 640, 'y': 64, 'z': 0},
                                {'name': 'Wall1', 'angle_index': 1, 'x': 558, 'y': 67, 'z': 0}, 
                                {'name': 'Floor Blank', 'angle_index': 0, 'x': 475, 'y': 229, 'z': 10},
                                {'name': 'Wall2', 'angle_index': 0, 'x': 717, 'y': 118, 'z': 4}, 
                                {'name': 'Floor Blank', 'angle_index': 3, 'x': 633, 'y': 228, 'z': 8}, 
                                {'name': 'Floor Blank', 'angle_index': 1, 'x': 554, 'y': 286, 'z': 11}, 
                                {'name': 'Wall1', 'angle_index': 1, 'x': 477, 'y': 123, 'z': 12},
                            ]
            self.db.add_user_eqp_furniture(self.current_uuid, default_space)

            self.db.add_user_eqp_clothes(self.current_uuid)
            
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

    def save_user_money(self, uuid, money):
        self.db.update_user_money(uuid, money)

    def retrive_user_money(self, uuid):
        return self.db.query_user_money(uuid)
    
    def save_user_furniture_data(self, uuid, inventory_furniture, placed_furniture):
        inv_set = set(inventory_furniture)
        inv_dict = {}

        for item in inv_set:
            inv_dict[item] = inventory_furniture.count(item)

        self.db.add_user_inv_furniture(uuid, inv_dict)
        self.db.add_user_eqp_furniture(uuid, placed_furniture)

    def retrieve_user_furniture_data(self, uuid):
        inv_furn_list = self.db.query_user_inv_furniture(uuid)
        place_items_list = self.db.query_user_eqp_furniture(uuid)

        return inv_furn_list, place_items_list
    
    def save_user_clothe_data(self, uuid, invenory_clothes, equipped_clothes):
        self.db.update_user_eqp_clothes(uuid, equipped_clothes)
        self.db.add_user_inv_clothes(uuid, invenory_clothes)

    def retrieve_user_clothe_data(self, uuid):
        equipped_clothes = self.db.query_user_eqp_clothes(uuid)
        inventory_clothes = self.db.query_user_inv_clothes(uuid)

        return inventory_clothes, equipped_clothes

        



# Inventory Sent: ['Item', 'Item']
# Equipped Sent: {'Head': None, 'Torso': None, 'Legs': 'Jeans', 'Feet': None}
# class GameData:
#     def __init__(self):
#         self.money = 100000
#         self.inventory_clothes = []
#         self.worn_clothes = []
#         self.equipped_clothes = []
#         self.inventory_furniture = []
#         self.placed_furniture = [
#                                 {'name': 'Floor Blank', 'angle_index': 0, 'x': 555, 'y': 172, 'z': 0}, 
#                                 {'name': 'Wall1', 'angle_index': 0, 'x': 640, 'y': 64, 'z': 0},
#                                 {'name': 'Wall1', 'angle_index': 1, 'x': 558, 'y': 67, 'z': 0}, 
#                                 {'name': 'Floor Blank', 'angle_index': 0, 'x': 475, 'y': 229, 'z': 10},
#                                 {'name': 'Wall2', 'angle_index': 0, 'x': 717, 'y': 118, 'z': 4}, 
#                                 {'name': 'Floor Blank', 'angle_index': 3, 'x': 633, 'y': 228, 'z': 8}, 
#                                 {'name': 'Floor Blank', 'angle_index': 1, 'x': 554, 'y': 286, 'z': 11}, 
#                                 {'name': 'Wall1', 'angle_index': 1, 'x': 477, 'y': 123, 'z': 12}
#                             ]