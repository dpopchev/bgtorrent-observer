# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.16.4
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# %%
from bgtorrent_observer.sample import sample

# %%
sample()

# %%
a = '''
[p2pbg.credentials]
user = "p2pbguser"
password = "p2pbgpassword"

[p2pbg.series_key1]
name = "search string"
season = 1

[p2pbg.series_key2]
name = "query string"
season = 1

[arenabg.credentials]
user = "arenabguser"
password = "arenabgpassword"

[arenabg.show_key1]
name = "search string"
season = 2

[arenabg.show_key2]
name = "query string"
season = 2

[arenabg.show_key3]
name = "name of show"
season = 3
'''

# %%
import tomllib
config = tomllib.loads(a)

# %%
config['p2pbg']

# %%
