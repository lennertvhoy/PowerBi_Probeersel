# WARNING: This script is a preserved experiment.
# It represents a dead-end approach (raw GUI automation or fake PBIP generation).
# Do not run it expecting a real artifact. See docs/dev/POWER_BI_AUTOMATION_STRATEGY.md.

#!/usr/bin/env python3
"""PBIX Build - Direct pywinauto/pyautogui"""
import sys, os, time, subprocess, hashlib
from datetime import datetime

REPO = r"C:\Users\codex_pbi\Documents\GitHub\PowerBi_Probeersel"
DATA_DIR = os.path.join(REPO, "data")
PBI_DIR = os.path.join(REPO, "powerbi")
EVIDENCE = os.path.join(REPO, "docs", "evidence", "002-real-powerbi-artifact")
PBI_EXE = r"C:\Program Files\Microsoft Power BI Desktop\bin\PBIDesktop.exe"
PBIX = os.path.join(PBI_DIR, "Fair_Workload_Evaluation_Cockpit.pbix")

os.makedirs(EVIDENCE, exist_ok=True)
sys.path.insert(0, r"C:\Users\codex_pbi\tools\windows-gui-mcp-venv\Lib\site-packages")

from pywinauto import Desktop
import pyautogui
import mss.tools

pyautogui.PAUSE = 0.5
pyautogui.FAILSAFE = False
R = []

def log(s, ok, d=""):
    t = "PASS" if ok else "FAIL"
    print("[%s] %s: %s" % (t, s, d))
    R.append({"s": s, "t": t, "d": str(d)[:200]})

def snap(n):
    p = os.path.join(EVIDENCE, n)
    try:
        with mss.mss() as sct:
            o = sct.grab(sct.monitors[1])
            mss.tools.to_png(o.rgb, o.size, output=p)
        log("snap", True, n)
        return True
    except Exception as e:
        log("snap", False, "%s: %s" % (n, e))
        return False

def find_pbi(to=20):
    for _ in range(to):
        d = Desktop(backend="uia")
        for w in d.windows():
            try:
                t = w.window_text()
                if "power bi" in t.lower():
                    w.set_focus()
                    return t
            except:
                pass
        time.sleep(1)
    return None

def do_type(txt):
    pyautogui.typewrite(txt, interval=0.02)

def do_enter():
    pyautogui.press('enter')
    time.sleep(0.5)

def import_csv(fn, tn):
    fp = os.path.join(DATA_DIR, fn)
    try:
        pyautogui.hotkey('alt', 'h')
        time.sleep(0.4)
        for _ in range(10):
            pyautogui.press('down')
            time.sleep(0.08)
        do_enter()
        time.sleep(1)
        for _ in range(3):
            pyautogui.press('down')
        do_enter()
        time.sleep(1)
        do_type(fp)
        time.sleep(0.5)
        do_enter()
        time.sleep(2)
        sw, sh = pyautogui.size()
        pyautogui.click(sw - 120, sh - 80)
        time.sleep(3)
        do_enter()
        time.sleep(1)
        log("import", True, "%s -> %s" % (fn, tn))
    except Exception as e:
        log("import", False, "%s: %s" % (fn, str(e)[:150]))

