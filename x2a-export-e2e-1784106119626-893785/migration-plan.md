# MIGRATION FROM CHEF/INSPEC TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that demonstrate how to use Chef InSpec for compliance testing alongside Ansible for configuration management. The migration scope is relatively small, focusing on two main components:

1. Chef InSpec tests for compliance verification
2. Chef Automate/Chef Infra Server deployment scripts

The migration complexity is **LOW to MEDIUM** with an estimated timeline of **1-2 weeks** for a small team. The primary focus will be on replacing InSpec tests with Ansible-compatible testing frameworks while preserving the existing Ansible playbooks.

## Module Migration Plan

This repository contains Chef InSpec tests and shell scripts that need individual migration planning:

### MODULE INVENTORY

- **chef-inspec-tests**:
    - Description: InSpec tests for verifying HTTPS website configuration and SSH security compliance
    - Path: chef-and-ansible/tests
    - Technology: Chef InSpec
    - Key Features: SSL/TLS protocol verification, SSH configuration compliance checks, web server response testing

- **chef-automate-deployment**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash scripts
    - Key Features: Chef Automate installation, Chef Infra Server configuration, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks with InSpec verification. Will need to be replaced with Ansible-compatible testing framework configuration.
- `website_https.yml`: Ansible playbook for configuring Apache with HTTPS. Can be preserved as-is.
- `poodle_fix.yml`: Ansible playbook for fixing SSL POODLE vulnerability. Can be preserved as-is.
- `index.html`: Sample HTML file used in the web server configuration. Can be preserved as-is.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml)
- **Cloud Platform**: Not specified, appears to be platform-agnostic with potential for on-premises or cloud deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Ansible Molecule for integration testing
  - Option 2: Ansible Assert module for in-playbook testing
  - Option 3: Maintain InSpec as a separate tool but invoke it from Ansible

- **Test Kitchen**: Replace with:
  - Ansible Molecule for testing infrastructure
  - Or adapt existing kitchen.yml to use a pure Ansible approach

- **Chef Automate/Infra Server**: Replace deployment scripts with:
  - Ansible roles for configuration management
  - Consider migrating to Ansible Tower/AWX for enterprise features

### Security Considerations

- **SSL/TLS Configuration**: The migration must preserve the security hardening in the POODLE fix playbook:
  - Ensure TLSv1.2 is enforced
  - Disable older SSL/TLS protocols
  - Maintain certificate generation and management

- **SSH Hardening**: The SSH compliance profile must be converted to equivalent Ansible security:
  - Disable root login
  - Maintain CCI-000774 compliance
  - Preserve STIG compliance requirements

- **Vault/secrets management**:
  - Hardcoded credentials in deployment scripts (username, password) should be migrated to Ansible Vault
  - SSL certificate generation should use Ansible Vault for key storage
  - Count of credentials detected: 3 (username, password, and SSL keys)

### Technical Challenges

- **Compliance Testing Framework**: InSpec provides specialized security testing capabilities that need equivalent functionality in Ansible:
  - Challenge: Finding Ansible modules that can test SSL/TLS protocols and configurations
  - Mitigation: Consider using Ansible's uri module with custom verification or maintaining InSpec as a separate tool called from Ansible

- **Test Kitchen to Molecule Migration**: 
  - Challenge: Ensuring test scenarios are properly translated
  - Mitigation: Create equivalent Molecule scenarios for each Test Kitchen suite

- **Chef Automate Functionality**: 
  - Challenge: Replacing Chef Automate's compliance reporting
  - Mitigation: Evaluate Ansible Tower/AWX compliance capabilities or integrate with third-party compliance tools

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk, already in Ansible format, no migration needed
2. **Testing Framework**: Medium complexity, convert InSpec tests to Ansible-compatible testing
3. **Deployment Scripts**: Higher complexity, convert Chef Automate/Infra Server deployment to Ansible roles

### Assumptions

1. The primary purpose of this repository is demonstrating InSpec with Ansible rather than production deployment
2. The Chef InSpec tests are used for verification only and not for remediation
3. The deployment scripts are examples and may contain simplified security practices not suitable for production
4. The target environment is Ubuntu 20.04 running on Vagrant VMs
5. There are no external dependencies or integrations beyond what's visible in the repository
6. The hardcoded credentials in the deployment scripts are for demonstration purposes only
7. No custom InSpec resources are being used that would require specialized migration
8. The Apache configuration is relatively standard and doesn't include complex customizations