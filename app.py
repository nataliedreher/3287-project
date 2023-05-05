import sqlite3

from flask import Flask, redirect, g, url_for, request, render_template, make_response, session, flash
from wtforms import Form, StringField, SelectField, SubmitField
from wtforms.validators import DataRequired

class SearchForm(Form):
    search = StringField('Player Search', [DataRequired()])
    submit = SubmitField('Search', render_kw={'class': 'btn btn-success btn-block'})

class AddGameForm(Form):
    choices = ["ANA", "ARI", "BOS", "BUF", "CAR", "CBJ", "CGY", "CHI", "COL", "DAL", "DET", "EDM", "FLA", "LAK", "MIN", "MTL", "NJD", "NSH", "NYI", "NYR", "OTT", "PHI", "PIT", "SEA", "SJS", "STL", "TBL", "TOR", "VAN", "VGK", "WPG", "WSH"]
    homeTeam = SelectField('Home Team:', choices=choices)
    awayTeam = SelectField('Away Team:', choices=choices)
    gameDate = StringField('Game Date (DD/MM/YYYY)', [DataRequired()])
    homeScore = StringField('Home Score', [DataRequired()])
    awayScore = StringField('Away Score', [DataRequired()])
    firstStar = StringField('First Star', [DataRequired()])
    secondStar = StringField('Second Star', [DataRequired()])
    thirdStar = StringField('Third Star', [DataRequired()])
    comments = StringField('comments', [DataRequired()])
    submit = SubmitField('Submit', render_kw={'class': 'btn btn-success btn-block'})

class AddPlayForm(Form):
    choices = ["Goal", "Penalty", "Save", "Hit"]
    playType = SelectField('Home Team:', choices=choices)
    team = StringField('Team:', [DataRequired()]) 
    player = StringField('Player:', [DataRequired()]) 
    period = StringField('Period:', [DataRequired()]) 
    comment = StringField('Comment:', [DataRequired()]) 
    submit = SubmitField('Search', render_kw={'class': 'btn btn-success btn-block'})


app = Flask(__name__)

class PrefixMiddleware(object):
    def __init__(self, app, prefix=''):
        self.app = app
        self.prefix = prefix

    def __call__(self, environ, start_response):
        # set the prefix for all url to the Jupyterhub URL for my virtual machine
        # this path is set to my user [KNOX] and port [3308] 
        # (see the code at bottom to see how port is set to 3308 instead of 5000)
        environ['SCRIPT_NAME'] = "/" 
       
        # call the default processing
        return self.app(environ, start_response)

# insert our proxy setting url class as wrapper to the app
app.wsgi_app = PrefixMiddleware(app.wsgi_app)


def get_db_connection():
    conn = sqlite3.connect('hockey.db')
    c = conn.cursor()
    return conn

@app.route('/')
def index():
    return make_response(render_template("index.html"))

@app.route('/games')
@app.route('/games/<int:season>')
@app.route('/games/<int:season>/<string:team1>')
@app.route('/games/<int:season>/<string:team1>/<string:team2>')
def games(season=None, team1=None, team2=None):
    gamesLst = []
    teamsLst = ['ANA','ARI','BOS','BUF','CAR','CBJ','CGY','CHI','COL','DAL','DET','EDM','FLA','LAK','MIN','MTL','NJD','NSH','NYI','NYR','OTT','PHI','PIT','SEA','SJS','STL','TBL','TOR','VAN','VGK','WPG','WSH']
    if (team2):
        conn = sqlite3.connect('hockey.db')
        c = conn.cursor()
        c.execute("SELECT * FROM games WHERE season=? AND (team=? AND opposingTeam=?) ORDER BY gameDate DESC;", (str(season), team1, team2))
        gamesLst = c.fetchall()
        conn.commit()
        conn.close()
    return make_response(render_template("games.html", season=season, team1=team1, team2=team2, gamesLst=gamesLst, teamsLst=teamsLst))

@app.route('/goalies')
@app.route('/goalies/<string:team1>')
def goalies(team1=None):
    goalieLst = []
    if (team1):
        conn = sqlite3.connect('hockey.db')
        c = conn.cursor()
        c.execute("SELECT * FROM goalies WHERE team=?;", (team1, ))
        goalieLst = c.fetchall()
        conn.commit()
        conn.close()
    return make_response(render_template("goalies.html", team1=team1, goalieLst=goalieLst))

@app.route('/lines')
@app.route('/lines/<string:team1>')
def lines(team1=None):
    linesLst = []
    if (team1):
        conn = sqlite3.connect('hockey.db')
        c = conn.cursor()
        c.execute("SELECT * FROM lines WHERE team=?;", (team1, ))
        linesLst = c.fetchall()
        conn.commit()
        conn.close()
    return make_response(render_template("lines.html", team1=team1, linesLst=linesLst))

