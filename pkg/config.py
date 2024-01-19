class Config:
    APP_NAME = "New Years App"

class LiveConfig(Config):
    DBNAME = "Live"
    DBPWD = "Live1234"


class TestConfig(Config):
    DBNAME = "Test"
    DBPWD = "Test1234"