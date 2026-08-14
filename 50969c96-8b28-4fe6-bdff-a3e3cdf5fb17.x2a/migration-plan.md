# MIGRATION FROM CHEF INSPEC AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a combination of Ansible playbooks and Chef InSpec tests that are used together to deploy and validate secure web applications. The primary focus is on demonstrating how Chef InSpec can be used alongside Ansible for compliance automation. The migration scope is relatively small, focusing on converting the existing Ansible playbooks to a more structured Ansible role-based approach while preserving the InSpec testing capabilities.

**Estimated Timeline**: 1-2 weeks for a single developer to complete the migration, including testing and documentation.

## Module Migration Plan

This repository contains Ansible playbooks and Chef InSpec tests that need individual migration planning:

### MODULE INVENTORY

- **website-https**:
    - Description: Ansible playbook that deploys an Apache web server with HTTPS configuration, including self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **poodle-fix**:
    - Description: Ansible playbook that remediates SSL POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening

- **website-https-verify**:
    - Description: Chef InSpec test profile that validates HTTPS configuration and website availability
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh-profile**:
    - Description: Chef InSpec test profile that validates SSH security configuration (root login disabled)
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, CCI compliance checks, STIG validation

- **chef-automate-deploy**:
    - Description: Bash script to deploy Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization setup

- **chef-server-deploy**:
    - Description: Bash script to deploy Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash
    - Key Features: Chef Server installation, user and organization setup

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Migration consideration: Replace with Ansible Molecule for testing.
- `chef-and-ansible/index.html`: Simple HTML file used as a template. Migration consideration: Convert to Ansible template.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible Molecule with Testinfra for infrastructure testing
  - Option 2: Maintain InSpec as a separate testing tool but invoke it from Ansible
  - Option 3: Convert InSpec tests to equivalent Ansible assert tasks

- **Test Kitchen**: Replace with Ansible Molecule for testing infrastructure

- **Chef Automate/Server**: The deployment scripts should be converted to Ansible roles for infrastructure deployment. Consider if Chef Automate/Server is still needed or if it can be replaced with:
  - AWX/Ansible Tower for orchestration
  - Compliance automation using OpenSCAP or similar tools

### Security Considerations

- **SSL/TLS Configuration**: The migration must maintain the security hardening that disables SSLv3 and enables only TLSv1.2
  - Migration approach: Create an Ansible role for Apache that includes proper SSL/TLS configuration

- **Self-signed Certificates**: The current implementation generates self-signed certificates
  - Migration approach: Create an Ansible role that handles certificate generation or integrates with Let's Encrypt for production environments

- **SSH Hardening**: The InSpec tests validate SSH security configurations
  - Migration approach: Create an Ansible role for SSH hardening that implements the same controls tested by the InSpec profile

- **Vault/secrets management**:
  - Hardcoded credentials in setup-automate scripts (username, password)
  - Migration approach: Use Ansible Vault to secure credentials

### Technical Challenges

- **InSpec Test Conversion**: Converting InSpec tests to equivalent Ansible testing mechanisms
  - Mitigation strategy: Use Ansible's assert module for basic tests and consider maintaining InSpec for complex compliance testing

- **Maintaining Compliance Validation**: Ensuring that the compliance checks currently performed by InSpec are preserved
  - Mitigation strategy: Document all compliance requirements and ensure they are covered in the new Ansible implementation

- **Apache Configuration Complexity**: The Apache configuration includes virtual hosts and SSL settings
  - Mitigation strategy: Use the `apache2_module` and `apache2_conf` Ansible modules for cleaner configuration management

### Migration Order

1. **website-https playbook** (Priority 1): Convert to an Ansible role with proper variable structure
2. **poodle-fix playbook** (Priority 2): Integrate into the Apache role as a security hardening task
3. **InSpec tests** (Priority 3): Convert to Ansible Molecule tests or maintain as separate InSpec profiles
4. **Chef deployment scripts** (Priority 4): Convert to Ansible roles for infrastructure deployment

### Assumptions

1. The primary goal is to maintain the same functionality while moving to a more structured Ansible approach
2. The InSpec tests are valuable and should be preserved in some form
3. The deployment scripts for Chef Automate/Server are still needed (if not, they can be excluded from migration)
4. The target environment will remain Ubuntu 20.04 or compatible
5. No additional functionality beyond what's in the current repository is required
6. The security hardening measures are required in the migrated solution
7. Test Kitchen is used for development/testing only and not for production deployments