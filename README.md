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