@app.route('/skaters')
@app.route('/skaters/<string:team1>')
def skaters(team1=None):
    skaterLst = []
    if (team1):
        conn = sqlite3.connect('hockey.db')
        c = conn.cursor()
        c.execute("SELECT * FROM skaters WHERE team=?;", (team1, ))
        skaterLst = c.fetchall()
        conn.commit()
        conn.close()
    return make_response(render_template("skaters.html", team1=team1, skaterLst=skaterLst))


@app.route('/search', methods=['GET', 'POST'])
def search():
    form = SearchForm(request.form)
    resLst = []
    if request.method == 'POST':
        conn = sqlite3.connect('hockey.db')
        c = conn.cursor()
        search_string = form.data['search']

        if len(search_string) < 3:
            return render_template('search.html', form=form, foundRes=True, resLst=[], tooShort=True)
        
        nameQuery = "SELECT name, playerId FROM skaters WHERE situation='all' AND name LIKE '%" + search_string + "%';"
        c.execute(nameQuery)
        resLst = c.fetchall()
        conn.commit()
        conn.close()

        if len(resLst) > 1:
            return render_template('search.html', form=form, foundRes=True, resLst=resLst, tooShort=False)
        
        elif len(resLst) == 1:
            url = '/player/' + str(resLst[0][1])
            return redirect(url)
        
        else:
            return render_template('search.html', form=form, foundRes=False, resLst=resLst, tooShort=False)

    return render_template('search.html', form=form, foundRes=True, resLst=resLst, tooShort=False)


query = '''
SELECT s1.name, s1.team, s1.season, s1.position, s1.Assists, 
(COUNT(CASE WHEN s2.Assists > s1.Assists THEN 1 END)+1) AS aRank,
    s1.goals, (COUNT(CASE WHEN s2.goals > s1.goals THEN 1 END)+1) AS gRank,
    s1.points, (COUNT(CASE WHEN s2.points > s1.points THEN 1 END)+1) AS pRank,
    s1.penalties, s1.penalityMinutes, s1.hits, s1.penaltiesDrawn, s1.shotsBlockedByPlayer, s1.PlusMinus 
FROM (SELECT name, season, team, position, (primaryAssists + secondaryAssists) AS Assists, goals, points, 
        penalties, penalityMinutes, hits, penaltiesDrawn, shotsBlockedByPlayer,
        (OnIce_F_goals - OnIce_A_goals) AS PlusMinus 
    FROM skaters WHERE situation="all" AND playerId=?) s1, 
(SELECT (primaryAssists + secondaryAssists) AS Assists, goals, points, 
    penalties, penalityMinutes, hits, penaltiesDrawn, shotsBlockedByPlayer, 
    (OnIce_F_goals - OnIce_A_goals) AS PlusMinus 
    FROM skaters WHERE situation="all") s2;
'''
@app.route('/player')
@app.route('/player/<int:id1>')
@app.route('/player/<int:id1>/<int:id2>')
def player(id1=None, id2=None):
    playerLst1 = []
    playerLst2 = []
    bestLine1 = []
    bestLine2 = []
    if (id1):
        conn = sqlite3.connect('hockey.db')
        c = conn.cursor()
        c.execute(query, (str(id1), ))
        playerLst1 = c.fetchall()
        fullName = playerLst1[0][0].split()
        nameQuery = "SELECT name, MAX(goalsFor) FROM lines WHERE name LIKE '%" + fullName[-1] + "%';"
        c.execute(nameQuery)
        bestLine1 = c.fetchall()
        conn.commit()
        conn.close()

    if (id2):
        conn = sqlite3.connect('hockey.db')
        c = conn.cursor()
        c.execute(query, (str(id2), ))
        playerLst2 = c.fetchall()
        fullName = playerLst2[0][0].split()
        nameQuery = "SELECT name, MAX(goalsFor) FROM lines WHERE name LIKE '%" + fullName[-1] + "%';"
        c.execute(nameQuery)
        bestLine2 = c.fetchall()
        conn.commit()
        conn.close()

    return make_response(render_template("player.html", id1=id1, playerLst1=playerLst1, id2=id2, playerLst2=playerLst2, bestLine1=bestLine1, bestLine2=bestLine2))


