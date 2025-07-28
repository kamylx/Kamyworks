# DEFINE ROTAS(URLs) DA APLICAÇÃO
from flask import render_template, url_for, flash, redirect, request, Blueprint
from app.models import Player, Match, User # Certifique-se que Match está importado
from app.forms import PlayerRegistrationForm, UserRegistrationForm, LoginForm, PlayerForm, MatchForm, VideoSubmissionForm # Certifique-se que MatchForm está importado
from app import db
import datetime as dt
from flask_login import login_required, current_user,logout_user, login_user

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
@main_bp.route('/home')
def home():
    #if current_user.is_authenticated:
    #return render_template('home_logged_in.html', title='Dashboard')
    return render_template('home.html', title='Início')


@main_bp.route('/about')
def about():
    return render_template('about.html', title='Sobre')

#--- ROTA REGISTRO DE JOGADOR
@main_bp.route('/register', methods=['GET', 'POST'])
@login_required
def register():
    form = PlayerRegistrationForm()
    if form.validate_on_submit():
        player = Player (
            name=form.name.data,
            position=form.position.data,
            number=form.number.data,
            birth_date=form.birth_date.data)
        try:
            db.session.add(player)
            db.session.commit()
            flash(f'Jogador {form.name.data} registrado com sucesso!', 'success')
            return redirect(url_for('main.home'))
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao registrar jogador: {e}', 'danger')
    return render_template('register.html', title='Registrar', form=form)

# --- ROTAS DE PARTIDAS (LISTAR, ADICIONAR, EDITAR, EXCLUIR) ---
#LISTAR
@main_bp.route('/matches')
@login_required
def matches():

    all_matches = Match.query.order_by(Match.date.desc()).all()
    for match in all_matches:
        if isinstance(match.date, str):
            try:
                date_obj_to_use = dt.datetime.strptime(match.date, "%Y-%m-%d")
            except ValueError:
                print(f'Erro no formato de data para a partida: {match.date}. Não foi possível converter para datetime')
                date_obj_to_use = None

        if isinstance(date_obj_to_use, (dt.date, dt.datetime)):
            match.formatted_Date = date_obj_to_use.strftime('%d/%m/%Y')
        else:
            match.formatted_date = str(match.date)
    return render_template('matches.html', title='Partidas', matches=all_matches)

# AUTENTICAÇÃO DE TREINADORES
@main_bp.route('/register_coach', methods=['GET', 'POST'])
def register_coach():
    form = UserRegistrationForm()
    if form.validate_on_submit():
        user = User(
            username = form.username.data,
            email = form.email.data
        )
        user.set_password(form.password.data)
        try:
            db.session.add(user)
            db.session.commit()
            flash('Treinador registrado com sucesso!', 'success')
            return redirect(url_for('main.login'))
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao registrar treinador: {e}', 'danger')
    return render_template('register_coach.html', title='Registrar Treinador', form=form)

    #if current_user.is_authenticated:
        #return redirect(url_for('main.home'))

    form = UserRegisterForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Sua conta foi criada com sucesso! Agora você pode fazer login.', 'sucess')
        return redirect(url_for('main.login'))
    return render_template('register_coach.html', title='Registrar treinador', form=form)

@main_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    #if current_user.is_authenticated:
        #user = User.query.filter_by(email=form.email.data).first()
        #return redirect(url_for('main.home'))

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data): #verifica a senha
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            flash('Login realizado com sucesso', 'sucess')
            return redirect (next_page) if next_page else redirect(url_for('main.home'))
        else:
            flash('Login sem sucesso. Por favor, verifique email e senha.', 'danger')
    return render_template('login.html', title='Login', form=form)
    
@main_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Você foi desconectado.', 'info')
    return redirect(url_for('main.home')) 

