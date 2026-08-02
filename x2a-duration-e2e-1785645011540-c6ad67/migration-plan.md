# MIGRATION FROM ANSIBLE AND CHEF TO ANSIBLE

## Executive Summary

This repository contains a mix of Ansible playbooks and Chef InSpec tests, along with Chef Automate and Chef Infra Server deployment scripts. The migration scope is relatively small, focusing on converting existing Ansible playbooks to a more standardized Ansible structure while preserving the compliance testing capabilities currently provided by Chef InSpec. The estimated timeline for migration is 1-2 weeks, with low to medium complexity.

## Module Migration Plan

This repository contains Ansible playbooks and Chef InSpec tests that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that remediates SSL POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening

- **chef-automate-deployment**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization setup

- **chef-server-deployment**:
    - Description: Bash script for deploying standalone Chef Infra Server
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization setup

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test to verify HTTPS configuration
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec test to verify SSH security configuration

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible's built-in testing capabilities or integrate with Molecule for testing
  - Migration strategy: Convert InSpec tests to Ansible assert modules or Molecule verifiers
  - Alternative: Keep InSpec as a testing tool but integrate it into an Ansible-based workflow

- **Test Kitchen**: Replace with Molecule for Ansible role testing
  - Migration strategy: Create equivalent Molecule scenarios for each Test Kitchen suite

- **Chef Automate/Infra Server**: Evaluate if these components are needed or can be replaced with Ansible alternatives
  - Migration strategy: Consider migrating to Ansible Tower/AWX for similar functionality

### Security Considerations

- **SSL/TLS Configuration**: The playbooks configure Apache with TLS 1.2 and disable insecure protocols
  - Migration approach: Preserve these security hardening measures in the Ansible roles
  
- **SSH Hardening**: InSpec tests verify SSH root login is disabled
  - Migration approach: Create an Ansible role for SSH hardening that implements the same controls

- **Vault/secrets management**:
  - Hardcoded credentials in deployment scripts (username, password)
  - Migration approach: Replace with Ansible Vault for secure credential storage

### Technical Challenges

- **InSpec Test Conversion**: Converting InSpec tests to equivalent Ansible assertions
  - Mitigation strategy: Use Ansible's assert module or consider keeping InSpec as a testing tool integrated with Ansible

- **Self-signed Certificate Generation**: Ensuring the OpenSSL certificate generation works consistently
  - Mitigation strategy: Use Ansible's crypto modules which are more mature in recent Ansible versions

- **Apache Configuration**: Ensuring idempotent Apache configuration
  - Mitigation strategy: Use Ansible's apache2_* modules instead of file manipulation

### Migration Order

1. **website_https.yml** (Priority 1) - Convert to Ansible role with proper structure
   - Create role structure with tasks, templates, handlers
   - Move inline templates to template files
   - Implement idempotent certificate generation

2. **poodle_fix.yml** (Priority 1) - Incorporate into Apache role or security hardening role
   - Create a dedicated SSL hardening task file
   - Ensure idempotent configuration

3. **InSpec Tests** (Priority 2) - Convert to Ansible testing framework
   - Create equivalent tests using Ansible assert or Molecule

4. **Chef Deployment Scripts** (Priority 3) - Convert to Ansible roles for infrastructure setup
   - Create roles for deploying equivalent CI/CD infrastructure
   - Implement secure credential management

### Assumptions

1. The current Ansible playbooks are functional but not structured according to best practices
2. InSpec tests are used for compliance validation and should be preserved in some form
3. The Chef Automate and Chef Infra Server deployment scripts are used for setting up the infrastructure
4. No complex Chef cookbooks or recipes are present that would require significant logic translation
5. The target environment will continue to be Ubuntu 20.04 or compatible systems
6. The self-signed certificates are acceptable for the environment (not production)
7. No external dependencies or third-party modules are required beyond what's visible in the repository