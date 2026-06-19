# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation. The primary focus appears to be showing how Chef InSpec can be used alongside Ansible for compliance testing. Additionally, there are bash scripts for deploying Chef Automate and Chef Infra Server.

The migration scope is relatively small, as most of the Ansible components are already in place. The main migration effort will involve:
1. Converting Chef InSpec tests to Ansible-native testing solutions
2. Migrating Chef Automate/Infra Server deployment scripts to Ansible playbooks
3. Ensuring the existing Ansible playbooks follow best practices

Estimated timeline: 1-2 weeks for a small team (1-2 engineers)

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS enabled using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables vulnerable SSL protocols, enables TLSv1.2

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec test that verifies SSH security configuration (root login disabled)
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, security compliance checks with STIG references

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
- `index.html`: Simple HTML file used as a test page for the web server

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic with potential for on-premises or cloud deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's built-in `assert` module for basic testing
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Use ansible-lint for static analysis
  - Option 4: Consider Ansible's integration with pytest for advanced testing scenarios

- **Test Kitchen**: Replace with:
  - Molecule for Ansible role testing
  - Or continue using Test Kitchen with the `kitchen-ansible` plugin if preferred

- **Chef Automate/Infra Server**: Replace with:
  - Ansible AWX/Tower for enterprise automation platform
  - GitLab CI/CD or Jenkins for pipeline automation
  - Compliance scanning tools like OpenSCAP or Ansible's built-in security automation

### Security Considerations

- **SSL Configuration**: The current playbooks properly configure Apache with TLSv1.2 and disable vulnerable protocols. This should be maintained in the migrated solution.
  - Migration approach: Preserve the same SSL hardening in the Ansible roles

- **SSH Hardening**: The InSpec tests verify SSH security configurations (disabling root login).
  - Migration approach: Create Ansible tasks to enforce the same SSH hardening and use Ansible's assert module to verify compliance

- **Vault/secrets management**:
  - Hardcoded credentials in the Chef deployment scripts (username, password)
  - Migration approach: Replace with Ansible Vault for secure credential storage

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec's declarative testing syntax to Ansible's procedural approach
  - Mitigation: Use Ansible's assert module with appropriate conditionals to replicate InSpec tests
  - Example: Replace `describe port(443) { it { should be_listening } }` with Ansible tasks that check port status and assert the result

- **Compliance Reporting**: InSpec provides rich compliance reporting that needs to be replicated
  - Mitigation: Consider integrating with tools like OpenSCAP or using Ansible AWX/Tower for compliance reporting

- **Chef Automate Functionality**: Replacing Chef Automate's compliance dashboard and reporting
  - Mitigation: Implement Ansible AWX/Tower with custom reporting dashboards or integrate with third-party compliance tools

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk as they're already in Ansible format
   - Refactor to follow Ansible best practices (roles, variables, etc.)
   - Add proper documentation

2. **InSpec Tests** (website_https_verify.rb, ssh_profile.rb): Moderate complexity
   - Convert to Ansible assert tasks or Molecule tests
   - Ensure all compliance checks are preserved

3. **Chef Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh): High complexity
   - Convert to Ansible playbooks
   - Implement secure credential management with Ansible Vault

### Assumptions

1. The primary goal is to move away from Chef InSpec while maintaining the same level of compliance testing
2. The existing Ansible playbooks are functional but may need refactoring to follow best practices
3. The deployment scripts for Chef Automate/Infra Server will be replaced with equivalent Ansible automation
4. The target environment will continue to be Ubuntu 20.04 or similar Linux distributions
5. Test Kitchen can be replaced with Molecule or another Ansible-native testing framework
6. The hardcoded credentials in the deployment scripts are for demonstration purposes only and will be properly secured in the migrated solution
7. The compliance requirements (especially those referenced in the SSH profile with STIG IDs) must be maintained in the new solution