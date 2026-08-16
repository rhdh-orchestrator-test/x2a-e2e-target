# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together for compliance automation. The repository appears to be a demonstration or example repository rather than a production infrastructure codebase. The migration scope is relatively small, focusing on:

1. Migrating Chef InSpec tests to Ansible-compatible testing frameworks
2. Updating existing Ansible playbooks to follow current best practices
3. Converting Chef Automate and Chef Server deployment scripts to Ansible playbooks

Given the limited scope and the fact that most of the code is already in Ansible format, this migration is estimated to be low complexity and could be completed within 1-2 weeks.

## Module Migration Plan

This repository contains a mix of Ansible playbooks and Chef InSpec tests that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS enabled using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate the POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: SSL protocol configuration, service restart handlers

- **ssh_profile**:
    - Description: Chef InSpec test profile that verifies SSH root login is disabled
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, compliance testing

- **website_https_verify**:
    - Description: Chef InSpec test profile that verifies HTTPS is properly configured
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **chef-automate-deploy**:
    - Description: Bash script to deploy Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deploy**:
    - Description: Bash script to deploy Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration file that uses Ansible as the provisioner and InSpec as the verifier. Will need to be updated to use Ansible-native testing frameworks.
- `chef-and-ansible/index.html`: Simple HTML file used as a template for the website deployment.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (used in kitchen.yml for testing)
- **Cloud Platform**: Not specified, appears to be platform-agnostic

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-compatible testing frameworks:
  - Option 1: Use Ansible's built-in `assert` module for simple tests
  - Option 2: Use Molecule for more comprehensive testing
  - Option 3: Use pytest-ansible for Python-based testing

- **Test Kitchen**: Replace with:
  - Option 1: Molecule for Ansible role testing
  - Option 2: Ansible's own testing framework

- **Chef Automate/Server**: Replace deployment scripts with:
  - Ansible playbooks that install and configure monitoring and compliance tools like:
    - Prometheus + Grafana for monitoring
    - OpenSCAP or Compliance as Code for compliance scanning

### Security Considerations

- **SSL Configuration**: The existing playbooks configure SSL for Apache. Migration should maintain or improve the security posture:
  - Update SSL protocols to current best practices (TLS 1.3 support)
  - Ensure proper cipher suite configuration
  - Consider integrating with Let's Encrypt for certificate management instead of self-signed certificates

- **SSH Hardening**: The InSpec tests verify SSH hardening. Migration should:
  - Maintain SSH hardening checks
  - Implement SSH hardening via Ansible's `openssh_server` module or dedicated roles

- **Vault/secrets management**:
  - Hardcoded credentials in `deploy-automate.sh` and `deploy-chef-server.sh` should be migrated to Ansible Vault
  - SSL certificates should be managed securely, potentially using Ansible Vault or integration with a secrets management solution

### Technical Challenges

- **Testing Framework Migration**: Converting InSpec tests to Ansible-compatible testing frameworks will require:
  - Understanding the InSpec test logic
  - Implementing equivalent tests in the target framework
  - Ensuring the same level of compliance validation

- **Chef Server Replacement**: If Chef Server functionality is needed, alternatives must be considered:
  - AWX/Ansible Tower for inventory management and job scheduling
  - GitLab CI/CD or GitHub Actions for pipeline-based automation
  - Ansible Semaphore for a lightweight Ansible UI

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk, already in Ansible format, just need updates to follow current best practices
2. **InSpec Tests** (ssh_profile.rb, website_https_verify.rb): Moderate complexity, requires conversion to Ansible-compatible testing frameworks
3. **Chef Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh): Higher complexity, requires complete rewrite as Ansible playbooks and consideration of replacement technologies

### Assumptions

1. The repository is primarily for demonstration purposes and not a production codebase
2. The existing Ansible playbooks are functional and can be used as a starting point
3. There is no requirement to maintain backward compatibility with Chef InSpec
4. The team is familiar with Ansible and can adapt to new testing frameworks
5. The hardcoded credentials in the deployment scripts are for demonstration purposes only
6. The self-signed certificates are acceptable for the demonstration environment
7. The target environment will continue to be Ubuntu 20.04 or compatible
8. There are no external dependencies or integrations not visible in the repository