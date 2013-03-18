Python Little Unix Server Toolkit
===========

This project implements the basics of creating a proper modern daemon on a Unix
system in Python.  It has the following features:

1. A simpler logging system than the default python logging meant for small servers.
2. Functions to do the usual chroot, drop privileges, daemonize dance.
3. Functions to manage pid files and check if a server is running or not.
4. A small simple framework for creating servers that does most of the dance for you if you don't mind how it is done.
5. A simplification of the Python .ini file format for managing config files.

The library tries to keep things in the correct places for most platforms and
follow the usual conventions.  These are:

1. /var/run/ for pid files.
2. /etc/ for config files.
3. pid files and config files named after the program.
4. /var/run/NAME for the chroot directory.

You can change all of these easily, they are just defaults that are common on
most unix systems.


How Daemonize/Chroot/Drop Priv Works
====

Many people don't realize it, but there's sort of a defacto loose standard for
making a secure server (well, better secured):

1. Start the process as root.
2. Daemonize to become a forked server.
3. Chroot to a safe directory where the process lives.
4. Change directory to "/" to ensure it's really in the right place.
5. Drop privileges immediately to a safe user so that you are not root anymore.

The purpose of this dance is to make it so that the server, should it get
attacked and give up a remote shell or access, is jailed off into a useless
directory that restricts the attacker's access.  This isn't foolproof, but is
handy.

A secondary purpose is that using a chroot eliminates all path traversal bugs.
These are the bugs where you hit a webserver asking for /../../../../etc/passwd
and you get the server's password list.  By doing a chroot that path will stay
within the server's jail area and won't go anywhere.

So what do each of these things do?  Here's a quick informal explanation of
each:

* __daemonize__ -- C has a function for this, but in Python you effectively do a
    double _os.fork_ call.
* __chroot__ -- This is a function call for the OS that forces the process to
    only have a target directory as its root.  If you chroot to /var/run/stuff/
    then in that process any path starting with "/" is actually forced to
    here.  It effectively tricks the process into thinking this directory contains
    all the files it will ever see.
* __chdir("/")__ -- For some idiotic reason this isn't done for you, even though 
    that's the whole point of chroot. Don't ask me why, just do this right after
    _chroot_.
* __drop_privileges__ -- This needs to be done *right* after chroot, and what it
    does is change the process from being owned by _root_ to being owned by
    someone else, say nobody:nogroup.  This gets rid of one more security concern
    that, should someone get your server to run arbitrary code, then it
    just runs as this safer user in the chroot jail.  If you run as root then
    the chroot is fairly pointless.

How Python-LUST Does It
====

To see how all of this is implemented in Python (or as good as I could figure
out in Python), see the lust/unix.py file.  The code is small and easy
to read.


Security Concerns
===

To make the chroot work though you need to satisfy these requirements:

* No root user defined within the chroot environment.
* No SUID binaries accessible.
* No device files.

A way to look at this is if you put anything from /etc, /dev, or a binary file,
in the chroot target directory, then an attacker can use those to bust out of
the chroot jail.  It gets more complicated than that, but to be safe, just
don't put them there.

There's also the problem that it's not clear what Python's race conditions are
with these system calls.  It's possible that an attacker could hit the process
just before the drop privileges but after the chroot, but not sure.

And as usual, there's a chance I totally did this wrong. It seems right to me
but if you notice that I'm doing things out of order then send me a link to the
information I need to evaluate how to do it right.


Configuration Files
====

The module lust.config (in log/config.py) has a very dead simple logging
system.  It's one function that loads a standard Python .ini file using the
SafeConfigParser and then turns it into a sane dict for you to use.

You don't have to use this, it's just a reasonable default and works for 90% of
the kinds of servers you might implement.  It's the default in the
lust.server.Simple framework but not required.

Logs
====

Every logging API blows. Seriously, screw all overly complicated stupid APIs
out there.  If you need whatever insanity they give you then fine, use theirs.
I wrote a dead simple one that's good enough, and I'm using it.  It's main
feature is that you can understand the damn thing, followed by it just reroutes
stderr/stdout to a file closing off everything else.

For 90% of your logging needs *in a daemon* this will work and also captures
all sys.stderr and sys.stdout output and spews it into the logs.  This is handy
since it can catch a lot of things that you might miss after daemonizing.

If you are not writing a daemon don't use this library.  You can use it, but
don't call lust.log.setup because it'll close all the currently open files and
reroute stderr/stdout.  It's meant for daemons.


Simple Server Framework
====

Python lust comes with another module named lust.server (in lust/server.py)
that implements a very simple "framework" for making daemons.  I put
hipster-quotes around "framework" because it's just a single class that
implements a lot of the things you'd have to do to make a daemon using the
lust.unix module.

There are two very little examples you can check out to see how this thing
works.

First, take a look at tests/server\_tests.py and the server it runs in
tests/simple\_test\_server.py.  The test itself is very lame, and basically
just runs this simple server as root and tries to control it.  You can see how
a basic server is implemented and how it works though.

Then, take a look at examples/thread\_server.py which implements a simple
ThreadedTCPServer using the python SocketServer module.  This example
implements probably the most common thing you'll run into with a daemonized
server: How to grab low/secure ports but still drop privileges.  Take a look at
the thread\_server.py:ThreadDaemon.before\_drop\_privs to see how this is done.

Finally, the lust.server.Simple framework just implements a tiny command
processing function that handles commands like "start", "stop", "status".  You
can override this and do whatever else you want here instead.


Working With Process Managers
====

If you want to use one of the many horribly written process supervisors
(seriously, look at their code some day), then here's how you do it:

    Don't use python-lust.

See? Easy. Just add an option to whatever command line thing you've got going
or the config file that skips all this gear and do whatever that process manage
needs.

Can't believe I have to figure that out for people.  It's like nobody can code
anymore.


Things To Do
===

* Need an atexit handler to clean up pid files.
* If you chroot then python modules all need to be in the chroot. Virtualenv could solve that.
* Reloading sucks because the process is chroot somewhere and command line args aren't saved.
* Logging needs a "threadsafety" option that locks all the calls.


FAQ
===

This FAQ is a defense against what I call "Bikeshed Marketing", a geek
favorite.  Bikeshed Marketing goes like this:

1. You make something cool and publish it somewhere.
2. Random dude goes "Why didn't you use X", some technology he is a fan of and loves promoting.
3. Yet, he isn't going to help implement it, so this is just bikeshedding.
4. Being bikeshedding you don't see the thinly disguised marketing for his favorite tech and proceed to defend your decision.
5. The only real answer is "Shut The Fuck Up", which is what you'd say if he asked, "Why aren't you taking Viagra? I got some to sell you!"

This FAQ is my premptive STFUs.


Q. Why didn't you just use Twisted?

A. Shut up.

Q. Why doesn't this work on Windows too?

A. Shut up.

Q. How come you aren't using Python's logging?

A. Shut the fuck up. Seriously?

Q. Why didn't you just use Go? Go has all of this too.

A. Seriously, shut the fuck up.

Q. Why don't you just use supervisord?

A. Alright. Say it with me. SHUT THE FUCK UP.

Q. If you won't use supervisord, then why not daemontools or runit or
s6? They don't require PID file management and take care of the logs
too.

A. Seriously? At least supervisord is python. SHUT THE FUCK **UP**.

Q. Why aren't you using TOML, JSON, YAML for config files?

A. Holy mother fuck dude. FUHG GUR SHPX HC!

![Seriously, Shut the fuck up](http://i.imgur.com/hrm1M.gif)
