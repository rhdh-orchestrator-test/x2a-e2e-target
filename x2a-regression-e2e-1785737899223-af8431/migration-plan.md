# MIGRATION FROM ANSIBLE AND CHEF TO ANSIBLE

## Executive Summary

This repository contains examples of Chef InSpec with Ansible and Chef Automate/Chef Infra Server deployment scripts. The migration scope is relatively small, focusing on:

1. Ansible playbooks that deploy and configure a web server with HTTPS
2. Chef InSpec tests used for compliance verification of the Ansible-managed infrastructure
3. Shell scripts for deploying Chef Automate and Chef Infra Server

The migration complexity is low to medium, with an estimated timeline of 1-2 weeks. The primary focus will be on:
- Converting existing Ansible playbooks to follow Ansible best practices
- Integrating Chef InSpec tests into an Ansible-native testing framework
- Replacing Chef Automate/Infra Server deployment scripts with Ansible playbooks

## Module Migration Plan

This repository contains Ansible playbooks and Chef components that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures Apache with HTTPS using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that remediates SSL POODLE vulnerability in Apache
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening

- **website_https_verify**:
    - Description: Chef InSpec test profile that verifies HTTPS configuration and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening tests, HTTPS content verification, SSL protocol security checks

- **automate-deploy**:
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

- `kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification
- `index.html`: Static HTML content for the web server

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (used in kitchen.yml for testing)
- **Cloud Platform**: Not specified, appears to be platform-agnostic

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's built-in `assert` module for basic testing
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Keep InSpec but integrate it with Ansible using the `inspec` Ansible module

- **Test Kitchen**: Replace with:
  - Option 1: Molecule for Ansible role/playbook testing
  - Option 2: Ansible-compatible CI/CD pipeline (GitHub Actions, Jenkins, etc.)

- **Chef Automate/Infra Server**: Replace with:
  - Option 1: Ansible AWX/Tower for infrastructure management
  - Option 2: GitOps approach using Git repositories and CI/CD pipelines

### Security Considerations

- **SSL Configuration**: The current playbooks configure Apache with SSL and harden against POODLE vulnerability
  - Migration approach: Maintain the same security configurations in the Ansible roles
  - Consider using the `ansible.posix.seboolean` module for SELinux contexts if applicable

- **Self-signed Certificates**: Currently using OpenSSL for certificate generation
  - Migration approach: Use Ansible's `openssl_*` modules (already in use) with proper certificate management
  - Consider integrating with a certificate management system for production environments

- **Vault/secrets management**:
  - Hardcoded credentials in the Chef deployment scripts (username, password)
  - Migration approach: Replace with Ansible Vault for secure credential storage

### Technical Challenges

- **InSpec Testing Integration**: The current setup uses InSpec for compliance testing
  - Challenge: Maintaining compliance testing capabilities while migrating to Ansible
  - Mitigation: Either keep InSpec and integrate with Ansible or migrate tests to Ansible-native solutions

- **Chef Automate Functionality**: Chef Automate provides compliance reporting and visualization
  - Challenge: Replicating compliance reporting capabilities in an Ansible-only environment
  - Mitigation: Integrate with tools like Prometheus/Grafana or ELK stack for visualization and reporting

### Migration Order

1. **website_https playbook** (Priority 1, low risk)
   - Already an Ansible playbook, needs minimal changes to follow best practices
   - Convert to a proper Ansible role structure with variables, handlers, and templates

2. **poodle_fix playbook** (Priority 1, low risk)
   - Already an Ansible playbook, needs minimal changes
   - Consider merging with the website_https role as a security hardening task

3. **InSpec tests** (Priority 2, moderate complexity)
   - Decide on testing strategy (keep InSpec or migrate to Ansible-native)
   - Implement chosen testing approach

4. **Chef deployment scripts** (Priority 3, high complexity)
   - Replace with Ansible playbooks for infrastructure management
   - Implement secure credential handling with Ansible Vault

### Assumptions

1. The repository is primarily for demonstration/example purposes rather than production use
2. The InSpec tests are essential for compliance verification and should be maintained in some form
3. The target environment will continue to be Ubuntu-based systems
4. The self-signed certificates are acceptable for the use case (not production)
5. The Chef Automate/Infra Server deployment is a one-time setup rather than ongoing management
6. No external dependencies or integrations beyond what's visible in the repository
7. No specific performance requirements for the Apache web server
8. No specific backup or disaster recovery requirements