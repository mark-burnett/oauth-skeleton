# Scratch OAuth
[![Build Status](https://travis-ci.org/mark-burnett/oauth-skeleton.svg?branch=master)](https://travis-ci.org/mark-burnett/oauth-skeleton)

## Description

This repo is for exploring how to implement an OAuth 2.0 provider and consumers
using [oauthlib](https://github.com/idan/oauthlib).

The repo has several components:

- `s_auth` - the OAuth provider (web service)
- `s_client` - an OAuth client (web service), which also stores some resources
- `s_resource` - a resource server (web service)
- `s_user` - an SDK for this pretend web app
- `s_common` - misc. code used by one or more of the above modules

To run tests:

    $ pip install tox
    $ tox
