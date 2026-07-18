# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible configurations that need to be migrated to a unified Ansible solution. The repository primarily consists of:

1. Chef Automate and Chef Infra Server deployment scripts
2. Ansible playbooks for configuring HTTPS websites with Apache
3. InSpec tests for compliance verification

The migration complexity is relatively low as most of the configuration is already in Ansible format. The primary focus will be on replacing the Chef server deployment scripts with Ansible equivalents and ensuring the InSpec tests can still be used for compliance verification. Estimated timeline: 1-2 weeks for a complete migration.

## Module Migration Plan

This repository contains Chef and Ansible configurations that need individual migration planning:

### MODULE INVENTORY

- **chef-and-ansible**:
    - Description: Ansible playbooks for configuring HTTPS websites with Apache and InSpec tests for compliance verification
    - Path: chef-and-ansible
    - Technology: Ansible with Chef InSpec
    - Key Features: Apache HTTPS configuration, SSL/TLS security settings, InSpec compliance tests

- **setup-automate**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash scripts for Chef deployment
    - Key Features: Chef Automate deployment, Chef Infra Server deployment, user and organization creation

### Infrastructure Files

- `chef-and-ansible/website_https.yml`: Ansible playbook for configuring Apache with HTTPS. Migration considerations: Already in Ansible format, can be used as-is with minor adjustments.
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook for fixing SSL vulnerabilities in Apache. Migration considerations: Already in Ansible format, can be used as-is.
- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for testing Ansible playbooks with InSpec. Migration considerations: Update to use pure Ansible testing framework or adapt to continue using InSpec.
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test for verifying HTTPS configuration. Migration considerations: Can be kept as-is for compliance testing with Ansible.
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec test for SSH security compliance. Migration considerations: Can be kept as-is for compliance testing with Ansible.
- `setup-automate/deploy-automate.sh`: Bash script for deploying Chef Automate and Chef Infra Server. Migration considerations: Replace with Ansible playbook for configuration management.
- `setup-automate/deploy-chef-server.sh`: Bash script for deploying Chef Infra Server. Migration considerations: Replace with Ansible playbook for configuration management.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (identified from kitchen.yml and apt package manager usage in Ansible playbooks)
- **Virtual Machine Technology**: Vagrant (identified from kitchen.yml driver configuration)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM deployment

## Migration Approach

### Key Dependencies to Address

- **Chef Automate CLI**: Replace with Ansible roles for configuration management
- **Chef Server CLI**: Replace with Ansible roles for configuration management
- **InSpec**: Keep as a compliance testing tool that can work alongside Ansible
- **Apache 2.4.41**: Continue to manage with existing Ansible playbooks
- **OpenSSL**: Continue to manage with existing Ansible playbooks

### Security Considerations

- **SSL/TLS Configuration**: The repository includes specific SSL/TLS security settings (disabling SSLv3, enabling TLSv1.2). These should be preserved in the migration.
  - Migration approach: Keep the existing Ansible tasks for SSL configuration.

- **SSH Security**: The repository includes InSpec tests for SSH security compliance.
  - Migration approach: Keep the InSpec tests and ensure Ansible configurations comply with these tests.

- **Self-signed Certificates**: The playbooks generate self-signed certificates for HTTPS.
  - Migration approach: Consider replacing with Let's Encrypt integration for production environments.

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password)
  - Count: 2 sets of credentials in deploy scripts
  - Migration approach: Replace with Ansible Vault for secure credential storage

### Technical Challenges

- **InSpec Integration**: Ensuring InSpec tests continue to work with pure Ansible deployments.
  - Mitigation strategy: Use Ansible's `verify` module or integrate with InSpec directly through custom modules.

- **Chef Server Replacement**: Determining if Chef Server functionality needs to be replaced or if it can be eliminated.
  - Mitigation strategy: Evaluate if Chef Server is being used for actual configuration management or just as a deployment target. If the latter, it can be eliminated entirely.

### Migration Order

1. **chef-and-ansible Ansible playbooks** (low risk, high value): These are already in Ansible format and can be used with minimal changes.
2. **InSpec tests** (low risk, high value): These can continue to be used with Ansible for compliance verification.
3. **setup-automate deployment scripts** (moderate complexity): Replace with Ansible playbooks for deploying configuration management tools if still needed.

### Assumptions

1. The Chef Automate and Chef Infra Server deployment is primarily for demonstration purposes and not critical to the actual infrastructure configuration.
2. The InSpec tests are valuable for compliance verification and should be preserved.
3. The target environment is Ubuntu 20.04 running on Vagrant VMs.
4. The Apache HTTPS configuration is the primary workload being managed.
5. There are no external dependencies or integrations not visible in the repository.
6. The hardcoded credentials in the deployment scripts are for demonstration purposes and not used in production.
7. The repository is primarily educational/demonstrational rather than production infrastructure.