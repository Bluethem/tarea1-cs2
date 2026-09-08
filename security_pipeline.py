import subprocess
import sys
from datetime import datetime

OUTPUT_FILE = "dependency-report.txt"


def run(cmd):
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.stdout + result.stderr


def main():
    lines = []
    lines.append("=" * 54)
    lines.append("REPORTE DE DEPENDENCIAS — Security News Analyzer")
    lines.append(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("=" * 54)

    lines.append("\n--- pip list ---\n")
    lines.append(run(["pip", "list"]))

    lines.append("\n--- pipdeptree ---\n")
    lines.append(run(["pipdeptree"]))

    lines.append("\n--- pip-audit ---\n")
    audit_output = run(["pip-audit"])
    lines.append(audit_output)

    report = "\n".join(lines)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(report)

    print(report)
    print(f"\nReporte guardado en: {OUTPUT_FILE}")

    if "known vulnerabilit" in audit_output and "No known" not in audit_output:
        print("\n[FAIL] Se encontraron vulnerabilidades. Pipeline detenido.")
        sys.exit(1)

    print("\n[PASS] Sin vulnerabilidades conocidas.")
    sys.exit(0)


if __name__ == "__main__":
    main()
