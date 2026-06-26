# VERSION: parking_prices_v5_top_price_map
# This is the NEW app.py with:
# - CSV-impact scoring
# - more nearby businesses
# - watch_note support
# - visible Lots to Watch section
# - renamed blank template download


import math
import re
from urllib.parse import quote_plus
from datetime import date, datetime, timedelta

import folium
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
from folium.plugins import HeatMap
from streamlit_folium import st_folium


# ============================================================
# FIXED PARKING LOTS
# Coordinates are starter coordinates so the app works without APIs.
# Replace lat/lon with exact lot coordinates when you have them.
# ============================================================

PARKING_LOTS = [
    {"lot_id": "100_venice_way", "name": "100 Venice Way Parking", "display": "100 Venice Way", "address": "100 Venice Way", "lat": 33.9872, "lon": -118.4737, "zone": "Venice Beach"},
    {"lot_id": "102_washington_arbor_2", "name": "102 Washington Parking (Arbor 2)", "display": "102 Washington Blvd", "address": "102 Washington Blvd", "lat": 33.9808, "lon": -118.4638, "zone": "Washington/Marina"},
    {"lot_id": "102_washington_arbor", "name": "102 Washington Parking (Arbor)", "display": "102 Washington Parking", "address": "102 Washington Blvd", "lat": 33.9809, "lon": -118.4642, "zone": "Washington/Marina"},
    {"lot_id": "11801_olympic", "name": "11801 W Olympic Blvd Parking", "display": "Cadillac Hotel", "address": "11801 W Olympic Blvd", "lat": 34.0318, "lon": -118.4493, "zone": "West LA"},
    {"lot_id": "1218_half_lincoln", "name": "1218 1/2 Lincoln Blvd Parking", "display": "1218 1/2 Lincoln", "address": "1218 1/2 Lincoln Blvd", "lat": 33.9948, "lon": -118.4558, "zone": "Lincoln/Venice"},
    {"lot_id": "121_windward", "name": "121 Windward Parking", "display": "121 Windward - BOA Venice", "address": "121 Windward Ave", "lat": 33.9871, "lon": -118.4716, "zone": "Venice Beach"},
    {"lot_id": "124_washington_grand_canal", "name": "124 Washington Parking (Grand Canal)", "display": "124 Washington Blvd", "address": "124 Washington Blvd", "lat": 33.9810, "lon": -118.4652, "zone": "Washington/Marina"},
    {"lot_id": "139_south_beverly", "name": "139 South Beverly Parking", "display": "139 S Beverly", "address": "139 S Beverly Dr", "lat": 34.0646, "lon": -118.3993, "zone": "Beverly Hills"},
    {"lot_id": "1501_main", "name": "1501 Main Parking", "display": "1501 Main St", "address": "1501 Main St", "lat": 34.0138, "lon": -118.4925, "zone": "Santa Monica"},
    {"lot_id": "18th_avenue", "name": "18th Avenue Parking", "display": "18th Avenue", "address": "18th Ave", "lat": 33.9844, "lon": -118.4686, "zone": "Venice Beach"},
    {"lot_id": "2415_main_edgemar", "name": "2415 Main St Parking (Edgemar)", "display": "2415 Main Street", "address": "2415 Main St", "lat": 34.0040, "lon": -118.4864, "zone": "Main Street"},
    {"lot_id": "29_windward", "name": "29 Windward Ave Parking **", "display": "29 Windward Ave", "address": "29 Windward Ave", "lat": 33.9870, "lon": -118.4730, "zone": "Venice Beach"},
    {"lot_id": "3016_main", "name": "3016 Main Parking", "display": "3016 Main Street (T2P)", "address": "3016 Main St", "lat": 33.9990, "lon": -118.4809, "zone": "Main Street"},
    {"lot_id": "601_ocean_front", "name": "601 Ocean Front Walk Parking **", "display": "601 Ocean Front Walk", "address": "601 Ocean Front Walk", "lat": 33.9933, "lon": -118.4770, "zone": "Venice Beach"},
    {"lot_id": "6125_hollywood", "name": "6125 Hollywood Blvd Parking **", "display": "6125 Hollywood", "address": "6125 Hollywood Blvd", "lat": 34.1016, "lon": -118.3246, "zone": "Hollywood"},
    {"lot_id": "909_ocean_front", "name": "909 OCEAN FRONT WALK Parking **", "display": "909 Ocean Front", "address": "909 Ocean Front Walk", "lat": 33.9892, "lon": -118.4752, "zone": "Venice Beach"},
    {"lot_id": "909_garage", "name": "909 (Garage) Parking", "display": "909 Garage", "address": "909 Ocean Front Walk", "lat": 33.9894, "lon": -118.4747, "zone": "Venice Beach"},
    {"lot_id": "801_speedway", "name": "801 Speedway Parking", "display": "801 Ocean Front Walk", "address": "801 Speedway", "lat": 33.9908, "lon": -118.4748, "zone": "Venice Beach"},
    {"lot_id": "801_ocean_front", "name": "801 Ocean Front Walk Parking", "display": "801 Ocean Front Walk", "address": "801 Ocean Front Walk", "lat": 33.9906, "lon": -118.4754, "zone": "Venice Beach"},
    {"lot_id": "407_colorado", "name": "407 Colorado Parking", "display": "Bank of the West", "address": "407 Colorado Ave", "lat": 34.0147, "lon": -118.4910, "zone": "Santa Monica"},
    {"lot_id": "5_dudley", "name": "5 Dudley ave, Venice Parking", "display": "Cadillac Hotel", "address": "5 Dudley Ave", "lat": 33.9926, "lon": -118.4763, "zone": "Venice Beach"},
    {"lot_id": "25_rose", "name": "25 Rose Parking", "display": "25 Rose", "address": "25 Rose Ave", "lat": 33.9968, "lon": -118.4780, "zone": "Rose"},
    {"lot_id": "gladstones", "name": "Gladstones Parking **", "display": "Gladstones", "address": "17300 Pacific Coast Hwy", "lat": 34.0385, "lon": -118.5594, "zone": "PCH/Beach"},
    {"lot_id": "155_washington", "name": "155 Washington Parking", "display": "Remax (155 Washington)", "address": "155 Washington Blvd", "lat": 33.9814, "lon": -118.4637, "zone": "Washington/Marina"},
    {"lot_id": "220_rose", "name": "220 Rose Parking", "display": "Rose Cafe", "address": "220 Rose Ave", "lat": 33.9973, "lon": -118.4752, "zone": "Rose"},
    {"lot_id": "816_washington_scopa_2", "name": "816 Washington Parking (Scopa 2)", "display": "Scopa Restaurant", "address": "816 Washington Blvd", "lat": 33.9890, "lon": -118.4529, "zone": "Washington/Marina"},
    {"lot_id": "2913_washington_scopa_1", "name": "2913 Washington Parking (Scopa 1)", "display": "2913 Washington", "address": "2913 Washington Blvd", "lat": 33.9882, "lon": -118.4537, "zone": "Washington/Marina"},
    {"lot_id": "46_market", "name": "46 Market Street Parking", "display": "Venice Market", "address": "46 Market St", "lat": 33.9878, "lon": -118.4729, "zone": "Venice Beach"},
    {"lot_id": "pardee", "name": "Pardee Parking **", "display": "Pardee", "address": "Pardee", "lat": 33.9950, "lon": -118.4748, "zone": "Venice Beach"},
]


# ============================================================
# DEFAULT BUSINESS PATTERNS
# These are used when the CSV does not include record_type=business.
# If your CSV includes business rows, they will be added into the score too.
# ============================================================

