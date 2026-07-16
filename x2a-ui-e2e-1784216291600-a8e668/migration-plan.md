# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation. The primary focus is on using Chef InSpec for compliance testing alongside Ansible for configuration management. The repository also includes Chef Automate and Chef Infra Server deployment scripts. The migration scope is relatively small, with only a few Ansible playbooks and InSpec tests to migrate. The estimated timeline for migration is 1-2 weeks, with low complexity.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables SSLv3 and enables only TLSv1.2

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response verification, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec test that verifies SSH security configuration
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login verification, compliance with security standards (SRG-OS-000112)

- **chef-automate-deployment**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Infra Server configuration, user and organization creation

- **chef-server-deployment**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Migration consideration: Replace with Ansible Molecule for testing.
- `index.html`: Simple HTML file used for testing. Migration consideration: Keep as-is or include in Ansible templates.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible Molecule with Testinfra for infrastructure testing
  - Option 2: Use Ansible Molecule with Goss for infrastructure testing
  - Option 3: Maintain InSpec as a separate tool but invoke it from Ansible

- **Test Kitchen**: Replace with Ansible Molecule for testing infrastructure

- **Chef Automate/Infra Server**: Replace with Ansible Automation Platform or alternative compliance solutions:
  - Option 1: Migrate to Ansible Automation Platform for orchestration and compliance
  - Option 2: Use OpenSCAP with Ansible for compliance scanning
  - Option 3: Use Ansible with Prometheus/Grafana for monitoring and reporting

### Security Considerations

- **SSL Configuration**: The playbooks configure Apache with SSL. Migration should maintain or improve the security posture:
  - Ensure TLSv1.2 or higher is enforced (currently done in poodle_fix.yml)
  - Consider adding more modern cipher suites
  - Implement automatic certificate renewal if moving to production

- **SSH Security**: The InSpec tests verify SSH security configurations:
  - Ensure SSH root login remains disabled in Ansible-managed configurations
  - Maintain compliance with security standards referenced in the InSpec tests (SRG-OS-000112, V-38607)

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be migrated to Ansible Vault
  - Self-signed certificates should be managed securely, potentially using Ansible Vault or external certificate management

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible-native testing frameworks:
  - Challenge: InSpec has specific syntax for compliance testing that may not directly map to Ansible testing tools
  - Mitigation: Use Ansible assert modules or Molecule with Testinfra/Goss to replicate InSpec tests

- **Chef Automate Replacement**: Finding equivalent functionality in Ansible ecosystem:
  - Challenge: Chef Automate provides integrated compliance reporting that needs an equivalent in Ansible
  - Mitigation: Implement Ansible Automation Platform or combine Ansible with compliance tools like OpenSCAP

- **Maintaining Compliance Standards**: Ensuring the same level of compliance verification:
  - Challenge: The InSpec tests reference specific security standards (SRG-OS-000112, etc.)
  - Mitigation: Map these standards to equivalent Ansible checks and document the mapping

### Migration Order

1. **website_https.yml** (Priority 1, already Ansible): Review and optimize existing Ansible playbook
2. **poodle_fix.yml** (Priority 1, already Ansible): Review and optimize existing Ansible playbook
3. **InSpec Tests** (Priority 2): Convert to Ansible-native testing framework
4. **Chef Deployment Scripts** (Priority 3): Convert to Ansible roles for deploying alternative compliance solutions

### Assumptions

1. The primary goal is to consolidate on Ansible and remove Chef dependencies
2. Compliance testing is a critical requirement that must be maintained
3. The target environment will continue to be Ubuntu 20.04 or compatible systems
4. Vagrant will continue to be used for development/testing environments
5. The security standards referenced in the InSpec tests (SRG-OS-000112, etc.) must continue to be enforced
6. The repository is primarily for demonstration/educational purposes rather than production use
7. Self-signed certificates are acceptable for the demonstration environment
8. The hardcoded credentials in the deployment scripts are for demonstration only and will be replaced with secure alternatives