import os
import json
import secrets
import click
from flask import Flask, g
from flask.cli import with_appcontext
from flask_migrate import Migrate
from flask_cors import CORS
from sqlalchemy import create_engine, text, MetaData

from .database import db
from .config_manager import get_config
from .routes import user_bp
from .routes.sites_routes import sites_bp
from .routes.redirect_site import before_request, disconnect_db
from .utils.site import get_base_path, get_config_db_root, get_list_sites
from jinja2 import Environment, FileSystemLoader

TEMPLATE_FILE = "nginx-template.conf.j2"
TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), "templates")
env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
BASE_DIR = "/tmp/sites" 

OUTPUT_FILE = "nginx.conf"

def create_app(config_name=None):
    app = Flask(__name__)
    
    # Carrega configuração
    config = get_config(config_name)
    app.config.from_object(config)
    
    # Configurações do banco de dados
    app.config['SQLALCHEMY_DATABASE_URI'] = config.get_database_url()
    
    # Configurar CORS
    CORS(app, resources={
        r"/api/*": {
            "origins": ["http://localhost:3000", "http://localhost:8080"],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })
    
    # Inicializa extensões
    db.init_app(app)
    
    # Inicializa Flask-Migrate
    migrate = Migrate(app, db)
    
    # Importa modelos para que o Flask-Migrate os encontre
    from .models.user import User, Role
    
    # Middleware para gerenciar sessões
    app.before_request(before_request)
    app.teardown_appcontext(disconnect_db)
    
    # Registra os blueprints
    app.register_blueprint(user_bp)
    app.register_blueprint(sites_bp)
    
    return app

app = create_app()
migrate = Migrate(app, db)

@app.route("/create-site/<site_name>", methods=["POST"])
def create_site(site_name):
    """
    Cria um novo site com um banco de dados exclusivo usando SQLite.
    """
    site_folder = os.path.join(BASE_DIR, "sites", site_name)
    os.makedirs(site_folder, exist_ok=True)  # Cria a pasta do site, se não existir

    # Definição do caminho do banco SQLite
    new_db_path = os.path.join(site_folder, "database.db")
    new_db_url = f"sqlite:///{new_db_path}"

    try:
        # Criando o banco de dados SQLite
        engine_new = create_engine(new_db_url)
        metadata = MetaData()
        metadata.create_all(engine_new)  # Garante que as tabelas sejam criadas
    except Exception as e:
        return {"error": f"Erro ao criar as tabelas: {str(e)}"}

    # Configuração do site
    site_config = {
        "site_name": site_name,
        "db_path": new_db_path,
        "db_url": new_db_url,
    }

    try:
        # Salvando as configurações em um arquivo JSON
        config_path = os.path.join(site_folder, "site_config.json")
        with open(config_path, "w") as config_file:
            json.dump(site_config, config_file, indent=4)
    except Exception as e:
        return {"error": f"Erro ao salvar a configuração do site: {str(e)}"}

    return site_config

    # click.echo(f"Site '{site_name}' criado com sucesso!")
    
@app.cli.command("init")
@with_appcontext
def init_instancia():
    """Inicializa a configuração do banco de dados"""
    from .config_manager import Config
    
    master_user = click.prompt("DB user [root]:", type=str, default="root")
    master_password = click.prompt("DB password:", hide_input=True)
    master_db_url = f"mysql+pymysql://{master_user}:{master_password}@localhost"

    # Salva as configurações
    Config.save_database_config(master_db_url)
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

