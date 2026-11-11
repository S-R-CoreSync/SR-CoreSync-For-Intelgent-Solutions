"""Export the structure plan to PDF so it can be followed from another IDE.

Kept separate from build_plan_page.py because it needs a browser; the chain is
  python docs/build_plan_page.py && python docs/build_plan_pdf.py
"""
import pathlib, subprocess, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
HTML = ROOT / "docs" / "plan-v18-structure.html"
PDF = ROOT / "docs" / "plan-v18-structure.pdf"
CHROME = [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
]


def main():
    if not HTML.exists():
        print("build the page first:")
        return 2
    binary = next((c for c in CHROME if pathlib.Path(c).exists()), None)
    if not binary:
        print("no Chrome/Edge found for PDF export")
        return 3
    profile = pathlib.Path(r"C:\Windows\Temp\sr-plan-pdf")
    subprocess.run([binary, "--headless=new", "--disable-gpu", "--no-first-run",
                    f"--user-data-dir={profile}", "--no-pdf-header-footer",
                    "--print-to-pdf=" + str(PDF), HTML.as_uri()],
                   check=False, capture_output=True)
    if PDF.exists():
        print(f"wrote {PDF} ({PDF.stat().st_size:,} bytes)")
        return 0
    print("PDF was not produced")
    return 4


if __name__ == "__main__":
    sys.exit(main())
