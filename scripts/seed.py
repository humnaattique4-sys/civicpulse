import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from app.database import SessionLocal, engine, Base
from app.models import Complaint
from app.services.triage_service import run_triage
import app.models

Base.metadata.create_all(bind=engine)

COMPLAINTS = [
    ("Burst water main flooding Street 12 since fajr, water entering ground floors", "Street 12, G-9"),
    ("Streetlight not working near park for two weeks, very dark at night", "F-10 Park Road"),
    ("Garbage not collected in our sector for five days, smell is very bad", "I-8 Sector 3"),
    ("Pothole on main road causing accidents, two bikes fell yesterday", "Main Boulevard"),
    ("Power outage in whole street since morning, no update from WAPDA", "Model Town Block C"),
    ("Sewage water overflowing onto the road near mosque", "Chowk Yadgar"),
    ("Traffic signal not working at busy intersection, causing jams", "Mall Road Crossing"),
    ("Transformer sparking near school, children scared to pass", "Township Sector A"),
    ("Water supply contaminated, smells bad, whole mohalla affected", "Green Town Phase 2"),
    ("Broken sign board fell on footpath, blocking pedestrians", "University Road"),
    ("Electricity wire hanging low near bus stop, dangerous for public", "Satellite Town"),
    ("Trash piling up near children's park, health hazard", "Wapda Town Block D"),
    ("Road caved in after rain, big hole in middle of street", "Ferozepur Road"),
    ("Streetlights all off in entire colony since three days", "Johar Town Phase 1"),
    ("Sanitation workers not visiting our street for over a week", "Faisal Town Block B"),
    ("Water pipe leaking continuously, wasting a lot of water", "Gulberg III"),
    ("Electric pole leaning dangerously after storm last night", "Cantt Area"),
    ("Garbage bin overflowing outside market, attracting stray animals", "Liberty Market"),
    ("No streetlight on the whole road, women feel unsafe at night", "DHA Phase 5"),
    ("Sewage line blocked, water backing up into houses", "Samanabad"),
    ("Fire hazard - exposed electrical wiring near petrol station", "Ring Road"),
    ("Road sign missing at dangerous curve, several near misses reported", "Canal Road"),
    ("Water tank overflowing and flooding the street daily", "Township Sector C"),
    ("Broken manhole cover, dangerous for pedestrians and vehicles", "Anarkali Bazaar"),
    ("Streetlight flickering constantly, needs replacement", "Cavalry Ground"),
    ("Illegal dumping of construction waste blocking drainage", "Shadman Colony"),
    ("Transformer burnt out, no electricity for two days now", "Iqbal Town"),
    ("Potholes multiplying after rain, road almost undrivable", "Multan Road"),
    ("Water leakage from underground pipe creating sinkhole risk", "Model Colony"),
    ("Garbage truck hasn't come in over a week, bins overflowing everywhere", "Askari Sector 4"),
    ("Broken streetlight pole lying on the footpath since the storm", "Bahria Town Phase 3"),
    ("Contaminated water coming from taps, children fell sick", "Township Sector F"),
]

def seed():
    db = SessionLocal()
    try:
        existing = db.query(Complaint).count()
        if existing >= len(COMPLAINTS):
            print(f"Already seeded ({existing} complaints exist). Skipping.")
            return

        added = 0
        for text_, location in COMPLAINTS:
            already = db.query(Complaint).filter(Complaint.text == text_).first()
            if already:
                continue
            category, priority, summary, provider, latency_ms = run_triage(text_, location)
            complaint = Complaint(
                text=text_,
                location=location,
                category=category,
                priority=priority,
                ai_summary=summary,
                triaged_by=provider,
                triage_latency_ms=latency_ms,
            )
            db.add(complaint)
            added += 1

        db.commit()
        print(f"Seeded {added} new complaints.")
    finally:
        db.close()

if __name__ == "__main__":
    seed()