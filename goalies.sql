DROP TABLE IF EXISTS goalies;

CREATE TABLE goalies (
    team TEXT,
    season INTEGER,
    playerId INTEGER PRIMARY KEY,
    name TEXT,
    position TEXT,
    situation TEXT,
    games_played INTEGER,
    goals INTEGER,
    rebounds INTEGER,
    lowDangerShots INTEGER,
    mediumDangerShots INTEGER,
    highDangerShots INTEGER,
    lowDangerGoals INTEGER,
    mediumDangerGoals INTEGER,
    highDangerGoals INTEGER,
    penalityMinutes INTEGER,
    penalties INTEGER,
);