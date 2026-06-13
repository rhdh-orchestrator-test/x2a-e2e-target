# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation. The primary focus is on using Chef InSpec for compliance testing alongside Ansible for configuration management. The repository also includes shell scripts for deploying Chef Automate and Chef Infra Server.

The migration scope is relatively small, as most of the configuration is already in Ansible format. The main migration effort will involve:
1. Converting Chef InSpec tests to Ansible-compatible testing frameworks
2. Adapting the Chef Automate/Infra Server deployment scripts to Ansible playbooks
3. Ensuring the existing Ansible playbooks follow best practices

**Estimated Timeline**: 1-2 weeks for a small team (1-2 engineers)
**Complexity**: Low to Medium

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
    - Description: Chef InSpec test that verifies HTTPS configuration on a web server
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec test that verifies SSH server security configuration
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login check, compliance with security standards (STIG)

- **chef-automate-deployment**:
    - Description: Bash script that deploys Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash
    - Key Features: System configuration, Chef Automate installation, user and organization creation

- **chef-server-deployment**:
    - Description: Bash script that deploys Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash
    - Key Features: System configuration, Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Migration considerations include replacing with Ansible-native testing frameworks like Molecule.
- `index.html`: Simple HTML file used for testing web server configuration. Can be directly incorporated into Ansible playbooks.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-compatible testing frameworks:
  - Option 1: Use Ansible's built-in `assert` module for basic testing
  - Option 2: Use Molecule for more comprehensive testing
  - Option 3: Integrate with other testing frameworks like Serverspec or Testinfra

- **Test Kitchen**: Replace with Molecule for testing Ansible roles and playbooks

- **Chef Automate/Infra Server**: Replace deployment scripts with Ansible playbooks that:
  - Configure system parameters (hostname, sysctl)
  - Install and configure alternative compliance and infrastructure management tools

### Security Considerations

- **SSL/TLS Configuration**: The migration must maintain the security improvements in the poodle_fix.yml playbook, ensuring only secure protocols are enabled.
  - Migration approach: Preserve the same configuration in the Ansible playbooks

- **SSH Security**: The SSH security tests in ssh_profile.rb need to be converted to equivalent Ansible tests.
  - Migration approach: Create Ansible tasks that verify the same SSH configuration parameters

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - Self-signed certificates should be managed securely
  - Count of credentials detected: 
    - chef-automate-deployment: 3 (username, useremail, userpassword)
    - chef-server-deployment: 3 (username, useremail, userpassword)

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible-compatible testing frameworks will require understanding the equivalent assertions and checks.
  - Mitigation strategy: Create a mapping of InSpec resources to Ansible modules and gradually convert each test.

- **Chef Automate Replacement**: Determining the appropriate replacement for Chef Automate functionality.
  - Mitigation strategy: Evaluate alternatives like AWX/Ansible Tower for infrastructure management and compliance tools like OpenSCAP for compliance testing.

### Migration Order

1. **Existing Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk, already in Ansible format, may need refactoring to follow best practices
2. **InSpec Tests** (website_https_verify.rb, ssh_profile.rb): Medium complexity, requires conversion to Ansible-compatible testing
3. **Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh): High complexity, requires replacing Chef-specific functionality

### Assumptions

1. The primary goal is to move all configuration and testing to Ansible, eliminating dependencies on Chef products.
2. The existing Ansible playbooks are functional and can be used as a reference for the migration.
3. The target environment will continue to be Ubuntu 20.04 or compatible systems.
4. The deployment scripts are used for setting up test environments and not production systems.
5. The hardcoded credentials in the deployment scripts are for demonstration purposes and not used in production.
6. The InSpec tests are used for compliance validation and not for continuous integration/deployment.
7. The migration will maintain the same level of security and compliance checking as the original implementation.
8. There is no requirement to maintain backward compatibility with Chef InSpec or Chef Automate.