# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used for demonstration purposes related to compliance automation. The repository appears to be a set of examples rather than a production infrastructure codebase. The migration scope is relatively small, focusing on:

1. Chef InSpec tests that need to be migrated to Ansible-compatible testing frameworks
2. Ansible playbooks that may need to be updated or standardized
3. Chef Automate and Chef Infra Server deployment scripts that need to be replaced with Ansible equivalents

Given the limited scope and example nature of the repository, this migration is estimated to be of low complexity and could be completed within 1-2 weeks by a single engineer familiar with both Chef and Ansible technologies.

## Module Migration Plan

This repository contains a mix of Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS enabled using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables vulnerable SSL protocols, enables only TLSv1.2

- **ssh_profile**:
    - Description: Chef InSpec test that verifies SSH root login is disabled
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: Compliance test for SSH configuration security

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS website functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Tests port 443 listening, HTTPS response, SSL/TLS protocol security

- **deploy-automate**:
    - Description: Bash script that deploys Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, user and organization creation

- **deploy-chef-server**:
    - Description: Bash script that deploys Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Will need to be updated to use Ansible-native testing frameworks.
- `chef-and-ansible/index.html`: Simple HTML file used for testing the web server deployment.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-compatible testing frameworks:
  - Option 1: Use Ansible's built-in `assert` module for basic testing
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Use pytest-ansible for Python-based testing

- **Test Kitchen**: Replace with:
  - Molecule for Ansible role testing
  - Or continue using Test Kitchen with the `kitchen-ansible` plugin

- **Chef Automate/Infra Server**: Replace with:
  - Ansible AWX/Tower for web UI and job scheduling
  - Git repositories for Ansible playbook storage
  - Consider using ansible-lint for static code analysis

### Security Considerations

- **SSL Configuration**: The playbooks configure Apache with SSL/TLS. Ensure the migration maintains or improves the security posture:
  - Update to enforce TLS 1.3 where possible
  - Implement modern cipher suites
  - Add HSTS headers

- **SSH Hardening**: The InSpec tests verify SSH security configurations. Ensure these checks are maintained in the Ansible solution:
  - Create equivalent Ansible assertions or use ansible-lint rules

- **Credentials Management**: The deployment scripts contain hardcoded credentials:
  - Replace with Ansible Vault for secure credential storage
  - Consider integration with external secret management systems

- **Vault/secrets management**:
  - Hardcoded credentials in deploy-automate.sh and deploy-chef-server.sh (username, password)
  - Self-signed certificates generated in website_https.yml

### Technical Challenges

- **Test Framework Conversion**: Converting InSpec tests to Ansible assertions or Molecule tests:
  - InSpec has a rich DSL for compliance testing that doesn't directly map to Ansible
  - Solution: Create custom Ansible modules or use community modules that provide similar functionality

- **Certificate Management**: The current solution generates self-signed certificates:
  - Consider integrating with Let's Encrypt for production-ready certificates
  - Use Ansible's crypto modules for certificate generation and management

- **Idempotency**: Ensure all converted playbooks maintain idempotency:
  - Review commands that use a2ensite, a2dissite, a2enmod which may not be idempotent
  - Replace with Ansible's apache2_* modules where possible

### Migration Order

1. **website_https.yml** (Priority 1): Already an Ansible playbook, just needs review and potential updates for best practices
2. **poodle_fix.yml** (Priority 1): Already an Ansible playbook, just needs review and potential updates for best practices
3. **InSpec Tests** (Priority 2): Convert to Ansible-compatible testing framework
4. **Chef Deployment Scripts** (Priority 3): Convert to Ansible playbooks for deploying alternative solutions

### Assumptions

1. The repository is primarily for demonstration purposes and not a production environment
2. The target environment will continue to be Ubuntu 20.04 or similar
3. The security requirements demonstrated in the InSpec tests need to be maintained
4. The Chef Automate and Infra Server deployment will be replaced with Ansible AWX/Tower or similar
5. No external dependencies or integrations beyond what's visible in the repository
6. The migration is focused on technology change rather than functionality changes
7. Test Kitchen can be replaced with Molecule or similar Ansible-native testing frameworks
8. Self-signed certificates are acceptable for the demonstration environment