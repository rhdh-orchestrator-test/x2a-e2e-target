# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation. The primary focus appears to be on showing how Chef InSpec can be used alongside Ansible for compliance testing rather than being a pure Chef cookbook repository. There are also setup scripts for deploying Chef Automate and Chef Infra Server.

The migration scope is relatively small, as most of the content is already in Ansible format. The main migration effort will involve:
1. Converting the Chef InSpec tests to equivalent Ansible testing frameworks
2. Replacing the Chef Automate/Infra Server setup scripts with Ansible playbooks

Estimated timeline: 1-2 weeks for a small team, with most of the effort focused on replacing InSpec tests with equivalent Ansible testing solutions.

## Module Migration Plan

This repository contains a mix of Ansible playbooks and Chef InSpec tests that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS enabled using a self-signed certificate
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables vulnerable SSL protocols, enables TLSv1.2

- **ssh_profile**:
    - Description: Chef InSpec test that verifies SSH root login is disabled
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: Compliance testing for SSH configuration

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS is properly configured
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Tests for port 443 listening, HTTPS response, and SSL/TLS protocol configuration

- **chef-automate-setup**:
    - Description: Bash script to deploy Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-setup**:
    - Description: Bash script to deploy Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration file that uses Ansible as the provisioner and InSpec as the verifier
- `README.md`: Documentation explaining the purpose of the repository

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic with potential for on-premises or cloud deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-compatible testing frameworks:
  - Option 1: Use Ansible's built-in `assert` module for basic testing
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Use the Ansible `command` module to run external testing tools

- **Test Kitchen**: Replace with:
  - Molecule for Ansible role testing
  - Or continue using Test Kitchen with the Ansible provisioner

- **Chef Automate/Infra Server**: Replace with:
  - Ansible Tower/AWX for enterprise automation
  - Or GitLab CI/CD or Jenkins for CI/CD pipelines

### Security Considerations

- **SSL/TLS Configuration**: The playbooks configure Apache with TLS 1.2 and disable older protocols. This security practice should be maintained in the migrated solution.
  - Migration approach: Keep the same TLS configuration in the Ansible playbooks

- **SSH Security**: The InSpec tests verify that SSH root login is disabled.
  - Migration approach: Create an equivalent test using Ansible's assert module or Molecule

- **Self-signed Certificates**: The playbooks generate self-signed certificates for HTTPS.
  - Migration approach: Consider using Ansible's `community.crypto` collection for certificate management in production environments

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password)
  - Migration approach: Replace with Ansible Vault for secure credential storage

### Technical Challenges

- **Challenge 1: InSpec Test Conversion**
  - Description: Converting InSpec tests to equivalent Ansible testing frameworks
  - Mitigation strategy: Use Ansible's assert module for simple tests, and consider Molecule for more complex testing scenarios

- **Challenge 2: Chef Automate/Infra Server Replacement**
  - Description: Replacing Chef Automate and Infra Server with equivalent Ansible-based solutions
  - Mitigation strategy: Evaluate Ansible Tower/AWX as a replacement for Chef Automate's dashboard and reporting capabilities

### Migration Order

1. **website_https.yml and poodle_fix.yml** (low risk, already in Ansible format)
   - No migration needed, these are already Ansible playbooks
   - Just review and optimize according to current Ansible best practices

2. **InSpec Tests** (moderate complexity)
   - Convert ssh_profile.rb and website_https_verify.rb to Ansible-compatible tests
   - Update kitchen.yml to use the new testing framework

3. **Chef Automate/Infra Server Setup Scripts** (high complexity)
   - Create Ansible playbooks to replace the bash scripts for setting up automation servers
   - Implement secure credential handling using Ansible Vault

### Assumptions

1. The primary goal is to move completely away from Chef technologies, including InSpec for testing
2. The existing Ansible playbooks are working correctly and don't need functional changes
3. The target environment will continue to be Ubuntu 20.04 or compatible systems
4. The team has experience with Ansible but may need training on Ansible testing frameworks
5. There's no requirement to maintain backward compatibility with Chef InSpec
6. The self-signed certificates are acceptable for the use case, rather than requiring integration with a certificate authority
7. The hardcoded credentials in the setup scripts are for demonstration purposes only and will be properly secured in the production environment