def default_businesses_for_lot(lot):
    zone = lot.get("zone", "")
    display = lot["display"]

    if zone == "Hollywood":
        return [
            {"business": "Hollywood Walk of Fame", "category": "tourism", "base": 82, "weekday_peak": "11-22", "weekend_peak": "10-24", "source": "default"},
            {"business": "Ovation Hollywood", "category": "retail/tourism", "base": 74, "weekday_peak": "11-20", "weekend_peak": "10-22", "source": "default"},
            {"business": "TCL Chinese Theatre", "category": "entertainment", "base": 70, "weekday_peak": "13-22", "weekend_peak": "11-23", "source": "default"},
            {"business": "El Capitan Theatre", "category": "entertainment", "base": 64, "weekday_peak": "14-22", "weekend_peak": "11-23", "source": "default"},
            {"business": "Hollywood nightlife", "category": "nightlife", "base": 84, "weekday_peak": "19-24", "weekend_peak": "18-2", "source": "default"},
            {"business": "Hollywood restaurants", "category": "food", "base": 70, "weekday_peak": "12-14,18-22", "weekend_peak": "11-15,18-23", "source": "default"},
            {"business": "Nearby hotels", "category": "hotel", "base": 58, "weekday_peak": "8-11,15-20", "weekend_peak": "9-12,15-21", "source": "default"},
            {"business": "Tour buses / sightseeing", "category": "tourism", "base": 66, "weekday_peak": "10-17", "weekend_peak": "9-18", "source": "default"},
        ]

    if zone == "Beverly Hills":
        return [
            {"business": "Rodeo Drive retail", "category": "retail", "base": 72, "weekday_peak": "11-18", "weekend_peak": "11-18", "source": "default"},
            {"business": "Beverly Hills restaurants", "category": "food", "base": 68, "weekday_peak": "12-14,18-22", "weekend_peak": "11-15,18-22", "source": "default"},
            {"business": "Nearby offices", "category": "office", "base": 75, "weekday_peak": "8-18", "weekend_peak": "0-0", "source": "default"},
            {"business": "Medical / appointment traffic", "category": "services", "base": 60, "weekday_peak": "9-17", "weekend_peak": "10-14", "source": "default"},
            {"business": "Hotel guest arrivals", "category": "hotel", "base": 55, "weekday_peak": "8-11,15-20", "weekend_peak": "9-12,15-21", "source": "default"},
            {"business": "Luxury shopping overflow", "category": "retail", "base": 64, "weekday_peak": "13-18", "weekend_peak": "12-19", "source": "default"},
            {"business": "Lunch crowd", "category": "food", "base": 66, "weekday_peak": "11-14", "weekend_peak": "11-15", "source": "default"},
            {"business": "Dinner crowd", "category": "food", "base": 70, "weekday_peak": "18-22", "weekend_peak": "18-23", "source": "default"},
        ]

    if zone == "West LA":
        return [
            {"business": "West LA offices", "category": "office", "base": 76, "weekday_peak": "8-18", "weekend_peak": "0-0", "source": "default"},
            {"business": "Olympic Blvd restaurants", "category": "food", "base": 62, "weekday_peak": "12-14,18-21", "weekend_peak": "12-15,18-21", "source": "default"},
            {"business": "Commuter traffic", "category": "traffic", "base": 74, "weekday_peak": "7-10,16-19", "weekend_peak": "11-16", "source": "default"},
            {"business": "Medical / office appointments", "category": "services", "base": 64, "weekday_peak": "9-17", "weekend_peak": "0-0", "source": "default"},
            {"business": "Lunch restaurants", "category": "food", "base": 68, "weekday_peak": "11-14", "weekend_peak": "11-15", "source": "default"},
            {"business": "Evening restaurants", "category": "food", "base": 62, "weekday_peak": "18-21", "weekend_peak": "18-22", "source": "default"},
            {"business": "Westside errands / retail", "category": "retail", "base": 55, "weekday_peak": "10-18", "weekend_peak": "10-17", "source": "default"},
            {"business": "Event overflow from SoFi / Westside", "category": "event-overflow", "base": 48, "weekday_peak": "16-22", "weekend_peak": "12-22", "source": "default"},
        ]

    if zone == "PCH/Beach":
        return [
            {"business": "Gladstones", "category": "restaurant", "base": 84, "weekday_peak": "12-15,18-21", "weekend_peak": "11-21", "source": "default"},
            {"business": "PCH beach visitors", "category": "beach", "base": 80, "weekday_peak": "11-17", "weekend_peak": "10-18", "source": "default"},
            {"business": "Malibu / PCH scenic traffic", "category": "tourism", "base": 74, "weekday_peak": "10-18", "weekend_peak": "9-19", "source": "default"},
            {"business": "Beach picnic / family groups", "category": "beach", "base": 66, "weekday_peak": "11-16", "weekend_peak": "10-18", "source": "default"},
            {"business": "Sunset dinner traffic", "category": "food", "base": 72, "weekday_peak": "17-21", "weekend_peak": "16-22", "source": "default"},
            {"business": "Surfers / morning beach", "category": "beach", "base": 56, "weekday_peak": "6-10", "weekend_peak": "6-11", "source": "default"},
            {"business": "PCH commuter traffic", "category": "traffic", "base": 60, "weekday_peak": "7-10,16-19", "weekend_peak": "11-18", "source": "default"},
        ]

    if zone == "Santa Monica":
        return [
            {"business": "Santa Monica Pier", "category": "tourism", "base": 86, "weekday_peak": "11-20", "weekend_peak": "10-22", "source": "default"},
            {"business": "Third Street Promenade", "category": "retail", "base": 72, "weekday_peak": "11-19", "weekend_peak": "10-21", "source": "default"},
            {"business": "Santa Monica Beach", "category": "beach", "base": 78, "weekday_peak": "11-18", "weekend_peak": "10-20", "source": "default"},
            {"business": "Main Street restaurants", "category": "food", "base": 70, "weekday_peak": "12-14,18-22", "weekend_peak": "10-16,18-23", "source": "default"},
            {"business": "Hotel arrivals", "category": "hotel", "base": 58, "weekday_peak": "8-11,15-20", "weekend_peak": "9-12,15-21", "source": "default"},
            {"business": "Beach bike path traffic", "category": "recreation", "base": 62, "weekday_peak": "10-17", "weekend_peak": "9-19", "source": "default"},
            {"business": "Dinner near Ocean Ave", "category": "food", "base": 66, "weekday_peak": "18-22", "weekend_peak": "17-23", "source": "default"},
            {"business": "Shopping / errands", "category": "retail", "base": 60, "weekday_peak": "10-18", "weekend_peak": "10-19", "source": "default"},
        ]

    if zone == "Main Street":
        return [
            {"business": "Main Street restaurants", "category": "food", "base": 76, "weekday_peak": "12-14,18-22", "weekend_peak": "10-16,18-23", "source": "default"},
            {"business": "Edgemar / shops", "category": "retail", "base": 62, "weekday_peak": "10-18", "weekend_peak": "10-18", "source": "default"},
            {"business": "Coffee / brunch traffic", "category": "food", "base": 68, "weekday_peak": "8-11", "weekend_peak": "8-14", "source": "default"},
            {"business": "Fitness studios", "category": "fitness", "base": 58, "weekday_peak": "6-9,16-20", "weekend_peak": "8-12", "source": "default"},
            {"business": "Retail errands", "category": "retail", "base": 58, "weekday_peak": "10-18", "weekend_peak": "10-17", "source": "default"},
            {"business": "Beach walk spillover", "category": "beach", "base": 64, "weekday_peak": "11-17", "weekend_peak": "10-19", "source": "default"},
            {"business": "Dinner / nightlife", "category": "nightlife", "base": 70, "weekday_peak": "18-22", "weekend_peak": "18-23", "source": "default"},
            {"business": f"{display} demand anchor", "category": "anchor", "base": 64, "weekday_peak": "10-14,18-21", "weekend_peak": "10-17,18-22", "source": "default"},
        ]

    if zone == "Rose":
        return [
            {"business": "Rose Cafe", "category": "food", "base": 78, "weekday_peak": "8-14,18-21", "weekend_peak": "8-16,18-22", "source": "default"},
            {"business": "Rose Ave restaurants", "category": "food", "base": 74, "weekday_peak": "12-14,18-22", "weekend_peak": "10-16,18-23", "source": "default"},
            {"business": "Rose Ave retail", "category": "retail", "base": 62, "weekday_peak": "11-18", "weekend_peak": "10-18", "source": "default"},
            {"business": "Brunch crowd", "category": "food", "base": 72, "weekday_peak": "9-13", "weekend_peak": "9-15", "source": "default"},
            {"business": "Beach visitors", "category": "beach", "base": 66, "weekday_peak": "11-17", "weekend_peak": "10-19", "source": "default"},
            {"business": "Abbot Kinney spillover", "category": "retail/food", "base": 58, "weekday_peak": "12-18", "weekend_peak": "11-20", "source": "default"},
            {"business": "Evening dinner traffic", "category": "food", "base": 70, "weekday_peak": "18-22", "weekend_peak": "18-23", "source": "default"},
        ]

    if zone == "Washington/Marina":
        return [
            {"business": "Washington Blvd restaurants", "category": "food", "base": 75, "weekday_peak": "12-14,18-22", "weekend_peak": "11-16,18-23", "source": "default"},
            {"business": "Scopa Italian Roots", "category": "food", "base": 78, "weekday_peak": "18-22", "weekend_peak": "18-23", "source": "default"},
            {"business": "Marina / canal visitors", "category": "tourism", "base": 60, "weekday_peak": "11-17", "weekend_peak": "10-18", "source": "default"},
            {"business": "Brunch traffic", "category": "food", "base": 68, "weekday_peak": "9-13", "weekend_peak": "9-15", "source": "default"},
            {"business": "Dinner traffic", "category": "food", "base": 76, "weekday_peak": "18-22", "weekend_peak": "18-23", "source": "default"},
            {"business": "Bar / nightlife traffic", "category": "nightlife", "base": 62, "weekday_peak": "20-24", "weekend_peak": "19-2", "source": "default"},
            {"business": "Marina errands / local retail", "category": "retail", "base": 54, "weekday_peak": "10-18", "weekend_peak": "10-17", "source": "default"},
            {"business": f"{display} demand anchor", "category": "anchor", "base": 68, "weekday_peak": "11-14,18-22", "weekend_peak": "10-16,18-23", "source": "default"},
        ]

    if zone == "Lincoln/Venice":
        return [
            {"business": "Lincoln Blvd local businesses", "category": "retail/service", "base": 58, "weekday_peak": "9-18", "weekend_peak": "10-16", "source": "default"},
            {"business": "Commuter traffic", "category": "traffic", "base": 62, "weekday_peak": "7-10,16-19", "weekend_peak": "11-17", "source": "default"},
            {"business": "Local restaurants", "category": "food", "base": 62, "weekday_peak": "12-14,18-21", "weekend_peak": "11-15,18-22", "source": "default"},
            {"business": "Neighborhood errands", "category": "retail/service", "base": 52, "weekday_peak": "10-17", "weekend_peak": "10-16", "source": "default"},
            {"business": "Gym / fitness traffic", "category": "fitness", "base": 54, "weekday_peak": "6-9,16-20", "weekend_peak": "8-12", "source": "default"},
            {"business": "Venice spillover", "category": "beach/tourism", "base": 56, "weekday_peak": "11-17", "weekend_peak": "10-19", "source": "default"},
        ]

    return [
        {"business": "Venice Beach Boardwalk", "category": "beach/tourism", "base": 84, "weekday_peak": "11-18", "weekend_peak": "10-20", "source": "default"},
        {"business": "Windward Avenue restaurants", "category": "food", "base": 72, "weekday_peak": "12-14,18-22", "weekend_peak": "10-16,18-23", "source": "default"},
        {"business": "Hotel Erwin / rooftop area", "category": "hotel/nightlife", "base": 68, "weekday_peak": "15-23", "weekend_peak": "12-24", "source": "default"},
        {"business": "Venice Skate Park", "category": "recreation", "base": 66, "weekday_peak": "12-18", "weekend_peak": "10-19", "source": "default"},
        {"business": "Muscle Beach / gym area", "category": "recreation", "base": 62, "weekday_peak": "10-17", "weekend_peak": "10-18", "source": "default"},
        {"business": "Beach bike path", "category": "recreation", "base": 60, "weekday_peak": "10-17", "weekend_peak": "9-19", "source": "default"},
        {"business": "Tourist foot traffic", "category": "tourism", "base": 66, "weekday_peak": "12-17", "weekend_peak": "10-19", "source": "default"},
        {"business": "Boardwalk shops", "category": "retail", "base": 64, "weekday_peak": "11-18", "weekend_peak": "10-20", "source": "default"},
        {"business": "Dinner / bar traffic", "category": "food/nightlife", "base": 68, "weekday_peak": "18-23", "weekend_peak": "18-2", "source": "default"},
        {"business": f"{display} demand anchor", "category": "anchor", "base": 62, "weekday_peak": "10-16,18-21", "weekend_peak": "10-19", "source": "default"},
    ]


