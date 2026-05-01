import csv
from pathlib import Path

from agent import SupportTriageAgent


def main() -> None:
    base = Path(__file__).resolve().parent.parent
    in_csv = base / "support_tickets" / "support_tickets.csv"
    out_csv = base / "support_tickets" / "output.csv"

    agent = SupportTriageAgent()

    with in_csv.open("r", encoding="utf-8", newline="") as fin, out_csv.open(
        "w", encoding="utf-8", newline=""
    ) as fout:
        reader = csv.DictReader(fin)
        fieldnames = ["status", "product_area", "response", "justification", "request_type"]
        writer = csv.DictWriter(fout, fieldnames=fieldnames)
        writer.writeheader()

        for row in reader:
            writer.writerow(agent.process_ticket(row))


if __name__ == "__main__":
    main()