#!/usr/bin/env python3
"""
FTC Advancement Points Calculator with Friendly CLI + PDF Export

Features:
- Correct Qualification Points formula
- Friendly award input parsing with example prompts
- Colorful terminal output (colorama)
- Export a neat PDF report with table and colors (reportlab)
- Works interactive or via command-line args

Author: ChatGPT (for you)
"""

from __future__ import annotations
import math
import argparse
import sys
from typing import List, Tuple, Optional
import re

try:
    import colorama
    from colorama import Fore, Style
    colorama.init(autoreset=True)
    FG_RED = Fore.RED
    FG_GREEN = Fore.GREEN
    FG_YELLOW = Fore.YELLOW
    FG_CYAN = Fore.CYAN
    FG_MAGENTA = Fore.MAGENTA
    FG_WHITE = Fore.WHITE
    STYLE_RESET = Style.RESET_ALL
except ImportError:
    FG_RED = '\033[31m'
    FG_GREEN = '\033[32m'
    FG_YELLOW = '\033[33m'
    FG_CYAN = '\033[36m'
    FG_MAGENTA = '\033[35m'
    FG_WHITE = '\033[37m'
    STYLE_RESET = '\033[0m'

try:
    from reportlab.lib.pagesizes import letter
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_CENTER
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.pdfbase import pdfmetrics
except ImportError:
    print(FG_RED + "Missing dependency: reportlab is required for PDF export." + STYLE_RESET)
    print("Run: pip install reportlab")
    sys.exit(1)

# --------------------------
# Math: inverse error function approximation
# --------------------------
def erfinv(y: float) -> float:
    """
    Inverse error function approximation with Newton-Raphson refinement.
    Accepts y in (-1,1).
    """
    if y <= -1.0:
        return float('-inf')
    if y >= 1.0:
        return float('inf')

    a = 0.147
    ln_part = math.log(1 - y*y)
    first = 2/(math.pi*a) + ln_part/2
    second = ln_part/a
    x = math.copysign(math.sqrt(max(0.0, math.sqrt(first*first - second) - first)), y)

    # Newton-Raphson refinement
    for _ in range(10):
        err = math.erf(x) - y
        deriv = (2/math.sqrt(math.pi)) * math.exp(-x*x)
        if deriv == 0:
            break
        step = err / deriv
        x -= step
        if abs(step) < 1e-14:
            break
    return x

def qualification_points(rank: int, teams: int, alpha: float = 1.07) -> int:
    """
    Qualification points formula:
    ceil( InvERF((N - 2R + 2) / (alpha * N)) * (7 / InvERF(1/alpha)) + 9 )
    """
    if teams < 2:
        raise ValueError("Number of teams must be >= 2")
    if rank < 1 or rank > teams:
        raise ValueError("Rank must be between 1 and number of teams")

    raw_input = (teams - 2*rank + 2) / (alpha * teams)
    eps = 1e-12
    if raw_input <= -1.0:
        raw_input = -1 + eps
    if raw_input >= 1.0:
        raw_input = 1 - eps

    inv = erfinv(raw_input)
    denom = erfinv(1/alpha)
    if denom == 0:
        raise ZeroDivisionError("InvERF(1/alpha) is zero - check alpha value")
    scaled = inv * (7 / denom) + 9
    return math.ceil(scaled)

# --------------------------
# Points by category
# --------------------------
def alliance_captain_points(captain_number: Optional[int]) -> int:
    if captain_number is None or captain_number <= 0:
        return 0
    return max(0, 21 - captain_number)

def draft_acceptance_points(draft_number: Optional[int]) -> int:
    if draft_number is None or draft_number <= 0:
        return 0
    return max(0, 21 - draft_number)

def playoff_advancement_points(place: Optional[int]) -> int:
    mapping = {1: 40, 2: 20, 3: 10, 4: 5}
    if place is None:
        return 0
    return mapping.get(place, 0)

def judged_award_points(kind: str, place: int) -> int:
    kind = kind.lower()
    inspire_awards = {1: 60, 2: 30, 3: 15}
    other_awards = {1: 12, 2: 6, 3: 3}
    if kind == 'inspire':
        return inspire_awards.get(place, 0)
    return other_awards.get(place, 0)

# --------------------------
# Terminal colors & prints
# --------------------------
def colored(text: str, color_code: str) -> str:
    return f"{color_code}{text}{STYLE_RESET}"

def print_header():
    print(colored("="*60, FG_CYAN))
    print(colored("FTC Advancement Points Calculator", FG_MAGENTA))
    print(colored("Friendly award input + PDF export included", FG_CYAN))
    print(colored("="*60, FG_CYAN))

def format_row(name: str, points: int, note: str = "") -> str:
    return f"{name:<30s} {points:>5d}   {note}"

