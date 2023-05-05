import sqlite3

conn = sqlite3.connect('hockey.db')
c = conn.cursor()
c.execute("DROP TABLE IF EXISTS userPlays")

query ='''CREATE TABLE userPlays(
    playNum INTEGER NOT NULL,
    userGameId INTEGER NOT NULL,
    playType TEXT NOT NULL,
    player TEXT NOT NULL,
    team TEXT NOT NULL,
    period INTEGER,
    comment TEXT,
    CHECK (period > 0 AND period < 5),
    CONSTRAINT fk_games
    FOREIGN KEY (userGameId)
        REFERENCES userGames (userGameId)
        ON DELETE CASCADE
)'''
c.execute(query)

print("Table created successfully........")

conn.commit()
conn.close()