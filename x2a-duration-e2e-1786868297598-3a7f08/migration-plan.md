# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef Automate/Infra Server deployment scripts and Ansible playbooks with Chef InSpec testing. The migration scope is relatively small, focusing on:

1. Converting Chef Automate/Infra Server deployment scripts to Ansible playbooks
2. Preserving existing Ansible playbooks while standardizing their structure
3. Maintaining Chef InSpec tests but integrating them into a pure Ansible workflow

**Estimated Timeline**: 1-2 weeks for a single engineer, with minimal complexity due to the limited scope of the repository.

## Module Migration Plan

This repository contains a mix of Ansible playbooks and Chef deployment scripts that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that deploys a secure Apache web server with SSL configuration
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that remediates SSL POODLE vulnerability in Apache
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables SSLv3, enforces TLSv1.2

- **chef-automate-deploy**:
    - Description: Bash script that deploys Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization setup

- **chef-server-deploy**:
    - Description: Bash script that deploys Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization setup

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification
- `chef-and-ansible/tests/website_https_verify.rb`: Chef InSpec test file for verifying HTTPS website deployment

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (used in kitchen.yml for testing)
- **Cloud Platform**: Not specified, appears to be platform-agnostic

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Maintain as a compliance testing tool but integrate with Ansible using ansible_playbook verifier or molecule
- **Test Kitchen**: Replace with Ansible Molecule for testing infrastructure
- **Chef Automate/Infra Server**: Replace deployment scripts with Ansible playbooks that achieve the same configuration

### Security Considerations

- **SSL Configuration**: The playbooks configure SSL for Apache. Migration must maintain the same security posture:
  - TLSv1.2 enforcement
  - Self-signed certificate generation
  - Proper file permissions for certificates (mode 0640)

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password)
  - Migration should use Ansible Vault to secure these credentials

### Technical Challenges

- **Chef InSpec Integration**: Ensuring InSpec tests continue to work with pure Ansible workflow
  - Mitigation: Use Ansible Molecule with InSpec verifier or create a custom verification step in CI/CD pipeline

- **Chef Automate/Server Deployment**: Converting bash scripts to idempotent Ansible playbooks
  - Mitigation: Use Ansible's package, command, and service modules with appropriate conditionals to ensure idempotency

### Migration Order

1. **Existing Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk, simply standardize format and integrate with Ansible best practices
2. **Chef Server Deployment Script** (deploy-chef-server.sh): Moderate complexity, convert to Ansible playbook
3. **Chef Automate Deployment Script** (deploy-automate.sh): Moderate complexity, convert to Ansible playbook
4. **Testing Framework**: Replace Test Kitchen with Molecule while preserving InSpec tests

### Assumptions

1. The repository is primarily used for demonstration/example purposes rather than production deployment, based on the README content
2. The Chef InSpec tests are intended to be preserved as they demonstrate compliance automation
3. The hardcoded credentials in the deployment scripts are for demonstration only and would be replaced with secure values in production
4. The Apache configuration is a simple example and not a complete production configuration
5. The target environment is Ubuntu 20.04 as specified in the kitchen.yml file