<!-- mdtocstart -->

# Table of Contents

- [Spyglass](#spyglass)
- [Development](#development)
    - [Dependencies](#dependencies)
    - [Running tests](#running-tests)
    - [Linting](#linting)
- [Configuration](#configuration)
- [Running](#running)
- [Why ?](#why-)
    - [Code Style](#code-style)
    - [Containers](#containers)
    - [Make](#make)
    - [Time Sensitive Tests](#time-sensitive-tests)
    - [Storage](#storage)
    - [TODO's](#todos)
        - [Integration Tests](#integration-tests)

<!-- mdtocend -->

# Spyglass

Spyglass is a monitoring system for websites. It is designed as a health
checker **spy** that given a set of health check targets
will probe them and send results to a Kafka topic and **spycollect**
which will subscribe to the same Kakfa topic, read the health status
messages and save them on PostgreSQL.

# Development

## Dependencies

To run the automation provided in the project through make
you will need to have installed on your host:

* Make
* Python >= 3.8

And run:

```
make deps
```

Which will install the dependencies on your host. If you want to avoid
installing the dependencies on your host and you already have
[Docker](https://docs.docker.com/) installed you can run:

```
make dev
```

And you will get an interactive shell inside a container with all
dependencies already installed.


## Running tests

Running unit tests is pretty straightforward, just run:

```
make test
```

Integration tests are more involved, they depend on configuration
(through environment variables) and also on pre-existing resources,
like kafka topics and database schemas.

See [configuration](#configuration) for more details on how to
do the configuration. Any missing config should be explicitly
informed by a skipping test when you run:

```
make test-integration
```

## Linting

To lint the code just run:

```
make lint
```

# Configuration

Configuration, both for production ready artifacts and integration
tests, is done through environment variables.

Both **spy** and **spycollect** can have their logging level configured
through the environment variable:

* SPYGLASS_LOG_LEVEL : Log level : ("debug", "info", "warning", "error")

Both **spy** and **spycollect** depend on Kafka and its configuration.
Kafka configuration is done through these environment variables:

* SPYGLASS_KAFKA_URI : URI used to connect on kafka
* SPYGLASS_KAFKA_SSL_CA : Path to CA file used to sign certificate
* SPYGLASS_KAFKA_SSL_CERT : Path to signed certificate
* SPYGLASS_KAFKA_SSL_KEY : Path to private key file

**spycollect** needs storage to save health status, it
uses PostgreSQL for that.

PostgreSQL configuration is done through these environment variables:

* SPYGLASS_POSTGRESQL_URI : URI used to connect on PostgreSQL

If the configuration has been done properly, just running **spy** and
**spycollect** should work.


# Running

To run the **spy** tool and the **spycollect** you need to
install all the [dependencies](#dependencies) or used the
development environment provided through **make dev**.

You can run:

```sh
./bin/spy
```

And:


```sh
./bin/spycollect
```

And if any configuration is missing you should get a helpful message
about which configurations are missing and what are each of them.

They are also packaged as Docker images, as a way to enable deployment.
To build the images you can run:

```
make image
```

And run:

```
docker run -ti katcipis/spyglass spy --help
```

Or:

```
docker run -ti katcipis/spyglass spycollect --help
```

## Setup Database

If the database is not set you can run:

```
make setup-database
```

To setup the database that will be used by **spycollect**, it will
create all required tables. It won't create the configured database,
the database must already exist.

The setup is idempotent, if the tables already exist no side effect
is generated.


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


## Storage

All storage related code (PostgreSQL) is not tested at all, the reason
is that I ran out of time :-(.

Design wise, it seemed like a good idea to partition the table by timestamp,
at least from what I understood reading about it
[here](https://www.postgresql.org/docs/11/ddl-partitioning.html).

Since I don't have a lot of experience with PostgreSQL, much less
as a time series, so it is not like a deep well informed decision :-).

For the timestamp type, by looking [here](https://www.postgresql.org/docs/9.1/datatype-datetime.html)
it seemed like the best option is "timestamp without time zone" since my
idea is to normalize on UTC always, so no need to store redundant time zone
information (it should always be UTC).

Also decided that what makes a unique entry is timestamp/domain/path and
avoid having duplicated entries (discard duplicates).


## TODO's

Some things that I ended up doing in a way that didn't made much happy but I
did it anyway because I wanted to finish it in time (prioritization).


### Integration Tests

On the kafka integration test I Would prefer to automate test
topic creation and deletion on teardown. Didn't find any create/delete
topic functionality on aiokafka and was running out of time
(other python sync kafka libs seemed to have these features).
Preferred to just depend on a pre-created topic for now
(but not feeling happy about it).
