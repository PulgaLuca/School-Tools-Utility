import os
import subprocess
import pandas as pd

# === CONFIGURATION ===

# Percorso alla cartella principale con tutti gli studenti
base_dir = "ALUMNI"

# Dizionario con gli output attesi degli script realizzati da ogni studente
expected_outputs = {
    "esercizio1.py": "Ciao Mondo\n",
    "esercizio2.py": "42\n"
}

# Punteggio massimo per esercizio corretto
punteggio_massimo = 1

# Lista per raccogliere i risultati dettagliati e creare il dataframe finale
results = []


for student in os.listdir(base_dir):
    student_path = os.path.join(base_dir, student)
    if os.path.isdir(student_path):
        for file in os.listdir(student_path):
            if file.endswith(".py"):
                script_path = os.path.join(student_path, file)
                try:
                    result = subprocess.run(
                        ["python", script_path],
                        capture_output=True,
                        text=True,
                        timeout=5
                    )
                    output = result.stdout
                    error = result.stderr

                    expected = expected_outputs.get(file, None)
                    if expected is None:
                        status = "output atteso non definito"
                        score = 0
                    elif output == expected:
                        status = "corretto"
                        score = punteggio_massimo
                    else:
                        status = "errato"
                        score = 0

                except subprocess.TimeoutExpired:
                    status = "timeout"
                    output = ""
                    expected = expected_outputs.get(file, "")
                    score = 0
                except Exception as e:
                    status = f"errore: {e}"
                    output = ""
                    expected = expected_outputs.get(file, "")
                    score = 0

                results.append({
                    "Studente": student,
                    "Script": file,
                    "Output ottenuto": output.strip(),
                    "Output atteso": (expected or "").strip(),
                    "Esito": status,
                    "Punteggio": score
                })

# === CREAZIONE DATAFRAME DETTAGLI ===
df = pd.DataFrame(results)

# === CALCOLO DEL PUNTEGGIO TOTALE PER STUDENTE ===
totali = df.groupby("Studente")["Punteggio"].sum().reset_index()
totali.rename(columns={"Punteggio": "Totale"}, inplace=True)

# === SCRITTURA SU FILE EXCEL ===
with pd.ExcelWriter("verifica_output_studenti.xlsx") as writer:
    df.to_excel(writer, sheet_name="Dettagli", index=False)
    totali.to_excel(writer, sheet_name="Riepilogo", index=False)

print("✅ File 'verifica_output_studenti.xlsx' creato con successo.")
