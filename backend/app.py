import os
import json
import secrets
import click
from flask import Flask, g
from flask.cli import with_appcontext
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine, text

from .routes import user_bp
from .routes.redirect_site import before_request, disconnect_db
from .utils.site import get_base_path, get_config_db_root, get_list_sites
from jinja2 import Environment, FileSystemLoader

TEMPLATE_FILE = "nginx-template.conf.j2"
TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), "templates")
env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))

OUTPUT_FILE = "nginx.conf"

# Instância global do SQLAlchemy
db = SQLAlchemy()

def create_app():
    app = Flask(__name__)

    # Configurações do banco de dados e SQLAlchemy
    app.instance_path = "/tmp/flask_instance"
    os.makedirs(app.instance_path, exist_ok=True)
    try:
        app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///" + os.path.join(app.instance_path, "database.db") # FIXME: reafatorar para pegar do arquivo de configuração
    except Exception as e:
        raise Exception("Erro ao buscar configuração do banco de dados, voce deve configurar o banco com o comando \"flask init\"")
    app.config['SQLALCHEMY_ECHO'] = True
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        "pool_pre_ping": True,
        "pool_recycle": 300,
    }

    # Inicializa o SQLAlchemy
    db.init_app(app)

    # Middleware para gerenciar sessões
    app.before_request(before_request)
    

    app.teardown_appcontext(disconnect_db)
    
    # Registra os blueprints
    app.register_blueprint(user_bp)
    
    return app

app = create_app()
migrate = Migrate(app, db)

@app.route("/create-site/<site_name>", methods=["POST"])
def create_site(site_name):
    """
    Cria um novo site com um banco de dados exclusivo.
    Solicita as credenciais do DB master e o usuário para o novo banco.
    """
    # master_user = click.prompt("DB user [root]:", type=str, default="root")
    # master_password = click.prompt("DB password:", hide_input=True)
    master_db_url = f"sqlite:///{os.path.join(get_base_path(), 'sites', 'master.db')}"

    new_db_password = secrets.token_hex(8)
    random_suffix = secrets.token_hex(4)
    new_db_username = click.prompt("New DB user [user_<random_suffix>]:", type=str, default=f"user_{random_suffix}")
    new_db_name = f"db_{random_suffix}"
    new_db_url = f"mysql+pymysql://{new_db_username}:{new_db_password}@localhost/{new_db_name}"

    try:
        engine_master = create_engine(master_db_url)
        with engine_master.connect() as conn:
            conn.execute(text(f"CREATE DATABASE IF NOT EXISTS {new_db_name}"))
            conn.execute(text(f"CREATE USER IF NOT EXISTS '{new_db_username}'@'localhost' IDENTIFIED BY '{new_db_password}'"))
            conn.execute(text(f"GRANT ALL PRIVILEGES ON {new_db_name}.* TO '{new_db_username}'@'localhost'"))
            conn.commit()
    except Exception as e:
        # click.echo(f"Erro ao criar o banco ou o usuário: {e}")
        return

    try:
        engine_new = create_engine(new_db_url)
        with engine_new.connect() as conn:
            db.metadata.create_all(engine_new)
    except Exception as e:
        # click.echo(f"Erro ao criar as tabelas: {e}")
        return

    site_config = {
        "site_name": site_name,
        "db_name": new_db_name,
        "db_username": new_db_username,
        "db_password": new_db_password,
        "db_url": new_db_url,
    }

    site_folder = os.path.join("sites", site_name)
    try:
        os.makedirs(site_folder, exist_ok=True)
        config_path = os.path.join(site_folder, "site_config.json")
        with open(config_path, "w") as config_file:
            json.dump(site_config, config_file, indent=4)
    except Exception as e:
        # click.echo(f"Erro ao salvar a configuração do site: {e}")
        return

    # click.echo(f"Site '{site_name}' criado com sucesso!")
    
@app.cli.command("init")
@with_appcontext
def init_instancia():
    master_user = click.prompt("DB user [root]:", type=str, default="root")
    master_password = click.prompt("DB password:", hide_input=True)
    master_db_url = f"mysql+pymysql://{master_user}:{master_password}@localhost"

    # coloca as configs na pasta sites/config.json chave dv_url
    # não precisa criar o banco, ele vai ser criado na primeira requisição
    config_path = os.path.join('.',"sites", "config.json")
    config = {
        "db_url": master_db_url
    }
    with open(config_path, "w") as config_file:
        json.dump(config, config_file, indent=4)@app.cli.command('setup-nginx')
    click.echo("Configuração inicializada com sucesso!")



@app.cli.command('setup-nginx')
@with_appcontext
def generate_nginx_config():
    """Gera um arquivo de configuração Nginx com base nas pastas de sites."""
    env = Environment(loader=FileSystemLoader("."))
    # print(TEMPLATE_DIR)
    # print(env.list_templates())
    template = env.get_template("templates/nginx")
    sites = []
    for site in get_list_sites():
        site_path = os.path.join(get_base_path(), 'sites', site)
        if os.path.isdir(site_path):
            sites.append({
                "server_name": site,
                "port": 80,
                "root_dir": site_path,
                "static_dir": os.path.join(site_path, "static"),
                "enable_php": False,  # Modifique se necessário
                "enable_ssl": False,  # Modifique se necessário
                "ssl_cert": "/etc/ssl/certs/example.crt",
                "ssl_key": "/etc/ssl/private/example.key",
                "php_fpm_socket": "unix:/run/php/php-fpm.sock"
            })
    
    config_content = template.render(sites=sites)

    with open(OUTPUT_FILE, "w") as f:
        f.write(config_content)
    
    click.echo(f"Configuração gerada: {sites}")

@app.cli.command("add-host")
@click.argument("domain")
@click.argument("ip", default="127.0.0.1")
def add_host(domain, ip):
    """
    Adiciona um domínio ao /etc/hosts para redirecionar para o IP especificado (padrão: 127.0.0.1).
    
    Exemplo:
        sudo env "PATH=$PATH" flask add-host batatinha.com
        sudo env "PATH=$PATH" flask add-host mydomain.com 192.168.1.100
    """
    hosts_file = "/etc/hosts"
    entry = f"{ip} {domain}\n"

    # Verifica se já existe uma entrada para o domínio
    with open(hosts_file, "r") as f:
        if any(domain in line for line in f.readlines()):
            click.echo(f"⚠️ O domínio {domain} já está no /etc/hosts.")
            return

    # Adiciona o domínio ao /etc/hosts
    try:
        with open(hosts_file, "a") as f:
            f.write(entry)
        click.echo(f"✅ Adicionado: {entry.strip()}")
    except PermissionError:
        click.echo("❌ Permissão negada! Tente rodar com sudo:\n    sudo flask add-host {domain} {ip}")

if __name__ == "__main__":
    # generate_nginx_config()
    app.run(debug=True)

