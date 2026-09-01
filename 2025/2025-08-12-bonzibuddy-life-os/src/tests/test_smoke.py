def test_home(client):
    r = client.get('/')
    assert r.status_code == 200
    assert b'BonziBuddy v2' in r.data
