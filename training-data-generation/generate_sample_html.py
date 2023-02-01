import names
import sqlite3
from random import randint
import string

con = sqlite3.connect("samples.db")
cur = con.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS samples(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    number TEXT NOT NULL,
    html TEXT
);
""")

with open("source-template/HomeScreen.html") as f:
    template_str = f.read()

def add_spaces(number):
    num_str = str(number)
    if len(num_str) != 10:
        raise Exception(f"{repr(num_str)} looks wrong")
    return " ".join([num_str[0:3], num_str[3:6], num_str[6:10]])


template = string.Template(template_str)
data = [(names.get_full_name().upper(),
         str(randint(4000000000, 4999999999))) for i in range(10000)]
expanded = [(name, number,
            template.substitute(name_in_caps=name,number_with_spaces=add_spaces(number)))
            for name, number in data]

cur.executemany("INSERT INTO samples (name, number, html) VALUES (?,?,?)",
    expanded)
con.commit()
