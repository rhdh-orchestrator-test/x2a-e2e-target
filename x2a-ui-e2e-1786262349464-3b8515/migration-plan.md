# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible configurations focused on compliance automation and Chef server deployment. The repository appears to be primarily educational/demonstration in nature rather than a production infrastructure codebase. The migration scope is relatively small, with only a few Ansible playbooks and Chef InSpec tests that need to be migrated to a pure Ansible solution. The estimated timeline for migration is 1-2 days given the limited scope.

## Module Migration Plan

This repository contains Ansible playbooks and Chef InSpec tests that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that addresses the POODLE vulnerability by disabling older SSL protocols and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening

- **ssh_profile**:
    - Description: Chef InSpec test that verifies SSH root login is disabled according to security requirements
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration compliance testing

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS is properly configured on the web server
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **chef-automate-deployment**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization setup

- **chef-server-deployment**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization setup

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration file for running Ansible playbooks and InSpec tests in a Vagrant environment. Migration consideration: Replace with Ansible Molecule for testing.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be targeting on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible Molecule with Testinfra for infrastructure testing
  - Option 2: Convert InSpec tests to Ansible assert tasks or custom modules
  - Option 3: Maintain InSpec as a separate testing tool but invoke it from Ansible

- **Test Kitchen**: Replace with Ansible Molecule for testing infrastructure

- **Chef Automate/Server**: Replace deployment scripts with Ansible playbooks that can:
  - Option 1: Deploy alternative compliance and infrastructure management tools
  - Option 2: Continue to deploy Chef components but using Ansible for the deployment automation

### Security Considerations

- **SSL/TLS Configuration**: The migration must maintain the security hardening present in the poodle_fix.yml playbook
  - Ensure TLSv1.2 remains the minimum protocol version
  - Consider upgrading to also allow TLSv1.3 for improved security

- **SSH Hardening**: Maintain the SSH security controls verified by the InSpec tests
  - Ensure root login remains disabled
  - Consider adding additional SSH hardening measures

- **Self-signed Certificates**: The current implementation uses self-signed certificates
  - Consider implementing Let's Encrypt integration for production environments
  - Ensure proper certificate rotation and management

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - Count: 2 credential sets (one in each deployment script)

### Technical Challenges

- **InSpec Test Conversion**: Converting InSpec tests to equivalent Ansible verification methods
  - Mitigation: Use Ansible assert modules or Molecule with Testinfra as alternatives
  - Consider maintaining InSpec as a separate tool if tests are complex

- **Chef Server Deployment**: Replacing Chef server deployment scripts with equivalent Ansible playbooks
  - Mitigation: Create Ansible roles for Chef server deployment or consider alternative configuration management solutions

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk as they are already in Ansible format, just need review and potential refactoring to follow best practices
2. **InSpec Tests** (ssh_profile.rb, website_https_verify.rb): Moderate complexity to convert to Ansible-native testing
3. **Chef Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh): Higher complexity to convert to Ansible playbooks

### Assumptions

1. The repository is primarily for demonstration/educational purposes rather than production use
2. The target environment is Ubuntu 20.04 running in Vagrant VMs
3. There are no external dependencies or integrations beyond what's visible in the code
4. The hardcoded credentials in the deployment scripts are for demonstration only
5. The self-signed certificates are acceptable for the intended use case
6. There is no requirement to maintain backward compatibility with Chef InSpec
7. The migration is focused on converting to pure Ansible rather than maintaining a hybrid approach