# ============================================================
# SAMPLE DATA IF NO CSV IS UPLOADED
# ============================================================

SAMPLE_WEEKLY_DATA = [
    {
        "date": (date.today() + timedelta(days=1)).isoformat(),
        "start_time": "18:00",
        "end_time": "22:00",
        "record_type": "event",
        "title": "Venice Beach Music Night",
        "parking_lot": "100 Venice Way Parking",
        "expected_people": 2400,
        "weather_condition": "",
        "temp_f": "",
        "rain_chance": "",
        "impact": 20,
        "lat": 33.9872,
        "lon": -118.4737,
        "notes": "Fake sample event",
    },
    {
        "date": (date.today() + timedelta(days=2)).isoformat(),
        "start_time": "10:00",
        "end_time": "18:00",
        "record_type": "event",
        "title": "Boardwalk Art Market",
        "parking_lot": "all",
        "expected_people": 5000,
        "weather_condition": "",
        "temp_f": "",
        "rain_chance": "",
        "impact": 15,
        "lat": "",
        "lon": "",
        "notes": "Affects beach lots",
    },
    {
        "date": (date.today() + timedelta(days=3)).isoformat(),
        "start_time": "",
        "end_time": "",
        "record_type": "holiday",
        "title": "Holiday / School Break",
        "parking_lot": "all",
        "expected_people": 0,
        "weather_condition": "",
        "temp_f": "",
        "rain_chance": "",
        "impact": 10,
        "lat": "",
        "lon": "",
        "notes": "Expected higher daytime traffic",
    },
    {
        "date": (date.today() + timedelta(days=1)).isoformat(),
        "start_time": "",
        "end_time": "",
        "record_type": "weather",
        "title": "Sunny beach weather",
        "parking_lot": "all",
        "expected_people": 0,
        "weather_condition": "sunny",
        "temp_f": 78,
        "rain_chance": 5,
        "impact": 8,
        "lat": "",
        "lon": "",
        "notes": "Good beach weather",
    },
]


# ============================================================
# HELPERS
# ============================================================

def norm(value):
    return str(value or "").strip().lower()


def normalize_lot_text(value):
    text = norm(value)
    return (
        text.replace("parking", "")
        .replace("**", "")
        .replace("(", "")
        .replace(")", "")
        .replace("-", " ")
        .replace("_", " ")
        .replace(",", " ")
        .replace(".", " ")
        .replace("  ", " ")
        .strip()
    )


def parse_hour(value, default=None):
    if value is None or str(value).strip() == "":
        return default

    text = str(value).strip()

    for fmt in ("%H:%M", "%H", "%I:%M %p", "%I %p"):
        try:
            return datetime.strptime(text, fmt).hour
        except ValueError:
            pass

    return default


def time_range_contains(range_text, selected_hour):
    if not range_text:
        return False

    ranges = [part.strip() for part in str(range_text).split(",") if part.strip()]

    for part in ranges:
        if "-" not in part:
            continue

        start_raw, end_raw = part.split("-", 1)
        start_hour = parse_hour(start_raw, 0)
        end_hour = parse_hour(end_raw, 24)

        if start_hour == end_hour:
            continue

        if start_hour < end_hour and start_hour <= selected_hour < end_hour:
            return True

        if start_hour > end_hour and (selected_hour >= start_hour or selected_hour < end_hour):
            return True

    return False


