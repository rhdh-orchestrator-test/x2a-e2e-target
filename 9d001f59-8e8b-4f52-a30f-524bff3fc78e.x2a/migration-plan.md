# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used for compliance automation and server configuration. The primary focus appears to be demonstrating how Chef InSpec can be used alongside Ansible for compliance testing. Additionally, there are shell scripts for deploying Chef Automate and Chef Infra Server.

The migration scope is relatively small, as most of the Ansible playbooks are already in place. The main migration effort will involve:
1. Converting Chef InSpec tests to Ansible-native testing solutions
2. Migrating Chef Automate/Infra Server deployment scripts to Ansible playbooks

**Estimated Timeline**: 1-2 weeks for a small team (1-2 engineers)
**Complexity**: Low to Medium

## Module Migration Plan

This repository contains a mix of technologies that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: SSL protocol configuration, service restart handlers

- **chef-automate-deploy**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deploy**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash
    - Key Features: Chef Infra Server installation, user and organization creation

- **website_https_verify**:
    - Description: Chef InSpec test profile for verifying HTTPS configuration
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response verification, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec test profile for verifying SSH security configuration
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login verification, compliance with security standards

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration file that uses Ansible as the provisioner and InSpec as the verifier. Used for testing the website_https playbook.
- `index.html`: HTML file in the chef-and-ansible directory, likely a static file for the web server.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (used in kitchen.yml)
- **Cloud Platform**: Not specified, but the deployment scripts are designed to work on both on-premises and cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's `assert` module for basic testing
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Use ansible-lint for static analysis
  - Option 4: Consider using the Ansible `community.general.inspec` module to continue using InSpec tests

- **Test Kitchen**: Replace with:
  - Option 1: Molecule for Ansible role/playbook testing
  - Option 2: Continue using Test Kitchen with the `kitchen-ansible` plugin

### Security Considerations

- **SSL Configuration**: The playbooks configure SSL for Apache. Ensure that:
  - The SSL protocols are updated to current security standards (TLS 1.3 support)
  - Self-signed certificates are replaced with proper CA-signed certificates in production
  - The SSL configuration is regularly tested for vulnerabilities

- **SSH Security**: The InSpec tests verify SSH security configurations. Ensure:
  - SSH root login remains disabled
  - SSH protocol and cipher configurations meet current security standards
  - SSH key-based authentication is enforced where appropriate

- **Vault/secrets management**:
  - Hardcoded credentials in the deployment scripts (username, password) should be moved to Ansible Vault
  - Count: 2 sets of credentials in deploy-automate.sh and deploy-chef-server.sh

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible-native testing solutions may require different approaches for different test types:
  - For simple state verification, Ansible's `assert` module can be used
  - For more complex compliance testing, a combination of Ansible modules or external tools may be needed
  - Migration strategy: Create equivalent Ansible tasks for each InSpec control, focusing on maintaining the same level of validation

- **Chef Automate/Server Deployment**: Converting the deployment scripts to Ansible playbooks:
  - Challenge: Ensuring idempotence in the deployment process
  - Challenge: Handling the Chef server API interactions for user and organization creation
  - Migration strategy: Create roles for Chef server and Automate deployment, with separate tasks for installation, configuration, and user management

### Migration Order

1. **InSpec Tests** (Priority 1, low risk):
   - Convert InSpec tests to Ansible assertions or Molecule tests
   - This allows for testing the existing Ansible playbooks with the new testing framework

2. **Chef Deployment Scripts** (Priority 2, moderate complexity):
   - Convert the bash scripts to Ansible playbooks
   - Create roles for Chef server and Automate deployment
   - Implement Ansible Vault for credential management

3. **Test Kitchen Configuration** (Priority 3, low complexity):
   - Replace Test Kitchen with Molecule or update the existing configuration to work with the new testing framework

### Assumptions

1. The repository is primarily used for demonstration purposes rather than production deployment, as indicated by the README.md mentioning "working examples" and "companion to a white paper".

2. The Chef InSpec tests are used to validate configurations managed by Ansible, not Chef-managed resources.

3. The deployment scripts are used for setting up test environments, not production deployments, given the hardcoded credentials.

4. The target environment is Ubuntu 20.04 as specified in the kitchen.yml file, though the deployment scripts might be used on other distributions.

5. The migration to Ansible is focused on standardizing on a single configuration management tool rather than addressing specific functional limitations.

6. The current setup uses Test Kitchen for testing, which will need to be replaced or reconfigured to work with the migrated Ansible content.