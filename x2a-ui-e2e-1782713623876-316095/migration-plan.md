# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation. The migration scope is relatively small, focusing on converting Chef InSpec tests to Ansible-compatible testing frameworks while preserving the existing Ansible playbooks. The repository also contains Chef Automate and Chef Infra Server deployment scripts that need to be converted to Ansible playbooks.

Estimated timeline: 1-2 weeks for a single developer, considering the limited scope and complexity.

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
    - Key Features: Disables SSLv3 and enables only TLSv1.2

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec test that verifies SSH security configuration
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login check, compliance with security standards (STIG)

- **chef-automate-deployment**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash script
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deployment**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash script
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Will need to be replaced with Ansible-specific testing framework configuration.
- `index.html`: Simple HTML file used as a test page for the web server. Can be preserved as-is or converted to a template.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (used in kitchen.yml as the driver)
- **Cloud Platform**: Not specified, but the setup scripts mention they can be used for on-prem or cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's built-in `assert` module for basic testing
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Use pytest-ansible for Python-based testing
  - Option 4: Keep InSpec but run it from Ansible using the `command` module

- **Test Kitchen**: Replace with:
  - Molecule for Ansible role testing
  - Or Ansible's own testing framework

- **Chef Automate/Infra Server**: Replace with:
  - Ansible AWX/Tower for web UI and control
  - GitLab CI/CD or Jenkins for pipeline automation
  - Ansible Vault for secrets management

### Security Considerations

- **SSL Configuration**: The playbooks configure Apache with SSL. Ensure the migration preserves:
  - Self-signed certificate generation
  - Proper SSL protocol settings (TLSv1.2 only)
  - Appropriate file permissions for certificates

- **SSH Security**: The InSpec tests verify SSH security configurations:
  - Ensure root login is disabled
  - Compliance with STIG requirements
  - Create equivalent Ansible tests or tasks to verify these settings

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - SSL certificates and keys should be handled securely

### Technical Challenges

- **Test Framework Conversion**: Converting InSpec tests to Ansible-compatible testing requires careful mapping of assertions:
  - Challenge: InSpec uses a domain-specific language for testing
  - Mitigation: Create equivalent assertions using Ansible's testing frameworks or modules

- **Compliance Reporting**: InSpec provides compliance reporting capabilities:
  - Challenge: Maintaining compliance reporting functionality
  - Mitigation: Integrate with tools like OpenSCAP or use Ansible's compliance capabilities

- **Chef Server Replacement**: The Chef Server deployment scripts need Ansible equivalents:
  - Challenge: Replicating user and organization management
  - Mitigation: Create Ansible roles for AWX/Tower setup with equivalent functionality

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk as they are already in Ansible format, may only need minor adjustments to follow best practices
2. **InSpec Tests** (website_https_verify.rb, ssh_profile.rb): Medium complexity, requires conversion to Ansible-compatible testing framework
3. **Chef Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh): Higher complexity, requires complete rewrite as Ansible playbooks and potential architectural changes

### Assumptions

1. The existing Ansible playbooks are compatible with current Ansible versions and don't require significant updates
2. The InSpec tests are used primarily for validation and not as part of a larger compliance framework
3. The deployment scripts are used for setting up test environments and not production systems
4. No external data sources or complex integrations are present beyond what's visible in the repository
5. The migration will maintain the same level of security and compliance checking
6. No custom Chef resources or complex Ruby code exists that would require special handling
7. The target environment will continue to be Ubuntu 20.04 or compatible systems