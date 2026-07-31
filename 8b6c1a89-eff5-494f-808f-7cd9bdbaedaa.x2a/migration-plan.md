# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used for compliance automation. The primary focus appears to be demonstrating how Chef InSpec can be used alongside Ansible for compliance testing. Additionally, there are setup scripts for Chef Automate and Chef Infra Server deployment.

The migration scope is relatively small, as most of the content is already in Ansible format. The main migration tasks will involve:
1. Converting Chef InSpec tests to Ansible-native testing solutions
2. Adapting the Chef Automate/Infra Server setup scripts to Ansible playbooks

**Estimated Timeline**: 1-2 weeks for a small team (1-2 engineers)
**Complexity**: Low to Medium

## Module Migration Plan

This repository contains a mix of Ansible playbooks and Chef InSpec tests that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: SSL protocol configuration, service restart handlers

- **chef-automate-setup**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate deployment, user and organization creation

- **chef-server-setup**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Infra Server deployment, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests
- `tests/website_https_verify.rb`: InSpec test for verifying HTTPS configuration
- `tests/ssh_profile.rb`: InSpec test for verifying SSH security configuration

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (used in Test Kitchen configuration)
- **Cloud Platform**: Not specified, appears to be platform-agnostic

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's `assert` module for basic testing
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Use ansible-lint for static analysis
  - Option 4: Consider maintaining InSpec as a separate testing tool if deeply integrated

- **Test Kitchen**: Replace with:
  - Molecule for Ansible role/playbook testing
  - Consider keeping Test Kitchen if it's preferred for multi-platform testing

### Security Considerations

- **SSL Configuration**: The playbooks configure SSL for Apache with specific security settings:
  - Ensure TLS 1.2 is enabled and older protocols are disabled
  - Maintain the same security posture in the migrated Ansible playbooks

- **SSH Security**: The InSpec tests verify SSH root login is disabled:
  - Ensure this security check is maintained in the Ansible testing framework

- **Credentials in Scripts**: The setup scripts contain hardcoded credentials:
  - Migrate these to Ansible Vault for secure storage
  - Count: 2 credential sets (username/password) in deploy-automate.sh and deploy-chef-server.sh

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible-native testing:
  - InSpec provides a domain-specific language for compliance testing
  - Ansible's testing capabilities are more general-purpose
  - Mitigation: Use a combination of Ansible assert, custom modules, and external tools like Molecule

- **Chef Automate/Server Setup**: Converting the Chef server setup scripts to Ansible:
  - The scripts use Chef-specific CLI tools
  - Mitigation: Create Ansible roles that either call these CLI tools or use API calls to achieve the same functionality

### Migration Order

1. **website_https.yml** (already in Ansible format, low risk)
2. **poodle_fix.yml** (already in Ansible format, low risk)
3. **InSpec Tests** (moderate complexity, requires testing framework decisions)
4. **Chef Server Setup Scripts** (higher complexity, requires understanding of Chef server deployment)

### Assumptions

1. The primary goal is to standardize on Ansible as the configuration management tool
2. Chef InSpec tests need to be converted to Ansible-native testing solutions
3. The Chef Automate and Chef Infra Server setup scripts are still needed (rather than being replaced by a different solution)
4. The target environment will remain Ubuntu 20.04 or compatible
5. Vagrant will continue to be used for development/testing environments
6. The security requirements (SSL/SSH configurations) must be maintained
7. The repository is primarily for demonstration/educational purposes rather than production use