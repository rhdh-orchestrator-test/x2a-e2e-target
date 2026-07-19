# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible configurations that need to be consolidated into a unified Ansible solution. The repository primarily consists of:

1. Chef Automate and Chef Infra Server deployment scripts
2. Ansible playbooks for configuring HTTPS websites with Apache
3. Chef InSpec tests for compliance verification

The migration complexity is relatively low as most of the configuration is already in Ansible format. The primary focus will be on replacing the Chef Automate/Infra Server deployment scripts with Ansible equivalents and ensuring the InSpec tests can be integrated into an Ansible-based workflow. Estimated timeline: 1-2 weeks for a complete migration.

## Module Migration Plan

This repository contains Chef and Ansible configurations that need individual migration planning:

### MODULE INVENTORY

- **chef-and-ansible**:
    - Description: Ansible playbooks for configuring HTTPS websites with Apache and InSpec tests for compliance verification
    - Path: chef-and-ansible
    - Technology: Ansible + Chef InSpec
    - Key Features: Apache HTTPS configuration, SSL/TLS security settings, InSpec compliance testing

- **setup-automate**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash + Chef
    - Key Features: Chef Automate deployment, Chef Infra Server deployment, user and organization creation

### Infrastructure Files

- `chef-and-ansible/website_https.yml`: Ansible playbook that configures an Apache web server with HTTPS support. Migration considerations: Already in Ansible format, can be used as-is with minor adjustments.
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability. Migration considerations: Already in Ansible format, can be used as-is.
- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for testing Ansible playbooks with InSpec. Migration considerations: Will need to be updated to use Ansible-native testing frameworks or adapted to work with Ansible-specific test runners.
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test for verifying HTTPS website configuration. Migration considerations: Can be kept as-is and integrated with Ansible using ansible-test or molecule.
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec test for verifying SSH security configuration. Migration considerations: Can be kept as-is and integrated with Ansible using ansible-test or molecule.
- `setup-automate/deploy-automate.sh`: Bash script for deploying Chef Automate and Chef Infra Server. Migration considerations: Will need to be replaced with Ansible playbooks for infrastructure deployment.
- `setup-automate/deploy-chef-server.sh`: Bash script for deploying Chef Infra Server. Migration considerations: Will need to be replaced with Ansible playbooks for infrastructure deployment.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (identified from kitchen.yml and Apache package version in website_https.yml)
- **Virtual Machine Technology**: Vagrant (identified from kitchen.yml driver configuration)
- **Cloud Platform**: Not specified, but the scripts are designed to work on both on-premises and cloud VMs (mentioned in script comments)

## Migration Approach

### Key Dependencies to Address

- **Chef Automate CLI**: Replace with Ansible roles for infrastructure management
- **Chef Server CLI**: Replace with Ansible roles for infrastructure management
- **Chef InSpec**: Integrate with Ansible using ansible-test, molecule, or similar testing frameworks
- **Test Kitchen**: Replace with Ansible-native testing frameworks like molecule

### Security Considerations

- **SSL/TLS Configuration**: The playbooks configure Apache with TLS 1.2 and disable older protocols. This security practice should be maintained in the migrated Ansible playbooks.
- **Self-signed Certificates**: The playbooks generate self-signed certificates. Consider implementing proper certificate management using Ansible vault or external certificate management systems.
- **SSH Security**: InSpec tests verify SSH root login is disabled. Ensure this security check is maintained in the migrated solution.
- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - SSL/TLS certificate references in the Apache configuration should be managed securely
  - Count of credentials detected: 3 (username, password, and SSL certificates)

### Technical Challenges

- **InSpec Integration**: Ensuring InSpec tests continue to work with the Ansible-only workflow. Mitigation: Use ansible-test or molecule for test integration.
- **Infrastructure Deployment**: Replacing Chef Automate and Chef Infra Server deployment with equivalent Ansible functionality. Mitigation: Use Ansible roles for infrastructure deployment or consider containerization with Docker/Kubernetes.

### Migration Order

1. **chef-and-ansible/website_https.yml and poodle_fix.yml** (low risk, high value): These are already in Ansible format and can be used as-is with minor adjustments.
2. **InSpec Tests** (moderate complexity): Integrate the existing InSpec tests with Ansible using ansible-test or molecule.
3. **Chef Automate and Infra Server Deployment** (high complexity): Replace the bash scripts with Ansible playbooks for infrastructure deployment.

### Assumptions

1. The target environment will continue to be Ubuntu 20.04 or compatible Linux distributions.
2. InSpec will still be used for compliance testing, just integrated with Ansible rather than Chef.
3. The self-signed certificates are acceptable for the environment; if not, proper certificate management will need to be implemented.
4. The hardcoded credentials in the setup scripts are for demonstration purposes and will be replaced with secure credential management in production.
5. The Apache configuration requirements (HTTPS, TLS 1.2, etc.) will remain the same in the migrated solution.
6. The organization is moving away from Chef Automate/Infra Server completely, rather than just adding Ansible as an additional tool.