# MIGRATION FROM CHEF INSPEC AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a combination of Chef InSpec tests and Ansible playbooks that are used together to deploy and validate secure web server configurations. The migration scope is relatively small, focusing on converting Chef InSpec tests to Ansible-native testing solutions while preserving the existing Ansible playbooks. The repository also contains Chef Automate and Chef Infra Server deployment scripts that will need to be replaced with Ansible equivalents.

Estimated timeline: 1-2 weeks for a single developer to complete the migration, with minimal complexity due to the limited scope of Chef components.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that deploys an Apache web server with HTTPS configuration using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that remediates SSL POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening

- **website_https_verify**:
    - Description: Chef InSpec test that validates HTTPS configuration on the web server
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec control that validates SSH root login is disabled for security compliance
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, security compliance check with STIG references

- **chef-automate-deployment**:
    - Description: Bash script to deploy Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash with Chef CLI
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization setup

- **chef-server-deployment**:
    - Description: Bash script to deploy Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash with Chef CLI
    - Key Features: Chef Server installation, user and organization setup

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and validating with InSpec tests. Will need to be replaced with Ansible-native testing framework configuration.
- `index.html`: Static HTML content for the web server. Can be preserved as-is for Ansible deployment.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be infrastructure-agnostic

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Replace InSpec tests with Ansible Molecule for infrastructure testing
  - Consider using ansible-lint for static code analysis
  - For compliance testing similar to InSpec, consider using:
    - ansible-test
    - Molecule with testinfra backend
    - OpenSCAP with Ansible integration

- **Test Kitchen**: Replace with Ansible Molecule for test orchestration

### Security Considerations

- **SSL/TLS Configuration**: The migration must preserve the security hardening in the poodle_fix.yml playbook that disables SSLv3 and enables only TLSv1.2
- **SSH Security Controls**: The SSH root login compliance check must be preserved in the Ansible testing framework
- **Self-signed Certificates**: The certificate generation process should be maintained in the Ansible playbook
- **Vault/secrets management**:
  - Hardcoded credentials detected in setup scripts (username, password)
  - Recommendation: Replace with Ansible Vault for secure credential storage

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec's declarative testing syntax to equivalent Ansible/Molecule tests will require careful mapping of test assertions
  - Mitigation: Create a mapping document for InSpec resources to Ansible/Molecule equivalents
  
- **Chef Automate Replacement**: Determining the appropriate Ansible-based alternative for Chef Automate's functionality
  - Mitigation: Consider AWX/Ansible Tower or other Ansible-compatible CI/CD and compliance platforms

- **Compliance Reporting**: Replicating InSpec's compliance reporting capabilities in Ansible
  - Mitigation: Evaluate tools like OpenSCAP, Ansible Tower compliance features, or custom reporting solutions

### Migration Order

1. **website_https.yml and poodle_fix.yml**: Already Ansible playbooks, no migration needed
2. **website_https_verify.rb**: Convert InSpec tests to Ansible Molecule tests
3. **ssh_profile.rb**: Convert InSpec compliance control to Ansible equivalent
4. **chef-automate-deployment and chef-server-deployment**: Replace with Ansible playbooks for deploying alternative solutions

### Assumptions

1. The primary goal is to eliminate Chef dependencies while maintaining the same functionality
2. The existing Ansible playbooks (website_https.yml, poodle_fix.yml) can remain largely unchanged
3. A replacement for Chef Automate's compliance and reporting features will be needed
4. The team has experience with Ansible but may need training on Ansible testing frameworks
5. The hardcoded credentials in the setup scripts are for demonstration purposes only and will be properly secured in the migrated solution
6. The migration will maintain the same level of security compliance validation currently provided by InSpec