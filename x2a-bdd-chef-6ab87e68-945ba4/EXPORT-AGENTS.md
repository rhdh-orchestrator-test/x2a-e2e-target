# Migration requirements

The FLPATH-4982 BDD requirement is preserved: `ansible/Makefile` must be non-empty, define the default `all` target, and invoke `ansible-playbook`.
