Fediscrape
==========

What is Fediscrape?
-------------------

A small script that scrapes a Fediverse user's profile and prints all their posts/replies on the terminal.

### Motivation

A lot of instances block searches. You would normally have to click "Show more" until you find what you're looking for (which is exactly what Fediscrape does). I put a delay between each "click" to avoid spamming servers. I'm sure there's a better way to do it but it's better than nothing.

Dependencies
------------

The `bs4` and `requests` python modules are required dependencies. They can be installed for your user using `pip3 install --user bs4 requests`, or globally using your distribution's package manager e.g. `apt-get install python3-requests python3-bs4`.

Usage
-----

Print all posts/replies:
```bash
./fediscrape.py username@example.com
```

Search for specific string:
```bash
./fediscrape.py username@example.com | grep "search string"
```

Write all posts/replies to a file:
```bash
./fediscrape.py username@example.com > filename
```

Contributing
------------

Please, avoid object-oriented programming.

“*Sometimes, the elegant implementation is just a function. Not a method. Not a class. Not a framework. Just a function.*”  
— John Carmack

More on this: http://harmful.cat-v.org/software/OO_programming/

License
-------

Fediscrape is released under the terms of the MIT license. See [LICENSE](LICENSE) for more
information or see https://opensource.org/licenses/MIT.

**Note:** Fediscrape currently only supports Mastodon and Pleroma.
