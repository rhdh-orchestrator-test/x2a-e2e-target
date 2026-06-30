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
    - Description: Ansible playbook that fixes SSL vulnerabilities in Apache by disabling older protocols
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening, service restart handlers

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol security verification

- **ssh_profile**:
    - Description: Chef InSpec test that verifies SSH security configuration
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login security check, compliance with security standards (STIG)

- **chef-automate-deployment**:
    - Description: Bash script that deploys Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization setup

- **chef-server-deployment**:
    - Description: Bash script that deploys Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization setup

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Will need to be replaced with Ansible-native testing framework configuration.
- `index.html`: Simple HTML file used for testing web server functionality. Can be preserved as-is or incorporated into Ansible content.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be infrastructure-agnostic

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-compatible testing frameworks:
  - Option 1: Use Ansible's built-in `assert` module for basic testing
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Use pytest-ansible for Python-based testing
  - Option 4: Maintain InSpec but invoke it from Ansible using the `command` or `shell` module

- **Test Kitchen**: Replace with:
  - Option 1: Molecule for Ansible role testing
  - Option 2: Ansible's own testing framework

- **Chef Server/Automate**: Replace with:
  - Option 1: Ansible AWX/Tower for enterprise automation
  - Option 2: GitLab CI/CD with Ansible for automation pipelines

### Security Considerations

- **SSL Configuration**: The playbooks handle SSL configuration for Apache. Migration should preserve the security hardening that disables vulnerable protocols.
  - Migration approach: Preserve the existing Ansible tasks that configure SSL protocols

- **SSH Security**: The InSpec tests verify SSH security configurations.
  - Migration approach: Convert InSpec tests to Ansible assert statements or Molecule tests that verify the same SSH security controls

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts: The Chef deployment scripts contain hardcoded passwords that should be moved to Ansible Vault
  - SSL certificate handling: Self-signed certificates are generated in the playbook; consider using Ansible Vault for storing pre-generated certificates in production environments
  - Document the count and type of credentials detected per module:
    - chef-automate-deployment: 1 password (userpassword variable)
    - chef-server-deployment: 1 password (userpassword variable)

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec's declarative testing syntax to Ansible's procedural approach may require additional logic.
  - Mitigation: Consider using Ansible's assert module with appropriate conditionals to replicate InSpec's behavior, or maintain InSpec as a separate tool called from Ansible.

- **Chef Server Deployment**: Replacing Chef Server deployment scripts with Ansible requires understanding of Chef Server architecture.
  - Mitigation: Create Ansible roles that replicate the Chef Server deployment steps, potentially using the `uri` module to interact with Chef Server APIs.

### Migration Order

1. **Existing Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk as they're already in Ansible format; only need review and potential refactoring to follow best practices.

2. **InSpec Tests** (website_https_verify.rb, ssh_profile.rb): Moderate complexity to convert to Ansible-compatible testing.

3. **Chef Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh): Higher complexity as they involve replacing Chef-specific tooling with Ansible alternatives.

### Assumptions

1. The existing Ansible playbooks are functioning correctly and don't require significant changes beyond potential refactoring.

2. The InSpec tests are currently being used for compliance validation and their functionality needs to be preserved.

3. The Chef Server deployment scripts are used for setting up infrastructure that will be managed by Ansible in the future.

4. The target environment will continue to be Ubuntu 20.04 or compatible systems.

5. There are no external dependencies or integrations not visible in the provided files.

6. The hardcoded credentials in the deployment scripts are for demonstration purposes and will be replaced with secure alternatives in production.

7. The migration will maintain the same level of security validation currently provided by the InSpec tests.