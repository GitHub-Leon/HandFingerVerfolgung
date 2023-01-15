import sqlite3
import time
import numpy as np


class Database:
    def __init__(self, correctZValues):
        self.con = sqlite3.connect("database/main_db")
        self.cursor = self.con.cursor()
        self.correctZValues = correctZValues

        self.moving_average = 20  # specify number of previous landmarks to save (for z value correction)
        self.landmark_buffer = {}  # create buffer for each landmark type (for z value correction)
        self.distance_threshold_moving_average = 0.2  # on 20% distance dif, we set the value to the moving average

        # create default values if no database was created yet
        if self.cursor.execute("""SELECT name FROM sqlite_master WHERE type='table' AND name='entry';""").fetchone() is None:
            self.session_id = 0
            self.entry_id = 0
            self.hand_id = 0
            self.landmark_typ_id = 0
            self.coordinates_id = 0
            self.mouse_id = 0
            self.mouse_coordinates_id = 0
            self.keyboard_id = 0
            self.keyboard_coordinates_id = 0
        else:  # else increment last stored values
            try:
                self.session_id = self.cursor.execute("""SELECT session_id FROM entry ORDER BY session_id DESC LIMIT 1""").fetchone()[0] + 1
            except Exception:
                self.session_id = 0
            try:
                self.entry_id = self.cursor.execute("""SELECT id FROM entry ORDER BY id DESC LIMIT 1""").fetchone()[0] + 1
            except Exception:
                self.entry_id = 0
            try:
                self.hand_id = self.cursor.execute("""SELECT id FROM hand ORDER BY id DESC LIMIT 1""").fetchone()[0] + 1
            except Exception:
                self.hand_id = 0
            try:
                self.landmark_typ_id = self.cursor.execute("""SELECT id FROM landmarkTypes ORDER BY id DESC LIMIT 1""").fetchone()[0] + 1
            except Exception:
                self.landmark_typ_id = 0
            try:
                self.coordinates_id = self.cursor.execute("""SELECT id FROM coordinates ORDER BY id DESC LIMIT 1""").fetchone()[0] + 1
            except Exception:
                self.coordinates_id = 0
            try:
                self.mouse_id = self.cursor.execute("""SELECT id FROM mouse ORDER BY id DESC LIMIT 1""").fetchone()[0] + 1
            except Exception:
                self.mouse_id = 0
            try:
                self.keyboard_id = self.cursor.execute("""SELECT id FROM keyboard ORDER BY id DESC LIMIT 1""").fetchone()[0] + 1
            except Exception:
                self.keyboard_id = 0
            try:
                self.mouse_coordinates_id = self.cursor.execute("""SELECT id FROM mouseCoordinates ORDER BY id DESC LIMIT 1""").fetchone()[0] + 1
            except Exception:
                self.mouse_coordinates_id = 0
            try:
                self.keyboard_coordinates_id = self.cursor.execute("""SELECT id FROM keyboardCoordinates ORDER BY id DESC LIMIT 1""").fetchone()[0] + 1
            except Exception:
                self.keyboard_coordinates_id = 0

        self.__create_tables()

    def __create_tables(self):
        """
        creates all necessary tables
        """
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS entry(id NOT NULL PRIMARY KEY , time, session_id)""")
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS mouse(id NOT NULL PRIMARY KEY , entry_id, FOREIGN KEY(entry_id) REFERENCES entry(id))""")
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS keyboard(id NOT NULL PRIMARY KEY , entry_id, FOREIGN KEY(entry_id) REFERENCES entry(id))""")
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS hand(id NOT NULL PRIMARY KEY , entry_id, is_right, distance_to_camera, FOREIGN KEY(entry_id) REFERENCES entry(id))""")
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS coordinates(id NOT NULL PRIMARY KEY , x, y, z)""")
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS landmarks(hand_id, landmark_typ_id, coordinates_id, FOREIGN KEY(hand_id) REFERENCES hand(id), FOREIGN KEY(landmark_typ_id) REFERENCES landmarkTypes(id), FOREIGN KEY(coordinates_id) REFERENCES coordinates(id))""")
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS mouseCoordinates(id NOT NULL PRIMARY KEY , mouse_id, coordinates_id, FOREIGN KEY(mouse_id) REFERENCES mouse(id), FOREIGN KEY(coordinates_id) REFERENCES coordinates(id))""")
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS keyboardCoordinates(id NOT NULL PRIMARY KEY , keyboard_id, coordinates_id, FOREIGN KEY(keyboard_id) REFERENCES keyboard(id), FOREIGN KEY(coordinates_id) REFERENCES coordinates(id))""")

        self.__create_landmark_types_table()

        self.con.commit()

    def database_entry(self, hand_landmarks, mouse_box, keyboard_box):
        """
        main function to create a database entry
        :param keyboard_box: entry of keyboard box in format: [['keyboard', '0.29', (73, 245, 404, 144)]]
        :param hand_landmarks: all landmarks in format: [['Right', 3, (537, 239, -0.07019183784723282)], ... ]
        :param mouse_box: coordinates of mouse box in format  [['mouse', '0.59', (20, 456, 760, 522)]]
        """
        self.__entry_entry()
        self.__landmarks_entry(hand_landmarks)
        self.__mouse_coordinates_entry(mouse_box)
        self.__keyboard_coordinates_entry(keyboard_box)

        self.con.commit()

    def __mouse_coordinates_entry(self, mouse_box):
        """entry for mouse coordinates [mouse_coordinates_id, mouse_id, coordinates_id]"""
        if mouse_box:
            self.__mouse_entry()
            mouse_coords = [(mouse_box[0][2][0], mouse_box[0][2][1]), (mouse_box[0][2][0] + mouse_box[0][2][2], mouse_box[0][2][1] + mouse_box[0][2][3])]
            for mouse_coord in mouse_coords:
                self.__coordinates_entry(mouse_coord[0], mouse_coord[1], -1)
                self.cursor.execute("""INSERT INTO mouseCoordinates VALUES (?, ?, ?)""", (self.mouse_coordinates_id, self.mouse_id - 1, self.coordinates_id - 1))
                self.mouse_coordinates_id = self.mouse_coordinates_id + 1

    def __mouse_entry(self):
        """entry for mouse [mouse_id, entry_id]"""
        self.cursor.execute("""INSERT INTO mouse VALUES (?, ?)""", (self.mouse_id, self.entry_id - 1))
        self.mouse_id = self.mouse_id + 1

    def __keyboard_coordinates_entry(self, keyboard_box):
        """entry for keyboard coordinates [keyboard_coordinates_id, keyboard_id, coordinates_id]"""
        if keyboard_box:
            self.__keyboard_entry()
            keyboard_coords = [(keyboard_box[0][2][0], keyboard_box[0][2][1]), (keyboard_box[0][2][0] + keyboard_box[0][2][2], keyboard_box[0][2][1] + keyboard_box[0][2][3])]
            for keyboard_coord in keyboard_coords:
                self.__coordinates_entry(keyboard_coord[0], keyboard_coord[1], -1)
                self.cursor.execute("""INSERT INTO keyboardCoordinates VALUES (?, ?, ?)""", (self.keyboard_coordinates_id, self.keyboard_id - 1, self.coordinates_id - 1))
                self.keyboard_coordinates_id = self.keyboard_coordinates_id + 1

    def __keyboard_entry(self):
        """entry for keyboard [keyboard_id, entry_id]"""
        self.cursor.execute("""INSERT INTO keyboard VALUES (?, ?)""", (self.keyboard_id, self.entry_id - 1))
        self.keyboard_id = self.keyboard_id + 1

    def __entry_entry(self):
        """entry for entry [id, timestamp, session_id]"""
        self.cursor.execute("""INSERT INTO entry VALUES (?, ?, ?)""", (self.entry_id, time.time(), self.session_id))
        self.entry_id = self.entry_id + 1

    def __hand_entry(self, is_right, distance_to_camera):
        """entry for hand [hand_id, entry_id, is_right, distance_to_camera]"""
        x1, y1 = -1, -1
        if self.hand_id >= 1:
            (x1, y1) = self.cursor.execute("""SELECT entry_id, is_right FROM hand ORDER BY id DESC LIMIT 1""").fetchone()
        if self.entry_id - 1 != x1 or (y1 != (is_right == 'Right')):
            self.cursor.execute("""INSERT INTO hand VALUES (?, ?, ?, ?) """, (self.hand_id, self.entry_id - 1, is_right == 'Right', distance_to_camera))
            self.hand_id = self.hand_id + 1

    def __landmarks_entry(self, landmarks):
        """entry for landmarks [hand_id, landmark_typ_id, coordinates_id]"""

        for landmark in landmarks:  # ['Right', 3, (537, 239, -0.07019183784723282), 75]
            hand_id = landmark[0]
            landmark_typ_id = landmark[1]
            coordinates = landmark[2]
            self.__hand_entry(hand_id, landmark[3])

            if self.correctZValues:
                if landmark_typ_id not in self.landmark_buffer:  # if this is the first time seeing this landmark type
                    self.landmark_buffer[landmark_typ_id] = np.array([coordinates[2]])  # create a new numpy array with this landmark type and add the current coordinates
                else:
                    self.landmark_buffer[landmark_typ_id] = np.append(self.landmark_buffer[landmark_typ_id], [coordinates[2]], axis=0)  # if this landmark type has been seen before, append the current coordinates
                    if len(self.landmark_buffer[landmark_typ_id]) > self.moving_average:
                        self.landmark_buffer[landmark_typ_id] = self.landmark_buffer[landmark_typ_id][-self.moving_average:]  # keep only the last x entries

                avg_coordinates = np.mean(self.landmark_buffer[landmark_typ_id], axis=0)  # calculate average coordinates

                if coordinates[2] < (1-self.distance_threshold_moving_average) * avg_coordinates or coordinates[2] > (1+self.distance_threshold_moving_average) * avg_coordinates:
                    coordinates = coordinates[:2] + (avg_coordinates,) + coordinates[3:]

            self.__coordinates_entry(coordinates[0], coordinates[1], coordinates[2])
            self.cursor.execute("""INSERT INTO landmarks VALUES (?, ?, ?) """, (self.hand_id - 1, landmark_typ_id, self.coordinates_id - 1))


    def __create_landmark_types_table(self):
        """entry for landmark types [landmark_typ_id, name]"""
        if self.cursor.execute("""SELECT name FROM sqlite_master WHERE type='table' AND name='landmarkTypes';""").fetchone() is None:  # only fill the DB if it hasn't been created yet
            self.cursor.execute("""CREATE TABLE IF NOT EXISTS landmarkTypes(id PRIMARY KEY , name VARCHAR(50) UNIQUE)""")

            names = ['WRIST', 'THUMB_CMC', 'THUMB_MCP', 'THUMB_IP', 'THUMB_TIP', 'INDEX_FINGER_MCP', 'INDEX_FINGER_PIP',
                     'INDEX_FINGER_DIP', 'INDEX_FINGER_TIP', 'MIDDLE_FINGER_MCP', 'MIDDLE_FINGER_PIP',
                     'MIDDLE_FINGER_DIP', 'MIDDLE_FINGER_TIP', 'RING_FINGER_MCP', 'RING_FINGER_PIP', 'RING_FINGER_DIP',
                     'RING_FINGER_TIP', 'PINKY_MCP', 'PINKY_PIP', 'PINKY_DIP', 'PINKY_TIP']
            for name in names:
                self.cursor.execute("""INSERT INTO landmarkTypes VALUES (?, ?)""", (self.landmark_typ_id, name))
                self.landmark_typ_id = self.landmark_typ_id + 1

    def __coordinates_entry(self, x, y, z):
        """entry for coordinates [x, y, z]"""
        self.cursor.execute("""INSERT INTO coordinates VALUES (?, ?, ?, ?)""", (self.coordinates_id, x, y, z))
        self.coordinates_id = self.coordinates_id + 1
