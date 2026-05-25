# MIGRATION FROM CHEF INSPEC AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a combination of Chef InSpec tests and Ansible playbooks that are used together to deploy and validate a secure web server configuration. The migration scope is relatively small, focusing on converting Chef InSpec tests to Ansible's native testing capabilities while preserving the existing Ansible playbooks. The repository also contains Chef Automate and Chef Infra Server deployment scripts that will need to be replaced with Ansible equivalents.

Estimated timeline: 1-2 weeks for a single developer to complete the migration, with minimal complexity due to the limited scope of the repository.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that deploys an Apache web server with HTTPS configuration using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that remediates the POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening, service restart handlers

- **website_https_verify**:
    - Description: Chef InSpec test that validates the HTTPS website deployment
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec control that validates SSH root login is disabled
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, security compliance check with STIG references

- **chef-automate-deploy**:
    - Description: Bash script that deploys Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash with Chef CLI
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deploy**:
    - Description: Bash script that deploys Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash with Chef CLI
    - Key Features: Chef Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and validating with InSpec. Will need to be replaced with Ansible Molecule or another Ansible-native testing framework.
- `index.html`: Static HTML content for the web server. Can be preserved as-is or converted to an Ansible template.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be targeting on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's `assert` module for basic validation
  - Option 2: Implement Molecule for comprehensive testing
  - Option 3: Use ansible-lint for static analysis
  - Option 4: Integrate with pytest-ansible for more complex test scenarios

- **Test Kitchen**: Replace with Ansible Molecule for infrastructure testing

- **Chef Automate/Infra Server**: Replace deployment scripts with Ansible playbooks that can:
  - Configure system settings (hostname, sysctl parameters)
  - Deploy alternative infrastructure management tools (AWX/Ansible Tower)
  - Set up users and organizations in the new system

### Security Considerations

- **SSL/TLS Configuration**: The current implementation enforces TLSv1.2 and disables SSLv3. This security hardening must be preserved in the Ansible migration.
  - Migration approach: Maintain the same Apache configuration settings in the Ansible playbooks

- **SSH Hardening**: The InSpec test validates that SSH root login is disabled.
  - Migration approach: Create an Ansible task that ensures the same SSH configuration and validates it

- **Self-signed Certificates**: The current implementation generates self-signed certificates.
  - Migration approach: Continue using Ansible's `openssl_*` modules for certificate generation or consider integrating with Let's Encrypt for production environments

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - Count: 2 credential sets detected in deployment scripts

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec's declarative testing syntax to Ansible's procedural approach may require additional logic.
  - Mitigation: Use Ansible's `assert` module with appropriate conditions to match InSpec's expectations

- **Compliance Validation**: The InSpec tests include STIG compliance references and validation.
  - Mitigation: Consider using OpenSCAP with Ansible for compliance validation or implement custom Ansible tasks that perform the same checks

- **Chef Server Replacement**: Determining the appropriate replacement for Chef Server functionality.
  - Mitigation: Evaluate AWX/Ansible Tower or other configuration management databases to replace Chef Server's functionality

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk as they can remain largely unchanged
2. **InSpec Tests** (website_https_verify.rb, ssh_profile.rb): Convert to Ansible-native testing
3. **Test Kitchen Configuration** (kitchen.yml): Replace with Molecule
4. **Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh): Create Ansible playbooks for infrastructure deployment

### Assumptions

1. The primary purpose of this repository is to demonstrate how Chef InSpec can be used alongside Ansible for compliance automation, not for production deployment.
2. The target environment is Ubuntu 20.04 running on Vagrant VMs.
3. The security configurations are examples and may need to be enhanced for production use.
4. The Chef Automate and Chef Infra Server deployment scripts are intended for lab environments, as they contain hardcoded credentials.
5. There is no complex data structure or state management that would require special handling during migration.
6. The repository does not contain actual Chef cookbooks, only InSpec tests used alongside Ansible playbooks.
7. The migration will focus on preserving functionality rather than optimizing the existing code.
8. No external dependencies or integrations beyond what's explicitly defined in the files.