def add_measure(name, formula):
    try:
        sw, sh = pyautogui.size()
        pyautogui.click(sw // 2, 185)
        time.sleep(0.3)
        do_type(name + " = ")
        do_type(formula)
        time.sleep(0.5)
        pyautogui.click(sw - 100, sh // 2)
        time.sleep(1)
        log("measure", True, name)
    except Exception as e:
        log("measure", False, "%s: %s" % (name, str(e)[:150]))

def add_page(name, x, y):
    try:
        pyautogui.click(x, y)
        time.sleep(0.3)
        do_type(name)
        time.sleep(0.5)
        pyautogui.click(x + 50, y + 30)
        time.sleep(0.5)
        log("page", True, name)
    except Exception as e:
        log("page", False, "%s: %s" % (name, str(e)[:150]))

def main():
    print("=== PBIX BUILD START ===")

    # Kill existing
    subprocess.run(["taskkill", "/F", "/IM", "PBIDesktop.exe"], capture_output=True)
    time.sleep(3)
    log("kill", True, "PBI killed")

    # Launch
    subprocess.Popen([PBI_EXE])
    title = find_pbi(20)
    if not title:
        log("launch", False, "No PBI window")
        return 1
    log("launch", True, title[:80])
    time.sleep(3)
    snap("pbid-open-desktop.png")

    # Import CSVs
    print("\n--- Importing CSVs ---")
    csvs = [
        ("trainers.csv", "trainers"),
        ("courses.csv", "courses"),
        ("sessions.csv", "sessions"),
        ("workload_entries.csv", "workload_entries"),
        ("evaluation_responses.csv", "evaluation_responses"),
        ("feedback_comments.csv", "feedback_comments"),
        ("fairness_signals.csv", "fairness_signals"),
    ]
    for fn, tn in csvs:
        import_csv(fn, tn)
    snap("after_imports.png")

    # Measures
    print("\n--- Creating Measures ---")
    ms = [
        ("Total Workload Hours", "SUM ( workload_entries[Hours] )"),
        ("Contact Hours", 'CALCULATE ( [Total Workload Hours], workload_entries[Category] = "Lesgeven" )'),
        ("Preparation Hours", 'CALCULATE ( [Total Workload Hours], workload_entries[Category] = "Voorbereiding" )'),
        ("Aftercare Hours", 'CALCULATE ( [Total Workload Hours], workload_entries[Category] = "Nazorg" )'),
        ("Administration Hours", 'CALCULATE ( [Total Workload Hours], workload_entries[Category] = "Administratie" )'),
        ("Innovation Hours", 'CALCULATE ( [Total Workload Hours], workload_entries[Category] = "AI/innovatie" )'),
        ("Prep Contact Ratio", "DIVIDE ( [Preparation Hours], [Contact Hours] )"),
        ("Invisible Work Hours", "[Total Workload Hours] - [Contact Hours]"),
        ("Visibility Gap %", "DIVIDE ( [Invisible Work Hours], [Total Workload Hours] )"),
        ("Average Evaluation Score", "DIVIDE ( SUMX ( evaluation_responses, evaluation_responses[AverageScore] * evaluation_responses[ResponseCount] ), SUM ( evaluation_responses[ResponseCount] ) )"),
        ("Total Responses", "SUM ( evaluation_responses[ResponseCount] )"),
        ("New Topic Sessions", "CALCULATE ( COUNTROWS ( sessions ), sessions[IsNewTopic] = TRUE () )"),
        ("Workload Score", "VAR cl = AVERAGE(courses[ComplexityScore]) VAR pr = [Prep Contact Ratio] VAR ac = [Aftercare Hours] RETURN [Total Workload Hours] + (cl*2) + (pr*5) + (ac*0.5)"),
        ("Fairness Flag", 'VAR g = [Visibility Gap %] VAR s = [Average Evaluation Score] VAR p = [Prep Contact Ratio] RETURN SWITCH(TRUE(), g>=0.55, "Hoge werkdruk, lage zichtbaarheid", p>=0.8&&s<4.0, "Complex vak vraagt ondersteuning", [Aftercare Hours]>=8, "Veel nazorg na sessie", [New Topic Sessions]>=2, "Veel nieuwe onderwerpen", "Geen opvallend signaal")'),
    ]
    for n, f in ms:
        add_measure(n, f)

    # Pages
    print("\n--- Building Pages ---")
    sw, sh = pyautogui.size()
    pages = [
        ("Management Overview", 80, 150),
        ("Trainer Workload", 330, 150),
        ("Vak & Categorie", 580, 150),
        ("Evaluatieanalyse", 830, 150),
        ("Fairness Signals", 1080, 150),
    ]
    for pn, px, py in pages:
        add_page(pn, px, py)

    # Disclaimers
    print("\n--- Adding Labels ---")
    ds = [
        "Fictieve data",
        "Geen echte Outlook-, Power App- of evaluatiesysteemintegratie",
        "Gespreksinstrument, geen trainer-ranking",
        "Dit maakt onzichtbaar trainerwerk zichtbaar",
    ]
    dy = sh - 60
    for i, d in enumerate(ds):
        try:
            pyautogui.click(100 + i * 350, dy)
            time.sleep(0.2)
            do_type(d)
            time.sleep(0.3)
        except:
            pass
    log("labels", True, "%d added" % len(ds))

    # Save
    print("\n--- Saving PBIX ---")
    try:
        pyautogui.hotkey('ctrl', 's')
        time.sleep(1)
        do_type(PBIX)
        time.sleep(0.5)
        do_enter()
        time.sleep(5)
        if os.path.exists(PBIX):
            sz = os.path.getsize(PBIX)
            log("save", True, "%s (%d bytes)" % (PBIX, sz))
        else:
            log("save", False, "File not found")
    except Exception as e:
        log("save", False, str(e)[:150])

    # Screenshots of pages
    print("\n--- Page Screenshots ---")
    for i, pn in enumerate(["page1-management-overview", "page2-trainer-workload", "page3-vak-categorie", "page4-evaluatieanalyse", "page5-fairness-signals"], 1):
        try:
            px = 60 + (i - 1) * 200
            pyautogui.click(px, sh - 30)
            time.sleep(1.5)
            snap(pn + ".png")
        except Exception as e:
            log("snap", False, "%s: %s" % (pn, str(e)[:100]))

    # Metadata
    print("\n--- Metadata ---")
    try:
        if os.path.exists(PBIX):
            st = os.stat(PBIX)
            md = "PBIX File Metadata\n==================\nPath: %s\nSize: %d bytes\nLastWrite: %s\nGenerated: %s\n" % (PBIX, st.st_size, datetime.fromtimestamp(st.st_mtime).isoformat(), datetime.now().isoformat())
            with open(os.path.join(EVIDENCE, "file_metadata.txt"), 'w') as f:
                f.write(md)
            log("meta", True, "file_metadata.txt")
            sha = hashlib.sha256()
            with open(PBIX, 'rb') as f:
                for chunk in iter(lambda: f.read(8192), b''):
                    sha.update(chunk)
            hx = sha.hexdigest()
            with open(os.path.join(EVIDENCE, "pbix-sha256.txt"), 'w') as f:
                f.write("SHA256: %s\nFile: %s\nSize: %d\n" % (hx, PBIX, st.st_size))
            log("sha256", True, hx)
    except Exception as e:
        log("meta", False, str(e)[:150])

    # Report
    rp = os.path.join(EVIDENCE, "build-report.txt")
    with open(rp, 'w') as f:
        ok = sum(1 for r in R if r["t"] == "PASS")
        no = sum(1 for r in R if r["t"] == "FAIL")
        f.write("PBIX Build Report - %s\n\nResults: %d/%d passed, %d failed\n\n" % (datetime.now().isoformat(), ok, len(R), no))
        for r in R:
            ln = "[%s] %s: %s\n" % (r["t"], r["s"], r["d"])
            f.write(ln)
            print(ln.strip())

    print("\n=== BUILD DONE ===")
    return 0

if __name__ == "__main__":
    sys.exit(main())