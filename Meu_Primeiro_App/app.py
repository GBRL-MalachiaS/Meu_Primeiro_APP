from flask import Flask, render_template, request, flash, redirect, url_for
from flask_wtf import FlaskForm
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_fresh, current_user, login_user, logout_user, login_required
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, Length, ValidationError, EqualTo

# Inicializa a aplicação Flask, chamando a classe Flask
app = Flask(__name__)


# Aqui definimos nossa configuração !
app.config['SECRET_KEY'] = 'uma-chave-secreta-muito-dificil-de-adivinhar'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'

# Aqui definimos nossos formularios

# Formulario de login


class FormLogin(FlaskForm):
    email = StringField('E-mail', validators=[
        DataRequired(message='Este campo é obrigatório!'),
        Email(message='Por favor, ensira uma E-MAIL valido')
    ])
    senha = PasswordField('Senha', validators=[
        DataRequired(message='Este campo é obrigatóro!')])
    enviar = SubmitField('Fazer Login')

    def validate_email(self, email):
        usuario = Usuario.query.filter_by(email=email.data).first()
        if not usuario:
            raise ValidationError(
                'Este e-mail não possui cadastro')

# Formulario de Registro


class FormRegistro(FlaskForm):
    email = StringField('E-mail', validators=[
        DataRequired(message="Este Campo é Obrigatório"),
        Email(message='Por favor, ensira um E-MAIL valido!')
    ])
    senha = PasswordField('Senha', validators=[
        DataRequired()
    ])
    confirmar_senha = PasswordField("Confirmar Senha", validators=[
        DataRequired(), EqualTo('senha', message='As senhas devem ser iguais')
    ])

    enviar = SubmitField('Enviar')

    def validate_email(self, email):
        usuario = Usuario.query.filter_by(email=email.data).first()
        if usuario:
            raise ValidationError(
                'Este e-mail já está em uso. Por favor, escolha outro')


db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

# Aqui criamos nosso models(modelo de banco de dados)


class Usuario(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    senha = db.Column(db.String(60), nullable=False)

    def __repr__(self):
        return f'Usuario({self.email})'


login_manager = LoginManager(app)
# Informa ao Flask-Login qual é a rota de login
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'  # Categoria da mensagem de flash


@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))


@app.route('/')
def index():
    titulo_da_pagina = "Bem-vindo ao meu site Dinâmico!"
    mensagem_de_boas_vindas = "Aqui usamos Flask e Jinja2 para criar está página"

    minhas_habilidades = ["Python", "Flask", "HTML", "Jinja2", "batata"]

    exibir_habilidades = True

    return render_template(
        'index.html',
        titulo=titulo_da_pagina,
        saudacao=mensagem_de_boas_vindas,
        habilidades=minhas_habilidades,
        mostrar_lista=exibir_habilidades)


@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    form = FormRegistro()

    if form.validate_on_submit():
        senha_criptografada = bcrypt.generate_password_hash(
            form.senha.data).decode('utf-8')

        usuario = Usuario(email=form.email.data, senha=senha_criptografada)
        db.session.add(usuario)
        db.session.commit()
        flash('sua conta foi criada com sucesso! Você já pode fazer login!')
        return redirect(url_for('index'))

    return render_template('cadastro.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = FormLogin()

    if form.validate_on_submit():
        # O uso do form.email.data serve para buscar o retorno do formulario na pagina web
        usuario = Usuario.query.filter_by(email=form.email.data).first()

        if usuario and bcrypt.check_password_hash(usuario.senha, form.senha.data):
            login_user(usuario, remember=True)
            flash('Login Efetuado', 'success')
            proxima_pagina = request.args.get('/conta')
            return redirect(proxima_pagina) if proxima_pagina else redirect(url_for('index'))
        else:
            flash('Falha no login. Por favor, verifique o e-mail e senha!', 'danger')
    return render_template('login.html', form=form)


@app.route('/conta')
@login_required
def conta():
    return render_template('conta.html')

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
