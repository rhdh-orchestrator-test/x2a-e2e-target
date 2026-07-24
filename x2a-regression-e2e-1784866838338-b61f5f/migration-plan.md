# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible configurations focused on demonstration and example purposes. The primary content consists of:

1. Ansible playbooks for configuring web servers with HTTPS
2. Chef InSpec tests for validating configurations
3. Shell scripts for deploying Chef Automate and Chef Infra Server

The migration scope is relatively small, with only a few Ansible playbooks that need to be updated to modern Ansible practices, and Chef InSpec tests that need to be converted to Ansible-native testing solutions. The estimated timeline for migration is 1-2 weeks, with low complexity.

## Module Migration Plan

This repository contains Ansible playbooks and Chef InSpec tests that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures Apache web server with HTTPS using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: SSL protocol configuration, service restart

- **chef-automate-deploy**:
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

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests
- `tests/website_https_verify.rb`: InSpec test to verify HTTPS configuration on the web server
- `tests/ssh_profile.rb`: InSpec test to verify SSH security configuration
- `index.html`: Sample HTML file for the web server

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Test Kitchen**: Replace with Ansible Molecule for testing
- **InSpec**: Replace with Ansible-native testing solutions like:
  - ansible-lint for static analysis
  - testinfra for infrastructure testing
  - ansible-test for module testing
- **Chef Automate/Infra Server**: Replace with Ansible Automation Platform or open-source alternatives like:
  - AWX (open-source version of Ansible Tower)
  - Semaphore (lightweight alternative)

### Security Considerations

- **SSL Configuration**: The playbooks configure SSL for Apache. Ensure modern TLS protocols and ciphers are used in the migrated Ansible roles.
- **SSH Hardening**: The InSpec tests verify SSH security configurations. Ensure these checks are maintained in the Ansible-native testing solution.
- **Credentials Management**: The deployment scripts contain hardcoded credentials:
  - Replace hardcoded passwords in deploy-automate.sh and deploy-chef-server.sh with Ansible Vault
  - Store sensitive variables in encrypted files
  - Consider using a secrets management solution like HashiCorp Vault

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible-native testing solutions will require understanding the equivalent assertions and test structures.
  - Mitigation: Use testinfra which has a similar syntax to InSpec for infrastructure testing.

- **Chef Automate Replacement**: Finding an equivalent to Chef Automate's compliance scanning in the Ansible ecosystem.
  - Mitigation: Consider integrating with OpenSCAP or other compliance tools that can work with Ansible.

### Migration Order

1. **website_https.yml** (low risk, already Ansible): Convert to Ansible role with modern practices
2. **poodle_fix.yml** (low risk, already Ansible): Convert to Ansible role or include in the website_https role
3. **InSpec Tests** (moderate complexity): Convert to testinfra or other Ansible-native testing
4. **Chef Deployment Scripts** (high complexity): Create Ansible playbooks for deploying Ansible Automation Platform or AWX

### Assumptions

1. The repository is primarily for demonstration purposes and not a production environment.
2. The InSpec tests are used for validation and compliance checking of the infrastructure.
3. The deployment scripts are used for setting up a Chef environment, which will be replaced with an Ansible environment.
4. The target environment is Ubuntu 20.04 running on Vagrant VMs.
5. No external dependencies or integrations beyond what's visible in the repository.
6. No complex data structures or custom facts are being used.
7. No existing Ansible inventory or group variables are present.
8. The migration will maintain the same functionality but using Ansible-native approaches.