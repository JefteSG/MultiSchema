from werkzeug.security import generate_password_hash, check_password_hash


def hash_password(password):
    """
    Gera um hash seguro para a senha usando Werkzeug
    """
    return generate_password_hash(password)


def verify_password(password, hashed_password):
    """
    Verifica se a senha corresponde ao hash
    """
    return check_password_hash(hashed_password, password)


def validate_password_strength(password):
    """
    Valida a força da senha
    """
    errors = []
    
    if len(password) < 8:
        errors.append("A senha deve ter pelo menos 8 caracteres")
    
    if not any(c.islower() for c in password):
        errors.append("A senha deve conter pelo menos uma letra minúscula")
    
    if not any(c.isupper() for c in password):
        errors.append("A senha deve conter pelo menos uma letra maiúscula")
    
    if not any(c.isdigit() for c in password):
        errors.append("A senha deve conter pelo menos um número")
    
    return errors