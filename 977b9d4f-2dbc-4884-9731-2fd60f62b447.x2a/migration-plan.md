# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible components focused on compliance automation and infrastructure deployment. The primary migration scope involves:

1. Chef InSpec tests that need to be converted to Ansible-compatible testing frameworks
2. Chef server deployment scripts that need to be converted to Ansible playbooks
3. Existing Ansible playbooks that need to be reviewed and potentially refactored

The migration complexity is **LOW to MEDIUM** as the repository primarily contains:
- Simple Ansible playbooks for web server configuration
- Chef InSpec tests for compliance validation
- Shell scripts for Chef server deployment

Estimated timeline: 1-2 weeks for a complete migration, with the ability to migrate components incrementally.

## Module Migration Plan

This repository contains a mix of Chef InSpec tests, Ansible playbooks, and Chef server deployment scripts that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that remediates SSL POODLE vulnerability in Apache configuration
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening, service restart handlers

- **ssh_profile**:
    - Description: Chef InSpec test profile that validates SSH root login is disabled
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, compliance with security standards

- **website_https_verify**:
    - Description: Chef InSpec test profile that validates HTTPS configuration
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port validation, HTTPS response validation, SSL/TLS protocol validation

- **chef-server-deployment**:
    - Description: Shell scripts for deploying Chef Infra Server and Chef Automate
    - Path: setup-automate/deploy-chef-server.sh, setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification
- `index.html`: Simple HTML file used as a test page for the web server

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic with potential for on-premises or cloud deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec (latest)**: Replace with Ansible-native testing solutions:
  - Option 1: Migrate to Ansible Molecule with Testinfra for testing
  - Option 2: Use community.general.assert module for basic validation
  - Option 3: Maintain InSpec as a standalone testing tool that works with Ansible

- **Apache2 (2.4.41-4ubuntu3.10)**: Use Ansible's apache2_module, apache2_conf modules from the community.general collection

- **OpenSSL**: Use Ansible's built-in openssl_* modules (already in use in the existing playbooks)

### Security Considerations

- **SSL/TLS Configuration**: The migration must maintain the security hardening that disables SSLv3 and only enables TLSv1.2
  - Approach: Use the same configuration parameters in Ansible apache2_module and apache2_conf tasks

- **SSH Hardening**: Maintain the security control that prevents root login via SSH
  - Approach: Create an Ansible task that ensures PermitRootLogin is set to 'no' in sshd_config

- **Self-signed Certificates**: The current implementation uses self-signed certificates
  - Approach: Maintain the same approach using Ansible's openssl_* modules, but consider adding a variable to allow for proper certificates in production

- **Vault/secrets management**:
  - Hardcoded credentials in setup-automate scripts (username, password)
  - Approach: Move these to Ansible Vault encrypted variables

### Technical Challenges

- **Chef InSpec to Ansible Testing**: Converting InSpec tests to equivalent Ansible validation
  - Mitigation: Use Ansible's assert module or Molecule with Testinfra for similar functionality

- **Chef Server Deployment**: Converting Chef server deployment scripts to Ansible
  - Mitigation: Create Ansible roles that perform the same server setup and configuration

### Migration Order

1. **website_https.yml** (Priority 1 - already Ansible, low risk)
   - Review and refactor the existing Ansible playbook
   - Add proper variable handling and templating
   - Implement idempotency improvements

2. **poodle_fix.yml** (Priority 1 - already Ansible, low risk)
   - Review and potentially merge with website_https.yml as they handle related functionality

3. **InSpec Tests** (Priority 2 - moderate complexity)
   - Convert ssh_profile.rb to Ansible assertions or Molecule tests
   - Convert website_https_verify.rb to Ansible assertions or Molecule tests

4. **Chef Server Deployment Scripts** (Priority 3 - higher complexity)
   - Create Ansible roles for Chef Infra Server deployment
   - Create Ansible roles for Chef Automate deployment
   - Implement proper secret management with Ansible Vault

### Assumptions

1. The repository is primarily used for demonstration purposes rather than production deployment, as indicated by the README mentioning "examples" and "companions to a white paper"

2. The Chef InSpec tests are used to validate configurations managed by Ansible, suggesting a hybrid approach where Chef tools are used for compliance testing while Ansible handles configuration management

3. The target environment is Ubuntu 20.04 based on the kitchen.yml configuration

4. The deployment scripts for Chef server are intended for lab/demo environments, as they contain hardcoded credentials and simplified setup

5. The migration goal is to fully convert to Ansible, including replacing Chef InSpec tests with Ansible-native testing solutions

6. The existing Ansible playbooks (website_https.yml and poodle_fix.yml) are already functional and may only need refactoring rather than complete rewriting