@main_bp.route('/submit_video', methods= ['GET', 'POST'])
@login_required
def submit_video():
    form = VideoSubmissionForm()
    if form.validate_on_submit():
        youtube_url = form.youtube_url.data
        try:
            yt = Youtube(youtube_url)
            stream = yt.streams.get_highest_resolution # Baixa maior resolução com aúdio

            if stream:
                download_dir = os.parth.join(os.getcwd(), 'downloads')
                os.makedirs(download_dir, filename)
                filename = f"{yt.video_id}.mp4"
                file_path = os.path.join(download_dir, filename)
                flash(f'Iniciando download de {yt.title}...', 'info')
                stream.download(output_path=download_dir, filename=yt.video_id)
                flash(f'Vídeo {yt.video_id} baixado com sucesso para:  {file_path}', 'sucess')
                flash('Análise de vídeo em desenvolvimento. O vídeo foi baixado.', 'warning')
            else:
                flash('Não foi possível encontrar uma steam de vídeo adequada para download.', 'danger')
        except Exception as e:
            flash(f'Ocorreu um erro ao baixar vídeo: {e}', 'danger')
            print(f'Erro ao baixar vídeo: {e}')
        
        return redirect(url_for('main.submit_video'))
    return render_template('submit_video.html', title= 'Análisar Video', form=form)

#ADICIONAR
@main_bp.route('/matches/add', methods=['GET', 'POST'])
def add_match():
    
    form = MatchForm()
    if form.validate_on_submit():
        date_string = form.date.data.strip()
        
        parsed_date = None
        try:
            parsed_date = dt.datetime.strptime(date_string, '%d/%m/%Y').date()   
        except ValueError as e:
            flash('Formato de data inválido. Por favor, use DD/MM/AAAA.', 'danger')
            return render_template('add_match.html', title='Adicionar Partida', form=form)

        new_match = Match(
            date=parsed_date,
            time=form.time.data,
            team_home_name=form.team_home_name.data,
            team_away_name=form.team_away_name.data,
            score_home=form.score_home.data,
            score_away=form.score_away.data,
            location=form.location.data,
            is_home_game=form.is_home_game.data,
            notes=form.notes.data,
            match_link = form.match_link.data if form.match_link.data else None,
            game_segments=form.game_segments.data if form.game_segments.data else None
        )
        try:
            db.session.add(new_match)
            db.session.commit()
            flash('Partida adicionada com sucesso!', 'success')
            return redirect(url_for('main.matches')) # Redireciona para a lista de partidas
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao adicionar partida: {e}', 'danger')
    
    # Para requisições GET, exibe o formulário vazio
    return render_template('add_match.html', title='Adicionar Partida', form=form)

#EDITAR
@main_bp.route('/matches/edit/<int:match_id>', methods=['GET', 'POST'])
def edit_match(match_id):
    """
    Rota para editar uma partida existente.
    """
    match = Match.query.get_or_404(match_id) # Busca a partida ou retorna 404
    form = MatchForm(obj=match)

    if form.validate_on_submit():
        # Processa os dados do formulário para atualização
        date_string = form.date.data.strip()
        try:
            match.date = dt.datetime.strptime(date_string, '%d/%m/%Y').date()
        except ValueError:
            flash('Formato de data inválido. Por favor, use DD/MM/AAAA.', 'danger')
            return render_template('edit_match.html', title='Editar Partida', form=form, match_id=match.id)
        
        match.time = form.time.data
        match.team_home_name = form.team_home_name.data
        match.team_away_name = form.team_away_name.data
        match.score_home = form.score_home.data
        match.score_away = form.score_away.data
        match.location = form.location.data
        match.is_home_game = form.is_home_game.data
        match.notes = form.notes.data
        match.match_link = form.match_link.data if form.match_link.data else None
        match.game_segments = form.game_segments.data if form.game_segments.data else None

        try:
            db.session.commit() # Salva as alterações no banco
            flash('Partida atualizada com sucesso!', 'success')
            return redirect(url_for('main.matches')) # Redireciona para a lista de partidas
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao atualizar partida: {e}', 'danger')
    
    elif request.method == 'GET':
        date_obj_for_form = match.date
        if isinstance(match.date, (dt.date, dt.datetime)):
            form.date.data = date_obj_for_form.strftime('%d/%m/%Y')
        else:
            form.date.data = match.date # Se não for um objeto datetime, passa a string original
            
        # Preenche o formulário com os dados atuais da partida para edição
        #form.date.data = match.date.strftime('%d/%m/%Y') # Formata para DD/MM/AAAA para o formulário
        form.time.data = match.time
        form.team_home_name.data = match.team_home_name
        form.team_away_name.data = match.team_away_name
        form.score_home.data = match.score_home
        form.score_away.data = match.score_away
        form.location.data = match.location
        form.is_home_game.data = match.is_home_game
        form.notes.data = match.notes
        form.match_link.data = match.match_link
        #form.game_segments = match.game_segments

    return render_template('edit_match.html', title='Editar Partida', form=form, match_id=match.id)

