import sqlite3

conn = sqlite3.connect('hockey.db')
c = conn.cursor()
c.execute("DROP TABLE IF EXISTS userGames")

query ='''CREATE TABLE userGames(
    userGameId INTEGER PRIMARY KEY AUTOINCREMENT,
    homeTeam TEXT NOT NULL,
    awayTeam TEXT NOT NULL,
    date TEXT NOT NULL,
    homeScore INTEGER,
    awayScore INTEGER,
    firstStar TEXT,
    secondStar TEXT,
    thirdStar TEXT,
    comments TEXT,
    CHECK (homeScore >= 0 AND awayScore >= 0)
)'''
c.execute(query)

print("Table created successfully........")

conn.commit()
conn.close()
