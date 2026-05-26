# MIGRATION FROM CHEF INSPEC AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a combination of Chef InSpec tests and Ansible playbooks that are used together to deploy and validate secure web server configurations. The primary focus is on demonstrating how Chef InSpec can be used alongside Ansible for compliance automation. The migration scope is relatively small, with only a few Ansible playbooks and InSpec tests to migrate. The estimated timeline for migration is 1-2 weeks, with low complexity as most of the content is already in Ansible format.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that deploys an Apache web server with HTTPS configuration and self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables vulnerable SSL protocols, enables TLSv1.2

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec test that verifies SSH security configuration
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login check, compliance with security standards (STIG)

- **chef-server-deployment**:
    - Description: Bash scripts for deploying Chef Infra Server and Chef Automate
    - Path: setup-automate/deploy-automate.sh, setup-automate/deploy-chef-server.sh
    - Technology: Bash
    - Key Features: Chef Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Migration considerations include replacing with Ansible Molecule for testing.
- `index.html`: Sample HTML content for the web server. No migration needed, can be used as-is in Ansible.

### Target Details

Analyze the source repository to determine target environment specifications:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible Molecule with Testinfra for infrastructure testing
  - Option 2: Convert InSpec tests to Ansible assert tasks
  - Option 3: Maintain InSpec as a separate tool but call it from Ansible

- **Test Kitchen**: Replace with Ansible Molecule for testing infrastructure

### Security Considerations

- **SSL/TLS Configuration**: The playbooks configure Apache with TLSv1.2 and disable older protocols. This security practice should be maintained in the migrated Ansible roles.
- **SSH Security**: The InSpec tests verify SSH root login is disabled. This check should be incorporated into the Ansible roles.
- **Self-signed Certificates**: The playbook generates self-signed certificates. Consider enhancing with Let's Encrypt integration for production environments.
- **Vault/secrets management**: 
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - No other credential patterns detected in the playbooks

### Technical Challenges

- **InSpec Test Conversion**: Converting InSpec tests to Ansible-native testing frameworks may require additional effort to maintain the same level of compliance validation.
  - Mitigation: Consider using Ansible's assert module or Molecule with Testinfra to replicate InSpec tests.

- **Chef Server Deployment**: The bash scripts for Chef Server deployment will need to be completely rewritten as Ansible roles.
  - Mitigation: Create dedicated Ansible roles for infrastructure management that replace the Chef Server functionality.

### Migration Order

1. **website_https playbook** (low risk, already in Ansible format)
2. **poodle_fix playbook** (low risk, already in Ansible format)
3. **InSpec tests** (moderate complexity, requires conversion to Ansible testing framework)
4. **Chef Server deployment scripts** (high complexity, requires complete rewrite)

### Assumptions

1. The primary goal is to migrate all functionality to pure Ansible without any Chef components.
2. The InSpec tests are currently used for compliance validation and their functionality needs to be preserved.
3. The repository is primarily used for demonstration purposes rather than production deployments.
4. The target environment will continue to be Ubuntu 20.04 or compatible systems.
5. The security requirements (TLS configuration, SSH hardening) need to be maintained in the migrated solution.
6. The Chef Server deployment scripts are included in the scope of migration, even though they are for deploying Chef infrastructure.