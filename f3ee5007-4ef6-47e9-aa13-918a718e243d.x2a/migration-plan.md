# MIGRATION FROM CHEF INSPEC AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a combination of Ansible playbooks and Chef InSpec tests that demonstrate how to use Chef InSpec for compliance testing alongside Ansible for configuration management. The migration scope is relatively small, focusing on converting the existing Ansible playbooks to a more structured Ansible role-based approach while preserving the compliance testing capabilities currently provided by Chef InSpec.

The estimated timeline for this migration is 1-2 weeks, with low complexity due to the limited number of playbooks and tests. The primary focus will be on restructuring the Ansible content and implementing equivalent compliance testing using Ansible's native capabilities or integrating with existing InSpec tests.

## Module Migration Plan

This repository contains Ansible playbooks and Chef InSpec tests that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that addresses the POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec profile that verifies SSH security configurations
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login verification, compliance with security standards

- **automate_deployment**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization setup

- **chef_server_deployment**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization setup

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Migration considerations include replacing with Ansible Molecule for testing or adapting to use Ansible's native testing capabilities.
- `index.html`: Static HTML content for the web server. Can be directly incorporated into Ansible role as a template.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be targeting on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's assert module for basic compliance checks
  - Option 2: Integrate with Ansible Lint for static analysis
  - Option 3: Maintain InSpec as a separate testing tool but invoke it from Ansible
  - Option 4: Migrate to Ansible Molecule for comprehensive testing

- **Test Kitchen**: Replace with Ansible Molecule for testing infrastructure

### Security Considerations

- **SSL Configuration**: The playbooks configure SSL for Apache with self-signed certificates. Migration should maintain or improve this security practice by:
  - Using Ansible's crypto modules for certificate generation
  - Implementing proper certificate management
  - Ensuring secure protocols (TLSv1.2+) are enforced

- **SSH Hardening**: The InSpec tests verify SSH security configurations. Migration should:
  - Incorporate SSH hardening into Ansible roles
  - Implement equivalent compliance checks in Ansible

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be migrated to Ansible Vault
  - Count: 2 credential sets in deploy-automate.sh and deploy-chef-server.sh

### Technical Challenges

- **InSpec Test Conversion**: Converting InSpec tests to equivalent Ansible assertions or checks may require additional tooling or custom modules.
  - Mitigation: Use Ansible's assert module for basic checks and consider maintaining InSpec for complex compliance testing if needed.

- **Chef Automate/Server Deployment**: The bash scripts for Chef Automate and Chef Server deployment need to be converted to Ansible playbooks.
  - Mitigation: Create dedicated Ansible roles for Chef infrastructure deployment, or consider if this functionality is still needed post-migration.

### Migration Order

1. **website_https playbook** (low risk, high value): Convert to an Ansible role with proper structure
2. **poodle_fix playbook** (low risk): Incorporate into the website_https role as a separate task or handler
3. **InSpec tests** (moderate complexity): Create equivalent tests using Ansible's testing capabilities
4. **Chef deployment scripts** (high complexity): Convert to Ansible roles if still needed, or document as deprecated

### Assumptions

1. The primary goal is to maintain the same functionality while moving to a more structured Ansible approach.
2. The Chef InSpec tests are valuable and should be preserved in some form.
3. The Chef Automate and Chef Server deployment scripts may be less relevant after migration to Ansible.
4. The target environment (Ubuntu 20.04) will remain the same.
5. No external dependencies or integrations beyond what's visible in the repository.
6. The repository is primarily for demonstration/educational purposes rather than production use, based on the README content.