import os
import pandas as pd
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from classroom_utils import get_course_id, get_coursework_id, get_students, get_submissions_with_attachments
from drive_utils import download_drive_file
from report import Report

def authenticate(scopes):
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", scopes)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", scopes)
            creds = flow.run_local_server(port=0)
        with open("token.json", "w") as token:
            token.write(creds.to_json())
    return creds

def download_assignments(service, drive_service, course_name, coursework_name):
    course_id = get_course_id(service, course_name)
    coursework_id = get_coursework_id(service, course_id, coursework_name)
    students = get_students(service, course_id)
    submissions = get_submissions_with_attachments(service, course_id, coursework_id)
    
    output_folder = os.path.join(course_name, coursework_name)
    os.makedirs(output_folder, exist_ok=True)
    
    for user_id, file_id in submissions:
        student_name = students.get(user_id, f"Unknown_Student_{user_id}")
        student_folder = os.path.join(output_folder, student_name)
        os.makedirs(student_folder, exist_ok=True)
        download_drive_file(drive_service, file_id, student_folder)
    
    output_excel = os.path.join(output_folder, "report.xlsx")
    Report.create_submission_report(students, submissions, output_excel)
    print(f"Compiti scaricati in {output_folder}")

def upload_grades(service, file_path):
    print(f"Caricamento voti da: {file_path}")
    
    # Leggere il file Excel
    df = pd.read_excel(file_path)
    
    # Assicurarsi che le colonne necessarie siano presenti
    required_columns = {"Cognome", "Nome", "Voto", "Note"}
    if not required_columns.issubset(df.columns):
        print("Errore: Il file Excel deve contenere le colonne Cognome, Nome, Voto e Note.")
        return
    
    # Creare la colonna 'Nome Completo' per facilitare la ricerca degli studenti
    df['Nome Completo'] = (df['Nome'] + " " + df['Cognome']).str.lower().str.strip()
    
    # Richiedere nome corso e nome prova
    course_name = input("Enter the name of the course: ")
    coursework_name = input("Enter the name of the assignment: ")
    
    # Recuperare ID del corso e ID della prova
    course_id = get_course_id(service, course_name)
    coursework_id = get_coursework_id(service, course_id, coursework_name)
    
    # Ottenere la lista degli studenti iscritti al corso
    students = get_students(service, course_id)
    student_dict = {v.lower().strip(): k for k, v in students.items()}  # Invertire nome e ID studente, con to lower

    # Recuperare i voti e commenti dal file e aggiornarli su Classroom
    for index, row in df.iterrows():
        nome_completo = row['Nome Completo']
        voto = row['Voto']
        commento = row['Note']
        
        # Saltare se il voto è vuoto o non valido
        if pd.isna(voto) or str(voto).strip() == "-":
            print(f"Nessun voto assegnato a {nome_completo}, salto aggiornamento.")
            continue

        if nome_completo in student_dict:
            student_id = student_dict[nome_completo]

            # Aggiornare il voto
            grade_body = {'draftGrade': voto}
            try:
                service.courses().courseWork().studentSubmissions().patch(
                    courseId=course_id,
                    courseWorkId=coursework_id,
                    id=student_id,
                    updateMask='draftGrade',
                    body=grade_body
                ).execute()
                print(f"Voto aggiornato per {nome_completo} - ({voto})")
            except Exception as e:
                print(f"Errore aggiornando il voto per {nome_completo}: {e}")

            # Aggiungere il commento privato (solo se il campo Note non è vuoto)
            if not pd.isna(commento) and str(commento).strip() != "":
                comment_body = {
                    'addAttachments': [
                        {
                            'link': {
                                'title': commento
                            }
                        }
                    ]
                }
                try:
                    print("student_id: ", student_id)
                    service.courses().courseWork().studentSubmissions().modifyAttachments(
                        courseId=course_id,
                        courseWorkId=coursework_id,
                        id=student_id,
                        body=comment_body
                    ).execute()
                    print(f"Commento aggiunto per {nome_completo}")
                except Exception as e:
                    print(f"Errore aggiungendo il commento per {nome_completo}: {e}")
            else:
                print(f"Nessun commento da aggiungere per {nome_completo}.")
        else:
            print(f"Studente {nome_completo} non trovato in Google Classroom.")
    
    print("Caricamento completato!")

def main():
    SCOPES = [
    'https://www.googleapis.com/auth/classroom.courses.readonly',
    'https://www.googleapis.com/auth/classroom.courseworkmaterials.readonly',
    'https://www.googleapis.com/auth/classroom.student-submissions.students.readonly',
    'https://www.googleapis.com/auth/classroom.rosters.readonly',
    'https://www.googleapis.com/auth/drive.readonly',
    'https://www.googleapis.com/auth/drive',
    'https://www.googleapis.com/auth/classroom.coursework.students'
    ]

    
    creds = authenticate(SCOPES)
    service = build("classroom", "v1", credentials=creds)
    drive_service = build("drive", "v3", credentials=creds)
    
    while True:
        print("\nMenu:")
        print("1. Scarica compiti di una classe")
        print("2. Carica voti da file Excel")
        print("3. Esci")
        
        choice = input("Seleziona un'opzione: ")
        
        if choice == "1":
            course_name = input("Inserisci il nome del corso: ")
            coursework_name = input("Inserisci il nome della prova: ")
            download_assignments(service, drive_service, course_name, coursework_name)
        elif choice == "2":
            file_path = input("Inserisci il percorso del file Excel con i voti: ")
            upload_grades(service, file_path)
        elif choice == "3":
            print("Uscita dal programma.")
            break
        else:
            print("Scelta non valida. Riprova.")

if __name__ == "__main__":
    main()
