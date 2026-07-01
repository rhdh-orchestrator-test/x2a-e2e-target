# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation. The migration scope is relatively small, focusing on converting Chef InSpec tests to Ansible-compatible testing frameworks while preserving the existing Ansible playbooks. Additionally, there are Chef Automate and Chef Infra Server deployment scripts that need to be converted to Ansible playbooks.

**Estimated Timeline**: 1-2 weeks for a single developer, considering the limited scope and complexity.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

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

- **inspec_tests**:
    - Description: Chef InSpec tests for verifying HTTPS website functionality and SSH security compliance
    - Path: chef-and-ansible/tests/
    - Technology: Chef InSpec
    - Key Features: Port listening checks, HTTPS content verification, SSL protocol verification, SSH configuration compliance

- **chef_automate_deployment**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization creation

- **chef_server_deployment**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Will need to be replaced with Ansible-specific testing framework configuration.
- `index.html`: Sample HTML file used for testing the web server setup.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be targeting on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec (latest)**: Replace with Ansible-native testing solutions:
  - Option 1: Ansible Molecule with Testinfra for infrastructure testing
  - Option 2: Convert InSpec tests to Ansible assert tasks
  - Option 3: Use community.general.inspec module to continue using InSpec tests from Ansible

- **Test Kitchen (latest)**: Replace with Ansible Molecule for testing infrastructure

- **Chef Automate/Infra Server**: Replace with:
  - Ansible AWX/Tower for web UI and job scheduling
  - GitLab CI/Jenkins for pipeline integration
  - Compliance scanning can be handled by OpenSCAP integrated with Ansible

### Security Considerations

- **SSL Configuration**: The playbooks configure SSL for Apache. Ensure the migration preserves the security settings:
  - Disable vulnerable protocols (SSLv3)
  - Enable only TLSv1.2 or higher
  - Maintain proper certificate generation and deployment

- **SSH Hardening**: The InSpec tests verify SSH root login is disabled. Ensure this security check is preserved in the Ansible testing framework.

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - Self-signed certificates are generated in the playbook and should be handled securely

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to an Ansible-compatible testing framework will require understanding the test logic and implementing equivalent checks.
  - Mitigation: Use Ansible's assert module or Molecule with Testinfra to implement similar tests.

- **Chef Server Deployment**: The Chef server deployment scripts need to be converted to Ansible playbooks.
  - Mitigation: Create equivalent Ansible roles for setting up Ansible AWX/Tower as a replacement for Chef Automate/Server.

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk as they are already in Ansible format. Only need to be reviewed and potentially updated to follow best practices.

2. **InSpec Tests**: Convert to Ansible-compatible testing framework. This is moderate complexity but essential for maintaining compliance verification.

3. **Chef Deployment Scripts**: Highest complexity, as they involve replacing Chef Automate/Server functionality with Ansible equivalents.

### Assumptions

1. The primary purpose of this repository is to demonstrate how Chef InSpec can be used alongside Ansible for compliance automation, as indicated in the README.

2. The existing Ansible playbooks (website_https.yml, poodle_fix.yml) are working correctly and don't need functional changes, just potential refactoring to follow best practices.

3. There's no direct dependency on Chef Infra for configuration management, only on InSpec for testing and Chef Automate/Server for deployment.

4. The target environment is Ubuntu 20.04 running on Vagrant VMs for testing purposes.

5. The hardcoded credentials in the deployment scripts are for demonstration purposes and will be replaced with secure credential management in the production environment.

6. The self-signed certificates generated in the playbooks are for testing purposes and would be replaced with proper certificates in a production environment.