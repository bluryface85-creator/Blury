from . import bin, gen, fake, leaderboard

def register(client):
    bin.register(client)
    gen.register(client)
    fake.register(client)
    leaderboard.register(client)
