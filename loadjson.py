# Ths program reads JSON file and inserts data into the vwquiz database
# It calls db_operations.db for database operations
import json
import uuid
from datetime import date
from vwquizfunclib import select_category, generate_uuid
from db_operations import connect_db, close_db, fetch_categories, fetch_subject_id, insert_question

def read_json_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"File {file_path} not found.")
    except json.JSONDecodeError:
        print(f"Invalid JSON format in {file_path}.")
    return None

def main():
    dryrun = input("Dry run? Yes for display only, No to import data into the database: Yes/No: ")
    source = input("Enter the source name: ")
    filename = input("Enter the filename of the JSON File: ")

    conn, cursor = connect_db()
    categories = fetch_categories(cursor)
    cat = select_category(categories)
    subject_id = fetch_subject_id(cursor, cat)

    if subject_id:
        subject_id = str(subject_id).replace('-', '')
        data = read_json_file(filename)
        if data:
            for question in data:
                question_id = generate_uuid()
                qtext = question['question']
                qtopic = question['topic']
                answer = question['correct_answer']
                difficulty_level = question['difficulty_level']
                reference = question['reference']
                answer_explanation = question['answer_explanation']
                qtype = question['type']
                created_at = date.today()
                updated_at = date.today()
          
                if question['type']=="IN":
                    optionstext=str(answer)
                else:
                    optionstext=question['choices']            
  
                question_data = (
                    question_id, created_at, updated_at, qtype, qtext, qtopic, 1,
                    answer_explanation, difficulty_level, reference, source, subject_id
                )

                if dryrun.lower() == "no":
                    insert_question(cursor, question_data)
                else:
                    print(question_data)
                    
          
                #optionstrue = [x==answer for x in options]
                optionstrue = [x in answer for x in optionstext]
                lookup_dict = dict(zip(optionstext, optionstrue))

                if question['type']=="IN":
                    answer=str(question['correct_answer'])
                    answer_id = generate_uuid()
                    is_correct=True
                    if dryrun=="No":   
                        cursor.execute('INSERT INTO quizapp_answer (uid, created_at, updated_at,answer,is_correct,question_id) VALUES (?, ?, ?, ?, ?, ?)', (answer_id, created_at, updated_at,answer,is_correct,question_id))
                        conn.commit()
                    else:
                        print (answer_id, created_at, updated_at,answer,is_correct,question_id)
          
                else:    
                # Iterate through List OptionsText and get corresponding values from List OptionsTrue
                    for a_option in optionstext:
                        answer_id = generate_uuid()
 
                        is_correct = lookup_dict.get(a_option) 
                
                        if dryrun=="No":   
                            cursor.execute('INSERT INTO quizapp_answer (uid, created_at, updated_at,answer,is_correct,question_id) VALUES (?, ?, ?, ?, ?, ?)', (answer_id, created_at, updated_at,a_option,is_correct,question_id))
                            conn.commit()
                        else:
                            print (answer_id, created_at, updated_at,a_option,is_correct,question_id)
                              

    close_db(conn)

if __name__ == "__main__":
    main()
    