def display_results(breakdown: List[Tuple[str, int, str]], total: int):
    print()
    print(colored("Points breakdown:", FG_YELLOW))
    print(colored("-"*60, FG_YELLOW))
    for label, pts, note in breakdown:
        color = FG_GREEN if pts > 0 else FG_WHITE
        print(colored(format_row(label, pts, note), color))
    print(colored("-"*60, FG_YELLOW))
    print(colored(f"{'TOTAL':<30s} {total:>5d}", FG_MAGENTA))
    print()

    print(colored("Your advancement points have been saved to 'advancement_points_report.pdf' 🎉", FG_CYAN))
    print()

# --------------------------
# PDF export logic using ReportLab
# --------------------------
def export_pdf_report(breakdown: List[Tuple[str, int, str]], total: int, filename: str = "advancement_points_report.pdf") -> None:
    doc = SimpleDocTemplate(filename, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='CenterTitle', alignment=TA_CENTER, fontSize=18, spaceAfter=20))
    elements = []

    elements.append(Paragraph("FTC Advancement Points Report", styles['CenterTitle']))

    # Table data with header
    data = [["Category", "Points", "Notes"]]
    for label, pts, note in breakdown:
        data.append([label, str(pts), note])

    # Add total row
    data.append(["TOTAL", str(total), ""])

    # Table style with colors
    tbl_style = TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.darkblue),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('ALIGN', (1,1), (-1,-1), 'CENTER'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 14),

        # Alternate row background colors for readability
        ('BACKGROUND', (0,1), (-1,-2), colors.whitesmoke),
        ('BACKGROUND', (0,2), (-1,-2), colors.lightgrey),
        ('GRID', (0,0), (-1,-1), 1, colors.black),

        # Total row highlight
        ('BACKGROUND', (0,-1), (-1,-1), colors.darkblue),
        ('TEXTCOLOR', (0,-1), (-1,-1), colors.whitesmoke),
        ('FONTNAME', (0,-1), (-1,-1), 'Helvetica-Bold'),
        ('FONTSIZE', (0,-1), (-1,-1), 16),
    ])

    # Alternate rows coloring (lightgrey and whitesmoke)
    for i in range(1, len(data)-1):
        if i % 2 == 0:
            tbl_style.add('BACKGROUND', (0,i), (-1,i), colors.lightgrey)
        else:
            tbl_style.add('BACKGROUND', (0,i), (-1,i), colors.whitesmoke)

    table = Table(data, colWidths=[250, 70, 180])
    table.setStyle(tbl_style)

    elements.append(table)
    elements.append(Spacer(1, 20))

    # Footer note
    footer = Paragraph("Generated by FTC Advancement Points Calculator", styles['Normal'])
    elements.append(footer)

    doc.build(elements)

# --------------------------
# Friendly award parsing with 3AM-proof help text
# --------------------------
def parse_award_input(line: str) -> Optional[Tuple[str, int]]:
    """
    Parse award input line.
    Acceptable examples:
      inspire 1
      inspire 2
      inspire 3
      other 1
      innovate 2
      control 3
    Unknown award kinds default to 'other'.
    Returns (kind, place) or None if invalid.
    """
    line = line.strip().lower()
    if not line:
        return None

    # Try to find two tokens: kind and place
    tokens = re.split(r'\s+', line)
    if len(tokens) != 2:
        return None

    kind_raw, place_raw = tokens
    # Try place int
    try:
        place = int(place_raw)
        if place not in (1, 2, 3):
            return None
    except ValueError:
        return None

    # Map known kinds, default unknown to 'other'
    known_inspire = {'inspire'}
    if kind_raw in known_inspire:
        kind = 'inspire'
    else:
        kind = 'other'

    return (kind, place)

def interactive_mode():
    print_header()
    print(colored("Welcome! Let's calculate your FTC Advancement Points. 🏆", FG_YELLOW))
    print()
    print(colored("Step 1: Enter your event info.", FG_CYAN))
    while True:
        try:
            teams_raw = input("Number of teams in qualification (N) [e.g. 28]: ").strip()
            teams = int(teams_raw)
            if teams < 2:
                print(colored("Oops! There must be at least 2 teams.", FG_RED))
                continue
            break
        except ValueError:
            print(colored("Please enter a valid number!", FG_RED))

    while True:
        try:
            rank_raw = input(f"Your qualification rank (R) [1..{teams}]: ").strip()
            rank = int(rank_raw)
            if rank < 1 or rank > teams:
                print(colored(f"Rank must be between 1 and {teams}.", FG_RED))
                continue
            break
        except ValueError:
            print(colored("Please enter a valid rank!", FG_RED))

    alpha_raw = input("Alpha constant (press Enter for default 1.07): ").strip()
    alpha = float(alpha_raw) if alpha_raw else 1.07

    print()
    print(colored("Step 2: Alliance and draft info.", FG_CYAN))
    captain_raw = input("Alliance captain number (0 if none): ").strip()
    captain = int(captain_raw) if captain_raw.isdigit() else 0
    draft_raw = input("Draft acceptance number (0 if none): ").strip()
    draft = int(draft_raw) if draft_raw.isdigit() else 0

    print()
    print(colored("Step 3: Playoff placement.", FG_CYAN))
    playoff_raw = input("Playoff place (1..4) or 0 if none: ").strip()
    playoff = int(playoff_raw) if playoff_raw.isdigit() else 0

    print()
    print(colored("Step 4: Judged Awards Entry 🏅", FG_CYAN))
    print(colored("Type your awards one at a time, like these examples:", FG_YELLOW))
    print(colored("  inspire 1    (Inspire Award 1st place - 60 points)", FG_GREEN))
    print(colored("  inspire 2    (Inspire Award 2nd place - 30 points)", FG_GREEN))
    print(colored("  inspire 3    (Inspire Award 3rd place - 15 points)", FG_GREEN))
    print(colored("  innovate 1   (Other Award 1st place - 12 points)", FG_GREEN))
    print(colored("  control 2    (Other Award 2nd place - 6 points)", FG_GREEN))
    print(colored("  other 3      (Other Award 3rd place - 3 points)", FG_GREEN))
    print(colored("When you are done, just press ENTER on an empty line.", FG_YELLOW))
    print()

    awards = []
    while True:
        line = input("Award (type place): ").strip()
        if not line:
            break
        parsed = parse_award_input(line)
        if parsed is None:
            print(colored("Oops! Enter awards like: inspire 1 or other 2", FG_RED))
            continue
        awards.append(parsed)

    args = argparse.Namespace(
        rank=rank,
        teams=teams,
        alpha=alpha,
        captain=captain,
        draft=draft,
        playoff=playoff,
        award=awards,
    )
    return args

