from flask import Blueprint, render_template, request, redirect, url_for, session, flash

voo_bp = Blueprint('voos', __name__, url_prefix='/voos')

# Dicionário de voos
voos = {
    "ED101": {
        "origem": "São Paulo",
        "destino": "Rio de Janeiro",
        "milhas": 220,
        "preco": 350.00,
        "aeronave": "Airbus A320",
        "assentos": 180
    }
}