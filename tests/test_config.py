import tempfile
from app.utils.config import load_channels

def test_load_channels_valid(tmp_path):
    file = tmp_path / "test.csv"

    file.write_text("""channel_id,channel_name,category
UC11111111111111111111,Graham Stephan,finance
UC22222222222222222222,Jeff Nippard,fitness
""")

    channels = load_channels(str(file))

    assert len(channels) == 2
