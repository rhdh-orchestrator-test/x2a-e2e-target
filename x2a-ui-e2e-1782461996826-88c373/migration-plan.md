# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation. The primary focus appears to be showing how Chef InSpec can be used alongside Ansible for compliance testing. Additionally, there are Chef Automate and Chef Infra Server deployment scripts. The migration scope is relatively small, with only a few Ansible playbooks and InSpec tests to migrate. The estimated timeline for migration is 1-2 weeks, with low complexity for the Ansible components (which are already in Ansible format) and medium complexity for converting the InSpec tests to Ansible-compatible testing frameworks.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables SSLv3 and enables only TLSv1.2 in Apache configuration

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec control that verifies SSH root login is disabled for security compliance
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, security compliance check with STIG references

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

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Migration considerations include replacing with Ansible-native testing frameworks like Molecule.
- `index.html`: Simple HTML file used as a test page. No migration considerations needed.

### Target Details

Analyze the source repository to determine target environment specifications:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-compatible testing frameworks:
  - Option 1: Use Ansible's built-in `assert` module for basic testing
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Use pytest-ansible for Python-based testing
  - Option 4: Consider maintaining InSpec as a separate testing tool that can work with Ansible

- **Test Kitchen**: Replace with Molecule for Ansible role and playbook testing

### Security Considerations

- **SSL Configuration**: The migration must maintain the security hardening in the poodle_fix.yml playbook
  - Ensure TLSv1.2 is enforced and SSLv3 is disabled
  - Maintain proper certificate generation and configuration

- **SSH Security**: Maintain the SSH root login restrictions as verified by the InSpec test
  - Implement equivalent checks in Ansible or alternative testing framework

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be migrated to Ansible Vault
  - Self-signed certificates should be managed securely

### Technical Challenges

- **InSpec Test Conversion**: Converting InSpec tests to Ansible-compatible testing frameworks
  - Challenge: InSpec has specific resource types (like `ssl`, `port`, `http`) that need equivalent implementations
  - Mitigation: Map InSpec resources to Ansible modules or use Python-based testing with pytest-ansible

- **Chef Automate/Server Deployment**: Converting Chef server deployment scripts to Ansible
  - Challenge: Determining if Chef infrastructure is still needed or should be replaced
  - Mitigation: If Chef is being completely replaced, create Ansible playbooks for deploying alternative compliance and configuration management tools

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk as they are already in Ansible format, may need minor updates for best practices
2. **Testing Framework**: Implement Molecule or alternative testing framework to replace Test Kitchen
3. **InSpec Tests**: Convert InSpec tests to the chosen testing framework
4. **Deployment Scripts**: Convert Chef Automate/Server deployment scripts to Ansible playbooks if Chef infrastructure is being replaced

### Assumptions

1. The primary goal is to migrate all components to Ansible, including replacing Chef InSpec with Ansible-compatible testing
2. The Chef Automate and Chef Infra Server deployment scripts are intended to be replaced with Ansible equivalents
3. The target environment will continue to be Ubuntu 20.04 or compatible Linux distributions
4. The security requirements (SSL configuration, SSH hardening) must be maintained in the migrated solution
5. The repository is primarily for demonstration/educational purposes rather than production use
6. No external dependencies or integrations beyond what's visible in the repository need to be considered