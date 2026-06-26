import folium
import pandas as pd


def get_score_color(score):
    if pd.isna(score):
        return "gray"

    if score >= 75:
        return "green"

    if score >= 50:
        return "orange"

    return "red"


def build_location_map(df, selected_location=None):
    """
    Creates a Folium map showing every parking lot.
    If selected_location is provided, draws 1, 3, and 5 mile circles.
    """

    clean_df = df.dropna(subset=["lat", "lon"]).copy()

    if clean_df.empty:
        return folium.Map(location=[34.0522, -118.2437], zoom_start=10)

    center_lat = clean_df["lat"].mean()
    center_lon = clean_df["lon"].mean()

    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=12,
        tiles="OpenStreetMap"
    )

    for _, row in clean_df.iterrows():
        name = row.get("location_name", "Parking lot")
        address = row.get("address", "")
        score = row.get("location_score_0_100", None)

        popup_html = f"""
        <b>{name}</b><br>
        {address}<br><br>

        <b>Location score:</b> {score}<br><br>

        <b>Demand generators</b><br>
        1 mi: {row.get("demand_generator_count_1mi", 0)}<br>
        3 mi: {row.get("demand_generator_count_3mi", 0)}<br>
        5 mi: {row.get("demand_generator_count_5mi", 0)}<br><br>

        <b>Nearby parking competitors</b><br>
        1 mi: {row.get("parking_competition_count_1mi", 0)}<br>
        3 mi: {row.get("parking_competition_count_3mi", 0)}<br>
        5 mi: {row.get("parking_competition_count_5mi", 0)}
        """

        folium.CircleMarker(
            location=[row["lat"], row["lon"]],
            radius=9,
            popup=folium.Popup(popup_html, max_width=350),
            tooltip=f"{name}: score {score}",
            color=get_score_color(score),
            fill=True,
            fill_opacity=0.75
        ).add_to(m)

    if selected_location:
        selected_rows = clean_df[clean_df["location_name"] == selected_location]

        if not selected_rows.empty:
            row = selected_rows.iloc[0]

            circles = [
                (1, "1 mile"),
                (3, "3 miles"),
                (5, "5 miles"),
            ]

            for miles, label in circles:
                folium.Circle(
                    location=[row["lat"], row["lon"]],
                    radius=miles * 1609.344,
                    popup=label,
                    fill=False,
                    weight=2
                ).add_to(m)

    return m


    