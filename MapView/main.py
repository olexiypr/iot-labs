import asyncio
from kivy.app import App
from kivy_garden.mapview import MapMarker, MapView, MapMarkerPopup
from kivy.clock import Clock
from kivy.uix.label import Label
from kivy.graphics import Color, Rectangle
from lineMapLayer import LineMapLayer
from datasourceMQ import DatasourceMq as Datasource


class TrafficLightMarker(MapMarkerPopup):
    def __init__(self, cars_waiting: int, **kwargs):
        kwargs.setdefault("source", "images/traffic_light.png")
        super().__init__(**kwargs)

        self._label = Label(text="Cars: 0", font_size=14, color=(0, 0, 0, 1))
        self.add_widget(self._label)
        #self.add_widget(Label(text="Cars: 0", font_size=14, color=(0, 0, 0, 1)))
        # self._label = Label(
        #     text=f"Cars: {cars_waiting}",
        #     color=(1, 1, 1, 1),
        #     font_size=12,
        #     size_hint=(None, None),
        # )

    def update_cars_waiting(self, cars_waiting: int) -> None:
        self._label.text = f"Cars: {cars_waiting}"



class MapViewApp(App):
    def __init__(self, **kwargs):
        super().__init__()
        self.hazardsPoints = []
        self.traffic_light_markers = {}
        # додати необхідні змінні

    def on_start(self):
        """
        Встановлює необхідні маркери, викликає функцію для оновлення мапи
        """
        self.datasource = Datasource(1)
        Clock.schedule_interval(self.update, 1)

    def update(self, *args):
        """
        Викликається регулярно для оновлення мапи
        """
        points = self.datasource.get_new_points()
        traffic_lights = self.datasource.get_new_traffic_lights()
        print(traffic_lights)
        if len(points) == 0 and len(traffic_lights) == 0:
            return
        for point in points:
            if (point[2] != 'POTHOLE' and len(self.hazardsPoints) > 0):
                self.set_pothole_marker(self.hazardsPoints[int(len(self.hazardsPoints) / 2)])
                self.hazardsPoints = []

            if (point[2] == 'POTHOLE'):
                self.hazardsPoints.append(point)

            if (point[2] == 'BUMP'):
                self.set_bump_marker(point)

            if (point[3] == 'BAD AIR'):
                self.set_bad_air_marker(point)

            self.map_layer.add_point((point[0], point[1]))
        if points:
            self.update_car_marker(points[-1])
        for light in traffic_lights:
            self.update_traffic_light_marker(light)

    def update_car_marker(self, point):
        """
        Оновлює відображення маркера машини на мапі
        :param point: GPS координати
        """
        self.map_view.remove_marker(self.car_marker)
        self.car_marker.lon = point[0]
        self.car_marker.lat = point[1]
        self.map_view.add_marker(self.car_marker)

    def set_pothole_marker(self, point):
        """
        Встановлює маркер для ями
        :param point: GPS координати
        """
        self.map_view.add_marker(MapMarker(
            lon=point[0],
            lat=point[1],
            source="images/pothole.png",
        ))

    def set_bump_marker(self, point):
        """
        Встановлює маркер для лежачого поліцейського
        :param point: GPS координати
        """
        self.map_view.add_marker(MapMarker(
            lon=point[0],
            lat=point[1],
            source="images/bump.png",
        ))

    def set_bad_air_marker(self, point):
        self.map_view.add_marker(MapMarker(
            lon=point[0],
            lat=point[1],
            source="images/bad_air.png",
        ))

    def update_traffic_light_marker(self, light):
        """
        Оновлює відображення маркера світлофора на мапі
        :param light: (lat, lon, cars_waiting, traffic_light_id)
        """
        lat, lon, cars_waiting, traffic_light_id = light
        marker = self.traffic_light_markers.get(traffic_light_id)
        if marker is None:
            marker = TrafficLightMarker(cars_waiting=cars_waiting, lon=lon, lat=lat)
            self.traffic_light_markers[traffic_light_id] = marker
            self.map_view.add_marker(marker)
        else:
            marker.update_cars_waiting(cars_waiting)

    def build(self):
        """
        Ініціалізує мапу MapView(zoom, lat, lon)
        :return: мапу
        """
        self.map_layer = LineMapLayer()
        self.map_view = MapView(
            zoom=15,
            lon=50.45038,
            lat=30.52454
        )
        self.map_view.add_layer(self.map_layer, mode="scatter")
        self.car_marker = MapMarker(
            lon=50.450386085935094,
            lat=30.524547100067142,
            source="images/car.png",
        )
        self.map_view.add_marker(self.car_marker)
        return self.map_view


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(MapViewApp().async_run(async_lib="asyncio"))
    loop.close()
