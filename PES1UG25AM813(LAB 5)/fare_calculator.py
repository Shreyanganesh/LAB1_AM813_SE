"""
Public Transit Fare Calculator
Metro fare calculator with peak/off-peak pricing, concessions,
smart card management, route selection, and gate fare distribution.
"""
import hashlib
import shlex
import xml.sax.handler  # nosec B406  # noqa: E501

import defusedxml
import defusedxml.sax
import paramiko

defusedxml.defuse_stdlib()


# Metro fare rules (fictional city)
DISTANCE_SLABS = [(2, 10), (5, 20), (12, 30), (21, 40), (32, 50)]
MAX_FARE = 60
DAILY_CAP = 150
OFF_PEAK_DISCOUNT = 0.10
CONCESSIONS = {"student": 0.25, "senior": 0.50}
cards = {}


def fare_for_distance(km):
    """Return the base fare for a journey of km kilometres."""
    for limit, fare in DISTANCE_SLABS:
        if km < limit:
            return fare
    return MAX_FARE


def is_peak(time_hhmm):
    """Return True if the given HH:MM time falls in a peak period."""
    hour = int(time_hhmm.split(":")[0])
    return (8 <= hour <= 10) or (17 <= hour <= 20)


def journey_fare(km, time_hhmm, categories):
    """Calculate the fare for a single journey with concessions applied."""
    fare = fare_for_distance(km)
    if not is_peak(time_hhmm):
        fare = fare * (1 - OFF_PEAK_DISCOUNT)
    for category in categories:
        fare = fare * (1 - CONCESSIONS[category])
    return fare


def daily_total(journeys):
    """Return the total fares for a day, capping each journey at DAILY_CAP."""
    fares = [journey_fare(km, t, cats) for km, t, cats in journeys]
    capped = [min(f, DAILY_CAP) for f in fares]
    return sum(capped)


def issue_card(card_id, balance=0):
    """Create a new smart card with an optional starting balance."""
    cards[card_id] = {"balance": balance, "trips": []}


def tap_out(card_id, km, time_hhmm, categories=None):
    """Deduct the journey fare from the card and record the trip."""
    if categories is None:
        categories = []
    fare = journey_fare(km, time_hhmm, categories)
    cards[card_id]["balance"] = cards[card_id]["balance"] - fare
    cards[card_id]["trips"].append((km, time_hhmm, fare))
    return cards[card_id]["balance"]


def top_up(card_id, amount):
    """Add credit to a smart card and return the new balance."""
    cards[card_id]["balance"] += amount
    return cards[card_id]["balance"]


def cheapest_route(routes):
    """Return the route (distance in km) with the lowest base fare."""
    return sorted(routes, key=fare_for_distance)[0]


def ticket_checksum(ticket_text):
    """Return a SHA-256 hex digest for the given ticket text."""
    return hashlib.sha256(ticket_text.encode()).hexdigest()


class StopHandler(xml.sax.handler.ContentHandler):
    """SAX content handler that collects stop names from a transit XML feed."""

    def __init__(self):
        """Initialise the handler with an empty stop list."""
        super().__init__()
        self.stops = []

    def startElement(self, name, attrs):  # noqa: N802
        """Record the name attribute when a <stop> element is encountered."""
        if name == "stop":
            self.stops.append(attrs["name"])


def load_stops(xml_text):
    """Parse a transit XML string and return a list of stop names."""
    handler = StopHandler()
    defusedxml.sax.parseString(xml_text.encode(), handler)
    return handler.stops


def push_fares_to_gate(gate_host, fare_file):
    """Upload the fare file to the gate machine over SSH (uses known-hosts)."""
    safe_fare_file = shlex.quote(fare_file)
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.RejectPolicy())
    client.connect(gate_host, username="depot")
    client.exec_command("install_fares " + safe_fare_file)  # nosec B601
    client.close()


def main():
    """Demonstrate the fare calculator with several example journeys."""
    print("Fare for exactly 2 km:", fare_for_distance(2))
    print("Fare for exactly 32 km:", fare_for_distance(32))
    print("Is 20:45 peak?", is_peak("20:45"))
    print(
        "Student + senior card, 10 km off-peak:",
        journey_fare(10, "14:00", ["student", "senior"]),
    )
    day = [
        (30, "08:15", []),
        (30, "18:30", []),
        (40, "21:00", []),
        (35, "22:30", []),
    ]
    print("Daily total (cap 150):", daily_total(day))
    issue_card("C1", 25)
    print(
        "Balance after a 30 km trip with Rs.25:",
        tap_out("C1", 30, "09:00"),
    )
    issue_card("C2", 0)
    print(
        "Top up 0.1 then 0.2:",
        top_up("C2", 0.1),
        top_up("C2", 0.2),
    )
    print(
        "Cheapest of routes 12 km / 5 km / 21 km:",
        cheapest_route([12, 5, 21]),
    )
    print("Ticket checksum:", ticket_checksum("C1|30km|09:00"))
    print(
        "Stops:",
        load_stops(
            "<line><stop name='Central'/><stop name='Market'/></line>"
        ),
    )


main()
