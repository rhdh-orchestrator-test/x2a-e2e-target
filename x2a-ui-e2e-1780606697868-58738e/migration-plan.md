# MIGRATION FROM CHEF/INSPEC TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec testing profiles and Ansible playbooks that demonstrate how to use Chef InSpec for compliance testing alongside Ansible for configuration management. The migration scope is relatively small, focusing on two main components:

1. Ansible playbooks with InSpec testing (chef-and-ansible directory)
2. Chef Automate and Chef Infra Server deployment scripts (setup-automate directory)

The migration complexity is low to moderate, with an estimated timeline of 1-2 weeks. The primary focus will be on replacing InSpec tests with Ansible-native testing solutions while preserving the existing Ansible playbooks.

## Module Migration Plan

This repository contains Chef InSpec profiles and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website-https-configuration**:
    - Description: Ansible playbook that configures Apache with HTTPS, creates self-signed certificates, and deploys a simple website
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible (already)
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle-vulnerability-fix**:
    - Description: Ansible playbook that fixes SSL POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible (already)
    - Key Features: Apache SSL module configuration, security hardening

- **website-https-compliance-tests**:
    - Description: Chef InSpec profile that verifies HTTPS configuration, port availability, and website content
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: HTTPS validation, SSL protocol verification, content verification

- **ssh-security-compliance-tests**:
    - Description: Chef InSpec profile that verifies SSH security configurations (root login disabled)
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH security compliance, STIG validation, CCI controls

- **chef-automate-deployment**:
    - Description: Bash script that deploys Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash with Chef CLI
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deployment**:
    - Description: Bash script that deploys Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash with Chef CLI
    - Key Features: Chef Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests - will need to be replaced with Ansible-native testing framework (Molecule)
- `index.html`: Sample HTML file used in testing - can be preserved as-is or incorporated into Ansible templates

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic with potential for on-premises or cloud deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Ansible Lint for static analysis
  - Option 2: Molecule for integration testing
  - Option 3: Ansible Test Kitchen plugin (if maintaining Test Kitchen is desired)
  - Option 4: Convert InSpec tests to Ansible assert tasks

- **Test Kitchen**: Replace with Molecule for Ansible-native testing framework

- **Chef Automate/Infra Server**: Replace deployment scripts with Ansible playbooks that can:
  - Option 1: Deploy alternative compliance solutions (e.g., OpenSCAP, Prometheus with compliance exporters)
  - Option 2: Deploy Ansible AWX/Tower for centralized management

### Security Considerations

- **SSL/TLS Configuration**: The migration must preserve the security hardening in the poodle_fix.yml playbook
  - Approach: Maintain the same Apache SSL configuration but implement as an Ansible role for better reusability

- **SSH Hardening**: The SSH compliance tests must be converted to Ansible checks
  - Approach: Create Ansible tasks that verify SSH configuration using assert modules

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - Self-signed certificates should be managed securely, potentially using ansible-vault for private keys

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec's declarative testing syntax to Ansible's procedural approach
  - Mitigation: Use Ansible's assert module with carefully crafted conditions that match InSpec's intent
  - Example: Replace `describe port(443) { it { should be_listening } }` with appropriate Ansible wait_for or uri module checks

- **Compliance Reporting**: InSpec provides rich compliance reporting that needs an equivalent in Ansible
  - Mitigation: Consider integrating with tools like OpenSCAP, Compliance as Code, or custom reporting solutions

- **Test Kitchen Workflow**: Teams may be accustomed to Test Kitchen's workflow
  - Mitigation: Provide documentation on Molecule workflows and create similar patterns to ease transition

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml) - Low risk as they're already in Ansible format
   - Convert to roles for better organization
   - Add documentation and improve variable naming

2. **InSpec Tests** (website_https_verify.rb, ssh_profile.rb) - Medium complexity
   - Convert to Ansible assert tasks or Molecule tests
   - Ensure equivalent coverage and reporting

3. **Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh) - Higher complexity
   - Convert to Ansible playbooks
   - Implement secure credential management with Ansible Vault
   - Add idempotence to ensure repeatable deployments

### Assumptions

1. The primary goal is to eliminate Chef InSpec dependencies while maintaining equivalent testing capabilities
2. The existing Ansible playbooks are functioning correctly and don't require significant refactoring
3. There's no requirement to maintain backward compatibility with Chef tools
4. The team has Ansible expertise or will receive training as part of the migration
5. The hardcoded credentials in deployment scripts are for demonstration purposes only and will be properly secured in the migrated solution
6. The Test Kitchen configuration is used primarily for development/testing and not in production pipelines
7. The SSH compliance profile is intended to be run against the same systems configured by the Ansible playbooks