from llama_cpp import Llama
import numpy as np
import re
import sqlite3

class UserTask():
    def __init__(self, uuid, taskid, name, date_due, time_due, deadline, status, subdivisions, reward, subtasks, grant_status):
        self.uuid = uuid
        self.taskid = taskid
        self.name = name
        self.status = status
        self.subdivisions = subdivisions
        self.deadline = deadline
        self.time_due = time_due
        self.date_due = date_due
        self.reward = reward
        self.grant_status = grant_status
        self.subtasks = subtasks

class AIEngine():
    def __init__(self):
        self.llm = Llama(
            model_path="qwen2.5-0.5b-instruct-q4_k_m.gguf", 
            n_ctx=2048, 
            n_gpu_layers=0, 
            verbose=False
        )

    def get_subtask_list(self, task_name, num_steps):
        list_msg = [
            {
                "role": "system", 
                "content": "You are a rigid automated planner. Output ONLY a numbered list."
            },

            {
                "role": "user", 
                "content": f"Task: {task_name}\nRequirement: Create exactly {num_steps} steps."
            }
        ]

        task_list = self.llm.create_chat_completion(
            messages=list_msg,
            temperature=0.1,
            max_tokens=250
        )

        task_list = task_list['choices'][0]['message']['content']
        sub_tasks_dict = self.split_task_list(task_list)

        return sub_tasks_dict
    
    def get_task_diff(self, task_name):
        diff_msg = [
            {
                "role": "system", 
                "content": "You are a difficulty rater. Output ONLY a single integer number between 0 and 100. Do not write words."
            },

            {
                "role": "user", 
                "content": f"Task: {task_name}\nRequirement: Rate a difficulty out of 100."
            }
        ]
        
        difficulty = self.llm.create_chat_completion(
            messages=diff_msg,
            temperature=0.1,
            max_tokens=250
        )

        difficulty = int(difficulty['choices'][0]['message']['content'])
        difficulty = np.interp(difficulty, [75, 100], [0, 100])

        return difficulty
    
    def split_task_list(self, task_list):
        segments = re.split(r'(\d+)\.', task_list)
        sub_tasks_dict = {}

        for i in range(1, len(segments), 2):
            step_number = int(segments[i])
            step_text = segments[i+1].strip()
            sub_tasks_dict[step_number] = step_text
        
        return sub_tasks_dict
    
ai_engine = AIEngine()

class TaskDataHandler():
    def __init__(self, db_path='app_data'):
        self.db_path = db_path

    def _get_conn(self):
        return sqlite3.connect(self.db_path)
    
    def task_insertion(self, task_specs):
        try:
            with self._get_conn() as conn:
                curr = conn.cursor()
                curr.execute(
                    'INSERT INTO tasks (uuid, name, subdivisions, deadline, date_due, time_due, reward) VALUES (?, ?, ?, ?, ?, ?, ?)', 
                    (task_specs.uuid, task_specs.name, task_specs.subdivisions, task_specs.deadline, task_specs.date_due, task_specs.time_due, task_specs.reward)
                )
                current_task_id = curr.lastrowid
                conn.commit()
        except sqlite3.IntegrityError:
            return 0
        
        if task_specs.subdivisions != 0:
            for i in range(task_specs.subdivisions):
                try:
                    with self._get_conn() as conn:
                        conn.cursor().execute(
                            'INSERT INTO subtasks (parent_id, subtask_order, name) VALUES (?, ?, ?)', 
                            (current_task_id, i, task_specs.subtasks[i+1])
                        )
                        conn.commit()
                except sqlite3.IntegrityError as e:
                    print(e)
                    return 0
                
    def query_user_tasks(self, uuid):
        taskid_list = []

        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT taskid FROM tasks WHERE uuid = ?', (uuid,))
            result = cursor.fetchall()

        for i in range(len(result)):
            taskid_list.append(result[i][0])
        
        if not taskid_list:
            return []

        taskid_string = ',' .join(['?'] * len(taskid_list))
        
        sql = f"SELECT * FROM tasks WHERE taskid IN ({taskid_string})"
        
        user_task_list = []
        
        with self._get_conn() as conn:
            conn.row_factory = sqlite3.Row 
            cursor = conn.cursor()
            cursor.execute(sql, taskid_list)
            rows = cursor.fetchall()
            
            for row in rows:
                row_data = dict(row) 
                row_data['subtasks'] = None 
                if row_data['subdivisons'] != 0:
                    pass
                user_task = UserTask(**row_data)
                user_task_list.append(user_task)

        return user_task_list
    
    def task_update_status(self, status, taskid):
        with self._get_conn() as conn:
            conn.cursor().execute('UPDATE tasks SET status = ? WHERE taskid = ?', (status, taskid))
            conn.commit()

    def subtask_update_status(self):
        pass

    def task_deletion(self, taskid):
        with self._get_conn() as conn:
            conn.cursor().execute('DELETE FROM tasks WHERE taskid = ?', (taskid,))
            conn.commit()