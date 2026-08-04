# MIGRATION FROM ANSIBLE AND CHEF TO ANSIBLE

## Executive Summary

This repository contains a mix of Ansible playbooks and Chef InSpec tests, along with Chef Automate and Chef Infra Server deployment scripts. The migration scope is relatively small, focusing on converting existing Ansible playbooks to a more standardized Ansible structure and integrating Chef InSpec testing capabilities into the Ansible workflow. The estimated timeline for this migration is 1-2 weeks, with low to moderate complexity.

## Module Migration Plan

This repository contains Ansible playbooks and Chef InSpec tests that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that addresses SSL POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening

- **website_https_verify**:
    - Description: Chef InSpec test profile that verifies HTTPS functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec test profile that verifies SSH security configuration
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login verification, compliance with security standards

- **automate-deploy**:
    - Description: Bash script to deploy Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Infra Server configuration, user and organization setup

- **chef-server-deploy**:
    - Description: Bash script to deploy Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Infra Server installation, user and organization setup

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Migration considerations include replacing with Ansible Molecule for testing or adapting to use Ansible-native testing frameworks.
- `index.html`: Static HTML content for the web server. Can be directly migrated to Ansible templates.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be targeting on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's built-in `assert` module for basic testing
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Keep InSpec as a testing tool but invoke it from Ansible

- **Test Kitchen**: Replace with Ansible Molecule for testing infrastructure

- **Chef Automate/Infra Server**: Replace with Ansible Automation Platform or other Ansible-compatible management solutions:
  - Option 1: Migrate to Ansible Automation Platform (AAP)
  - Option 2: Use AWX (open-source upstream of Ansible Tower)
  - Option 3: Use GitLab CI/CD or Jenkins with Ansible

### Security Considerations

- **SSL Configuration**: The playbooks configure Apache with SSL. Migration should maintain or improve the security posture:
  - Ensure TLS 1.2+ is enforced (already implemented in poodle_fix.yml)
  - Consider adding more modern security headers
  - Implement proper certificate management

- **SSH Hardening**: The InSpec tests verify SSH security configurations:
  - Ensure Ansible roles implement the same SSH hardening measures
  - Consider using established Ansible security roles like dev-sec.ssh-hardening

- **Vault/secrets management**:
  - Hardcoded credentials in setup-automate scripts (username, password) should be migrated to Ansible Vault
  - Self-signed certificates should be managed securely
  - Count of credentials detected: 3 (username, password, SSL certificates)

### Technical Challenges

- **InSpec Test Conversion**: Converting InSpec tests to Ansible assertions or Molecule tests will require careful mapping of test logic:
  - Challenge: InSpec has specific matchers and resource types that may not have direct equivalents in Ansible
  - Mitigation: Create custom Ansible modules or use community modules that provide similar functionality

- **Certificate Management**: The current solution generates self-signed certificates:
  - Challenge: Ensuring secure certificate generation and management in Ansible
  - Mitigation: Use established Ansible roles for certificate management or integrate with external certificate authorities

- **Idempotency**: Ensuring all converted playbooks remain idempotent:
  - Challenge: Some commands in the current playbooks may not be idempotent (e.g., a2ensite, a2enmod)
  - Mitigation: Replace command modules with appropriate Ansible modules that ensure idempotency

### Migration Order

1. **website_https.yml** (Priority 1): Core web server configuration, relatively straightforward to migrate to an Ansible role
2. **poodle_fix.yml** (Priority 1): Security hardening, can be integrated into the web server role
3. **InSpec Tests** (Priority 2): Convert to Ansible-native testing or Molecule tests
4. **Chef Deployment Scripts** (Priority 3): Convert to Ansible roles for deploying alternative management platforms

### Assumptions

1. The target environment will continue to be Ubuntu 20.04 or compatible systems
2. The migration will maintain the same functionality but improve structure and maintainability
3. Self-signed certificates are acceptable for the target environment
4. The Chef Automate and Infra Server deployment scripts are used for setting up management infrastructure, which will be replaced with Ansible-compatible alternatives
5. The current Ansible playbooks do not use any external roles or collections
6. The InSpec tests are used for validation only and not for remediation
7. There are no external dependencies or integrations not visible in the repository
8. The migration will standardize on Ansible best practices, including role-based organization