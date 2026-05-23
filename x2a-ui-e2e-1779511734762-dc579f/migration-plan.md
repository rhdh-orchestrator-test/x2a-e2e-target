# MIGRATION FROM CHEF INSPEC AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a combination of Chef InSpec tests and Ansible playbooks that are used for compliance automation. The primary focus appears to be demonstrating how Chef InSpec can be used alongside Ansible for continuous compliance validation. The migration scope is relatively small, as most of the content is already in Ansible format, with Chef InSpec being used for testing and validation. The migration will primarily involve replacing Chef InSpec tests with equivalent Ansible-native testing solutions.

**Estimated Timeline**: 1-2 weeks for a small team (1-2 engineers)
**Complexity**: Low to Medium
**Primary Focus**: Converting InSpec tests to Ansible-native testing solutions while preserving compliance validation capabilities

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that remediates SSL POODLE vulnerability in Apache by enforcing TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening, service restart handlers

- **website_https_verify**:
    - Description: Chef InSpec test profile that validates HTTPS functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL/TLS protocol security verification

- **ssh_profile**:
    - Description: Chef InSpec test profile that validates SSH security configuration (root login disabled)
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, STIG compliance check, security control validation

- **chef-server-deployment**:
    - Description: Bash script for deploying Chef Infra Server
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash with Chef Server CLI
    - Key Features: Chef Server installation, user and organization creation

- **automate-deployment**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash with Chef Automate CLI
    - Key Features: Chef Automate installation, Chef Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and validating with InSpec tests. Migration consideration: Replace with Ansible Molecule for testing.
- `index.html`: Sample HTML file, likely used as a template. No migration needed.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, though the setup scripts mention they can be used for on-prem or cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Ansible Molecule with testinfra for infrastructure testing
  - Option 2: Ansible Molecule with Goss for infrastructure testing
  - Option 3: Ansible Molecule with custom Ansible assertions

- **Test Kitchen**: Replace with Ansible Molecule for test orchestration

- **Chef Automate/Server**: The deployment scripts for Chef Automate and Chef Server should be replaced with Ansible playbooks that either:
  - Deploy alternative compliance and automation tools (e.g., AWX/Tower for automation, OpenSCAP for compliance)
  - Or, if Chef Automate/Server must be maintained, create Ansible playbooks that perform the same installation and configuration

### Security Considerations

- **SSL/TLS Configuration**: The migration must maintain the security hardening present in the poodle_fix.yml playbook, ensuring TLSv1.2 is enforced and older protocols are disabled.
  - Migration approach: Preserve the same configuration in the Ansible playbooks.

- **SSH Security**: The SSH security controls tested by the ssh_profile.rb InSpec test must be maintained.
  - Migration approach: Create an Ansible role that enforces the same SSH security configurations and includes assertions to validate the settings.

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts: The deploy-automate.sh and deploy-chef-server.sh scripts contain hardcoded usernames and passwords. These should be migrated to Ansible Vault.
  - Count: 2 credential sets (username/password) in deployment scripts

### Technical Challenges

- **Compliance Testing**: The primary challenge will be replacing Chef InSpec's declarative testing approach with equivalent Ansible-native testing capabilities.
  - Mitigation strategy: Use Ansible Molecule with testinfra or Goss for infrastructure testing, or develop custom Ansible assertion tasks that perform the same validation.

- **Test Coverage**: Ensuring that the new Ansible-native tests provide the same level of compliance validation as the existing InSpec tests.
  - Mitigation strategy: Create a test coverage matrix to map InSpec controls to new Ansible test assertions.

### Migration Order

1. **website_https.yml and poodle_fix.yml** (Priority 1, low risk): These are already Ansible playbooks and require minimal changes.
2. **InSpec Tests** (Priority 2, moderate complexity): Convert the InSpec tests to Ansible Molecule with appropriate test plugins.
3. **Chef Server/Automate Deployment Scripts** (Priority 3, high complexity): Replace with Ansible playbooks for deploying either Chef products or alternative solutions.

### Assumptions

1. The primary goal is to move away from Chef InSpec for testing while maintaining or enhancing compliance validation capabilities.
2. The existing Ansible playbooks (website_https.yml and poodle_fix.yml) are functioning correctly and don't require significant modifications.
3. There is no requirement to maintain backward compatibility with Chef InSpec.
4. The deployment scripts for Chef Server and Automate are intended to be replaced with equivalent Ansible functionality, rather than preserved as-is.
5. The hardcoded credentials in the deployment scripts are for demonstration purposes and will be replaced with secure credential management in the Ansible implementation.
6. The STIG compliance requirements referenced in the ssh_profile.rb test will need to be maintained in the Ansible implementation.