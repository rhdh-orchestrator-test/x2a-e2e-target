# Migration requirements

The FLPATH-4982 BDD requirement must be preserved: create a non-empty `ansible/Makefile` with a default `all` target that invokes `ansible-playbook`.
