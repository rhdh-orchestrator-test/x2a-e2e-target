# MIGRATION FROM CHEF INSPEC AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a combination of Chef InSpec tests and Ansible playbooks that are used together for compliance automation. The primary focus is on using Chef InSpec for compliance testing alongside Ansible for configuration management. The migration scope is relatively small, focusing on converting Chef InSpec tests to Ansible-native testing solutions while preserving the existing Ansible playbooks. The estimated timeline for this migration is 1-2 weeks, with low complexity due to the limited scope and clear separation of concerns.

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
    - Description: Chef InSpec test that verifies HTTPS functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol security verification

- **ssh_profile**:
    - Description: Chef InSpec control that verifies SSH root login is disabled for security compliance
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration security check with STIG compliance metadata

- **chef-automate-deployment**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization setup

- **chef-server-deployment**:
    - Description: Bash script for deploying standalone Chef Infra Server
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization setup

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Migration considerations include replacing with Ansible-native testing frameworks like Molecule.
- `index.html`: Simple HTML file used for testing the web server. No migration needed as it's a static content file.

### Target Details

Analyze the source repository to determine target environment specifications:

- **Operating System**: Ubuntu 20.04 LTS (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic with potential for on-premises or cloud deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec (latest)**: Replace with Ansible-native testing solutions:
  - Option 1: Ansible's `assert` module for basic testing
  - Option 2: Molecule for comprehensive testing
  - Option 3: Integration with other testing frameworks like Serverspec or TestInfra

- **Test Kitchen (latest)**: Replace with Molecule for Ansible role testing

- **Vagrant (latest)**: Can be retained for local development testing or replaced with containerized testing using Docker with Molecule

### Security Considerations

- **SSL/TLS Configuration**: The migration must preserve the security hardening in the poodle_fix.yml playbook that enforces TLSv1.2 and disables vulnerable protocols.
  
- **SSH Security Controls**: The SSH root login compliance check needs to be migrated to an equivalent Ansible-based test.

- **Self-signed Certificates**: The current implementation uses self-signed certificates. Consider implementing a more robust certificate management solution in the migrated version.

- **Vault/secrets management**: 
  - Hardcoded credentials in setup scripts (username, password) should be migrated to Ansible Vault
  - No encrypted data bags or Chef Vault usage detected
  - 1 credential set detected in deploy-automate.sh and deploy-chef-server.sh

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec's declarative testing syntax to equivalent Ansible testing constructs will require careful mapping of assertions and resources.
  - Mitigation: Create a mapping document for InSpec resources to Ansible modules/assertions and validate each test conversion individually.

- **Compliance Metadata**: The InSpec tests include rich compliance metadata (STIG IDs, CCI references) that needs to be preserved in the Ansible-based solution.
  - Mitigation: Use Ansible role metadata, tags, or documentation to maintain compliance mapping information.

- **Chef Automate Replacement**: Determining an equivalent compliance reporting solution for Ansible to replace Chef Automate's functionality.
  - Mitigation: Evaluate options like AWX/Tower with compliance reporting plugins or integration with third-party compliance tools.

### Migration Order

1. **website_https.yml** (low risk, already Ansible): No migration needed, already in Ansible format
2. **poodle_fix.yml** (low risk, already Ansible): No migration needed, already in Ansible format
3. **website_https_verify.rb** (moderate complexity): Convert InSpec tests to Ansible assertions or Molecule tests
4. **ssh_profile.rb** (moderate complexity): Convert InSpec compliance control to Ansible-based test with compliance metadata
5. **deploy-automate.sh and deploy-chef-server.sh** (high complexity): Convert to Ansible roles for infrastructure deployment, replacing Chef-specific components

### Assumptions

1. The primary goal is to eliminate Chef InSpec dependency while maintaining the same level of compliance testing.
2. The existing Ansible playbooks (website_https.yml and poodle_fix.yml) are working correctly and don't require modification beyond testing integration.
3. There is no requirement to maintain backward compatibility with Chef Automate or Chef Server.
4. The target environment will continue to be Ubuntu 20.04 LTS.
5. The self-signed certificate approach is acceptable for the migrated solution.
6. The hardcoded credentials in the deployment scripts are for demonstration purposes and will be properly secured in the migrated solution.
7. The compliance metadata in the InSpec tests (STIG IDs, CCI references) needs to be preserved in some form in the migrated solution.