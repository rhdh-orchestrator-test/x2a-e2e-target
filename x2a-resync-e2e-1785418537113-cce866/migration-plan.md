# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used for compliance automation and server configuration. The migration scope is relatively small, focusing on:

1. Converting Chef InSpec tests to Ansible-compatible testing frameworks
2. Consolidating existing Ansible playbooks
3. Migrating Chef Automate and Chef Infra Server deployment scripts to Ansible playbooks

The estimated timeline for this migration is 1-2 weeks, with low to moderate complexity. The primary challenge will be preserving the compliance testing functionality currently provided by Chef InSpec.

## Module Migration Plan

This repository contains a combination of Ansible playbooks and Chef InSpec tests that need individual migration planning:

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
    - Description: Chef InSpec profile that verifies SSH security configuration (root login disabled)
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, STIG compliance checks

- **automate-deploy**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deploy**:
    - Description: Bash script for deploying standalone Chef Infra Server
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for running Ansible playbooks with InSpec verification. Migration will require converting to Ansible-native testing frameworks.
- `chef-and-ansible/index.html`: Static HTML file used by the website_https playbook. Can be directly used in Ansible.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (used in kitchen.yml for testing)
- **Cloud Platform**: Not specified, appears to be platform-agnostic with potential for both on-premises and cloud deployment (referenced in script comments)

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-compatible testing frameworks:
  - Option 1: Use Ansible's built-in `assert` module for basic testing
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Use pytest-ansible for Python-based testing
  - Option 4: Maintain InSpec as a separate tool called from Ansible

- **Test Kitchen**: Replace with:
  - Molecule for Ansible role testing
  - Ansible's built-in `--check` mode for validation

- **Chef Automate/Infra Server**: Replace with:
  - Ansible AWX or Ansible Tower for enterprise automation
  - GitLab CI/CD or Jenkins for pipeline orchestration
  - Compliance scanning tools like OpenSCAP or Ansible's built-in security automation

### Security Considerations

- **SSL Configuration**: The current playbooks configure Apache with SSL/TLS. Migration must preserve the security hardening that disables SSLv3 and enables only TLSv1.2.
  - Approach: Use Ansible's `openssl_*` modules to generate certificates and configure Apache securely

- **SSH Hardening**: The InSpec tests verify SSH security configurations. Migration must include equivalent checks.
  - Approach: Convert InSpec tests to Ansible assertions or use Ansible security automation roles

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be migrated to Ansible Vault
  - Count: 2 credential sets in deploy scripts (username/password combinations)

### Technical Challenges

- **InSpec Test Conversion**: Converting InSpec tests to equivalent Ansible testing mechanisms will require careful mapping of test assertions.
  - Mitigation: Create a mapping document for InSpec resources to Ansible modules/assertions

- **Compliance Validation**: Ensuring that the migrated solution provides the same level of compliance validation as the original InSpec tests.
  - Mitigation: Implement comprehensive testing of the migrated solution against the same compliance benchmarks

- **Maintaining Idempotency**: Ensuring that the migrated Ansible playbooks maintain proper idempotency, especially for the server deployment scripts.
  - Mitigation: Use Ansible's built-in idempotent modules rather than direct command execution

### Migration Order

1. **Existing Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk, already in Ansible format, may need minor adjustments for best practices
2. **InSpec Tests** (website_https_verify.rb, ssh_profile.rb): Moderate complexity, requires conversion to Ansible-compatible testing
3. **Chef Server Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh): High complexity, requires complete rewrite as Ansible playbooks

### Assumptions

1. The primary goal is to consolidate on Ansible as the single automation tool, eliminating the need for Chef components.
2. The compliance testing functionality provided by InSpec is still required in the migrated solution.
3. The deployment scripts are used in production environments and need to be preserved as Ansible playbooks.
4. The current Test Kitchen setup is used for development and testing, not production.
5. No external data sources or inventory systems are referenced in the current implementation.
6. The hardcoded credentials in the deployment scripts are placeholders and will be replaced with secure alternatives.
7. The Apache configuration and SSL settings represent actual production requirements that must be maintained.
8. The STIG compliance checks in the SSH profile represent actual compliance requirements that must be preserved.