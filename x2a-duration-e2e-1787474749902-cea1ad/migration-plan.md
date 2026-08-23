# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used for compliance automation and server configuration. The repository appears to be a demonstration or example repository showing how Chef InSpec can be used alongside Ansible for compliance testing. Additionally, there are bash scripts for deploying Chef Automate and Chef Infra Server.

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
    - Key Features: SSL protocol configuration, service restart

- **ssh_profile**:
    - Description: Chef InSpec test that verifies SSH root login is disabled
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration testing, compliance verification

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

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Will need to be updated to use Ansible-native testing frameworks.
- `chef-and-ansible/index.html`: Static HTML file, can be directly used in Ansible.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be targeting on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-compatible testing frameworks:
  - Option 1: Use Ansible's built-in `assert` module for basic testing
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Use the Ansible `command` module to run external testing tools

- **Test Kitchen**: Replace with:
  - Molecule for Ansible role testing
  - Ansible's built-in testing capabilities

- **Chef Automate/Infra Server**: Replace deployment scripts with:
  - Ansible playbooks that perform the same server setup
  - Consider using Ansible AWX/Tower as a replacement for Chef Automate's functionality

### Security Considerations

- **SSL Configuration**: The playbooks configure SSL for Apache. Ensure proper SSL/TLS protocols are maintained in the migrated Ansible playbooks.
  - Migration approach: Maintain the same SSL configuration parameters in the Ansible tasks.

- **SSH Security**: The InSpec tests verify SSH root login is disabled. Ensure this compliance check is maintained.
  - Migration approach: Convert InSpec test to Ansible assert or use ansible-lint for SSH configuration validation.

- **Self-signed Certificates**: The playbooks generate self-signed certificates. Consider implementing proper certificate management.
  - Migration approach: Use Ansible's `openssl_*` modules (already in use) but consider integrating with a certificate authority for production.

- **Vault/secrets management**: 
  - Hardcoded credentials in the Chef Automate/Infra Server deployment scripts need to be moved to Ansible Vault.
  - Count: 2 credential sets (username/password) in the deployment scripts.

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible-compatible testing frameworks may require different approaches for different test types.
  - Mitigation: Use a combination of Ansible's assert module, Molecule, and external testing tools as appropriate.

- **Maintaining Compliance Automation**: The repository demonstrates compliance automation with InSpec. Ensuring this capability is maintained in an Ansible-only environment.
  - Mitigation: Implement a comprehensive testing strategy using Ansible's native capabilities or integrate with external compliance tools.

- **Chef Automate Functionality**: If Chef Automate is being used for features beyond what's shown in the deployment scripts, additional Ansible components may be needed.
  - Mitigation: Evaluate all Chef Automate use cases and map to appropriate Ansible solutions (e.g., AWX/Tower, custom dashboards).

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): These are already in Ansible format and require minimal changes, mainly to improve practices and remove any Chef-specific references.

2. **Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh): Convert these bash scripts to Ansible playbooks, implementing proper variable handling with Ansible Vault for credentials.

3. **InSpec Tests** (ssh_profile.rb, website_https_verify.rb): Convert these to Ansible-compatible testing frameworks, ensuring all compliance checks are maintained.

4. **Infrastructure Files** (kitchen.yml): Replace with Ansible-native testing configuration.

### Assumptions

1. The repository is primarily for demonstration purposes, showing how Chef InSpec can work alongside Ansible, rather than a production deployment.

2. The Chef Automate and Chef Infra Server deployment scripts are intended to be replaced entirely, not integrated with Ansible.

3. The compliance testing functionality provided by InSpec is a critical requirement that must be maintained in the Ansible migration.

4. The target environment will continue to be Ubuntu 20.04 or compatible systems.

5. There are no external dependencies or integrations beyond what's visible in the repository.

6. The migration will maintain the same level of security and compliance checking currently implemented.