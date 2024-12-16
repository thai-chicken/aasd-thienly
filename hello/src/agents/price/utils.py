import json
from typing import List, Union

from src.agents.price.helpers import FlatFeatures

PATH_FLAT_PARAMS = "data/prices/flat_params.json"
MAX_SIMILAR_FLATS = 3


def get_flat_features(city: str, address: str) -> Union[FlatFeatures, None]:
    """ """
    with open(PATH_FLAT_PARAMS, "r") as file:
        data = json.load(file)

    if city not in data or address not in data[city]:
        return None

    return FlatFeatures.from_dict(data[city][address])


def load_accessible_flats(json_file_path: str) -> List[FlatFeatures]:
    """ """
    with open(json_file_path, "r") as file:
        data = json.load(file)

    return [FlatFeatures.from_dict(item) for item in data]


def get_similar_flats(service_flats: List[FlatFeatures], target_flat: FlatFeatures) -> List[FlatFeatures]:
    flats_scores = [(flat, FlatFeatures.similarity_score(flat, target_flat)) for flat in service_flats]
    sorted_flats = sorted(flats_scores, key=lambda x: x[1], reverse=True)
    return [{"flat": flat, "score": score} for flat, score in sorted_flats[:MAX_SIMILAR_FLATS]]
