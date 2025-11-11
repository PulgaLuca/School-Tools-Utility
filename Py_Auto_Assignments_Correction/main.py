import os
import subprocess
import pandas as pd

# === CONFIGURAZIONE ===

BASE_DIR = "ALUMNI"

EXPECTED_OUTPUTS = {
    "esercizio1.py": "14-PROGRAMMAZIONE-P-e\n",
    "esercizio2.py": "\n",
    "esercizio3.py": "ÈO\n",
    "esercizio4.py": "80.0---120.0\n"
}

PUNTEGGIO_MASSIMO = 1


# === FUNZIONI ===

def esegui_script(script_path):
    """Esegue uno script Python e restituisce output, errore ed esito."""
    try:
        result = subprocess.run(
            ["python", script_path],
            capture_output=True,
            text=True,
            timeout=5
        )
        return result.stdout, result.stderr, None
    except subprocess.TimeoutExpired:
        return "", "", "timeout"
    except Exception as e:
        return "", str(e), "errore esecuzione"


def valuta_output(file_name, output, error, expected):
    """Valuta il risultato di uno script confrontandolo con l'output atteso."""
    if error:
        return "errore", 0, error.strip()

    if expected is None:
        return "output atteso non definito", 0, "Output atteso non fornito."

    if output == expected:
        return "corretto", PUNTEGGIO_MASSIMO, ""
    else:
        descrizione = f"Output errato. Ottenuto: '{output.strip()}', Atteso: '{expected.strip()}'"
        return "errato", 0, descrizione


def correggi_studente(student_path, student_name):
    """Corregge tutti gli esercizi di uno studente e restituisce i risultati."""
    risultati = []
    for file in os.listdir(student_path):
        if not file.endswith(".py"):
            continue

        script_path = os.path.join(student_path, file)
        output, error, stato_exec = esegui_script(script_path)

        expected = EXPECTED_OUTPUTS.get(file)
        if stato_exec == "timeout":
            esito, punteggio, descrizione = "timeout", 0, "Esecuzione scaduta (timeout)."
        elif stato_exec == "errore esecuzione":
            esito, punteggio, descrizione = "errore", 0, f"Errore durante l'esecuzione: {error}"
        else:
            esito, punteggio, descrizione = valuta_output(file, output, error, expected)

        risultati.append({
            "Studente": student_name,
            "Script": file,
            "Output ottenuto": output.strip(),
            "Output atteso": (expected or "").strip(),
            "Esito": esito,
            "Descrizione": descrizione,
            "Punteggio": punteggio
        })

    return risultati


def scrivi_report_txt(student_name, risultati, output_dir="ZZ_report_txt"):
    """Crea un file di riepilogo .txt per ogni studente."""
    os.makedirs(output_dir, exist_ok=True)
    filepath = os.path.join(output_dir, f"{student_name}_report.txt")

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(f"Riepilogo esercizi per: {student_name}\n")
        f.write("=" * 50 + "\n\n")
        for r in risultati:
            f.write(f"File: {r['Script']}\n")
            f.write(f"Esito: {r['Esito']}\n")
            if r["Descrizione"]:
                f.write(f"Descrizione: {r['Descrizione']}\n")
            f.write("\n")
    return filepath


def correggi_tutti():
    """Esegue la correzione su tutti gli studenti e genera i report."""
    risultati_globali = []

    for student in os.listdir(BASE_DIR):
        student_path = os.path.join(BASE_DIR, student)
        if not os.path.isdir(student_path):
            continue

        print(f"🔍 Correzione per {student}...")
        risultati = correggi_studente(student_path, student)
        risultati_globali.extend(risultati)
        scrivi_report_txt(student, risultati)

    return risultati_globali


def salva_excel(risultati):
    """Salva i risultati in un file Excel con dettaglio e riepilogo."""
    df = pd.DataFrame(risultati)
    totali = df.groupby("Studente")["Punteggio"].sum().reset_index()
    totali.rename(columns={"Punteggio": "Totale"}, inplace=True)

    with pd.ExcelWriter("verifica_output_studenti.xlsx") as writer:
        df.to_excel(writer, sheet_name="Dettagli", index=False)
        totali.to_excel(writer, sheet_name="Riepilogo", index=False)

    print("✅ File 'verifica_output_studenti.xlsx' creato con successo.")


# === ESECUZIONE ===
if __name__ == "__main__":
    risultati = correggi_tutti()
    salva_excel(risultati)
    print("📄 Report TXT generati in 'ZZ_report_txt/'")