def extract_from_notes(notes, key):
    text = str(notes or "")
    match = re.search(rf"{re.escape(key)}\s*=\s*([^;]+)", text, flags=re.IGNORECASE)
    return match.group(1).strip() if match else ""


def normalize_weekly_csv(df):
    df = df.copy()
    df.columns = [str(c).strip().lower().replace(" ", "_") for c in df.columns]

    aliases = {
        "type": "record_type",
        "event_type": "record_type",
        "lot": "parking_lot",
        "lot_name": "parking_lot",
        "parking_lot_name": "parking_lot",
        "event": "title",
        "event_name": "title",
        "name": "title",
        "attendance": "expected_people",
        "expected_attendance": "expected_people",
        "people": "expected_people",
        "temperature": "temp_f",
        "rain": "rain_chance",
        "business_name": "business",
    }

    for old, new in aliases.items():
        if old in df.columns and new not in df.columns:
            df[new] = df[old]

    defaults = {
        "date": "",
        "start_time": "",
        "end_time": "",
        "record_type": "event",
        "title": "",
        "parking_lot": "all",
        "expected_people": 0,
        "weather_condition": "",
        "temp_f": "",
        "rain_chance": "",
        "impact": 0,
        "lat": "",
        "lon": "",
        "notes": "",
        "business": "",
        "category": "",
        "base_popularity": "",
        "weekday_peak": "",
        "weekend_peak": "",
        "source": "",
        "priority": "",
        "direction": "",
        "reason_type": "",
        "reason": "",
        "expected_impact": "",
        "suggested_action": "",
    }

    for col, default in defaults.items():
        if col not in df.columns:
            df[col] = default

    df["date_raw"] = df["date"].astype(str)
    df["date"] = pd.to_datetime(df["date"], errors="coerce").dt.date
    df["expected_people"] = pd.to_numeric(df["expected_people"], errors="coerce").fillna(0)
    df["impact"] = pd.to_numeric(df["impact"], errors="coerce").fillna(0)
    df["temp_f"] = pd.to_numeric(df["temp_f"], errors="coerce")
    df["rain_chance"] = pd.to_numeric(df["rain_chance"], errors="coerce")
    df["lat"] = pd.to_numeric(df["lat"], errors="coerce")
    df["lon"] = pd.to_numeric(df["lon"], errors="coerce")
    df["base_popularity"] = pd.to_numeric(df["base_popularity"], errors="coerce")
    df["record_type"] = df["record_type"].fillna("event").astype(str).str.lower().str.strip()

    return df


def haversine_miles(lat1, lon1, lat2, lon2):
    if pd.isna(lat2) or pd.isna(lon2):
        return None

    radius = 3958.8
    phi1 = math.radians(lat1)
    phi2 = math.radians(float(lat2))
    dphi = math.radians(float(lat2) - lat1)
    dlambda = math.radians(float(lon2) - lon1)

    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return 2 * radius * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def row_applies_to_lot(row, lot, event_radius_miles=12.0):
    raw_lot = str(row.get("parking_lot", "") or "").strip()

    if raw_lot == "" or raw_lot.lower() in {"all", "all lots", "everywhere"}:
        return True

    row_lot = normalize_lot_text(raw_lot)

    lot_names = [
        lot["lot_id"],
        lot["name"],
        lot["display"],
        lot["address"],
        lot.get("zone", ""),
    ]

    for candidate in lot_names:
        candidate_norm = normalize_lot_text(candidate)
        if candidate_norm and (row_lot == candidate_norm or row_lot in candidate_norm or candidate_norm in row_lot):
            return True

    # If the CSV row has coordinates, let it affect lots within radius.
    distance = haversine_miles(lot["lat"], lot["lon"], row.get("lat"), row.get("lon"))
    return distance is not None and distance <= event_radius_miles


def row_matches_date(row, selected_date):
    return not pd.isna(row.get("date")) and row.get("date") == selected_date


def row_matches_time(row, selected_hour, pre_event_window_hours=0):
    start_hour = parse_hour(row.get("start_time"), None)
    end_hour = parse_hour(row.get("end_time"), None)

    if start_hour is None and end_hour is None:
        return True

    if start_hour is None:
        start_hour = 0
    if end_hour is None:
        end_hour = 24

    # Exact active window.
    if start_hour == end_hour:
        active_now = True
    elif start_hour < end_hour:
        active_now = start_hour <= selected_hour < end_hour
    else:
        active_now = selected_hour >= start_hour or selected_hour < end_hour

    if active_now:
        return True

    # Events should influence parking before they start.
    if pre_event_window_hours > 0:
        diff = start_hour - selected_hour
        if 0 <= diff <= pre_event_window_hours:
            return True

    return False


def records_for_lot(weekly_df, lot, selected_date, selected_hour, record_type=None, event_radius_miles=12.0, pre_event_window_hours=4):
    if weekly_df.empty:
        return weekly_df

    df = weekly_df.copy()
    mask = df.apply(lambda row: row_applies_to_lot(row, lot, event_radius_miles), axis=1)
    mask = mask & df.apply(lambda row: row_matches_date(row, selected_date), axis=1)

    if record_type:
        mask = mask & (df["record_type"] == record_type)

    if record_type == "event":
        mask = mask & df.apply(lambda row: row_matches_time(row, selected_hour, pre_event_window_hours), axis=1)
    elif record_type in {"weather", "holiday"}:
        # Weather and holidays usually apply all day unless times are provided.
        mask = mask & df.apply(lambda row: row_matches_time(row, selected_hour, 0), axis=1)
    elif record_type == "business":
        # Business rows are reference rows. Date does not matter much; keep them for the selected week/day.
        pass

    return df[mask].copy()


def business_rows_from_csv(weekly_df, lot, selected_date, event_radius_miles=12.0):
    if weekly_df.empty or "record_type" not in weekly_df.columns:
        return []

    business_df = weekly_df[weekly_df["record_type"] == "business"].copy()

    if business_df.empty:
        return []

    rows = []

    for _, row in business_df.iterrows():
        if not row_applies_to_lot(row, lot, event_radius_miles):
            continue

        title = str(row.get("business") or row.get("title") or "").strip()
        if not title:
            continue

        base = row.get("base_popularity")
        if pd.isna(base):
            base = row.get("impact", 50)

        weekday_peak = str(row.get("weekday_peak") or "").strip() or extract_from_notes(row.get("notes"), "weekday_peak")
        weekend_peak = str(row.get("weekend_peak") or "").strip() or extract_from_notes(row.get("notes"), "weekend_peak")

        # Fallback to start/end time if the business row does not have peak fields.
        if not weekday_peak and row.get("start_time"):
            weekday_peak = f"{row.get('start_time')}-{row.get('end_time') or '24'}"
        if not weekend_peak and row.get("start_time"):
            weekend_peak = f"{row.get('start_time')}-{row.get('end_time') or '24'}"

        rows.append({
            "business": title,
            "category": str(row.get("category") or "csv").strip() or "csv",
            "base": float(base or 50),
            "weekday_peak": weekday_peak or "10-18",
            "weekend_peak": weekend_peak or "10-18",
            "source": "uploaded CSV",
        })

    return rows


def popularity_for_business(business, selected_date, selected_hour):
    weekday = selected_date.weekday()
    is_weekend = weekday >= 5
    base = float(business.get("base", 50))

    peak_field = "weekend_peak" if is_weekend else "weekday_peak"
    in_peak = time_range_contains(business.get(peak_field, ""), selected_hour)

    if in_peak:
        score = min(base + 25, 100)
        status = "Peak"
    else:
        score = max(base - 20, 5)
        status = "Off peak"

    return round(score, 1), status



