from app import db
#from sqlalchemy import Date, Text, Boolean, ForeignKey, DateTime, Integer, String # Importar Integer e String para tipos de coluna
from sqlalchemy.orm import relationship 
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

#--- CLASSE USER (PARA TREINADOR)
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id) 

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash (self.password_hash, password)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"
    
class PlayerMatchStat(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    
    match_id = db.Column(db.Integer, db.ForeignKey('match.id'), nullable=False)
    player_id = db.Column(db.Integer, db.ForeignKey('player.id'), nullable=False)
    
    goals = db.Column(db.Integer, default=0)
    errors = db.Column(db.Integer, default=0)
    assists = db.Column(db.Integer, default=0)

    match_ref = relationship('Match', back_populates='stats_entries')
    player_ref = relationship('Player', back_populates='stats_entries')

    def __repr__(self):
        return f"<PlayerMatchStat MatchID: {self.match_id}, PlayerID: {self.player_id}>"
    
class Match(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(10), nullable=False) # data
    time = db.Column(db.String(5), nullable=False) # hora
    team_home_name = db.Column(db.String(100), nullable=False) # time da casa
    team_away_name = db.Column(db.String(100), nullable=False) # time visitante
    score_home = db.Column(db.Integer, default=0) # placar casa 
    score_away = db.Column(db.Integer, default=0) # placar visitante
    location = db.Column(db.String(100)) # local da partida
    is_home_game = db.Column(db.Boolean, default=False) # foi em casa?
    notes = db.Column(db.Text) # notas
    match_link = db.Column(db.String ( 500), nullable=True)
    game_segments = db.Column(db.Text, nullable=True)

    # Relacionamento para os eventos desta partida
    stats_entries = relationship('PlayerMatchStat', back_populates= 'match_ref', lazy=True)
    events = relationship('PlayerMatchEvent', back_populates='match_ref', lazy=True) # <-- NOVO RELACIONAMENTO

    def __repr__(self):
        # return f"<Match {self.id}: {self.team_home_name} vs {self.team_away_name} em ({self.date})>"
        return f"Partida({self.team_home_name} vs {self.team_away_name} em {self.date.strftime('%d-%m-%Y')} {self.time})"

class PlayerMatchEvent(db.Model):
    
    #Modelo para armazenar eventos/movimentações de um jogador em uma partida específica.
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Chave estrangeira para a partida
    match_id = db.Column(db.Integer, db.ForeignKey('match.id'), nullable=False)
    # Chave estrangeira para o jogador envolvido no evento (pode ser nullable se o evento não envolver um jogador específico)
    player_id = db.Column(db.Integer, db.ForeignKey('player.id'), nullable=True) # <-- nullable=True se o evento não sempre tiver um jogador

    # Tempo no jogo (ex: "10:35" ou segundos desde o início)
    timestamp_in_match = db.Column(db.String(10), nullable=False) 
    
    # Tipo do evento (ex: Gol, Erro de Passe, Roubada de Bola, Defesa, Falta, etc.)
    event_type = db.Column(db.String(50), nullable=False) 
    
    # Descrição detalhada do evento
    description = db.Column(db.Text, nullable=True) 

    # Relacionamentos bidirecionais
    match_ref = relationship('Match', back_populates='events') # <-- back_populates para Match.events
    player_ref = relationship('Player', back_populates='events') # <-- back_populates para Player.events

    def __repr__(self):
        player_name = self.player_ref.name if self.player_ref else "N/A"
        return f"<Event {self.id}: {self.event_type} - {player_name} @ {self.timestamp_in_match} (Match {self.match_id})>"

class Player(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    position = db.Column(db.String(50))
    number = db.Column(db.Integer)
    birth_date = db.Column(db.Date)
    # pode ter outras característcas como altura, peso e histórico

    # Relacionamento para os eventos deste jogador
    stats_entries = relationship('PlayerMatchStat', back_populates= 'player_ref', lazy=True)
    events = relationship('PlayerMatchEvent', back_populates='player_ref', lazy=True) # <-- NOVO RELACIONAMENTO

    def __repr__(self):
        #return f"<Player {self.id}: {self.name}>"
        return f"Jogador('{self.name}', '{self.position}', '{self.number or 'N/A'}')"