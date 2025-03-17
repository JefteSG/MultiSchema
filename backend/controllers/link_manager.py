from flask import jsonify
from models.link import Link, LinkerTree, db  # Importa o modelo Link e a instância do SQLAlchemy


def get_all_links():
    links = Link.query.all()
    links_data = [link.to_dict() for link in links]

def get_link(link_id):
    link = Link.query.get(link_id)
    if not link:
        return jsonify({'error': 'Link not found'}), 404
    return jsonify(link.to_dict()), 200

def get_linktree(linkertree_id):
    linkertree = LinkerTree.query.get(linkertree_id)
    if not linkertree:
        return jsonify({'error': 'Linkertree not found'}), 404
    return jsonify(linkertree.to_dict()), 200

def create_linktree(data):
    new_linkertree = LinkerTree(
        route=data['route'],
        title=data['title'],
        logo=data['logo'],
        imagem=data['imagem']
    )

    db.session.add(new_linkertree)
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Error saving linkertree', 'details': str(e)}), 500

    return jsonify(new_linkertree.to_dict()), 201

def create_link(data):
    linkertree = LinkerTree.query.get(data['linkertree_id'])
    if not linkertree:
        return jsonify({'error': 'Linkertree not found'}), 404

    new_link = Link(
        url=data['url'],
        icon=data['icon'],
        title=data['title'],
        idx=data['idx'],
        linkertree_id=linkertree.id
    )

    db.session.add(new_link)
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Error saving link', 'details': str(e)}), 500

    return jsonify(new_link.to_dict()), 201