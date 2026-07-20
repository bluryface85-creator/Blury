from . import addpremium, rmpremium, ban, unban, stats, gkey, keylist, rkey, broadcast, adminmgmt, auth

def register(client):
    addpremium.register(client)
    rmpremium.register(client)
    ban.register(client)
    unban.register(client)
    stats.register(client)
    gkey.register(client)
    keylist.register(client)
    rkey.register(client)
    broadcast.register(client)
    adminmgmt.register(client)
    auth.register(client)
