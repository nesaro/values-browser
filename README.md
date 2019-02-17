# Values manager

This is an experiment on two things: CQRS and ontologies as concept

## ncurses-ui Values manager

Ncurses interface that allows to browse relationships between values. It is developed using CQRS-ish and abstracting events and signals

### Example 1: File list manager

Usage:

    <escape>dir /
    <escape>:q

It displays a list of the contents of a directory. Enter will change the URL to the subdirectory.
