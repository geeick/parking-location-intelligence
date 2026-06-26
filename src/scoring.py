import pandas as pd


DEMAND_WEIGHTS = {
    "businesses": 0.7,
    "tourist_attractions": 1.4,
    "restaurants": 0.9,
    "venues": 1.5,
}

RADIUS_WEIGHTS = {
    1: 3.0,
    3: 1.5,
    5: 0.75,
}

PARKING_COMPETITION_WEIGHTS = {
    1: 1.2,
    3: 0.6,
    5: 0.25,
}


def add_location_scores(df: pd.DataFrame) -> pd.DataFrame:
    """
    Adds:
    - location_score_raw
    - location_score_0_100
    - demand_generator_count_1mi
    - demand_generator_count_3mi
    - demand_generator_count_5mi
    - parking_competition_count_1mi
    - parking_competition_count_3mi
    - parking_competition_count_5mi
    """

    df = df.copy()

    for radius in [1, 3, 5]:
        df[f"demand_generator_count_{radius}mi"] = 0

        for category in DEMAND_WEIGHTS:
            col = f"{category}_{radius}mi"

            if col not in df.columns:
                df[col] = 0

            df[f"demand_generator_count_{radius}mi"] += df[col].fillna(0)

        parking_col = f"nearby_parking_lots_{radius}mi"

        if parking_col not in df.columns:
            df[parking_col] = 0

        df[f"parking_competition_count_{radius}mi"] = df[parking_col].fillna(0)

    raw_scores = []

    for _, row in df.iterrows():
        demand_score = 0
        competition_penalty = 0

        for radius, radius_weight in RADIUS_WEIGHTS.items():
            for category, category_weight in DEMAND_WEIGHTS.items():
                col = f"{category}_{radius}mi"
                demand_score += row.get(col, 0) * category_weight * radius_weight

        for radius, penalty_weight in PARKING_COMPETITION_WEIGHTS.items():
            col = f"nearby_parking_lots_{radius}mi"
            competition_penalty += row.get(col, 0) * penalty_weight

        raw_score = demand_score - competition_penalty
        raw_scores.append(raw_score)

    df["location_score_raw"] = raw_scores

    min_score = df["location_score_raw"].min()
    max_score = df["location_score_raw"].max()

    if max_score == min_score:
        df["location_score_0_100"] = 50
    else:
        df["location_score_0_100"] = (
            100
            * (df["location_score_raw"] - min_score)
            / (max_score - min_score)
        )

    df["location_score_raw"] = df["location_score_raw"].round(2)
    df["location_score_0_100"] = df["location_score_0_100"].round(1)

    return df

    