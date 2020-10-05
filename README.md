# Spyglass

Spyglass is a monitoring system for websites

# Dependencies

To run tests and the project itself you will need to have
installed on your host:

* Make
* Python >= 3.8

And run:

```
make deps
```

Which will install the dependencies on your host, if you want to avoid
installing the dependencies on your host and you already have
[Docker](https://docs.docker.com/) installed you can run:

```
make dev
```

And you will get an interactive shell inside a container with all
dependencies already installed.

# Why ?

On this section I describe the reasoning of some of the design
decisions. It has been 2 years since I don't work continuously in
production with Python, so this has been an interesting exercise :-).

## Code Style

I really like the Go's approach of instead of discussing code style
just use automation to ensure consistency, like the Go proverb:

```
Gofmt's style is no one's favorite, yet gofmt is everyone's favorite.
```

For this project I chose the [Flake 8](https://pypi.org/project/flake8/)
because it is what I used on the past and it worked well (for my needs at least).

Regarding testing also got some ideas from
[Good Integration Practices](https://docs.pytest.org/en/latest/goodpractices.html).

## Containers

I tried to not impose the use of containers and docker on the project and
make it simple and focused on actual code. But I really like
the isolation and easier reproducibility that containers can bring
(not necessarily, depends on how you use them). There are other tools to
help with isolation and avoiding different projects stepping on each other
toes, like [venv](https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/).
I ended up using containers because I always worked with more than one
language and I like how containers allow me to address the isolation
problem consistently (just one tool).

## Make

Why use make ? It is related to the consistency/multiple languages argument
used before, I worked for some time with Python and Go in production and I
enjoyed having a uniform interface to run things like tests, linting, coverage
reports etc. The interface is decoupled from the underlying tooling, using make,
so it didn't made a difference if it used containers or not, or the tools
used for testing. The experience for moving across projects were more smooth
than previous projects I worked where you ended up having to read a lot of
docs just to understand how to run basic things like tests.

## Time Sensitive Tests

It is hard to avoid flaky tests when dealing with time, but I had some
positive experiences in the past when working with confidence
intervals. Also worked with mocking time in main loops (NodeJS), it can work
well but sometimes it gets out of hand and also results on flaky tests.

It could be a broken approach to mocking time, side effects of mocking
persisted across tests because other third party modules also
depended on time (NodeJS main loop itself included).

One alternative to messing around with global/default time facilities
is to inject some sort of timer through the API. That alternative is
safer and deterministic but always made me feel bad because the API
gets more complex and clumsy, beyond the test itself I never seem a
client of an API interested on passing its own timer, so it imposes
complexity on the caller that doesn't seem desirable.

Anyway I don't feel like I have a definitive answer for this,
but in this case I'm going with "no time mocking". The intervals used
are quite big, the idea is to catch big regressions in the time sensitive
logic, some bugs can still slip through.

This is not the same as tests that required some sort of synchronization but
instead an sleep was added and "it just works", I really hate that kind of stuff.
