# FORMULÁRIOS PARA CADASTRO E ATUALIZAÇÃO

from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    PasswordField,
    IntegerField,
    DateField,
    SelectField,
    TextAreaField,
    BooleanField,
    SubmitField,
)
from wtforms.validators import (
    DataRequired,
    Length,
    Email,
    EqualTo,
    ValidationError,
    NumberRange,
    Optional,
    URL,
)
from wtforms.widgets import DateInput
from app.models import User


# ---REGISTRO JOGADOR ---
class PlayerRegistrationForm(FlaskForm):
    name = StringField("Nome do Jogador", validators=[DataRequired(), Length(min=2, max=100)])
    position = SelectField("Posição",
        choices=[
            ("Goleiro", "Goleiro"),("Armador Central", "Armador Central"),("Armador Esquerdo", "Armador Esquerdo"),("Armador Direito", "Armador Direito"),
            ("Ponta Direita", "Ponta Direita"),("Ponta Esquerda", "Ponta Esquerda"),("Pivô", "Pivô"),
        ],validators=[DataRequired()],)
    number = IntegerField("Número da Camisa", validators=[DataRequired(), NumberRange(min=0, max=99)])
    birth_date = DateField("Data de Nascimento(AAAA-MM-DD)",
        format="%Y-%m-%d",widget=DateInput(),validators=[DataRequired()])
    submit = SubmitField("Registrar Jogador")

# --- FORMULÁRIO REGISTRO TREINADOR 
class UserRegistrationForm(FlaskForm):
    username = StringField("Nome de Usuário", validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Senha", validators=[DataRequired()])
    confirm_password = PasswordField("Confirmar Senha", validators=[DataRequired(), EqualTo("password")])
    submit = SubmitField("Registrar Treinador")

    # Validação para verificar se o nome de usuário já existe
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError("Esse nome de usuário já está em uso. Por favor, escolha outro.")

    # Validação para verificar se o email já existe
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError("Esse email já está registrado. Por favor, use outro ou faça login.")

# --- FORMULÁRIO LOGIN
class LoginForm(FlaskForm):
        email = StringField("Email", validators=[DataRequired(), Email()])
        password = PasswordField("Senha", validators=[DataRequired()])
        remember = BooleanField("lembrar-me") # Lembrar login 
        submit = SubmitField("Login")

# --- FORMULÁRIO VÍDEO
class VideoSubmissionForm(FlaskForm):
    youtube_url = StringField('URL do Vídeo', validators=[DataRequired(), URL()],
                            render_kw={'placeholder: Ex: https://www.youtube.com/watch?v...'}) # Linha 71 ou similar
    submit = SubmitField('Enviar Vídeo')
    

class PlayerForm(FlaskForm):
    name = StringField("Nome", validators=[DataRequired(), Length(max=100)])
    position = StringField("Posição", validators=[Length(max=50)])
    number = IntegerField("Número", validators=[DataRequired(), NumberRange(min=0)])
    birth_date = DateField(
        "Data de Nascimento(AAAA-MM-DD)", format="%Y-%m-%d", widget=DateInput(), validators=[DataRequired()])
    submit = SubmitField("Salvar Jogador")


# --- REGISTRO PARTIDA ---
class MatchForm(FlaskForm):
    date = StringField("Data da Partida (DD/MM/AAAA)", validators=[DataRequired(), Length(min=10, max=10)],)
    time = StringField("Hora da Partida (HH:MM)", validators=[DataRequired(), Length(min=5, max=5)])
    team_home_name = StringField("Time da Casa", validators=[DataRequired(), Length(min=2, max=100)])
    team_away_name = StringField("Time Adversário", validators=[DataRequired(), Length(min=2, max=100)])
    score_home = IntegerField("Nosso Placar", validators=[DataRequired(), NumberRange(min=0)])
    score_away = IntegerField("Placar Adversário", validators=[DataRequired(), NumberRange(min=0)])
    location = StringField("Local da Partida", validators=[Length(max=100)])
    is_home_game = BooleanField("Jogo em Casa?")
    notes = TextAreaField("Observações da Partida")
    match_link = StringField("Link do Jogo", validators=[Optional(), URL()])
    game_segments = TextAreaField("Segmentos do Jogo no vídeo (EX: Jogo 1: 00:00, Jogo 2: 15:30)", validators=[Optional()])
    submit = SubmitField("Adicionar Partida")

class PlayerMatchEventForm(FlaskForm):
    timestamp_in_match = StringField("Tempo no jogo (HH:MM:SS ou MM:SS)", validators=[DataRequired(), Length(max=10)])
    event_type = SelectField("Tipo de Evento",choices=[
            ("Gol", "Gol"),
            ("Erro de Passe", "Erro de Passe"),
            ("Roubada de Bola", "Roubada de Bola"),
            ("Defesa Goleiro", "Defesa Goleiro"),
            ("Falta", "Falta"),
            ("Assistência", "Assistência"),
            ("Perda de Posse", "Perda de Posse"),
            ("Bloqueio", "Bloqueio"),
            ("Outro", "Outro"),
        ],
        validators=[DataRequired()],
    )
    notes = TextAreaField("Notas do Evento", validators=[Optional(), Length(max=200)])

    # Este SelectField será populado dinamicamente na rota
    player_id = SelectField("Jogador Envolvido", coerce=int, validators=[Optional()])  # Optional para permitir eventos sem jogador específico
    description = TextAreaField("Descrição Detalhada", validators=[Optional()])
    submit = SubmitField("Registrar Evento")

    