# --------------------------
# Main compute + run
# --------------------------
def compute_points_from_args(args: argparse.Namespace):
    breakdown = []

    # Qualification
    q_pts = qualification_points(args.rank, args.teams, args.alpha)
    breakdown.append((f"Qualification Performance (rank {args.rank})", q_pts, f"Alpha={args.alpha}"))

    # Alliance captain
    cap_pts = alliance_captain_points(args.captain)
    note_cap = f"Alliance Captain #{args.captain}" if args.captain > 0 else ""
    breakdown.append(("Alliance Captain", cap_pts, note_cap))

    # Draft acceptance
    draft_pts = draft_acceptance_points(args.draft)
    note_draft = f"Draft acceptance #{args.draft}" if args.draft > 0 else ""
    breakdown.append(("Draft Order Acceptance", draft_pts, note_draft))

    # Playoff
    pp_pts = playoff_advancement_points(args.playoff)
    note_pp = f"Playoff place {args.playoff}" if args.playoff > 0 else ""
    breakdown.append(("Playoff Advancement", pp_pts, note_pp))

    # Judged awards sum
    awards_list = args.award or []
    total_awards_pts = 0
    award_notes = []
    for kind, place in awards_list:
        pts = judged_award_points(kind, place)
        total_awards_pts += pts
        award_notes.append(f"{kind.title()} #{place} (+{pts})")

    if total_awards_pts > 0:
        breakdown.append(("Judged Awards (sum)", total_awards_pts, ", ".join(award_notes)))
    else:
        breakdown.append(("Judged Awards (sum)", 0, ""))

    total = sum(p for _, p, _ in breakdown)
    return breakdown, total

def main():
    parser = argparse.ArgumentParser(description="FTC Advancement Points Calculator with PDF export")
    parser.add_argument("--rank", type=int, help="Qualification rank (R)")
    parser.add_argument("--teams", type=int, help="Number of teams (N)")
    parser.add_argument("--alpha", type=float, default=1.07, help="Alpha constant (default 1.07)")
    parser.add_argument("--captain", type=int, default=0, help="Alliance captain number")
    parser.add_argument("--draft", type=int, default=0, help="Draft acceptance number")
    parser.add_argument("--playoff", type=int, choices=[0,1,2,3,4], default=0, help="Playoff place (1..4), 0 if none")
    parser.add_argument("--award", action='append', nargs=2, metavar=('TYPE', 'PLACE'),
                        help="Judged award (e.g. inspire 1). Can be repeated.")
    args = parser.parse_args()

    if len(sys.argv) == 1:
        # Interactive mode
        user_args = interactive_mode()
    else:
        # Command line mode, parse awards list if present
        awards = []
        if args.award:
            for t,p in args.award:
                try:
                    place = int(p)
                    if place not in (1,2,3):
                        raise ValueError()
                    kind = t.lower()
                    if kind != 'inspire':
                        kind = 'other'  # default other
                    awards.append((kind, place))
                except Exception:
                    print(FG_RED + f"Invalid award input: {t} {p}" + STYLE_RESET)
                    sys.exit(1)
        user_args = argparse.Namespace(
            rank=args.rank,
            teams=args.teams,
            alpha=args.alpha,
            captain=args.captain,
            draft=args.draft,
            playoff=args.playoff,
            award=awards,
        )
        if user_args.rank is None or user_args.teams is None:
            print(FG_RED + "Rank and number of teams must be provided in command line mode." + STYLE_RESET)
            sys.exit(1)

    breakdown, total = compute_points_from_args(user_args)
    print_header()
    display_results(breakdown, total)
    export_pdf_report(breakdown, total)

if __name__ == "__main__":
    main()
