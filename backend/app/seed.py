from app.database import SessionLocal
from app.models import Complaint, Status
from app.services.triage_service import run_triage

SAMPLES = [
    ("Burst water main flooding Street 12 since fajr", "Street 12"),
    ("Streetlight out for two weeks near the park", "Park Road"),
    ("Garbage not collected for five days", "I-8 Markaz"),
    ("Large pothole damaging cars on the main road", "Kashmir Highway"),
    ("Power outage in the whole block since last night", "F-10"),
    ("Sewage overflowing onto the street near the school", "G-9"),
    ("Sparking wire hanging from a transformer", "Blue Area"),
    ("Traffic signal not working at the intersection", "Zero Point"),
    ("Water supply has been very low for a week", "H-8"),
    ("Broken lamp post leaning over the footpath", "Sector E-11"),
    ("Trash piled up behind the market", "Bhara Kahu"),
    ("Gas leak smell near the bakery", "I-9"),
    ("Road sign fell down after the storm", "Murree Road"),
    ("Pipe leak flooding the basement of our building", "Gulberg"),
    ("Electric pole tilted dangerously after rain", "Satellite Town"),
    ("Waste bins overflowing, bad smell in the lane", "Model Town"),
    ("Streetlights not turning on after sunset", "Johar Town"),
    ("Deep potholes after the rain on the service road", "DHA Phase 2"),
    ("Something unusual noise near the community hall", "Sector C"),
    ("Fire near the electric panel in the market", "Raja Bazaar"),
]


def seed():
    db = SessionLocal()
    try:
        if db.query(Complaint).count() >= len(SAMPLES):
            print("already seeded, nothing to do")
            return
        for i, (text, location) in enumerate(SAMPLES):
            category, priority, summary, triaged_by, latency_ms = run_triage(text, location)
            complaint = Complaint(
                text=text,
                location=location,
                category=category,
                priority=priority,
                ai_summary=summary,
                triaged_by=triaged_by,
                triage_latency_ms=latency_ms,
            )
            if i % 5 == 0:
                complaint.status = Status.in_progress
            db.add(complaint)
        db.commit()
        print(f"seeded {len(SAMPLES)} complaints")
    finally:
        db.close()


if __name__ == "__main__":
    seed()