from typing import List, Dict, Any


def transform_data(data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    transformed = []
    for record in data:
        transformed.append({
            "id": record["id"],
            "title": record.get("title", ""),
            "description": record.get("description", ""),
            "imdb_rating": record.get("rating", 0),
            "genres": record.get("genres", "").split(",") if record.get("genres") else [],
            "actors": [{"id": actor_id, "name": name} for actor_id, name in zip(record.get("actors_ids", []), record.get("actors_names", []))],
            "directors": [{"id": director_id, "name": name} for director_id, name in zip(record.get("directors_ids", []), record.get("directors_names", []))],
            "writers": [{"id": writer_id, "name": name} for writer_id, name in zip(record.get("writers_ids", []), record.get("writers_names", []))],
        })
    return transformed