def date_matches_watch_note(row, selected_date):
    parsed_date = row.get("date")

    if not pd.isna(parsed_date) and parsed_date == selected_date:
        return True

    raw = str(row.get("date_raw", "") or row.get("date", "") or "")

    # Support rows like "2026-06-29 to 2026-07-05"
    if "to" in raw:
        parts = [part.strip() for part in raw.split("to", 1)]
        if len(parts) == 2:
            start = pd.to_datetime(parts[0], errors="coerce")
            end = pd.to_datetime(parts[1], errors="coerce")
            if not pd.isna(start) and not pd.isna(end):
                return start.date() <= selected_date <= end.date()

    return False


def watch_note_applies_to_lot(row, lot):
    raw = norm(row.get("parking_lot"))

    if raw in {"", "all", "all lots", "everywhere"}:
        return True

    candidate_text = " ".join([
        norm(lot.get("lot_id")),
        norm(lot.get("name")),
        norm(lot.get("display")),
        norm(lot.get("address")),
        norm(lot.get("zone")),
    ])

    if any(part.strip() and part.strip() in candidate_text for part in raw.split(";")):
        return True

    zone = norm(lot.get("zone"))
    name = candidate_text

    group_rules = [
        ("beach", zone in {"venice beach", "santa monica", "main street", "rose", "washington/marina", "pch/beach"} or "ocean front" in name or "venice" in name),
        ("coastal", zone in {"venice beach", "santa monica", "main street", "rose", "washington/marina", "pch/beach"}),
        ("venice", "venice" in name or zone in {"venice beach", "lincoln/venice"}),
        ("santa monica", zone == "santa monica"),
        ("main street", zone == "main street"),
        ("rose", zone == "rose"),
        ("washington", zone == "washington/marina" or "washington" in name),
        ("marina", zone == "washington/marina"),
        ("hollywood", zone == "hollywood"),
        ("beverly", zone == "beverly hills"),
        ("west la", zone == "west la"),
        ("westside", zone in {"west la", "beverly hills", "santa monica"}),
    ]

    return any(keyword in raw and applies for keyword, applies in group_rules)


def watch_notes_for_lot(weekly_df, lot, selected_date):
    if weekly_df.empty or "record_type" not in weekly_df.columns:
        return pd.DataFrame()

    notes = weekly_df[weekly_df["record_type"] == "watch_note"].copy()

    if notes.empty:
        return notes

    mask = notes.apply(lambda row: date_matches_watch_note(row, selected_date), axis=1)
    mask = mask & notes.apply(lambda row: watch_note_applies_to_lot(row, lot), axis=1)

    return notes[mask].copy()


def all_watch_notes_for_date(weekly_df, selected_date):
    if weekly_df.empty or "record_type" not in weekly_df.columns:
        return pd.DataFrame()

    notes = weekly_df[weekly_df["record_type"] == "watch_note"].copy()

    if notes.empty:
        return notes

    return notes[notes.apply(lambda row: date_matches_watch_note(row, selected_date), axis=1)].copy()



def watch_note_priority_value(row):
    text = " ".join([
        str(row.get("priority", "")),
        str(row.get("title", "")),
    ]).lower()

    if "critical" in text:
        return 4
    if "high" in text:
        return 3
    if "medium" in text:
        return 2
    if "low" in text:
        return 1
    if "manual" in text or "closure placeholder" in text:
        return 0
    return 1


def watch_note_priority_label(row):
    priority = str(row.get("priority", "") or "").strip()
    if priority:
        return priority

    title = str(row.get("title", "") or "")
    lowered = title.lower()

    if "critical" in lowered:
        return "Critical"
    if "high" in lowered:
        return "High"
    if "medium" in lowered:
        return "Medium"
    if "manual" in lowered:
        return "Manual update"
    return "Watch"


def watch_note_summary_fields(note):
    title = str(note.get("title") or "Watch note").strip()
    lot_text = str(note.get("parking_lot") or "All lots").strip()
    time_window = str(note.get("start_time") or "All day").strip()
    priority = watch_note_priority_label(note)
    direction = str(note.get("direction") or "").strip()

    reason = str(note.get("reason") or "").strip()
    if not reason:
        reason = str(note.get("notes") or "").strip()

    reason_type = str(note.get("reason_type") or "").strip()
    expected_impact = str(note.get("expected_impact") or "").strip()
    suggested_action = str(note.get("suggested_action") or "").strip()

    if not suggested_action and "Suggested action:" in reason:
        pieces = reason.split("Suggested action:", 1)
        reason = pieces[0].strip()
        suggested_action = pieces[1].strip()

    return {
        "title": title,
        "lot_text": lot_text,
        "time_window": time_window,
        "priority": priority,
        "direction": direction,
        "reason_type": reason_type,
        "reason": reason,
        "expected_impact": expected_impact,
        "suggested_action": suggested_action,
    }


def is_manual_placeholder(note):
    text = " ".join([
        str(note.get("priority", "")),
        str(note.get("title", "")),
        str(note.get("reason_type", "")),
        str(note.get("notes", "")),
        str(note.get("reason", "")),
    ]).lower()

    return "needs manual update" in text or "closure placeholder" in text or "manual closure checklist" in text


def filtered_real_watch_notes(notes_df):
    if notes_df.empty:
        return notes_df
    return notes_df[~notes_df.apply(is_manual_placeholder, axis=1)].copy()


def sort_watch_notes(notes_df):
    if notes_df.empty:
        return notes_df

    df = notes_df.copy()
    df["_priority_sort"] = df.apply(watch_note_priority_value, axis=1)
    df["_date_sort"] = pd.to_datetime(df.get("date_raw", df.get("date")), errors="coerce")
    return df.sort_values(["_priority_sort", "_date_sort"], ascending=[False, True]).drop(
        columns=["_priority_sort", "_date_sort"],
        errors="ignore",
    )


def render_watch_note_cards(notes_df):
    if notes_df.empty:
        st.info("No specific lots-to-watch notes match this selection.")
        return

    notes_df = sort_watch_notes(notes_df)

    for _, note in notes_df.iterrows():
        fields = watch_note_summary_fields(note)

        priority_value = watch_note_priority_value(note)

        # Build clean Markdown with real line breaks.
        lines = [
            f"### {fields['title']}",
            f"**Priority:** {fields['priority']}",
        ]

        if fields["direction"]:
            lines.append(f"**Direction:** {fields['direction']}")

        lines.extend([
            f"**When:** {fields['time_window']}",
            f"**Lots:** {fields['lot_text']}",
        ])

        if fields["reason_type"]:
            lines.append(f"**Why:** {fields['reason_type']}")

        if fields["reason"]:
            lines.append(fields["reason"])

        if fields["expected_impact"]:
            lines.append(f"**Expected impact:** {fields['expected_impact']}")

        if fields["suggested_action"]:
            lines.append(f"**Suggested action:** {fields['suggested_action']}")

        body = "\n\n".join(lines)

        if priority_value >= 4:
            st.error(body)
        elif priority_value >= 3:
            st.warning(body)
        else:
            st.info(body)


def weather_modifier(weather_rows):
    if weather_rows.empty:
        return 0, "No weather record uploaded for this time."

    modifier = 0
    messages = []

    for _, row in weather_rows.iterrows():
        condition = norm(row.get("weather_condition"))
        temp = row.get("temp_f")
        rain = row.get("rain_chance")
        manual_impact = float(row.get("impact", 0) or 0)

        modifier += manual_impact

        if "rain" in condition or (not pd.isna(rain) and rain >= 50):
            modifier -= 18
            messages.append("Rain likely reduces beach/tourist parking.")
        elif "sun" in condition or "clear" in condition:
            modifier += 8
            messages.append("Sunny weather likely increases beach/tourist parking.")

        if not pd.isna(temp):
            if temp >= 82:
                modifier += 6
                messages.append("Warm weather likely increases beach demand.")
            elif temp <= 55:
                modifier -= 8
                messages.append("Cold weather may reduce casual visitors.")

    if not messages:
        messages.append("Weather impact comes from uploaded CSV impact value.")

    return round(modifier, 1), " ".join(messages)


