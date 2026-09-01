import pytest
from app.factory import create_app

@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_index_page(client):
    """Test that the index page loads correctly."""
    response = client.get('/')
    assert response.status_code == 200
    assert b'Welcome' in response.data or b'index' in response.data

def test_explore_page(client):
    """Test that the explore page loads correctly."""
    response = client.get('/explore')
    assert response.status_code == 200
    assert b'Interactive Learning Labs' in response.data

def test_lab_basics_page(client):
    """Test that the supply & demand basics lab page loads correctly."""
    response = client.get('/lab/basics')
    assert response.status_code == 200
    assert b'The Market Story' in response.data

def test_lab_supply_demand_page(client):
    """Test that the supply & demand lab page loads correctly."""
    response = client.get('/lab/supply-demand')
    assert response.status_code == 200
    assert b'Supply' in response.data and b'Demand' in response.data

def test_lab_consumer_theory_page(client):
    """Test that the consumer theory lab page loads correctly."""
    response = client.get('/lab/consumer-theory')
    assert response.status_code == 200
    assert b'The Consumer\'s Journey' in response.data

def test_lab_producer_theory_page(client):
    """Test that the producer theory lab page loads correctly."""
    response = client.get('/lab/producer-theory')
    assert response.status_code == 200
    assert b'The Producer\'s Challenge' in response.data

def test_lab_market_equilibrium_page(client):
    """Test that the market equilibrium lab page loads correctly."""
    response = client.get('/lab/market-equilibrium')
    assert response.status_code == 200
    assert b'The Market Awakens' in response.data

def test_lab_game_theory_page(client):
    """Test that the game theory lab page loads correctly."""
    response = client.get('/lab/game-theory')
    assert response.status_code == 200
    assert b'The Strategic Challenge' in response.data

def test_lab_auctions_page(client):
    """Test that the auctions lab page loads correctly."""
    response = client.get('/lab/auctions')
    assert response.status_code == 200
    assert b'The Auction House' in response.data


def test_lab_growth_models_page(client):
    """Test that the growth models lab page loads correctly."""
    response = client.get('/lab/growth-models')
    assert response.status_code == 200
    assert b'The Development Journey' in response.data
