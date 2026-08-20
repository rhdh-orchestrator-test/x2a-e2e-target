# MIGRATION FROM ANSIBLE AND CHEF TO ANSIBLE

## Executive Summary

This repository contains examples of Chef InSpec being used alongside Ansible for compliance automation, as well as Chef Automate and Chef Infra Server deployment scripts. The migration scope is relatively small, focusing on:

1. Ansible playbooks that deploy and configure a web server with HTTPS
2. Chef InSpec tests for compliance verification
3. Shell scripts for Chef Automate and Chef Infra Server deployment

The migration complexity is low to moderate, with an estimated timeline of 1-2 weeks. The primary focus will be on converting the InSpec tests to Ansible-compatible testing frameworks while preserving the existing Ansible playbooks.

## Module Migration Plan

This repository contains Ansible playbooks and Chef InSpec tests that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures an Apache web server with HTTPS using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables SSLv3 and enables only TLSv1.2

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS configuration and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response verification, SSL protocol security verification

- **automate-deploy**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deploy**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests
- `index.html`: Static HTML content for the web server

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (used in Test Kitchen configuration)
- **Cloud Platform**: Not specified, appears to be platform-agnostic

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Migrate to Ansible Molecule for testing
  - Option 2: Use ansible-test framework
  - Option 3: Integrate with pytest-ansible for more complex testing scenarios

- **Test Kitchen**: Replace with:
  - Ansible Molecule for testing infrastructure
  - Or continue using Test Kitchen with the Ansible provisioner (already in use)

### Security Considerations

- **SSL/TLS Configuration**: The migration must maintain the security hardening in the poodle_fix.yml playbook
  - Ensure TLSv1.2 remains the minimum protocol version
  - Consider upgrading to include TLSv1.3 support

- **Self-signed Certificates**: The current implementation uses self-signed certificates
  - Consider implementing Let's Encrypt integration for production environments
  - Maintain the same key strength and security parameters

- **Vault/secrets management**:
  - No encrypted secrets were found in the repository
  - The deploy scripts contain hardcoded credentials that should be moved to Ansible Vault

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to an Ansible-compatible testing framework
  - Mitigation: Use Ansible Molecule which provides similar functionality for testing
  - Alternative: Implement custom Ansible playbooks that perform the same validation checks

- **Chef Automate/Server Deployment**: Converting the Chef server deployment scripts to Ansible
  - Mitigation: Create Ansible roles that perform the same server setup and configuration
  - Consider using the official Chef Ansible Collection if available

### Migration Order

1. **website_https playbook** (low risk, already Ansible)
   - Review and optimize the existing Ansible playbook
   - No migration needed, just incorporate into the new structure

2. **poodle_fix playbook** (low risk, already Ansible)
   - Review and optimize the existing Ansible playbook
   - No migration needed, just incorporate into the new structure

3. **website_https_verify tests** (moderate complexity)
   - Convert InSpec tests to Ansible Molecule tests
   - Ensure all compliance checks are maintained

4. **Chef deployment scripts** (high complexity)
   - Create Ansible roles to replace the Chef Automate and Chef Server deployment scripts
   - Implement proper secret management with Ansible Vault

### Assumptions

1. The primary goal is to standardize on Ansible and remove Chef dependencies where possible
2. The InSpec tests are used for compliance verification and need to be replaced with equivalent Ansible-based testing
3. The deployment scripts for Chef Automate and Chef Infra Server need to be converted to Ansible roles
4. The current Test Kitchen setup is used for development and testing, and a similar workflow is desired in the migrated solution
5. No external dependencies or integrations beyond what's visible in the repository
6. The hardcoded credentials in the deployment scripts are for demonstration purposes and will be properly secured in the migrated solution