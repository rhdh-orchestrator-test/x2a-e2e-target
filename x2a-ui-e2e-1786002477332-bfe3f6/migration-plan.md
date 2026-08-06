# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used for compliance automation and server configuration. The migration scope is relatively small, focusing on:

1. Converting Chef InSpec tests to Ansible-compatible testing frameworks
2. Consolidating existing Ansible playbooks
3. Migrating Chef Automate and Chef Infra Server deployment scripts to Ansible playbooks

The complexity is moderate, with the main challenge being the conversion of InSpec tests to an Ansible-compatible testing framework. The estimated timeline for migration is 1-2 weeks, depending on the team's familiarity with Ansible testing frameworks.

## Module Migration Plan

This repository contains a mix of Ansible playbooks and Chef InSpec tests that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate the POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: SSL protocol configuration, service restart

- **chef-automate-deploy**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization setup

- **chef-server-deploy**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization setup

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Migration will require updating to use Ansible-native testing frameworks.
- `tests/website_https_verify.rb`: InSpec test that verifies HTTPS configuration on the web server. Will need conversion to Ansible-compatible test framework.
- `tests/ssh_profile.rb`: InSpec test that verifies SSH configuration security. Will need conversion to Ansible-compatible test framework.
- `index.html`: Sample HTML file used for testing web server configuration. Can be used as-is in Ansible.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (used in kitchen.yml for testing)
- **Cloud Platform**: Not specified, but scripts are designed to work on both on-premises and cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-compatible testing frameworks like:
  - Molecule for infrastructure testing
  - ansible-lint for playbook linting
  - testinfra for Python-based infrastructure testing

- **Test Kitchen with Ansible**: Replace with Molecule for testing Ansible roles and playbooks

- **Chef Automate/Infra Server**: Replace with:
  - Ansible AWX or Ansible Tower for web UI and REST API
  - GitLab CI/CD or Jenkins for pipeline automation
  - Ansible Vault for secrets management

### Security Considerations

- **SSL Configuration**: The playbooks configure SSL for Apache. Migration should maintain or improve the security posture:
  - Ensure TLS 1.2+ is enforced (already implemented in poodle_fix.yml)
  - Consider adding more modern cipher suites
  - Add HSTS headers

- **SSH Hardening**: The InSpec tests verify SSH security configurations. Migration should:
  - Maintain SSH hardening checks
  - Implement remediation in Ansible if checks fail

- **Vault/secrets management**:
  - Hardcoded credentials in setup-automate scripts (username, password)
  - Self-signed certificates generated in website_https.yml
  - Migration should use Ansible Vault for credential storage

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to an Ansible-compatible testing framework will require:
  - Understanding the InSpec test logic
  - Implementing equivalent tests in Molecule/testinfra
  - Ensuring test coverage is maintained

- **Chef Automate/Server Deployment**: Replacing Chef Automate/Server deployment scripts with Ansible:
  - Determining if Chef Automate/Server is still needed or if it can be fully replaced by Ansible Tower/AWX
  - If Chef is still needed, creating Ansible playbooks to deploy and configure Chef components

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk, already in Ansible format
   - Review and optimize existing playbooks
   - Add documentation
   - Implement idempotency checks

2. **Testing Framework** (InSpec tests):
   - Set up Molecule testing framework
   - Convert InSpec tests to Molecule/testinfra
   - Ensure tests pass against the existing infrastructure

3. **Chef Deployment Scripts**:
   - Determine if Chef components are still needed
   - If yes, create Ansible playbooks to replace bash scripts
   - If no, document the deprecation and removal process

### Assumptions

1. The repository is primarily used for demonstration and educational purposes, as indicated by the README.md.
2. The Chef InSpec tests are used alongside Ansible for compliance automation, not as part of a larger Chef ecosystem.
3. The setup-automate scripts are examples and not used in production, given the hardcoded credentials.
4. The target environment is Ubuntu 20.04 running on Vagrant VMs for testing.
5. There's no complex data structure or state management that would require special handling during migration.
6. The migration is primarily focused on standardizing on Ansible rather than maintaining a hybrid Chef/Ansible environment.