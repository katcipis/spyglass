# Spyglass

Spyglass is a monitoring system for websites

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
