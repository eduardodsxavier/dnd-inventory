from cs50 import SQL

db = SQL("sqlite:///inventory.db")

while True:
    
    name = input("name:")
    price = input("price:")
    weight = input("weight:")
    damage = input("damage:")
    description = input("description:")
    
    db.execute("INSERT INTO items(type, name, category, price, weight, damage, description) VALUES('weapon', ?, 'Armas Simples Corpo-a-Corpo', ?, ?, ?, ?)", name, price, weight, damage, description)

    