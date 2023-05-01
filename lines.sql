DROP TABLE IF EXISTS lines;

CREATE TABLE lines (
    team TEXT,
    season INTEGER,
    name TEXT PRIMARY KEY,
    position TEXT,
    games_played INTEGER,
    icetime INTEGER,
    goalsFor INTEGER,
    penaltiesFor INTEGER,
    penalityMinutesFor INTEGER,
    hitsFor INTEGER,
    takeawaysFor INTEGER,
    giveawaysFor INTEGER,
    goalsAgainst INTEGER,
    penaltiesAgainst INTEGER,
    penalityMinutesAgainst INTEGER,
);