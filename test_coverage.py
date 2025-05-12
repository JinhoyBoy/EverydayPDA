import unittest
import os
import coverage
import xml.etree.ElementTree as ET


def write_coverage_to_readme():
    # Coverage XML einlesen
    tree = ET.parse("coverage.xml")
    root = tree.getroot()

    # Gesamt-Coverage berechnen
    total_coverage = float(root.attrib["line-rate"]) * 100  # In Prozent umwandeln

    # Alle Dateien und deren Coverage extrahieren
    file_coverage = []
    for package in root.findall(".//package"):
        for clazz in package.findall(".//class"):
            filename = clazz.attrib["filename"]
            line_rate = float(clazz.attrib["line-rate"]) * 100  # In Prozent umwandeln
            file_coverage.append((filename, line_rate))

    # Markdown-Tabelle generieren
    table_header = "| Datei | Coverage (%) |\n|---|---|\n"
    table_rows = "\n".join(f"| {fname} | {coverage:.1f}% |" for fname, coverage in file_coverage)
    project_total_row = f"| **Projekt** | **{total_coverage:.1f}%** |"  # Gesamtwert hinzufügen
    table = table_header + table_rows + "\n" + project_total_row  # Tabelle zusammenfügen

    # README einlesen
    with open("ReadMe.md", "r") as file:
        content = file.readlines()

    # Coverage Badge hinzufügen oder ersetzen
    badge = f"![Coverage](https://img.shields.io/badge/Coverage-{total_coverage:.1f}%25-brightgreen)\n"
    found_badge = False
    found_table = False

    for i, line in enumerate(content):
        if "![Coverage]" in line:
            content[i] = badge
            found_badge = True
        if "| Datei | Coverage (%) |" in line:
            start_index = i
            while i < len(content) and content[i].strip():
                i += 1
            content[start_index:i] = [table + "\n"]
            found_table = True
            break

    # Falls kein Badge vorhanden ist, anhängen
    if not found_badge:
        content.append("\n" + badge)

    # Falls keine Tabelle vorhanden ist, anhängen
    if not found_table:
        content.append("\n" + table)

    # README aktualisieren
    with open("ReadMe.md", "w") as file:
        file.writelines(content)


def discover_and_run_tests():
    # Initialisiere Coverage
    cov = coverage.Coverage(source=["."], omit=["*/test_*"])
    cov.start()

    # Suche alle Dateien, die mit 'test_' beginnen
    test_files = []
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file.startswith('test_') and file.endswith('.py'):
                test_files.append(os.path.join(root, file))
    
    # Lade alle Tests mit unittest
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    for test_file in test_files:
        # Füge jede Test-Datei zum Test-Suite hinzu
        suite.addTests(loader.discover(os.path.dirname(test_file), pattern=os.path.basename(test_file)))
    
    # Führe die Tests aus
    runner = unittest.TextTestRunner()
    runner.run(suite)

    # Stoppe Coverage und gib das Ergebnis aus
    cov.stop()
    cov.save()
    cov.xml_report(outfile="coverage.xml")
    cov.report()

    write_coverage_to_readme()

if __name__ == "__main__":
    discover_and_run_tests()
