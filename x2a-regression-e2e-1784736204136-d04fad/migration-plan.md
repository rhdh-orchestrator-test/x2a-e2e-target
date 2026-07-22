# MIGRATION FROM ANSIBLE AND CHEF INSPEC TO ANSIBLE

## Executive Summary

This repository contains a mixed environment with Ansible playbooks for configuration management and Chef InSpec for compliance testing, along with bash scripts for Chef Automate/Server deployment. The migration scope involves consolidating these technologies into a pure Ansible solution. After thorough analysis, no traditional Puppet modules (manifests/init.pp), Chef cookbooks (recipes/default.rb), or PowerShell modules (.psd1) were found in this repository. The repository is relatively small with only a few playbooks and test files, making this a low-complexity migration with an estimated timeline of 1-2 weeks.

## Module Migration Plan

This repository contains Ansible playbooks, Chef InSpec tests, and Chef deployment scripts that need individual migration planning:

### MODULE INVENTORY

**CRITICAL PATH VERIFICATION:**
A thorough search was performed using file_search for Puppet modules (manifests/init.pp), Chef cookbooks (recipes/default.rb), and PowerShell modules (.psd1). No traditional modules of these types were found in the repository.

The repository contains the following components that need migration:

- **website_https**:
    - Description: Ansible playbook that configures Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that remediates SSL POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS functionality and port availability
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec test that verifies SSH security configuration (root login disabled)
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, security compliance check

- **chef-automate-deployment**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization setup

- **chef-server-deployment**:
    - Description: Bash script for deploying standalone Chef Infra Server
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization setup

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Will need to be replaced with Ansible Molecule for testing.
- `index.html`: Static HTML content for the website. Can be directly used in Ansible templates.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be targeting on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible's native testing capabilities:
  - For basic tests: Use Ansible's `assert` module and `command`/`shell` modules with `register` and conditional checks
  - For comprehensive testing: Implement Ansible Molecule with testinfra or ansible-test
  - For compliance testing: Consider migrating to OpenSCAP with Ansible integration or Ansible Compliance as Code

- **Test Kitchen**: Replace with Ansible Molecule for testing infrastructure
  - Molecule provides similar functionality for testing Ansible roles and playbooks
  - Can use the same Vagrant driver for local testing

- **Chef Automate/Server**: The deployment scripts suggest this environment was using Chef for infrastructure management
  - Replace with Ansible AWX/Tower for web UI, inventory management, and job scheduling
  - Implement Ansible Collections to organize and distribute Ansible content

### Security Considerations

- **SSL Configuration**: The playbooks handle SSL configuration for Apache
  - Migration should maintain or improve the security posture by using modern TLS configurations
  - Consider using Ansible Vault for storing sensitive information like certificates

- **SSH Hardening**: The InSpec tests verify SSH security configurations
  - Implement equivalent checks using Ansible's `assert` module or Molecule with testinfra
  - Consider using the `ansible.posix.sshd` module for managing SSH configuration

- **Vault/secrets management**:
  - No explicit secrets management was found in the repository
  - The Chef deployment scripts contain hardcoded passwords that should be moved to Ansible Vault
  - Credentials detected: 1 user password in each deployment script

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible assertions or testinfra
  - Mitigation: Create a mapping of InSpec resources to equivalent Ansible modules or testinfra methods
  - Example: InSpec's `describe port(443)` can be replaced with testinfra's `host.socket("tcp://0.0.0.0:443").is_listening`

- **Chef Automate Deployment**: Replacing Chef Automate deployment with Ansible AWX/Tower
  - Mitigation: Create Ansible playbooks to deploy AWX/Tower with similar functionality
  - Consider containerized deployment using Docker or Kubernetes

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk as they're already in Ansible format, just need review and potential refactoring
2. **InSpec Tests** (website_https_verify.rb, ssh_profile.rb): Convert to Ansible-native testing solutions
3. **Chef Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh): Replace with Ansible playbooks for deploying Ansible AWX/Tower

### Assumptions

1. The repository is primarily used for demonstration purposes rather than production, based on the README indicating it's for "examples" and "content created by Technical Product Marketing."
2. The Chef InSpec tests are used for compliance validation of infrastructure configured by Ansible, suggesting a hybrid approach.
3. The Chef Automate and Chef Server deployment scripts may be used in a separate environment and are not directly related to the Ansible playbooks.
4. The hardcoded credentials in deployment scripts are for demonstration purposes and not used in production environments.
5. The Test Kitchen configuration suggests this is a development/testing environment rather than production.
6. No complex data structures or external dependencies are used in the Ansible playbooks, making migration straightforward.