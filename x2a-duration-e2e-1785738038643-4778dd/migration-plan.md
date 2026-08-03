# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used for compliance automation and server configuration. The migration scope is relatively small, focusing on:

1. Converting Chef InSpec tests to Ansible-compatible testing frameworks
2. Consolidating existing Ansible playbooks into a more structured Ansible project
3. Migrating Chef server deployment scripts to Ansible playbooks

The complexity is moderate, with most of the work centered on converting InSpec tests to equivalent Ansible testing solutions. The estimated timeline for this migration is 2-3 weeks, with the majority of time spent on test conversion and validation.

## Module Migration Plan

This repository contains a mix of Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that remediates SSL POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening, service restart handlers

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS configuration on a web server
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec profile that verifies SSH security configurations
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login verification, compliance with security standards (STIG)

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

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Used for local development and testing. Migration will require converting to Ansible-native testing frameworks.
- `index.html`: Static HTML content for the website deployment. Can be directly used in Ansible without modification.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (used in kitchen.yml for local testing)
- **Cloud Platform**: Not specified, but scripts are designed to work on both on-premises and cloud VMs (mentioned in script comments)

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's `assert` module for basic compliance checks
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Use ansible-lint for static analysis of playbooks

- **Test Kitchen**: Replace with Molecule for Ansible playbook testing and development

- **Chef Automate/Server**: Replace deployment scripts with Ansible roles for infrastructure management:
  - Create roles for configuration management
  - Use Ansible Vault for secrets management
  - Implement collections for reusable components

### Security Considerations

- **SSL Configuration**: The playbooks handle SSL configuration for Apache. Migration should maintain or enhance security by:
  - Ensuring TLS 1.2+ is enforced
  - Generating proper self-signed certificates
  - Providing options for using trusted certificates

- **SSH Hardening**: The InSpec tests verify SSH security configurations. Migration should:
  - Convert InSpec tests to Ansible assertions
  - Maintain compliance with security standards (STIG)
  - Implement SSH hardening as an Ansible role

- **Vault/secrets management**:
  - Hardcoded credentials in deployment scripts (username, password) should be moved to Ansible Vault
  - SSL certificates and keys should be managed securely
  - Count of credentials detected: 3 (username, password, and SSL keys)

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to equivalent Ansible testing mechanisms will require careful mapping of test assertions and validation logic.
  - Mitigation: Create a mapping document for InSpec resources to Ansible modules
  - Consider using ansible.builtin.assert or custom modules for complex validations

- **Maintaining Compliance Standards**: Ensuring that the migrated Ansible code maintains compliance with security standards referenced in InSpec tests.
  - Mitigation: Create a compliance matrix to track requirements and implementation

- **Chef Server Deployment**: Converting Chef server deployment scripts to Ansible requires understanding of Chef infrastructure.
  - Mitigation: Research existing Ansible roles for Chef deployment or create custom roles

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk as they're already in Ansible format, just need restructuring
2. **InSpec Tests** (website_https_verify.rb, ssh_profile.rb): Moderate complexity, requires converting to Ansible testing framework
3. **Chef Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh): High complexity, requires creating equivalent Ansible roles

### Assumptions

1. The repository is primarily used for demonstration and educational purposes, not production deployments (based on README content)
2. The InSpec tests are used alongside Ansible for compliance validation, not as part of a larger Chef ecosystem
3. The deployment scripts are examples and may contain simplified configurations not suitable for production
4. The hardcoded credentials in scripts are for demonstration purposes only
5. The target environment is Ubuntu 20.04 running on Vagrant for testing
6. The Apache configuration is basic and doesn't include complex customizations
7. The SSL configuration focuses specifically on POODLE vulnerability remediation
8. The repository doesn't contain actual Chef cookbooks or recipes that need migration