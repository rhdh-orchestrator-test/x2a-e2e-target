# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used for compliance automation and server configuration. The repository appears to be a demonstration or example repository showing how Chef InSpec can be used alongside Ansible for compliance testing. There are also bash scripts for deploying Chef Automate and Chef Infra Server.

The migration scope is relatively small, as most of the Ansible components are already in place. The primary focus will be on:
1. Converting Chef InSpec tests to Ansible-compatible testing frameworks
2. Ensuring the Chef Automate/Infra Server deployment scripts are replaced with Ansible playbooks
3. Maintaining the compliance testing capabilities while fully migrating to Ansible

**Estimated Timeline**: 1-2 weeks for a complete migration, with minimal complexity due to the small codebase and limited dependencies.

## Module Migration Plan

This repository contains a mix of Ansible playbooks and Chef InSpec tests that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables vulnerable SSL protocols, enables TLSv1.2

- **ssh_profile**:
    - Description: Chef InSpec test that verifies SSH root login is disabled
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration compliance testing

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS configuration on a web server
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response verification, SSL protocol verification

- **chef-automate-deploy**:
    - Description: Bash script to deploy Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deploy**:
    - Description: Bash script to deploy Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration file that uses Ansible as the provisioner and InSpec as the verifier. Will need to be updated to use Ansible-native testing frameworks.
- `chef-and-ansible/index.html`: Simple HTML file used as a test page for the web server configuration.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-compatible testing frameworks:
  - Option 1: Use Ansible's built-in `assert` module for basic testing
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Use pytest-ansible for Python-based testing

- **Test Kitchen**: Replace with:
  - Molecule for Ansible role testing
  - Or continue using Test Kitchen with the Ansible provisioner but replace InSpec verifier

- **Chef Automate/Infra Server**: Replace deployment scripts with:
  - Ansible playbooks that perform the same server setup
  - Consider using Ansible AWX or Tower as a replacement for Chef Automate's functionality

### Security Considerations

- **SSL Configuration**: The playbooks configure SSL for Apache. Ensure the migration maintains:
  - Proper TLS protocol settings (TLSv1.2 enabled, older protocols disabled)
  - Self-signed certificate generation (currently using openssl_* modules)
  - Appropriate file permissions for certificates (mode 0640)

- **SSH Hardening**: The InSpec tests verify SSH root login is disabled. Ensure:
  - Equivalent tests are implemented in the Ansible testing framework
  - SSH configuration is properly managed in the migrated solution

- **Credentials Management**: The deployment scripts contain hardcoded credentials:
  - Replace with Ansible Vault for secure credential storage
  - Remove hardcoded passwords (e.g., 'password' in the deployment scripts)
  - Document the count and type of credentials detected per module:
    - chef-automate-deploy: 1 password
    - chef-server-deploy: 1 password

### Technical Challenges

- **Testing Framework Transition**: Moving from InSpec to Ansible-native testing:
  - Challenge: InSpec provides a domain-specific language for compliance testing that is more expressive than Ansible's built-in testing capabilities
  - Mitigation: Use a combination of Ansible assert modules and custom modules or external testing frameworks like Molecule

- **Maintaining Compliance Automation**: Ensuring the same level of compliance testing:
  - Challenge: The repository demonstrates compliance automation with InSpec, which needs to be preserved in an Ansible-only solution
  - Mitigation: Implement equivalent tests using Ansible's testing capabilities or integrate with compliance tools that work with Ansible

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): These are already in Ansible format and require minimal changes, mainly to improve security practices and remove any Chef-specific references.

2. **InSpec Tests** (ssh_profile.rb, website_https_verify.rb): Convert these to Ansible-compatible testing frameworks. This is a higher priority as it represents the core compliance functionality.

3. **Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh): Replace these with Ansible playbooks that perform equivalent server setup. This is the lowest priority as it's related to setting up Chef infrastructure that will be replaced.

### Assumptions

1. The repository is primarily for demonstration purposes showing how Chef InSpec can work alongside Ansible, rather than a production infrastructure repository.

2. The target environment is Ubuntu 20.04 running on Vagrant VMs, but the solution should be adaptable to other environments.

3. There is no complex data structure or state management that would require special handling during migration.

4. The compliance testing functionality is the most important aspect to preserve during migration.

5. No external Chef cookbooks or complex Chef-specific features are being used that would require significant re-architecture.

6. The deployment scripts are for setting up Chef infrastructure, which would be replaced by Ansible infrastructure in the migrated solution.