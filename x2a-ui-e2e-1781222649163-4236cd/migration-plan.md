# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation. The migration scope is relatively small, focusing on two main components:

1. Ansible playbooks for deploying and configuring a secure Apache web server
2. Chef InSpec tests for verifying compliance and security configurations

The migration complexity is low to moderate, as most of the content is already in Ansible format. The primary work will involve integrating the Chef InSpec tests into an Ansible-native testing framework. Estimated timeline: 1-2 weeks for a complete migration.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **apache-https-website**:
    - Description: Apache web server with HTTPS configuration, self-signed certificates, and security hardening
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: SSL/TLS configuration, virtual host setup, self-signed certificate generation

- **poodle-vulnerability-fix**:
    - Description: Security fix for POODLE vulnerability in Apache SSL configuration
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables vulnerable SSL protocols, enforces TLSv1.2

- **https-compliance-tests**:
    - Description: InSpec tests to verify HTTPS configuration and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening checks, HTTPS response validation, SSL/TLS protocol verification

- **ssh-security-profile**:
    - Description: InSpec profile for SSH security compliance checking
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login verification, compliance with security standards (SRG-OS-000112)

- **chef-server-deployment**:
    - Description: Deployment scripts for Chef Server and Chef Automate
    - Path: setup-automate/deploy-chef-server.sh, setup-automate/deploy-automate.sh
    - Technology: Bash scripts
    - Key Features: Chef Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Migration considerations include replacing with Ansible-native testing framework like Molecule.
- `index.html`: Sample HTML file for testing web server deployment. Can be directly used in Ansible content.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's built-in `assert` module for basic tests
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Use pytest-ansible for Python-based testing
  - Option 4: Maintain InSpec as a separate tool but invoke from Ansible

- **Test Kitchen**: Replace with Molecule for Ansible role testing

### Security Considerations

- **SSL/TLS Configuration**: The playbooks configure Apache with TLS 1.2 and disable older protocols. This security practice should be maintained in the migrated Ansible roles.
  
- **Self-signed Certificates**: The current implementation generates self-signed certificates. Consider enhancing with Let's Encrypt integration for production environments.

- **SSH Hardening**: The InSpec tests verify SSH security configurations. These checks should be incorporated into the Ansible roles to ensure compliance.

- **Vault/secrets management**: 
  - Hardcoded credentials in setup scripts (username, password)
  - Self-signed certificates generated during deployment
  - Consider migrating to Ansible Vault for credential storage

### Technical Challenges

- **InSpec Test Conversion**: Converting InSpec tests to Ansible-native assertions or Molecule tests will require careful mapping of test logic.
  - Mitigation: Create a mapping document for InSpec resources to Ansible modules/assertions.

- **Compliance Reporting**: InSpec provides rich compliance reporting that may need to be replicated in the Ansible solution.
  - Mitigation: Integrate with tools like AWX/Tower for reporting or implement custom reporting scripts.

- **Chef Server Deployment**: The Chef Server deployment scripts need to be completely removed as they won't be needed in an Ansible-only environment.
  - Mitigation: Document the transition plan for users currently relying on Chef Server.

### Migration Order

1. **apache-https-website** (low risk, already in Ansible format)
2. **poodle-vulnerability-fix** (low risk, already in Ansible format)
3. **https-compliance-tests** (moderate complexity, requires test framework conversion)
4. **ssh-security-profile** (moderate complexity, requires test framework conversion)
5. **chef-server-deployment** (optional, only if equivalent Ansible automation is needed)

### Assumptions

1. The primary purpose of this repository is to demonstrate how Chef InSpec can be used alongside Ansible for compliance automation, as indicated in the README.
2. The target environment is Ubuntu 20.04 running on Vagrant VMs.
3. The security requirements include TLS 1.2 enforcement and SSH hardening.
4. The Chef Server deployment scripts are included for demonstration purposes but may not be central to the main functionality.
5. No external dependencies or complex infrastructure are required beyond what's explicitly defined in the playbooks.
6. The migration goal is to maintain the same functionality but using Ansible-native solutions where possible.
7. The InSpec tests are currently run as part of the Test Kitchen workflow, which will need to be replaced with an Ansible-native testing approach.