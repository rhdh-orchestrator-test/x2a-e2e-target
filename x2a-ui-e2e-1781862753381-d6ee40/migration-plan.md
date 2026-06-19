# MIGRATION FROM CHEF/INSPEC TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that demonstrate how to use Chef InSpec for compliance testing alongside Ansible for configuration management. The migration scope is relatively small, focusing on converting Chef InSpec tests to Ansible-native solutions while preserving the existing Ansible playbooks. The estimated timeline for this migration is 1-2 weeks, with low complexity due to the limited number of components and clear separation of concerns.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that remediates SSL POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS website functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec control that verifies SSH root login is disabled for security compliance
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, security compliance check with STIG references

- **chef-automate-deployment**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh, setup-automate/deploy-chef-server.sh
    - Technology: Bash
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization setup

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests in a Vagrant environment
- `index.html`: Sample HTML file used by the website_https playbook

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml)
- **Cloud Platform**: Not specified, appears to be platform-agnostic with potential for on-premises or cloud deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Ansible's `assert` module for basic compliance checks
  - Option 2: Molecule for more comprehensive testing
  - Option 3: Use ansible-lint for static analysis of playbooks

- **Test Kitchen**: Replace with:
  - Molecule for Ansible role testing
  - Ansible's built-in `--check` mode for validation

### Security Considerations

- **SSL/TLS Configuration**: The migration must preserve the security hardening in the poodle_fix.yml playbook
  - Ensure the SSLProtocol settings are maintained during migration
  - Consider updating to include newer TLS versions (TLS 1.3) if appropriate

- **SSH Security**: The SSH root login compliance check must be preserved
  - Convert the InSpec control to an Ansible task that verifies the same configuration
  - Maintain the security metadata (STIG IDs, CCI references) in Ansible documentation

- **Self-signed Certificates**: The website_https.yml playbook generates self-signed certificates
  - Consider enhancing with Let's Encrypt integration for production environments
  - Ensure proper certificate permissions are maintained

- **Vault/secrets management**:
  - Hardcoded credentials in setup-automate scripts (username, password)
  - Recommend migrating these to Ansible Vault

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible assertions
  - Challenge: InSpec provides domain-specific language for compliance testing
  - Mitigation: Use Ansible's assert module with appropriate conditionals, or consider maintaining InSpec for testing while using Ansible for configuration

- **Compliance Metadata**: Preserving compliance metadata (STIG IDs, CCI references)
  - Challenge: Ansible doesn't have a native way to store compliance metadata
  - Mitigation: Use YAML comments or custom variables to maintain this information

- **Chef Automate Deployment**: Converting Chef Automate deployment scripts to Ansible
  - Challenge: The scripts install Chef-specific components
  - Mitigation: If Chef Automate is still needed, create Ansible roles that perform the same installation steps; if not, replace with alternative compliance solutions

### Migration Order

1. **website_https.yml** (already in Ansible, no migration needed)
2. **poodle_fix.yml** (already in Ansible, no migration needed)
3. **website_https_verify.rb** (convert InSpec tests to Ansible assertions)
4. **ssh_profile.rb** (convert InSpec control to Ansible task)
5. **Chef Automate deployment scripts** (convert to Ansible roles if Chef Automate is still needed)

### Assumptions

1. The primary goal is to eliminate Chef InSpec dependencies while maintaining the same level of compliance testing
2. The existing Ansible playbooks (website_https.yml, poodle_fix.yml) are working correctly and don't need functional changes
3. Chef Automate may still be needed for compliance reporting, but its deployment should be managed by Ansible
4. The target environment will continue to be Ubuntu 20.04 or compatible
5. Test Kitchen is used only for development/testing and not in production pipelines
6. No external data sources or dynamic inventories are being used
7. The hardcoded credentials in the setup scripts are for demonstration purposes and will be replaced with secure alternatives