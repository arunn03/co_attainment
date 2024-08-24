from tkinter import *
from tkinter import ttk, messagebox as msg, filedialog as fd
from datetime import datetime
from database import *
from csv_reader import *
from ocr.main import *
import pandas as pd
from PIL import Image, ImageTk
import cv2

class App(Tk):

    class MarkWindow(Toplevel):
        def __init__(self, master, marks, answer_script, callback):
            super().__init__(master)
            self.title()
            self.config(bg='white')

            style = ttk.Style(self)

            style.configure("Custom.Treeview.Heading", background="grey", font=('Calibri', 10, 'bold'),
                            foreground="black")

            self.marks = marks
            self.callback = callback

            self.mark_frame = Frame(self, bg='white')
            self.mark_frame.pack(side=TOP, fill=X, expand=True, padx=20, pady=20)

            self.image_frame = Frame(self, bg='white')
            self.image_frame.pack(side=BOTTOM, fill=BOTH, expand=True, padx=20, pady=10)

            self.image_title = Label(self.image_frame, bg='white', text='Answer Script')
            self.image_title.pack(pady=10)

            self.part_a_title = Label(self.mark_frame, bg='white', text='PART-A')
            self.part_a_title.pack(pady=10)

            # Create the Treeview table
            self.part_a_tree = ttk.Treeview(self.mark_frame, columns=(1, 2, 3, 4, 5, 6, 7, 8, 9, 10), show='headings', style="Custom.Treeview", height=1)
            self.part_a_tree.pack(fill=X, expand=True)

            for i in range(1, 11):
                self.part_a_tree.heading(i, text=f"{i}")
                self.part_a_tree.column(str(i), width=50, anchor=CENTER)

            self.part_a_tree.insert("", "end", iid=1, values=self.marks[0])
            self.part_a_tree.bind("<Double-1>", lambda event: self.on_double_click(event, self.part_a_tree))

            self.part_b_title = Label(self.mark_frame, bg='white', text='PART-B')
            self.part_b_title.pack(pady=10)

            self.part_b_tree = ttk.Treeview(self.mark_frame, columns=(1, 2, 3, 4, 5, 6, 7, 8, 9), show='headings', style="Custom.Treeview", height=3)
            self.part_b_tree.pack(fill=X, expand=True)

            self.part_b_tree.heading(1)
            self.part_b_tree.column('1', width=40, anchor=CENTER)
            for i in range(11, 19):
                self.part_b_tree.heading(i-9, text=f"{i}")
                self.part_b_tree.column(str(i-9), width=50, anchor=CENTER)

            for i in range(3):
                self.part_b_tree.insert('', 'end', iid=i, values=[chr(ord('a') + i)] + self.marks[i+1])
                self.part_b_tree.bind("<Double-1>", lambda event: self.on_double_click(event, self.part_b_tree))

            self.set_image(answer_script)

            self.transient(master)
            self.grab_set()
            self.focus_set()

            self.protocol("WM_DELETE_WINDOW", self.on_close)

        def set_image(self, answer_script_path):

            answer_script = cv2.imread(answer_script_path)
            x, y, w, h = 192, 1912, 2264, 1440
            answer_script = answer_script[y:y+h, x:x+w, :]
            answer_script = cv2.cvtColor(answer_script, cv2.COLOR_BGR2RGB)

            desired_height = 300
            ratio = desired_height / answer_script.shape[0]
            new_dimensions = (int(answer_script.shape[1] * ratio), desired_height)
            answer_script = cv2.resize(answer_script, new_dimensions, interpolation=cv2.INTER_AREA)

            self.pil_image = Image.fromarray(answer_script)
            self.photo = ImageTk.PhotoImage(image=self.pil_image)

            answer_script_image = Label(self.image_frame, image=self.photo)
            answer_script_image.pack()

            answer_script_image.image = self.photo

        def on_double_click(self, event, tree):
            item = tree.identify_row(event.y)
            column = tree.identify_column(event.x)
            if len(tree['columns']) == 9 and column == '#1':
                return
            if item and column:
                column_index = int(column[1:]) - 1
                x, y, width, height = tree.bbox(item, column)
                value = tree.set(item, column)

                self.entry = Entry(tree, width=width // 8)
                self.entry.place(x=x, y=y, width=width, height=height)
                self.entry.insert(0, value)
                self.entry.focus()

                self.entry.bind("<Return>", lambda e: self.on_return(item, column_index, tree))
                self.entry.bind("<FocusOut>", lambda e: self.on_return(item, column_index, tree))

        def on_return(self, item, column_index, tree):
            value = self.entry.get()
            tree.set(item, column=f"#{column_index + 1}", value=value)
            self.entry.destroy()

        def on_close(self):
            updated_marks = list(
                self.part_a_tree.item('1', "values"))
            for i in range(3):
                updated_marks.extend(self.part_b_tree.item(str(i), "values")[1:])

            if self.callback:
                self.callback(list(map(int, updated_marks)))
            self.destroy()

    def __init__(self):
        super().__init__()
        self.title('CO Attainment')
        self.geometry('800x400')
        self.config(bg='white')

        self.departments = ['CSE', 'ECE', 'MECH', 'CIVIL', 'EEE', 'AIDS', 'IT']
        current_year = datetime.now().year
        self.years = [i for i in range(current_year-10, current_year+1)]
        self.exams = ['MS1', 'MS2', 'FINAL']

        self.dept_var = StringVar()
        self.dept_var.set('Select')
        self.sub_code_var = StringVar()
        self.exam_var = StringVar()
        self.exam_var.set('Select')
        self.batch_var = IntVar()
        self.batch_var.set(current_year)
        self.co1_var = StringVar()
        self.co2_var = StringVar()
        self.co3_var = StringVar()
        self.co4_var = StringVar()
        self.co5_var = StringVar()
        self.co6_var = StringVar()

        self.main_frame = Frame(self, bg='white')
        self.main_frame.pack(padx=50, pady=20)

        self.btn_frame = Frame(self, bg='white')
        self.btn_frame.pack(padx=10, pady=15, side=BOTTOM)

        self.lbl_dept = Label(self.main_frame, bg='white', text='DEPT:')
        self.lbl_dept.grid(row=0, column=0, padx=5, pady=10, sticky='e')

        self.entry_dept = ttk.Combobox(self.main_frame, width=10, textvar=self.dept_var,
                                       values=self.departments, state='readonly')
        self.entry_dept.grid(row=0, column=1, padx=5, pady=10, sticky='w')

        self.lbl_sub_code = Label(self.main_frame, bg='white', text='SUBJECT:')
        self.lbl_sub_code.grid(row=0, column=2, padx=5, pady=10, sticky='e')

        self.entry_sub_code = ttk.Entry(self.main_frame, width=10, textvar=self.sub_code_var)
        self.entry_sub_code.grid(row=0, column=3, padx=5, pady=10, sticky='w')

        self.lbl_exam = Label(self.main_frame, bg='white', text='EXAM:')
        self.lbl_exam.grid(row=0, column=4, padx=5, pady=10, sticky='e')

        self.entry_exam = ttk.Combobox(self.main_frame, width=10, textvar=self.exam_var,
                                       values=self.exams, state='readonly')
        self.entry_exam.grid(row=0, column=5, padx=5, pady=10, sticky='w')

        self.lbl_batch = Label(self.main_frame, bg='white', text='BATCH:')
        self.lbl_batch.grid(row=0, column=6, padx=5, pady=10, sticky='e')

        self.entry_batch = ttk.Combobox(self.main_frame, width=5, textvar=self.batch_var, values=self.years)
        self.entry_batch.grid(row=0, column=7, padx=5, pady=10, sticky='w')

        self.lbl_co1 = Label(self.main_frame, bg='white', text='CO1:')
        self.lbl_co1.grid(row=1, column=0, padx=5, pady=10, sticky='e')

        self.entry_co1 = ttk.Entry(self.main_frame, textvar=self.co1_var)
        self.entry_co1.grid(row=1, column=1, padx=5, pady=10, sticky='w')

        self.lbl_co2 = Label(self.main_frame, bg='white', text='CO2:')
        self.lbl_co2.grid(row=1, column=2, padx=5, pady=10, sticky='e')

        self.entry_co2 = ttk.Entry(self.main_frame, textvar=self.co2_var)
        self.entry_co2.grid(row=1, column=3, padx=5, pady=10, sticky='w')

        self.lbl_co3 = Label(self.main_frame, bg='white', text='CO3:')
        self.lbl_co3.grid(row=1, column=4, padx=5, pady=10, sticky='e')

        self.entry_co3 = ttk.Entry(self.main_frame, textvar=self.co3_var)
        self.entry_co3.grid(row=1, column=5, padx=5, pady=10, sticky='w')

        self.lbl_co4 = Label(self.main_frame, bg='white', text='CO4:')
        self.lbl_co4.grid(row=2, column=0, padx=5, pady=10, sticky='e')

        self.entry_co4 = ttk.Entry(self.main_frame, textvar=self.co4_var)
        self.entry_co4.grid(row=2, column=1, padx=5, pady=10, sticky='w')

        self.lbl_co5 = Label(self.main_frame, bg='white', text='CO5:')
        self.lbl_co5.grid(row=2, column=2, padx=5, pady=10, sticky='e')

        self.entry_co5 = ttk.Entry(self.main_frame, textvar=self.co5_var)
        self.entry_co5.grid(row=2, column=3, padx=5, pady=10, sticky='w')

        self.lbl_co6 = Label(self.main_frame, bg='white', text='CO6:')
        self.lbl_co6.grid(row=2, column=4, padx=5, pady=10, sticky='e')

        self.entry_co6 = ttk.Entry(self.main_frame, textvar=self.co6_var)
        self.entry_co6.grid(row=2, column=5, padx=5, pady=10, sticky='w')

        self.btn_sub = ttk.Button(self.btn_frame, text='Submit', width=10, command=self.submit)
        self.btn_sub.grid(row=0, column=0, padx=5)

    def submit(self):
        dept = None if self.dept_var.get() == "Select" else self.dept_var.get()
        sub_code = None if self.sub_code_var.get() == "" else self.sub_code_var.get()
        exam = None if self.exam_var.get() == "Select" else self.exam_var.get()
        batch = self.batch_var.get()
        co1 = None if self.co1_var.get() == "" else self.co1_var.get().split(',')
        co2 = None if self.co2_var.get() == "" else self.co2_var.get().split(',')
        co3 = None if self.co3_var.get() == "" else self.co3_var.get().split(',')
        co4 = None if self.co4_var.get() == "" else self.co4_var.get().split(',')
        co5 = None if self.co5_var.get() == "" else self.co5_var.get().split(',')
        co6 = None if self.co6_var.get() == "" else self.co6_var.get().split(',')
        if dept is None or exam is None or sub_code is None or co1 is None or co2 is None or co3 is None:
            msg.showerror('Error Found', 'Please check all inputs')
            return
        coq = [
            {
                'name': 'CO1',
                'data': co1
            },
            {
                'name': 'CO2',
                'data': co2
            },
            {
                'name': 'CO3',
                'data': co3
            }
        ]
        if co4 is not None:
            coq.append({
                'name': 'CO4',
                'data': co4
            })
        if co5 is not None:
            coq.append({
                'name': 'CO5',
                'data': co5
            })
        if co6 is not None:
            coq.append({
                'name': 'CO6',
                'data': co6
            })

        answer_scripts = fd.askopenfilenames(
            title='Select answer scripts',
            filetypes=[("Image Files", "*.jpg *.jpeg *.png")]
        )

        columns = [
            '1', '2', '3', '4', '5', '6', '7', '8', '9', '10',
            '11a', '12a', '13a', '14a', '15a', '16a', '17a', '18a',
            '11b', '12b', '13b', '14b', '15b', '16b', '17b', '18b',
            '11c', '12c', '13c', '14c', '15c', '16c', '17c', '18c',
        ]

        mark_data = []

        def update_marks(data):
            mark_data.append(data)

        for answer_script in answer_scripts:
            marks = recognize_marks(answer_script)
            # temp_marks = [marks[:10], marks[10:18], marks[18: 26], marks[26:]]
            window = self.MarkWindow(self, [marks[:10], marks[10:18], marks[18:26], marks[26:]], answer_script, update_marks)
            # window.grab_set()
            window.wait_window()
            # mark_data.append(marks)

        df = pd.DataFrame(mark_data, columns=columns)
        filename = f'{exam}_{sub_code}_{dept}_{batch}.csv'
        df.to_csv(filename, index=False)

        result = compute_co_attainment(filename, coq)
        conn = DBConnection()
        cursor = conn.cursor()
        try:
            cursor.execute(BASE_QUERY)
            query_data = (
                sub_code,
                dept,
                exam,
                batch,
                result['CO1'],
                result['CO2'],
                result['CO3'],
                result['CO4'],
                result['CO5'],
                result['CO6']
            )
            cursor.execute(INSERT_QUERY, query_data)
        except:
            msg.showerror('Error Occurred', 'Please check all inputs.\nMay be duplicate records are found.')
            return
        conn.commit()
        cursor.close()
        conn.close()
        msg.showinfo('Success', 'All records inserted successfully')

if __name__ == '__main__':
    root = App()
    root.mainloop()

# 7,8,9,10,14b,13a,13b
# 3,5,6,11b,14a
# 1,2,4,11a