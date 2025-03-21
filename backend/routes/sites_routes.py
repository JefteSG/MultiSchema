from flask import Blueprint, request, jsonify, g
from sqlalchemy.orm import joinedload

sites_bp = Blueprint("Sites", __name__, url_prefix='/api/v1/site')



def create_site(site_name):
    """
    Cria um novo site com um banco de dados exclusivo.
    Solicita as credenciais do DB master e o usuário para o novo banco.
    """
    master_db_url = f'sqlite:///{g.db_path}'

    new_db_password = secrets.token_hex(8)
    random_suffix = secrets.token_hex(4)
    new_db_username = click.prompt("New DB user [user_<random_suffix>]:", type=str, default=f"user_{random_suffix}")
    new_db_name = f"db_{random_suffix}"
    new_db_url = f"sqlite:///{new_db_name}.db"

    try:
        engine_master = create_engine(master_db_url)
        with engine_master.connect() as conn:
            conn.execute(text(f"CREATE DATABASE IF NOT EXISTS {new_db_name}"))
            conn.execute(text(f"CREATE USER IF NOT EXISTS '{new_db_username}'@'localhost' IDENTIFIED BY '{new_db_password}'"))
            conn.execute(text(f"GRANT ALL PRIVILEGES ON {new_db_name}.* TO '{new_db_username}'@'localhost'"))
            conn.commit()
    except Exception as e:
        click.echo(f"Erro ao criar o banco ou o usuário: {e}")
        return

    try:
        engine_new = create_engine(new_db_url)
        with engine_new.connect() as conn:
            db.metadata.create_all(engine_new)
    except Exception as e:
        click.echo(f"Erro ao criar as tabelas: {e}")
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
        click.echo(f"Erro ao salvar a configuração do site: {e}")
        return

    return site_config