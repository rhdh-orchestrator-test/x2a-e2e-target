# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible components that need to be migrated to a standardized Ansible approach. The repository appears to be primarily a set of examples for Chef and Ansible integration, with a focus on using Chef InSpec for compliance testing of Ansible-managed infrastructure. The migration scope is relatively small, with only a few Ansible playbooks and Chef server setup scripts to consider. The estimated timeline for migration is 1-2 weeks, with low complexity.

## Module Migration Plan

This repository contains Ansible playbooks and Chef server setup scripts that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that addresses the POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening, service restart handlers

- **chef-automate-deploy**:
    - Description: Bash script to deploy Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization setup

- **chef-server-deploy**:
    - Description: Bash script to deploy Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization setup

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks in a Vagrant environment. Migration consideration: Replace with Ansible Molecule for testing.
- `tests/website_https_verify.rb`: Chef InSpec test file for verifying HTTPS configuration. Migration consideration: Convert to Ansible Molecule tests or maintain as InSpec tests integrated with Ansible.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (used in kitchen.yml for testing)
- **Cloud Platform**: Not specified, appears to be platform-agnostic with potential for on-premises or cloud deployment

## Migration Approach

### Key Dependencies to Address

- **Chef Automate CLI**: Replace with Ansible roles for configuration management
- **Chef Server**: Replace with Ansible AWX/Tower or other Ansible-based configuration management
- **Test Kitchen**: Replace with Ansible Molecule for testing
- **InSpec**: Can be maintained as a testing framework or replaced with Ansible Molecule

### Security Considerations

- **SSL Configuration**: The playbooks include SSL hardening (POODLE fix) that must be preserved in the migration
- **Self-signed certificates**: The website_https.yml playbook generates self-signed certificates which should be replaced with a more robust certificate management approach
- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - No encrypted data or vault usage detected in current implementation

### Technical Challenges

- **InSpec Integration**: Determining whether to maintain Chef InSpec for testing or migrate to native Ansible testing tools
- **Chef Server Deployment**: Creating equivalent Ansible roles to replace the Chef server deployment scripts

### Migration Order

1. **website_https playbook** (low risk, already in Ansible format)
2. **poodle_fix playbook** (low risk, already in Ansible format)
3. **Chef server deployment scripts** (moderate complexity, requires creating Ansible roles)

### Assumptions

1. The repository is primarily for demonstration purposes and may not represent production code
2. The Chef InSpec tests are intended to work alongside Ansible rather than being replaced by it
3. The Chef server deployment scripts are intended for setting up a Chef infrastructure, which may be replaced entirely by Ansible AWX/Tower
4. No actual Chef cookbooks were found in the repository, suggesting that the migration is primarily focused on the infrastructure setup scripts
5. The target environment is Ubuntu 20.04 based on the kitchen.yml configuration
6. The security configurations in the playbooks (especially SSL hardening) are important to preserve in the migration
7. There may be external dependencies or integrations not visible in the repository