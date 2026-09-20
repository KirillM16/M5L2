import sqlite3
from config import *
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature


class DB_Map():
    def __init__(self, database):
        self.database = database
    
    def create_user_table(self):
        conn = sqlite3.connect(self.database)
        with conn:
            conn.execute('''CREATE TABLE IF NOT EXISTS users_cities (
                                user_id INTEGER,
                                city_id TEXT,
                                FOREIGN KEY(city_id) REFERENCES cities(id)
                            )''')
            conn.commit()

    def add_city(self,user_id, city_name ):
        conn = sqlite3.connect(self.database)
        with conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM cities WHERE city=?", (city_name,))
            city_data = cursor.fetchone()
            if city_data:
                city_id = city_data[0]  
                conn.execute('INSERT INTO users_cities VALUES (?, ?)', (user_id, city_id))
                conn.commit()
                return 1
            else:
                return 0

            
    def select_cities(self, user_id):
        conn = sqlite3.connect(self.database)
        with conn:
            cursor = conn.cursor()
            cursor.execute('''SELECT cities.city 
                            FROM users_cities  
                            JOIN cities ON users_cities.city_id = cities.id
                            WHERE users_cities.user_id = ?''', (user_id,))

            cities = [row[0] for row in cursor.fetchall()]
            return cities


    def get_coordinates(self, city_name):
        conn = sqlite3.connect(self.database)
        with conn:
            cursor = conn.cursor()
            cursor.execute('''SELECT lat, lng
                            FROM cities  
                            WHERE city = ?''', (city_name,))
            coordinates = cursor.fetchone()
            return coordinates

    def create_graph(self, path, cities):
        fig = plt.figure(figsize=(12, 6))
        ax = plt.axes(projection=ccrs.PlateCarree())
        ax.add_feature(cfeature.OCEAN)
        ax.stock_img()
        ax.set_global()
        for city in cities:
            coordinates = self.get_coordinates(city)
            if coordinates is None:
                continue
            lat, lng = coordinates
            ax.plot(lng, lat, marker='x', color='green', markersize=6,
                    transform=ccrs.PlateCarree())
            ax.text(lng + 2, lat + 2, city, fontsize=7, color='blue',
                    transform=ccrs.PlateCarree())
        fig.savefig(path, dpi=150, bbox_inches='tight')
        plt.close(fig)

    def haversine_distance(self, lat1, lon1, lat2, lon2):
            """Вычисляет расстояние между двумя точками в километрах по формуле гаверсинуса."""
            R = 6371.0  # радиус Земли в км
            
            lat1_rad = plt.radians(lat1)
            lat2_rad = plt.radians(lat2)
            delta_lat = plt.radians(lat2 - lat1)
            delta_lon = plt.radians(lon2 - lon1)
            
            a = plt.sin(delta_lat / 2)**2 + \
                plt.cos(lat1_rad) * plt.cos(lat2_rad) * plt.sin(delta_lon / 2)**2
            c = 2 * plt.atan2(plt.sqrt(a), plt.sqrt(1 - a))
            
            distance = R * c
            return distance


    def draw_distance(self, city1, city2):
        """Вычисляет и возвращает расстояние между двумя городами в км."""
        coord1 = self.get_coordinates(city1)
        coord2 = self.get_coordinates(city2)
        
        if coord1 is None or coord2 is None:
            return None
        
        lat1, lng1 = coord1
        lat2, lng2 = coord2
        
        distance = self.haversine_distance(lat1, lng1, lat2, lng2)
        return distance


if __name__=="__main__":
    
    m = DB_Map(DATABASE)
    m.create_user_table()
