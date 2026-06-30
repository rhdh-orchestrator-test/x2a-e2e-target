# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation. The primary focus is on using Chef InSpec for compliance testing alongside Ansible for configuration management. The repository also includes scripts for deploying Chef Automate and Chef Infra Server.

The migration scope is relatively small, as most of the configuration is already in Ansible format. The main migration effort will involve:
1. Converting Chef InSpec tests to Ansible-compatible testing frameworks
2. Migrating Chef Automate/Infra Server deployment scripts to Ansible playbooks
3. Ensuring all compliance testing capabilities are preserved

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
    - Description: Ansible playbook that remediates SSL POODLE vulnerability in Apache by enforcing TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening, service restart handlers

- **inspec_website_tests**:
    - Description: Chef InSpec tests that verify HTTPS functionality and security compliance
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening verification, HTTPS content verification, SSL protocol security checks

- **inspec_ssh_profile**:
    - Description: Chef InSpec compliance profile for SSH security configuration
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login verification, compliance with security standards (SRG-OS-000112)

- **chef_automate_deployment**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, user and organization creation

- **chef_server_deployment**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Migration considerations include replacing with Ansible-native testing frameworks like Molecule.
- `index.html`: Simple HTML file used as a test page. No migration needed, can be used as-is.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic with potential for both on-premises and cloud deployment (based on comments in setup scripts)

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-compatible testing frameworks:
  - Option 1: Use Ansible's built-in `assert` module for basic testing
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Use pytest-ansible for Python-based testing
  - Option 4: Consider maintaining InSpec as a separate tool if its specific compliance capabilities are required

- **Test Kitchen**: Replace with Molecule for Ansible role and playbook testing

- **Chef Automate/Infra Server**: Replace deployment scripts with Ansible playbooks that can:
  - Install and configure alternative compliance and infrastructure management tools
  - Options include AWX/Ansible Tower for infrastructure management and compliance tools like OpenSCAP

### Security Considerations

- **SSL/TLS Configuration**: The migration must preserve the security hardening in the Apache configuration:
  - Disabling vulnerable SSL protocols (SSLv3)
  - Enforcing TLSv1.2
  - Proper certificate management

- **SSH Hardening**: Maintain compliance with security standards:
  - Ensure SSH root login remains disabled
  - Preserve compliance with security standards referenced in the InSpec profile (SRG-OS-000112, V-38607)

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be migrated to Ansible Vault
  - Self-signed certificates should be managed securely
  - Count of credentials detected: 3 (username, password, and SSL certificates)

### Technical Challenges

- **Compliance Testing**: Chef InSpec provides specific compliance testing capabilities that may be challenging to replicate exactly in Ansible:
  - Challenge: Replicating the detailed SSL protocol testing in InSpec
  - Mitigation: Consider using Ansible's `openssl_certificate_info` module combined with custom assertions or maintaining InSpec as a separate tool called from Ansible

- **Test Framework Integration**: Ensuring that the replacement for Test Kitchen works seamlessly with the existing playbooks:
  - Challenge: Maintaining the same level of test coverage and verification
  - Mitigation: Create a comprehensive test matrix in Molecule that covers all the scenarios currently tested in Test Kitchen

- **Chef Server Replacement**: If Chef Server functionality is required:
  - Challenge: Replacing Chef Server's organization and user management
  - Mitigation: Implement equivalent functionality using AWX/Ansible Tower or other configuration management platforms

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk as they're already in Ansible format, may only need minor updates to follow best practices
2. **Testing Framework**: Convert InSpec tests to Ansible-compatible testing (moderate complexity)
3. **Chef Deployment Scripts**: Convert to Ansible playbooks for deploying alternative infrastructure management tools (high complexity, may require architectural decisions)

### Assumptions

1. The primary purpose of this repository is to demonstrate the integration of Chef InSpec with Ansible for compliance automation, not to provide production-ready infrastructure code.
2. The Chef InSpec tests are used for compliance verification while Ansible handles the actual configuration management.
3. The deployment scripts for Chef Automate and Chef Infra Server are used for setting up a test environment, not for production deployment.
4. The hardcoded credentials in the deployment scripts are for demonstration purposes only and would be replaced with secure credential management in a production environment.
5. The target environment is Ubuntu 20.04 running on Vagrant VMs, but the code should be adaptable to other environments.
6. The migration will need to preserve all compliance testing capabilities currently provided by Chef InSpec.
7. It's unclear if the Chef Automate and Chef Infra Server deployment is a core requirement or if it's supplementary to the main functionality.