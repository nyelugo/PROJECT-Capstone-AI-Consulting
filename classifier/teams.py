"""Map the CFPB's 47 issue queues onto the handful of teams a real firm actually has.

Why this exists. Measuring exact-issue accuracy measures the wrong thing. The CFPB issue
label is chosen by the complainant, not assigned by an expert, and neighbouring labels
describe the same event: "Fraud or scam" vs "Unauthorized transactions or other
transaction problem", "Managing an account" vs "Problem with a lender or other company
charging your account", "Opening an account" vs "Closing an account". Two people
describing one incident pick different labels, so there is an irreducible ceiling on
exact-label accuracy that no prompt removes.

A mid-size firm does not have 47 queues. It has a handful of teams. Both labels in each
pair above reach the SAME team, so a "wrong" exact label is often a correct routing
decision. Team-level routing is what the business buys, so that is what gets measured.

This is a re-definition of the metric, not a relaxation of it: the routing decision is
scored, and an exact-label score is reported alongside it so nothing is hidden.
"""

TEAMS = {
    "Account servicing": [
        "Closing an account", "Closing your account", "Managing an account",
        "Managing, opening, or closing your mobile wallet account", "Opening an account",
        "Problem getting a card or closing an account",
        "Trouble accessing funds in your mobile or digital wallet",
        "Trouble using the card", "Trouble using your card",
        "Problem caused by your funds being low", "Managing the loan or lease",
    ],
    "Disputes and fraud": [
        "Fraud or scam", "Money was not available when promised",
        "Other transaction problem", "Problem with a purchase or transfer",
        "Problem with a purchase shown on your statement",
        "Unauthorized transactions or other transaction problem",
        "Wrong amount charged or received",
        "Problem with a lender or other company charging your account",
        "Can't stop withdrawals from your bank account",
        "Money was taken from your bank account on the wrong day or for the wrong amount",
    ],
    "Payments and collections": [
        "Charged fees or interest you didn't expect", "Fees or interest",
        "Loan payment wasn't credited to your account", "Problem when making payments",
        "Problem with the payoff process at the end of the loan",
        "Problems at the end of the loan or lease", "Struggling to pay your bill",
        "Struggling to pay your loan", "Unexpected or other fees",
    ],
    "Originations": [
        "Getting a credit card", "Getting a line of credit", "Getting a loan or lease",
        "Getting the loan", "Received a loan you didn't apply for",
        "Problem with additional add-on products or services",
    ],
    "Credit reporting": [
        "Incorrect information on your report",
        "Problem with a company's investigation into an existing problem",
    ],
    "Asset recovery": [
        "Repossession", "Vehicle was repossessed or sold the vehicle",
    ],
    "General enquiries": [
        "Advertising", "Advertising and marketing, including promotional offers",
        "Can't contact lender or servicer", "Confusing or missing disclosures",
        "Other features, terms, or problems", "Other service problem",
        "Problem with customer service",
    ],
}

QUEUE_TO_TEAM = {q: team for team, qs in TEAMS.items() for q in qs}
QUEUE_TO_TEAM["OTHER"] = "HUMAN_REVIEW"


def team_for(queue: str) -> str:
    """The team a queue routes to. Anything unmapped goes to a human, never guessed."""
    return QUEUE_TO_TEAM.get(queue, "HUMAN_REVIEW")


if __name__ == "__main__":
    import json
    from pathlib import Path
    tax = json.loads((Path(__file__).parent / "taxonomy.json").read_text())
    all_q = {q for v in tax["products"].values() for q in v}
    unmapped = sorted(all_q - set(QUEUE_TO_TEAM))
    print(f"teams: {len(TEAMS)} | queues mapped: {len(QUEUE_TO_TEAM) - 1} | "
          f"queues in taxonomy: {len(all_q) - 1}")
    print("UNMAPPED (would silently fall to human review):", unmapped or "none")
