# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation. The primary focus appears to be showing how Chef InSpec can be used alongside Ansible for compliance testing. Additionally, there are bash scripts for deploying Chef Automate and Chef Infra Server. The migration scope is relatively small, with only a few Ansible playbooks and InSpec tests to migrate. The estimated timeline for migration would be 1-2 weeks, with low complexity as most components are already in Ansible format.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS enabled using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables SSLv3 and enables only TLSv1.2 in Apache configuration

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Tests port 443 listening, HTTPS response, SSL/TLS protocol security

- **ssh_profile**:
    - Description: Chef InSpec test that verifies SSH root login is disabled (security compliance)
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: Checks SSH configuration for root login settings, includes STIG compliance information

- **chef-automate-deployment**:
    - Description: Bash script to deploy Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash
    - Key Features: Downloads and installs Chef Automate, configures users and organizations

- **chef-server-deployment**:
    - Description: Bash script to deploy Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash
    - Key Features: Downloads and installs Chef Infra Server, configures users and organizations

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Migration consideration: Replace with Ansible-native testing framework like Molecule.
- `index.html`: Simple HTML file used for testing. Migration consideration: Keep as-is or include in Ansible templates.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM setup

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's assert module for basic compliance checks
  - Option 2: Use Molecule with testinfra for more comprehensive testing
  - Option 3: Maintain InSpec as a separate tool but invoke it from Ansible

- **Test Kitchen**: Replace with Molecule for Ansible playbook testing

- **Chef Automate/Infra Server**: Replace deployment scripts with Ansible playbooks that can:
  - Option 1: Deploy alternative compliance and infrastructure management tools
  - Option 2: Still deploy Chef components if they're required in the environment

### Security Considerations

- **SSL/TLS Configuration**: The migration must maintain the security hardening present in the poodle_fix.yml playbook
  - Approach: Create an Ansible role for Apache security hardening that includes the TLS protocol restrictions

- **SSH Security**: The SSH root login restrictions tested by the InSpec profile must be maintained
  - Approach: Create an Ansible role for SSH hardening that implements the same controls

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - Self-signed certificates are generated on the fly; consider using Ansible Vault for pre-generated certificates in production

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible-native testing will require careful mapping of test assertions
  - Mitigation: Create a mapping document for InSpec resources to Ansible/testinfra equivalents

- **Compliance Reporting**: If Chef Automate is being used for compliance reporting, an alternative solution will be needed
  - Mitigation: Evaluate tools like OpenSCAP, Prometheus with Grafana, or AWX/Tower for compliance reporting

### Migration Order

1. **website_https.yml** and **poodle_fix.yml** (already in Ansible format, low risk)
2. **InSpec tests** (convert to Ansible-native testing, moderate complexity)
3. **Chef deployment scripts** (convert to Ansible playbooks, higher complexity)

### Assumptions

1. The primary purpose of this repository is demonstration/educational rather than production use
2. The Chef InSpec tests are being used alongside Ansible for compliance testing, not as part of a larger Chef ecosystem
3. The deployment scripts are examples and may contain simplified configurations not suitable for production
4. The hardcoded credentials in the deployment scripts are for demonstration purposes only
5. There's no indication of external dependencies or integration with other systems
6. The target environment is Ubuntu 20.04 running on Vagrant VMs
7. There's no indication of complex state management or data persistence requirements
8. The Apache configuration is relatively simple and focused on HTTPS/SSL security