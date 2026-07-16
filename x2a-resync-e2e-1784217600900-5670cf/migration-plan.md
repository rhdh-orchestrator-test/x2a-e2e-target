# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation. The primary focus is on using Chef InSpec for compliance testing alongside Ansible for configuration management. The repository also includes Chef Automate and Chef Infra Server deployment scripts. The migration scope is relatively small, with most components already in Ansible format. The estimated timeline for complete migration is 1-2 weeks, with low complexity.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables SSLv3 and enables TLSv1.2 only

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS configuration on the web server
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response verification, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec profile that verifies SSH security configuration
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login verification, compliance with security standards (STIG)

- **chef-automate-deployment**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Infra Server installation, user and organization creation

- **chef-server-deployment**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Migration considerations include replacing with Ansible-native testing frameworks like Molecule.
- `index.html`: Sample HTML file used for testing the web server. No migration needed, can be used as-is.

### Target Details

Analyze the source repository to determine target environment specifications:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec (latest)**: Replace with Ansible-native testing solutions:
  - Option 1: Convert InSpec tests to Ansible assert modules
  - Option 2: Use Ansible's built-in `assert` module with appropriate conditions
  - Option 3: Use Molecule for testing Ansible roles and playbooks

- **Test Kitchen (latest)**: Replace with Molecule for Ansible role testing
  - Molecule provides native testing for Ansible roles and playbooks
  - Supports multiple drivers (Docker, Vagrant, etc.)
  - Integrates with various verifiers (Testinfra, Goss, etc.)

- **Chef Automate/Infra Server**: Replace with Ansible Automation Platform or open-source alternatives:
  - AWX (open-source upstream of Ansible Tower)
  - Ansible Automation Platform (commercial)

### Security Considerations

- **SSL/TLS Configuration**: The migration must maintain the security hardening in the Apache SSL configuration:
  - Ensure TLSv1.2 is enforced
  - Disable older protocols (SSLv3)
  - Maintain proper certificate generation and deployment

- **SSH Security**: Maintain SSH hardening configurations:
  - Disable root login
  - Comply with STIG requirements (SRG-OS-000112, V-38607)

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be migrated to Ansible Vault
  - Self-signed certificates should be managed securely
  - Count of credentials detected: 3 (username, password, email in deployment scripts)

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible-native testing frameworks:
  - Challenge: InSpec has specific testing constructs that may not have direct equivalents in Ansible
  - Mitigation: Use Ansible's assert module with appropriate conditions or consider using Testinfra with Molecule

- **Chef Automate/Server Deployment**: Replacing Chef infrastructure deployment:
  - Challenge: Chef Automate and Chef Infra Server provide specific functionality that needs equivalent Ansible solutions
  - Mitigation: Deploy AWX or Ansible Automation Platform using Ansible playbooks

### Migration Order

1. **website_https.yml** and **poodle_fix.yml** (low risk, already in Ansible format)
   - Review and optimize existing Ansible playbooks
   - Consolidate into roles if appropriate

2. **InSpec Tests** (moderate complexity)
   - Convert website_https_verify.rb to Ansible assertions or Molecule tests
   - Convert ssh_profile.rb to Ansible assertions or Molecule tests

3. **Chef Deployment Scripts** (high complexity)
   - Create Ansible playbooks to replace deploy-automate.sh and deploy-chef-server.sh
   - Set up AWX or Ansible Automation Platform as replacement for Chef Automate/Server

### Assumptions

1. The repository is primarily used for demonstration purposes rather than production deployment
2. The InSpec tests are used for compliance verification rather than extensive functional testing
3. The deployment scripts are examples and may contain simplified configurations
4. No complex Chef cookbooks or recipes are present that would require significant refactoring
5. The target environment is Ubuntu 20.04 running on Vagrant VMs
6. No external dependencies or third-party integrations are required beyond what's visible in the repository
7. The hardcoded credentials in the deployment scripts are for demonstration purposes only
8. The self-signed certificates are acceptable for the target environment (not production)