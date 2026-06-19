# MIGRATION FROM CHEF INSPEC AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together for compliance automation. The primary focus is on using Chef InSpec for compliance testing alongside Ansible for configuration management. The migration scope is relatively small, as most of the configuration is already in Ansible format. The main migration effort will involve replacing Chef InSpec tests with Ansible-native testing solutions.

**Estimated Timeline**: 1-2 weeks
**Complexity**: Low to Medium
**Primary Focus**: Converting InSpec tests to Ansible-compatible testing frameworks

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
    - Key Features: Disables SSLv3 and enables only TLSv1.2 in Apache configuration

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response verification, SSL protocol security verification

- **ssh_profile**:
    - Description: Chef InSpec control that verifies SSH root login is disabled for security compliance
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration verification, security compliance check with STIG references

- **chef-automate-deployment**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh, setup-automate/deploy-chef-server.sh
    - Technology: Bash scripts
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization setup

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Will need to be replaced with Ansible-native testing framework configuration.
- `index.html`: Simple HTML file used for testing web server functionality. Can be reused as-is.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Molecule for Ansible role testing
  - Option 2: Ansible Test for integration testing
  - Option 3: Ansible Lint for static code analysis
  - Option 4: Consider using pytest-ansible for Python-based testing

- **Test Kitchen**: Replace with Molecule for Ansible role testing, which provides similar functionality but is designed specifically for Ansible.

- **Chef Automate/Infra Server**: The deployment scripts need to be converted to Ansible playbooks. Consider using:
  - Ansible roles for modular deployment
  - Ansible Vault for secure credential storage
  - Ansible Tower/AWX as a replacement for Chef Automate's functionality

### Security Considerations

- **SSL Configuration**: The current implementation configures Apache with SSL and disables vulnerable protocols. This security hardening should be maintained in the Ansible migration.
  - Migration approach: Create an Ansible role for Apache SSL configuration that enforces TLSv1.2+ and disables older protocols.

- **SSH Security**: The InSpec test verifies SSH root login is disabled. This security check should be maintained.
  - Migration approach: Create an Ansible role that configures SSH securely and use Ansible's assert module or Molecule to verify compliance.

- **Self-signed Certificates**: The current implementation generates self-signed certificates. Consider enhancing security by:
  - Migration approach: Add support for Let's Encrypt certificates using Ansible's acme_certificate module.

- **Vault/secrets management**: 
  - Hardcoded credentials in setup-automate scripts (username, password)
  - Migration approach: Move credentials to Ansible Vault

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible-native testing frameworks will require understanding the equivalent assertions and checks.
  - Mitigation: Create a mapping of InSpec resources to Ansible modules and assertions.

- **Compliance Reporting**: If Chef InSpec is being used for compliance reporting, an alternative solution will be needed.
  - Mitigation: Consider using OpenSCAP with Ansible, or implementing custom reporting using Ansible facts and a reporting database.

- **Chef Automate Functionality**: If Chef Automate is being used for features beyond compliance testing, equivalent functionality will need to be identified in the Ansible ecosystem.
  - Mitigation: Evaluate Ansible Tower/AWX as a replacement for Chef Automate's dashboard and reporting capabilities.

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): These are already in Ansible format and require minimal changes.
   - Review and optimize according to current Ansible best practices
   - Update any deprecated syntax or modules

2. **InSpec Tests** (website_https_verify.rb, ssh_profile.rb): Convert to Ansible-native testing solutions.
   - Create equivalent tests using Molecule or pytest-ansible
   - Ensure all compliance checks are maintained

3. **Chef Automate/Infra Server Deployment** (deploy-automate.sh, deploy-chef-server.sh): Convert to Ansible playbooks.
   - Create roles for Chef server deployment if still needed
   - Consider migrating to Ansible Tower/AWX instead of Chef Automate

4. **Testing Infrastructure** (kitchen.yml): Replace with Molecule configuration.
   - Set up equivalent test environments
   - Configure CI/CD integration

### Assumptions

1. The primary purpose of this repository is to demonstrate how Chef InSpec can be used alongside Ansible for compliance automation, rather than being a production deployment.

2. The Chef Automate and Chef Infra Server deployment scripts are examples and may not be actively used in the current workflow.

3. The security compliance requirements (such as STIG references in the SSH profile) need to be maintained in the Ansible migration.

4. The target environment is Ubuntu 20.04 running on Vagrant VMs, but the solution should be adaptable to other environments.

5. There is no complex data management or state handling that would require special migration considerations.

6. The current implementation uses self-signed certificates for demonstration purposes, but a production migration might require integration with a certificate authority.

7. The repository appears to be a demonstration or educational resource rather than a production system, based on the README content and simple examples.