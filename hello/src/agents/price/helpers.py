from datetime import datetime
from typing import Literal

from pydantic import BaseModel


class FlatFeatures(BaseModel):
    distance_city_center: float
    distance_public_transport: float
    distance_school: float
    distance_shop: float
    building_type: Literal["cegła", "blok", "nowe budownictwo"]
    date_construction: datetime
    area: float
    n_rooms: int
    nth_floor: int
    is_furnished: bool
    has_balcony: bool
    has_elevator: bool
    has_parking: bool
    has_security: bool
    price: float
    city: str
    district: str

    @staticmethod
    def from_dict(data: dict) -> "FlatFeatures":
        return FlatFeatures(
            distance_city_center=data["odleglosc_od_centrum_miasta_km"],
            distance_public_transport=data["odleglosc_do_komunikacji_miejskiej_m"],
            distance_school=data["odleglosc_do_najblizszej_szkoly_m"],
            distance_shop=data["odleglosc_do_najblizszego_sklepu_spozywczego_m"],
            building_type=data["rodzaj_budynku"],
            date_construction=datetime.strptime(data["data_budowy"], "%Y-%m-%d"),
            area=data["powierzchnia_m2"],
            n_rooms=data["liczba_pokoi"],
            nth_floor=data["pietro"],
            is_furnished=data["czy_umeblowane"] == "tak",
            has_balcony=data["czy_balkon"] == "tak",
            has_elevator=data["czy_winda"] == "tak",
            has_parking=data["czy_parking"] == "tak",
            has_security=data["czy_ochrona"] == "tak",
            price=data["cena_mieszkania_zl"],
            city=data["miasto"],
            district=data["dzielnica"],
        )

    def to_dict(self) -> dict:
        return {
            "odleglosc_od_centrum_miasta_km": self.distance_city_center,
            "odleglosc_do_komunikacji_miejskiej_m": self.distance_public_transport,
            "odleglosc_do_najblizszej_szkoly_m": self.distance_school,
            "odleglosc_do_najblizszego_sklepu_spozywczego_m": self.distance_shop,
            "rodzaj_budynku": self.building_type,
            "data_budowy": self.date_construction.strftime("%Y-%m-%d"),
            "powierzchnia_m2": self.area,
            "liczba_pokoi": self.n_rooms,
            "pietro": self.nth_floor,
            "czy_umeblowane": "tak" if self.is_furnished else "nie",
            "czy_balkon": "tak" if self.has_balcony else "nie",
            "czy_winda": "tak" if self.has_elevator else "nie",
            "czy_parking": "tak" if self.has_parking else "nie",
            "czy_ochrona": "tak" if self.has_security else "nie",
            "cena_mieszkania_zl": self.price,
            "miasto": self.city,
            "dzielnica": self.district,
        }

    @staticmethod
    def similarity_score(flat1: "FlatFeatures", flat2: "FlatFeatures") -> float:
        """Calcuates how close to each other are two flats (normalized to 1)."""

        def _get_absolute_difference(flat1_attrval: float, flat2_attrval: float, max_diff: float) -> float:
            absolute_diff = abs(flat1_attrval - flat2_attrval)
            if absolute_diff > max_diff:
                absolute_diff = max_diff
            return (max_diff - absolute_diff) / max_diff

        score = 0.0
        if flat1.city == flat2.city:
            score += 0.5
            if flat1.district == flat2.district:
                score += 0.5

        for attr in ["has_balcony", "has_elevator", "has_parking", "has_security"]:
            if getattr(flat1, attr) == getattr(flat2, attr):
                score += 1.0
        for attr in ["building_type"]:
            if getattr(flat1, attr) == getattr(flat2, attr):
                score += 0.5
        for attr in ["is_furnished"]:
            if getattr(flat1, attr) == getattr(flat2, attr):
                score += 1.5

        for attr, max_diff in zip(
            [
                "distance_city_center",
                "distance_public_transport",
                "distance_school",
                "distance_shop",
                "area",
                "n_rooms",
                "nth_floor",
            ],
            [10.0, 1500.0, 3000.0, 1500.0, 80.0, 4.0, 4.0],
        ):
            score += _get_absolute_difference(getattr(flat1, attr), getattr(flat2, attr), max_diff)

        score += _get_absolute_difference(flat1.date_construction.year, flat2.date_construction.year, 15.0)

        return score / 15.0
