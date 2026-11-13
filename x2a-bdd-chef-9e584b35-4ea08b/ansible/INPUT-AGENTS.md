# Migration input requirements

The generated Ansible project must preserve the FLPATH-4982 BDD Makefile requirement: create a non-empty `ansible/Makefile` with a default `all` target that invokes `ansible-playbook`.
