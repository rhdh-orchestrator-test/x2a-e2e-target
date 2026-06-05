# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation. The primary focus appears to be showing how Chef InSpec can be used alongside Ansible for compliance testing. Additionally, there are bash scripts for deploying Chef Automate and Chef Infra Server.

The migration scope is relatively small, as most of the Ansible components are already in place. The main migration effort will involve:
1. Converting Chef InSpec tests to Ansible-native testing solutions
2. Replacing Chef Automate/Infra Server deployment scripts with Ansible playbooks
3. Ensuring all compliance requirements are maintained during migration

**Estimated Timeline**: 1-2 weeks for a complete migration, with minimal complexity due to the small codebase and limited dependencies.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that remediates SSL POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening, service restart handlers

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec control that verifies SSH root login is disabled (STIG compliance)
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, STIG compliance check

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

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests
- `index.html`: Sample HTML file used in the website deployment example

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, but scripts are designed to work on both on-premises and cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use ansible-test for basic functionality testing
  - Option 2: Integrate Molecule for more comprehensive testing
  - Option 3: Use ansible-lint for static analysis and best practices
  - Option 4: For compliance testing specifically, consider OpenSCAP with Ansible

- **Test Kitchen**: Replace with:
  - Molecule for Ansible role/playbook testing
  - Ansible-specific CI/CD pipelines (GitHub Actions, GitLab CI, etc.)

- **Chef Automate/Infra Server**: Replace with:
  - Ansible AWX/Tower for enterprise automation platform
  - GitLab/GitHub for code repository and CI/CD
  - Compliance scanning tools like OpenSCAP or Ansible Automation Platform's compliance capabilities

### Security Considerations

- **SSL/TLS Configuration**: The current implementation enforces TLSv1.2 and disables vulnerable protocols. This security hardening must be maintained in the migrated solution.
  - Migration approach: Preserve the same Apache SSL configuration in the Ansible playbooks

- **SSH Hardening**: The InSpec test verifies SSH root login is disabled according to STIG requirements.
  - Migration approach: Create an Ansible task to enforce the same SSH configuration and use Ansible's assert module or OpenSCAP to verify compliance

- **Self-signed Certificates**: The current implementation generates self-signed certificates.
  - Migration approach: Continue using Ansible's openssl modules for certificate generation or consider integrating with a certificate management solution

- **Vault/secrets management**:
  - Hardcoded credentials in bash scripts (username, password) should be moved to Ansible Vault
  - Count: 2 credential sets (username/password) in deploy scripts

### Technical Challenges

- **Compliance Testing**: Replacing Chef InSpec with Ansible-native compliance testing tools.
  - Mitigation: Evaluate OpenSCAP integration with Ansible or use ansible.builtin.assert for basic compliance checks

- **Test Kitchen Replacement**: Finding an equivalent testing framework for Ansible.
  - Mitigation: Implement Molecule for testing Ansible roles and playbooks

- **Maintaining Compliance Standards**: Ensuring all STIG and other compliance requirements are preserved.
  - Mitigation: Document all compliance requirements and create verification steps for each

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk as they're already in Ansible format
   - Review and optimize according to current Ansible best practices
   - Update any deprecated modules or syntax

2. **Bash Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh): Medium complexity
   - Convert to Ansible playbooks
   - Move credentials to Ansible Vault
   - Implement idempotency checks

3. **InSpec Tests** (website_https_verify.rb, ssh_profile.rb): Highest complexity
   - Convert to Ansible-native testing solutions
   - Ensure all compliance checks are maintained
   - Integrate with new testing framework (Molecule)

### Assumptions

1. The primary purpose of this repository is to demonstrate Chef InSpec with Ansible rather than being a production deployment
2. The target environment will continue to be Ubuntu 20.04 or compatible systems
3. Vagrant will continue to be used for development/testing environments
4. There are no external dependencies or integrations beyond what's visible in the repository
5. The security requirements (TLS configuration, SSH hardening) must be maintained in the migrated solution
6. The Chef Automate/Infra Server deployment is for demonstration purposes and not a critical production component
7. No custom Chef resources or complex Chef-specific functionality is being used that would require special handling
8. The migration will be to pure Ansible without maintaining any Chef components