@app.route('/leaders')
@app.route('/leaders/<string:stat>')
def leaders(stat=None):
    if (not stat):
        stat = "goals"

    leaderQuery = '''
SELECT name, team, season, position, Assists, goals, points, 
    penalties, penalityMinutes, hits, penaltiesDrawn, shotsBlockedByPlayer, PlusMinus 
FROM (SELECT name, season, team, position, (primaryAssists + secondaryAssists) AS Assists, goals, points, 
        penalties, penalityMinutes, hits, penaltiesDrawn, shotsBlockedByPlayer,
        (OnIce_F_goals - OnIce_A_goals) AS PlusMinus 
    FROM skaters WHERE situation="all") s1 ORDER BY 
'''
    leaderQuery = leaderQuery + stat + " DESC LIMIT 10;"

    conn = sqlite3.connect('hockey.db')
    c = conn.cursor()
    c.execute(leaderQuery)
    leadersLst = c.fetchall()
    conn.commit()
    conn.close()

    return make_response(render_template("leaders.html", stat=stat, leadersLst=leadersLst))



@app.route('/addgame', methods=['GET', 'POST'])
def addgame():
    form = AddGameForm(request.form)
    resLst = []
    if request.method == 'POST':
        conn = sqlite3.connect('hockey.db')
        c = conn.cursor()
        homeTeamStr = form.data['homeTeam']
        awayTeamStr = form.data['awayTeam']
        dateStr = form.data['gameDate']
        homeScore = form.data['homeScore']
        awayScore = form.data['awayScore']
        first = form.data['firstStar']
        second = form.data['secondStar']
        third = form.data['thirdStar']
        comment = form.data['comments']
        addGameQuery = '''
            INSERT INTO userGames (homeTeam, awayTeam, date, homeScore, awayScore, firstStar, secondStar, thirdStar, comments)
            VALUES ('{}', '{}', '{}', {}, {}, '{}', '{}', '{}', '{}');
        '''.format(homeTeamStr, awayTeamStr, dateStr, homeScore, awayScore, first, second, third, comment)
        try:
            c.execute(addGameQuery)
            c.execute("SELECT userGameId FROM userGames ORDER BY userGameId DESC LIMIT 1;")
            ugID = c.fetchone()
            conn.commit()
            conn.close()
            url = '/usergames/' + str(ugID[0])
            return redirect(url)
        except:
            return make_response(render_template("addgame.html", form=form, tryAgain=True))
    
   
    return make_response(render_template("addgame.html", form=form, tryAgain=False))



@app.route('/usergames')
@app.route('/usergames/<string:gameid>')
def usergame(gameid=None):

    if gameid:
        conn = sqlite3.connect('hockey.db')
        c = conn.cursor()
        ugQuery = '''
            SELECT homeTeam, awayTeam, date, homeScore, awayScore, firstStar, secondStar, 
                thirdStar, comments, userGameId
            FROM userGames 
            WHERE userGameId={};
        '''.format(gameid)
        c.execute(ugQuery)
        ugLst = c.fetchone()

        playsQuery = '''
            SELECT playNum, playType, player, team, period, comment
            FROM userPlays WHERE userGameId={}
        '''.format(gameid)

        c.execute(playsQuery)
        playsLst = c.fetchall()
        return make_response(render_template("usergame.html", ugLst=ugLst, playsLst=playsLst))

    else:
        conn = sqlite3.connect('hockey.db')
        c = conn.cursor()
        c.execute("SELECT userGameId, homeTeam, awayTeam, date FROM userGames ORDER BY date;")
        ugIdList = c.fetchall()
        return make_response(render_template("usergames.html", ugIdList=ugIdList))



@app.route('/usergames/<string:gameid>/addplay', methods=['GET', 'POST'])
def addplay(gameid=None):
    form = AddPlayForm(request.form)

    if request.method == 'POST':
        conn = sqlite3.connect('hockey.db')
        c = conn.cursor()
        playType = form.data['playType']
        team = form.data['team']
        player = form.data['player']
        period = form.data['period']
        comment = form.data['comment']
        c.execute("SELECT COUNT(*) FROM userPlays WHERE userGameId=?", (gameid,))
        playNum = c.fetchone()
        addGameQuery = '''
            INSERT INTO userPlays (playNum, playType, player, team, period, comment, userGameId)
            VALUES ({}, '{}', '{}', '{}', '{}', '{}', {});
        '''.format((playNum[0]+1), playType, team, player, period, comment, gameid)
        try:
            c.execute(addGameQuery)
            conn.commit()
            conn.close()
            url = '/usergames/' + str(gameid)
            return redirect(url)
        except:
            return make_response(render_template("addplays.html", form=form, tryAgain=True))
        
   
    return make_response(render_template("addplays.html", form=form, tryAgain=False))