#DELETAR
@main_bp.route('/matches/delete/<int:match_id>', methods=['POST'])
def delete_match(match_id):
    """
    Rota para excluir uma partida.
    """
    match = Match.query.get_or_404(match_id)
     # Busca a partida ou retorna 404
    try:
        db.session.delete(match) # Marca a partida para exclusão
        db.session.commit()      # Confirma a exclusão no banco
        flash('Partida excluída com sucesso!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao excluir partida: {e}', 'danger')
    
    return redirect(url_for('main.matches')) # Redireciona para a lista de partidas

@main_bp.route('/matches/<int:match_id>/events')
def match_events(match_id):
    match = Match.query.get_or_404(match_id)
    events  = PlayerMatchEvent.query.filter_by(match_id=match.id).order_by(PlayerMatchEvent.timestamp_in_match).all()
    return render_template('match_events.html', title=f'Eventos da Partida {match.team_home_name} vs {match.team_away_name}', match=match, events=events)

@main_bp.route('/matches/<int:match_id>/add_events', methods=['GET', 'POST'])
def add_events(match_id):
    match = Match.query.get_or_404(match_id)
    form = PlayerMatchEventForm()

    players = Player.query.order_by(Player.name).all()
    form.player_id.choices = [(p.id, p.name) for p in players]
    form.player_id.choices.insert(0, (0,'Nenhum Jogador'))

    if form.validate_on_submit():
        player_id_val = form.player_id.data
        player_id_to_save = player_id_val if player_id_val != 0 else None

        new_event = PlayerMatchEvent(
            match_id = match_id,
            player_id = player_id_to_save,
            timestamp_in_match = form.timestamp_in_match.data, 
            event_type = form.event_type.data,
            description = form.description.data
        )
        try:
            db.session.add(new_event)
            db.session.commit()
            flash('Evento Registrado com sucess!', 'success')
            return redirect(url_for('main.match_events', match_id=match.id))
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao registrar evento: {e}', 'danger')
    return render_template('add_event.html', title=f'Adicionar à Partida {match.id}', form=form, match=match)

# --- FIM DAS ROTAS DE PARTIDAS ---


@main_bp.route('/players', methods=['GET', 'POST'])
def players():
    form = PlayerForm()
    if form.validate_on_submit():
        new_player = Player(
            name=form.name.data,
            position=form.position.data,
            number = form.number.data,
            birth_date=form.birth_date.data
        )
        try:
            db.session.add(new_player)
            db.session.commit()
            flash('Jogador adicionado com sucesso!', 'success')
            return redirect(url_for('main.players'))
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao adicionar jogador: {e}', 'danger')

    all_players = Player.query.order_by(Player.name).all()
    return render_template('players.html', title='Jogadores', form=form, players=all_players)

@main_bp.route('/player/edit/<int:player_id>', methods=['GET', 'POST'])
def edit_player(player_id):
    player = Player.query.get_or_404(player_id)
    form = PlayerForm()

    if form.validate_on_submit():
        player.name = form.name.data
        player.position = form.position.data
        player.number = form.number.data
        player.birth_date = form.birth_date.data
        try:
            db.session.commit()
            flash('Jogador atualizado com sucesso!', 'success')
            return redirect(url_for('main.players'))
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao atualizar jogador:  {e}', 'danger')
    elif request.method =='GET':
        form.name.data = player.name
        form.position.data = player.position
        form.number.data = player.number

        if isinstance(player.birth_date, (dt.date, dt.datetime)):
            form.birth_date.data = player.birth_date.strftime('%Y/%m/%d')
        else:
            form.birth_date.data = None
        
    return render_template('edit_player.html', title='Editar Jogador', form=form, player_id=player_id)

@main_bp.route('/player/delete/<int:player_id>', methods=['POST'])
def delete_player(player_id):
    player = Player.query.get_or_404(player_id)
    try:
        db.session.delete(player)
        db.session.commit()
        flash('Jogador excluído com sucesso!', 'success')
    except Exception as e:
        db.session.rolback()
        flash(f'Erro ao excluir jogador: {e}', 'danger')
    return redirect(url_for('main_players'))