def event_score(event_rows):
    if event_rows.empty:
        return 0

    score = 0
    for _, row in event_rows.iterrows():
        expected = float(row.get("expected_people", 0) or 0)
        manual = float(row.get("impact", 0) or 0)

        # Expected people score: 1000 people roughly adds 4 points, capped.
        score += min(expected / 1000 * 4, 35)
        score += manual

    return round(min(score, 80), 1)


def holiday_score(holiday_rows):
    if holiday_rows.empty:
        return 0

    return round(min(30, holiday_rows["impact"].astype(float).sum() + 10), 1)


def calculate_lot_score(lot, weekly_df, selected_date, selected_hour, event_radius_miles=12.0, pre_event_window_hours=4):
    default_businesses = default_businesses_for_lot(lot)
    csv_businesses = business_rows_from_csv(weekly_df, lot, selected_date, event_radius_miles)

    # Use both default and uploaded CSV businesses. This makes the CSV visibly affect business pull.
    businesses = default_businesses + csv_businesses

    business_rows = []
    business_scores = []

    for business in businesses:
        score, status = popularity_for_business(business, selected_date, selected_hour)
        business_scores.append(score)
        business_rows.append({
            "business": business["business"],
            "category": business["category"],
            "source": business.get("source", "default"),
            "status": status,
            "score": score,
            "weekday_peak": business["weekday_peak"],
            "weekend_peak": business["weekend_peak"],
        })

    avg_business_score = sum(business_scores) / len(business_scores) if business_scores else 0

    events = records_for_lot(weekly_df, lot, selected_date, selected_hour, "event", event_radius_miles, pre_event_window_hours)
    holidays = records_for_lot(weekly_df, lot, selected_date, selected_hour, "holiday", event_radius_miles, pre_event_window_hours)
    weather = records_for_lot(weekly_df, lot, selected_date, selected_hour, "weather", event_radius_miles, pre_event_window_hours)

    e_score = event_score(events)
    h_score = holiday_score(holidays)
    w_score, weather_note = weather_modifier(weather)

    final_score = avg_business_score * 0.52 + e_score * 0.30 + h_score * 0.10 + w_score
    final_score = max(0, min(100, round(final_score, 1)))

    breakdown = {
        "business_score": round(avg_business_score, 1),
        "event_score": e_score,
        "holiday_score": h_score,
        "weather_modifier": w_score,
        "final_score": final_score,
        "weather_note": weather_note,
        "csv_business_rows_used": len(csv_businesses),
        "event_rows_used": len(events),
        "weather_rows_used": len(weather),
        "holiday_rows_used": len(holidays),
    }

    return final_score, pd.DataFrame(business_rows), events, holidays, weather, breakdown


def score_color(score):
    if score >= 80:
        return "red"
    if score >= 60:
        return "orange"
    if score >= 40:
        return "blue"
    return "green"


def score_label(score):
    if score >= 80:
        return "Very busy"
    if score >= 60:
        return "Busy"
    if score >= 40:
        return "Moderate"
    return "Light"


def build_map(weekly_df, selected_date, selected_hour, selected_lot_id, event_radius_miles, pre_event_window_hours):
    all_scores = []
    heat_points = []

    for lot in PARKING_LOTS:
        score, _, _, _, _, _ = calculate_lot_score(
            lot,
            weekly_df,
            selected_date,
            selected_hour,
            event_radius_miles,
            pre_event_window_hours,
        )
        all_scores.append((lot, score))
        heat_points.append([lot["lat"], lot["lon"], score / 100])

    center_lat = sum(lot["lat"] for lot in PARKING_LOTS) / len(PARKING_LOTS)
    center_lon = sum(lot["lon"] for lot in PARKING_LOTS) / len(PARKING_LOTS)

    m = folium.Map(location=[center_lat, center_lon], zoom_start=11, tiles="OpenStreetMap", control_scale=True)

    HeatMap(
        heat_points,
        min_opacity=0.18,
        max_opacity=0.65,
        radius=38,
        blur=32,
        max_zoom=15,
        gradient={
            0.20: "#2b83ba",
            0.45: "#abdda4",
            0.65: "#ffffbf",
            0.80: "#fdae61",
            1.00: "#d7191c",
        },
        name="Predicted busyness",
        show=True,
    ).add_to(m)

    for lot, score in all_scores:
        selected = lot["lot_id"] == selected_lot_id
        popup = f"""
        <div style="font-family:Arial; min-width:230px">
          <h4 style="margin:0 0 8px 0">{lot["display"]}</h4>
          <b>Score:</b> {score}/100<br>
          <b>Status:</b> {score_label(score)}<br>
          <b>Address:</b> {lot["address"]}<br>
          <b>Lot ID:</b> {lot["lot_id"]}
        </div>
        """

        folium.Marker(
            [lot["lat"], lot["lon"]],
            popup=folium.Popup(popup, max_width=300),
            tooltip=lot["lot_id"],
            icon=folium.Icon(
                color="cadetblue" if selected else score_color(score),
                icon="car",
                prefix="fa",
            ),
        ).add_to(m)

    return m


def make_template_csv():
    return pd.DataFrame([
        {
            "date": (date.today() + timedelta(days=1)).isoformat(),
            "start_time": "18:00",
            "end_time": "22:00",
            "record_type": "event",
            "title": "Example concert / festival / game",
            "parking_lot": "100 Venice Way Parking",
            "expected_people": 2500,
            "weather_condition": "",
            "temp_f": "",
            "rain_chance": "",
            "impact": 15,
            "lat": "",
            "lon": "",
            "notes": "Use parking_lot=all to apply to every lot",
        },
        {
            "date": (date.today() + timedelta(days=1)).isoformat(),
            "start_time": "",
            "end_time": "",
            "record_type": "business",
            "title": "Example nearby restaurant",
            "parking_lot": "100 Venice Way Parking",
            "expected_people": "",
            "weather_condition": "",
            "temp_f": "",
            "rain_chance": "",
            "impact": 70,
            "lat": "",
            "lon": "",
            "category": "food",
            "base_popularity": 70,
            "weekday_peak": "12-14,18-22",
            "weekend_peak": "10-16,18-23",
            "notes": "Business rows now affect business pull.",
        },
        {
            "date": (date.today() + timedelta(days=1)).isoformat(),
            "start_time": "",
            "end_time": "",
            "record_type": "weather",
            "title": "Sunny weather",
            "parking_lot": "all",
            "expected_people": "",
            "weather_condition": "sunny",
            "temp_f": 78,
            "rain_chance": 5,
            "impact": 8,
            "lat": "",
            "lon": "",
            "notes": "Weather can apply to all or one lot",
        },
        {
            "date": (date.today() + timedelta(days=2)).isoformat(),
            "start_time": "",
            "end_time": "",
            "record_type": "holiday",
            "title": "Holiday / school break",
            "parking_lot": "all",
            "expected_people": "",
            "weather_condition": "",
            "temp_f": "",
            "rain_chance": "",
            "impact": 10,
            "lat": "",
            "lon": "",
            "notes": "Holiday rows boost demand",
        },
    ])



# ============================================================
# PARKOPEDIA / NEARBY COMPETITOR PRICES
# ============================================================

def to_parkopedia_datetime(value):
    """Parkopedia URL format: YYYYMMDDHHMM."""
    return value.strftime("%Y%m%d%H%M")


def format_display_dt(value):
    """Windows-safe datetime display. Avoids %-I, which crashes on Windows."""
    hour = value.strftime("%I").lstrip("0") or "0"
    return value.strftime(f"%a %m/%d, {hour}:%M %p")


def build_parkopedia_url(selected_lot, arriving_dt, leaving_dt):
    arriving = to_parkopedia_datetime(arriving_dt)
    leaving = to_parkopedia_datetime(leaving_dt)

    query = quote_plus(f"{selected_lot['address']} Los Angeles CA")

    return (
        "https://en.parkopedia.com/parking/"
        f"{query}/"
        f"?arriving={arriving}&leaving={leaving}"
    )


