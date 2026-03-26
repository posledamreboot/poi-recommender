import osmnx as ox
import pandas as pd
from shapely.geometry import Polygon
from shapely.geometry import box
from sympy.core.symbol import Str


def get_sadovoe_polygon():
    bbox = (55.750, 37.600, 55.800, 37.650)  # (north, south, east, west) в osmnx наоборот
    # ox.geometries_from_bbox требует: north, south, east, west
    north, south, east, west = bbox[0], bbox[2], bbox[1], bbox[3]
    # return ox.features_from_bbox(north, south, east, west, tags=tags)
    return box(west, south, east, north)

def get_poi_in_polygon(polygon, tags):
    # tags: словарь с тегами, например, {'amenity': True, 'tourism': True} – получить всё, что имеет эти ключи
    # osmnx.geometries_from_polygon возвращает всё, что попадает в полигон
    gdf = ox.features_from_polygon(polygon, tags)
    return gdf

def extract_poi_data(gdf):
    # Извлечение нужных полей
    poi_list = []
    for idx, row in gdf.iterrows():
        # геометрия: точка или полигон
        geom = row.geometry
        if geom is None:
            continue
        if geom.geom_type == 'Point':
            lon, lat = geom.x, geom.y
        elif geom.geom_type in ['Polygon', 'MultiPolygon']:
            # берем центроид
            centroid = geom.centroid
            lon, lat = centroid.x, centroid.y
        else:
            continue
        poi = {
            'id': idx,
            'name': row.get('name', ''),
            'lat': lat,
            'lon': lon,
            'category': _get_category(row),
            'address': str(row.get('addr:street', '')) + ' ' + str(row.get('addr:housenumber', '')),
            'phone': row.get('phone', ''),
            'website': row.get('website', ''),
            'opening_hours': row.get('opening_hours', ''),
            'rating': row.get('rating', None),
            'description': row.get('description', ''),
        }
        # можно добавить другие теги
        poi_list.append(poi)
    return pd.DataFrame(poi_list)

def _get_category(row):
    # определить категорию по наличию тегов
    if 'tourism' in row and row['tourism']:
        return f"tourism_{row['tourism']}"
    if 'amenity' in row and row['amenity']:
        return f"amenity_{row['amenity']}"
    if 'leisure' in row and row['leisure']:
        return f"leisure_{row['leisure']}"
    if 'historic' in row and row['historic']:
        return f"historic_{row['historic']}"
    if 'shop' in row and row['shop']:
        # ограничим только интересные shop
        interesting_shops = ['books', 'gift', 'art', 'music', 'toys']
        if row['shop'] in interesting_shops:
            return f"shop_{row['shop']}"
    return 'other'

if __name__ == '__main__':
    # tags – словарь, где ключ – тег, значение – True означает все значения
    tags = {
        'tourism': True,
        'amenity': True,
        'leisure': True,
        'historic': True,
        'shop': ['books', 'gift', 'art', 'music', 'toys']  # список значений
    }
    # полигон садового кольца – пока bbox, потом заменим на точный
    polygon = get_sadovoe_polygon()  # нужно будет корректно определить полигон
    gdf = get_poi_in_polygon(polygon, tags)
    df = extract_poi_data(gdf)
    df.to_csv('../data/poi_moscow_sadovoe.csv', index=False)