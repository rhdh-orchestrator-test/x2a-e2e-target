# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation. The migration scope is relatively small, focusing on converting Chef InSpec tests to Ansible-compatible testing frameworks while preserving the existing Ansible playbooks. Additionally, there are Chef server deployment scripts that need to be converted to Ansible playbooks. The estimated timeline for this migration is 1-2 weeks given the limited scope and complexity.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL vulnerabilities in Apache by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening, service restart handlers

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS functionality and security compliance
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol security verification

- **ssh_profile**:
    - Description: Chef InSpec control that verifies SSH root login is disabled for security compliance
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, security compliance check with STIG references

- **chef-server-deployment**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh, setup-automate/deploy-chef-server.sh
    - Technology: Bash scripts
    - Key Features: Chef server installation, user and organization creation, system configuration

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Migration considerations include replacing with Ansible-native testing frameworks like Molecule.
- `index.html`: Simple HTML file used for testing web server functionality. No migration needed as it's a static asset.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be infrastructure-agnostic

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec (latest)**: Replace with Ansible-compatible testing frameworks:
  - Option 1: Use Ansible's built-in `assert` module for basic testing
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Use pytest-ansible for Python-based testing
  - Option 4: Keep InSpec but invoke it from Ansible using the `command` or `shell` module

- **Test Kitchen (latest)**: Replace with Molecule for Ansible role testing

- **Chef Automate/Infra Server**: Replace deployment scripts with Ansible roles for:
  - Option 1: Deploy alternative configuration management solution
  - Option 2: Deploy Chef server using Ansible for organizations that want to maintain Chef infrastructure

### Security Considerations

- **SSL Configuration**: The migration must preserve the security hardening in the poodle_fix.yml playbook
  - Maintain TLSv1.2 requirement and disable insecure protocols
  - Ensure proper certificate generation and management

- **SSH Hardening**: Preserve the SSH security controls from the InSpec profile
  - Ensure PermitRootLogin is properly configured
  - Maintain compliance with referenced security standards (STIG)

- **Vault/secrets management**:
  - Hardcoded credentials in setup-automate scripts (username, password) should be moved to Ansible Vault
  - SSL certificates should be managed securely, potentially using ansible-vault for private keys

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible-compatible testing frameworks will require careful mapping of InSpec resources to Ansible modules
  - Challenge: InSpec's declarative testing style differs from Ansible's procedural approach
  - Mitigation: Use Ansible assert module with appropriate conditionals or maintain InSpec as a separate tool called from Ansible

- **Test Kitchen to Molecule**: Converting the test infrastructure will require reconfiguring test scenarios
  - Challenge: Ensuring test coverage remains consistent across frameworks
  - Mitigation: Create equivalent Molecule scenarios that match the existing Test Kitchen configuration

- **Chef Server Deployment**: Converting bash scripts to idempotent Ansible playbooks
  - Challenge: Ensuring proper error handling and idempotence
  - Mitigation: Use Ansible's built-in idempotence features and appropriate conditionals

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk as they are already in Ansible format, may need minor adjustments for best practices
2. **Testing Framework**: Convert from Test Kitchen to Molecule
3. **InSpec Tests**: Convert InSpec tests to Ansible-compatible testing
4. **Chef Server Deployment Scripts**: Convert bash scripts to Ansible playbooks

### Assumptions

1. The existing Ansible playbooks (website_https.yml, poodle_fix.yml) are working correctly and don't require functional changes
2. The organization is fully migrating away from Chef and doesn't need to maintain Chef-specific functionality
3. The security compliance requirements represented in the InSpec tests must be maintained in the Ansible solution
4. The target environment will continue to be Ubuntu 20.04 or compatible systems
5. The deployment scripts are currently used for setting up development/test environments and not production systems
6. No external data sources or integrations are present beyond what's visible in the repository
7. The hardcoded credentials in the deployment scripts are not used in production environments