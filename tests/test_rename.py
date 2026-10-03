from legends_dataforseo import client, documentation

def test_rename_preserves_existing_cache_and_ledger(tmp_path, monkeypatch):
    monkeypatch.setenv('LOCALAPPDATA', str(tmp_path))
    monkeypatch.setenv('XDG_CACHE_HOME', str(tmp_path))
    monkeypatch.setenv('XDG_STATE_HOME', str(tmp_path))
    monkeypatch.delenv('LEGENDS_DATAFORSEO_LEDGER', raising=False)
    assert 'legends-dataforseo-kit' not in str(documentation._default_cache())
    assert 'legends-dataforseo-kit' not in str(client.ledger_path())
    old = tmp_path / 'legends-dataforseo-kit'
    (old / 'docs').mkdir(parents=True)
    ledger = old / 'cost-ledger.jsonl'
    ledger.write_text('existing private ledger')
    assert documentation._default_cache() == old / 'docs'
    assert client.ledger_path() == ledger
    assert ledger.read_text() == 'existing private ledger'