def build_parkopedia_la_url(arriving_dt, leaving_dt):
    arriving = to_parkopedia_datetime(arriving_dt)
    leaving = to_parkopedia_datetime(leaving_dt)

    return (
        "https://en.parkopedia.com/parking/los_angeles/"
        f"?arriving={arriving}&leaving={leaving}"
    )


def nearby_price_status_text():
    return (
        "This tab opens live Parkopedia searches for the selected lot/date/time. "
        "The prices update dynamically on Parkopedia when you change the date or hour in the sidebar. "
        "The app is not scraping or storing Parkopedia prices."
    )


def nearby_lots_for_price_lookup(selected_lot, max_miles=3.0):
    nearby = []

    for lot in PARKING_LOTS:
        if lot["lot_id"] == selected_lot["lot_id"]:
            continue

        distance = haversine_miles(
            selected_lot["lat"],
            selected_lot["lon"],
            lot["lat"],
            lot["lon"],
        )

        if distance is not None and distance <= max_miles:
            nearby.append((lot, round(distance, 2)))

    return sorted(nearby, key=lambda item: item[1])


def build_price_lookup_map(selected_lot, arriving_dt, leaving_dt, max_miles=3.0):
    m = folium.Map(
        location=[selected_lot["lat"], selected_lot["lon"]],
        zoom_start=14,
        tiles="OpenStreetMap",
        control_scale=True,
    )

    selected_url = build_parkopedia_url(selected_lot, arriving_dt, leaving_dt)

    folium.Marker(
        [selected_lot["lat"], selected_lot["lon"]],
        tooltip=f"Selected: {selected_lot['display']}",
        popup=folium.Popup(
            f"""
            <div style="font-family:Arial; min-width:240px">
              <h4 style="margin:0 0 8px 0">{selected_lot['display']}</h4>
              <b>Your selected lot/area</b><br>
              <a href="{selected_url}" target="_blank">Open live Parkopedia prices</a>
            </div>
            """,
            max_width=320,
        ),
        icon=folium.Icon(color="green", icon="car", prefix="fa"),
    ).add_to(m)

    folium.Circle(
        location=[selected_lot["lat"], selected_lot["lon"]],
        radius=max_miles * 1609.34,
        color="#3388ff",
        fill=False,
        weight=2,
        tooltip=f"{max_miles} mile search radius",
    ).add_to(m)

    for lot, distance in nearby_lots_for_price_lookup(selected_lot, max_miles):
        url = build_parkopedia_url(lot, arriving_dt, leaving_dt)

        folium.Marker(
            [lot["lat"], lot["lon"]],
            tooltip=f"{lot['display']} ({distance} mi)",
            popup=folium.Popup(
                f"""
                <div style="font-family:Arial; min-width:240px">
                  <h4 style="margin:0 0 8px 0">{lot['display']}</h4>
                  <b>Distance from selected lot:</b> {distance} miles<br>
                  <b>Purpose:</b> price lookup area<br>
                  <a href="{url}" target="_blank">Open live Parkopedia prices</a>
                </div>
                """,
                max_width=320,
            ),
            icon=folium.Icon(color="blue", icon="search", prefix="fa"),
        ).add_to(m)

    return m


# ============================================================
# STREAMLIT APP
# ============================================================

st.set_page_config(page_title="Weekly Parking Demand Map", layout="wide")

st.title("Weekly Parking Demand Map v5 — Nearby Prices + Demand")
st.caption("Upload one weekly CSV. The app combines fixed lots, business patterns, events, holidays, and weather into a busyness score.")

with st.expander("Confirm this is the new app.py", expanded=False):
    st.markdown(
        """
        You are running the updated version if you see:
        - the title says **v5 — Nearby Prices + Demand**
        - the sidebar download says **Download blank weekly CSV template**
        - the top tabs include **Nearby prices**, **Demand map**, and **Details / weekly CSV**
        - the Nearby prices tab appears before the demand map
        """
    )


with st.sidebar:
    st.header("Weekly CSV")

    template_df = make_template_csv()
    st.download_button(
        "Download blank weekly CSV template",
        data=template_df.to_csv(index=False).encode("utf-8"),
        file_name="blank_weekly_parking_upload_template.csv",
        mime="text/csv",
    )

    uploaded = st.file_uploader("Upload this week's CSV", type=["csv"])

    if uploaded:
        weekly_df = normalize_weekly_csv(pd.read_csv(uploaded))
        st.success(f"Loaded {len(weekly_df)} uploaded rows.")
    else:
        weekly_df = normalize_weekly_csv(pd.DataFrame(SAMPLE_WEEKLY_DATA))
        st.info("No CSV uploaded yet. Showing sample fake weekly data.")

    valid_dates = sorted([d for d in weekly_df["date"].dropna().unique()])
    if not valid_dates:
        valid_dates = [date.today()]

    selected_date = st.date_input("Date", value=valid_dates[0])
    selected_hour = st.slider("Hour of day", 0, 23, 12)

    arriving_dt = datetime.combine(selected_date, datetime.min.time()).replace(hour=selected_hour)
    leaving_dt = arriving_dt + timedelta(hours=2)

    st.divider()

    event_radius_miles = st.slider(
        "Nearby event radius, miles",
        min_value=1,
        max_value=25,
        value=12,
        help="Rows with lat/lon affect a lot if they are within this many miles.",
    )

    pre_event_window_hours = st.slider(
        "Count events starting within next N hours",
        min_value=0,
        max_value=8,
        value=4,
        help="A 7 PM concert can affect parking at 3 PM if this is set to 4.",
    )

    st.divider()
    selected_lot_name = st.selectbox(
        "Selected parking lot",
        options=[lot["display"] for lot in PARKING_LOTS],
        index=0,
    )

    st.caption("Use the top tabs to switch between Nearby prices, Demand map, and Details.")

selected_lot = next(lot for lot in PARKING_LOTS if lot["display"] == selected_lot_name)

score, business_df, events_df, holidays_df, weather_df, breakdown = calculate_lot_score(
    selected_lot,
    weekly_df,
    selected_date,
    selected_hour,
    event_radius_miles,
    pre_event_window_hours,
)

price_tab, demand_tab, details_tab = st.tabs([
    "Nearby prices",
    "Demand map",
    "Details / weekly CSV",
])

with price_tab:
    st.header("Nearby parking prices")
    st.info(nearby_price_status_text())

    parkopedia_url = build_parkopedia_url(selected_lot, arriving_dt, leaving_dt)
    parkopedia_la_url = build_parkopedia_la_url(arriving_dt, leaving_dt)
    nearby_price_lots = nearby_lots_for_price_lookup(selected_lot, max_miles=3.0)

    p1, p2, p3, p4 = st.columns(4)
    p1.metric("Selected area", selected_lot["display"])
    p2.metric("Arriving", format_display_dt(arriving_dt))
    p3.metric("Leaving", format_display_dt(leaving_dt))
    p4.metric("Nearby areas", len(nearby_price_lots))

    st.markdown("### Price lookup map")
    st.caption(
        "This is a separate map for competitor-price lookups. Click a marker, then open its live Parkopedia price page."
    )

    map_col, link_col = st.columns([1.45, 0.85])

    with map_col:
        st_folium(
            build_price_lookup_map(selected_lot, arriving_dt, leaving_dt, max_miles=3.0),
            height=650,
            width=None,
            returned_objects=[],
            key=f"price_lookup_map_{selected_lot['lot_id']}_{selected_date}_{selected_hour}",
        )

    with link_col:
        st.subheader("Live Parkopedia links")
        st.link_button("Open selected lot prices", parkopedia_url)
        st.link_button("Open Los Angeles prices", parkopedia_la_url)

        st.markdown("#### Nearby areas")
        if not nearby_price_lots:
            st.info("No other company lots are within 3 miles of the selected lot.")
        else:
            for lot, distance in nearby_price_lots[:12]:
                url = build_parkopedia_url(lot, arriving_dt, leaving_dt)
                st.link_button(f"{lot['display']} ({distance} mi)", url)

        with st.expander("Try embedded Parkopedia page"):
            st.caption(
                "Some sites block being embedded inside Streamlit. If this area is blank, use the buttons above."
            )
            components.iframe(parkopedia_url, height=650, scrolling=True)

    st.markdown("### Pricing use")
    st.markdown(
        """
        Use Parkopedia as a live competitor check for the same time window. If your demand score is high
        and nearby public parking is more expensive, your lot may be underpriced. If demand is low and
        nearby public parking is cheaper, your lot may be overpriced.
        """
    )

