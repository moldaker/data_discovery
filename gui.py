# import library
from tkinter import *
from profiler import table_summary, field_summary, overall_summary
import pandas as pd

#  initialize window
window = Tk()

#  function for button
def click():
    entered_input = textentry_input.get()
    data = pd.read_csv(entered_input)

    entered_ouput = textentry_output.get()
    overall_summary(data, entered_ouput)

    output.delete(0.0, END)
    output.insert(END, 'profiling is complete. results available in working directory')

#  add title
window.title("Data Profiler")
window.configure(background='black')

#  add image and label
Label(window, text="What is your file path?", bg="black", fg="white", font="segoe 12 bold").grid(row=1, column=0, sticky=W)

#  add text entry box for file path
textentry_input = Entry(window, width=50, bg="grey")
textentry_input.grid(row=2, column=0, sticky=W)

#  add image and label
Label(window, text="Where would you like your summary?", bg="black", fg="white", font="segoe 12 bold").grid(row=3, column=0, sticky=W)

#  add text entry box for output file path
textentry_output = Entry(window, width=50, bg="blue")
textentry_output.grid(row=4, column=0, sticky=W)

#  create button
Button(window, text="Submit", width=6, command=click).grid(row=5, column=0, sticky=W)

#  create text box output
output = Text(window, width=75, height=2, wrap=WORD, background='grey')
output.grid(row=6, column=0, columnspan=2, sticky=W)

window.mainloop()

