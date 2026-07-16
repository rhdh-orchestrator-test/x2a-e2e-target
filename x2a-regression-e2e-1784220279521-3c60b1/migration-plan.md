# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation. The primary focus is on using Chef InSpec for compliance testing alongside Ansible for configuration management. The repository also includes bash scripts for deploying Chef Automate and Chef Infra Server.

The migration scope is relatively small, as most of the configuration is already in Ansible format. The main migration effort will involve:
1. Converting Chef InSpec tests to Ansible-native testing solutions
2. Adapting the Chef Automate/Infra Server deployment scripts to Ansible playbooks
3. Ensuring all compliance requirements are maintained during migration

Estimated timeline: 1-2 weeks for a small team (1-2 engineers)

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL vulnerabilities in Apache by disabling older protocols
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: SSL protocol configuration, service restart handlers

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec control that verifies SSH root login is disabled for security compliance
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, compliance tagging (STIG, CCI)

- **chef-automate-deployment**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deployment**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Migration consideration: Replace with Ansible-native testing framework like Molecule.
- `index.html`: Simple HTML file used for testing. Migration consideration: Can be used as-is or templated in Ansible.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be environment-agnostic

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's assert module for basic testing
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Use ansible-lint for static analysis
  - Option 4: Consider OpenSCAP integration for compliance testing

- **Test Kitchen**: Replace with Molecule for Ansible role testing

### Security Considerations

- **SSL Configuration**: The migration must maintain the security hardening in the poodle_fix.yml playbook
  - Ensure TLSv1.2 protocol enforcement is preserved
  - Maintain proper certificate generation and configuration

- **SSH Security**: The SSH root login compliance check must be preserved
  - Convert the InSpec control to an equivalent Ansible check
  - Maintain compliance metadata (STIG IDs, CCI numbers)

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - SSL certificates should be managed securely

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible-native testing will require careful mapping of test assertions
  - Challenge: InSpec has specific matchers that may not have direct equivalents in Ansible
  - Mitigation: Use a combination of Ansible assert module and custom scripts where needed

- **Compliance Metadata**: Preserving compliance metadata (STIG IDs, CCI numbers) in Ansible format
  - Challenge: Ansible doesn't have a native way to store compliance metadata like InSpec
  - Mitigation: Use YAML comments or custom variables to maintain this information

- **Chef Server Deployment**: Converting Chef server deployment scripts to Ansible
  - Challenge: The scripts perform Chef-specific operations that need Ansible equivalents
  - Mitigation: Use Ansible's uri module to interact with Chef APIs or consider if Chef server is still needed

### Migration Order

1. **website_https.yml** (already in Ansible format, low risk)
2. **poodle_fix.yml** (already in Ansible format, low risk)
3. **InSpec Tests** (moderate complexity, requires new testing approach)
4. **Chef Deployment Scripts** (high complexity, requires architectural decisions)

### Assumptions

1. The primary goal is to consolidate on Ansible and remove Chef dependencies
2. The compliance requirements (STIG, CCI) must be maintained in the new solution
3. The self-signed certificates approach is acceptable for the migrated solution
4. The Chef Automate and Chef Infra Server deployment scripts may be replaced entirely if their functionality is no longer needed
5. The target environment will continue to be Ubuntu 20.04 or compatible
6. The current Vagrant-based testing approach is acceptable to maintain
7. No external data sources or integrations beyond what's visible in the code
8. The hardcoded credentials in the deployment scripts are for testing only and will be properly secured in production