with demand_tab:
    left, right = st.columns([1.45, 1])

    with left:
        st.subheader("Demand map")
        map_result = st_folium(
            build_map(
                weekly_df,
                selected_date,
                selected_hour,
                selected_lot["lot_id"],
                event_radius_miles,
                pre_event_window_hours,
            ),
            height=680,
            width=None,
            returned_objects=["last_object_clicked_tooltip"],
            key=f"parking_map_{selected_date}_{selected_hour}_{selected_lot['lot_id']}_{event_radius_miles}_{pre_event_window_hours}",
        )

        clicked_lot_id = map_result.get("last_object_clicked_tooltip") if map_result else None
        if clicked_lot_id and clicked_lot_id != selected_lot["lot_id"]:
            clicked = next((lot for lot in PARKING_LOTS if lot["lot_id"] == clicked_lot_id), None)
            if clicked:
                st.info(f"Clicked: {clicked['display']}. Select it in the sidebar to inspect details.")

    with right:
        st.subheader(selected_lot["display"])
        st.caption(selected_lot["name"])
        st.metric("Aggregated busyness score", f"{score}/100", score_label(score))

        c1, c2 = st.columns(2)
        c1.metric("Business pull", f"{breakdown['business_score']}/100")
        c2.metric("Event boost", f"{breakdown['event_score']}")

        c3, c4 = st.columns(2)
        c3.metric("Holiday boost", f"{breakdown['holiday_score']}")
        c4.metric("Weather modifier", f"{breakdown['weather_modifier']}")

        st.write("**Weather explanation:**", breakdown["weather_note"])

        st.info(
            "CSV rows affecting this score: "
            f"{breakdown['csv_business_rows_used']} business, "
            f"{breakdown['event_rows_used']} event, "
            f"{breakdown['weather_rows_used']} weather, "
            f"{breakdown['holiday_rows_used']} holiday."
        )

        if breakdown["event_rows_used"] == 0:
            st.warning(
                "No event rows matched this lot/date/hour. Check the Events tab, "
                "increase the nearby event radius, or make sure the CSV parking_lot/date/time matches."
            )

        selected_watch_notes = filtered_real_watch_notes(
            watch_notes_for_lot(weekly_df, selected_lot, selected_date)
        )

        st.subheader("Lots to watch for this selected lot/date")
        render_watch_note_cards(selected_watch_notes)

with details_tab:
    subtab1, subtab2, subtab3, subtab4, subtab5 = st.tabs([
        "Nearby businesses",
        "Events",
        "Weather / holidays",
        "🚨 Lots to watch",
        "Uploaded CSV",
    ])

    with subtab1:
        st.subheader("Nearby businesses and likely busy times")
        st.dataframe(
            business_df[["business", "category", "source", "status", "score", "weekday_peak", "weekend_peak"]],
            use_container_width=True,
            hide_index=True,
        )

    with subtab2:
        st.subheader("Events affecting this lot at the selected date/hour")
        if events_df.empty:
            st.info("No matching event rows for this lot/time.")
        else:
            st.dataframe(
                events_df[["date", "start_time", "end_time", "title", "parking_lot", "expected_people", "impact", "lat", "lon", "notes"]],
                use_container_width=True,
                hide_index=True,
            )

        st.subheader("All event rows for the selected date")
        all_day_events = weekly_df[
            (weekly_df["record_type"] == "event") &
            (weekly_df["date"] == selected_date)
        ].copy()

        if all_day_events.empty:
            st.info("No event rows uploaded for this date.")
        else:
            st.dataframe(
                all_day_events[["date", "start_time", "end_time", "title", "parking_lot", "expected_people", "impact", "lat", "lon", "notes"]],
                use_container_width=True,
                hide_index=True,
            )

    with subtab3:
        st.subheader("Weather and holidays affecting this lot")
        if weather_df.empty and holidays_df.empty:
            st.info("No matching weather or holiday rows for this lot/time.")
        else:
            combined = pd.concat([weather_df, holidays_df], ignore_index=True)
            st.dataframe(
                combined[["date", "record_type", "title", "parking_lot", "weather_condition", "temp_f", "rain_chance", "impact", "notes"]],
                use_container_width=True,
                hide_index=True,
            )

    with subtab4:
        st.subheader("Lots to watch this week")

        all_week_watch_notes = weekly_df[weekly_df["record_type"] == "watch_note"].copy()
        real_week_watch_notes = filtered_real_watch_notes(all_week_watch_notes)
        manual_notes = all_week_watch_notes[all_week_watch_notes.apply(is_manual_placeholder, axis=1)].copy()

        selected_watch_notes = filtered_real_watch_notes(
            watch_notes_for_lot(weekly_df, selected_lot, selected_date)
        )
        all_date_watch_notes = filtered_real_watch_notes(
            all_watch_notes_for_date(weekly_df, selected_date)
        )

        if real_week_watch_notes.empty:
            st.warning(
                "No real watch_note rows were found. Upload the CSV named "
                "weekly_parking_upload_WITH_REAL_WATCH_NOTES_2026-06-29_to_2026-07-05.csv."
            )
        else:
            critical_count = int(real_week_watch_notes.apply(watch_note_priority_value, axis=1).ge(4).sum())
            high_count = int(real_week_watch_notes.apply(watch_note_priority_value, axis=1).eq(3).sum())

            m1, m2, m3 = st.columns(3)
            m1.metric("Critical notes", critical_count)
            m2.metric("High-priority notes", high_count)
            m3.metric("Total watch notes", len(real_week_watch_notes))

            st.markdown("### Biggest things to watch this week")
            render_watch_note_cards(real_week_watch_notes)

        st.markdown("### Matching the selected lot/date")
        render_watch_note_cards(selected_watch_notes)

        st.markdown("### All watch notes for selected date")
        if all_date_watch_notes.empty:
            st.info("No specific watch notes uploaded for this date.")
        else:
            render_watch_note_cards(all_date_watch_notes)

        with st.expander("Manual closure checklist"):
            if manual_notes.empty:
                st.info("No manual closure placeholder notes uploaded.")
            else:
                render_watch_note_cards(manual_notes)

        st.markdown("### Watch-note table")
        if real_week_watch_notes.empty:
            st.info("No watch-note table to show.")
        else:
            table_cols = [
                "date_raw", "start_time", "priority", "direction", "title",
                "parking_lot", "reason_type", "reason", "expected_impact", "suggested_action"
            ]
            table_cols = [c for c in table_cols if c in real_week_watch_notes.columns]
            st.dataframe(sort_watch_notes(real_week_watch_notes)[table_cols], use_container_width=True, hide_index=True)

    with subtab5:
        st.subheader("Current uploaded CSV data")
        st.dataframe(weekly_df, use_container_width=True, hide_index=True)

        st.markdown(
            """
            **CSV columns you can use:**

            `date`, `start_time`, `end_time`, `record_type`, `title`, `parking_lot`,
            `expected_people`, `weather_condition`, `temp_f`, `rain_chance`, `impact`,
            `lat`, `lon`, `notes`, `category`, `base_popularity`, `weekday_peak`, `weekend_peak`

            `record_type` can be: `event`, `weather`, `holiday`, `business`, or `watch_note`.

            `parking_lot` can be an exact lot name, a display name, a zone-ish name, or `all`.

            Event rows with `lat` and `lon` can affect lots within the sidebar event radius.
            """
        )


