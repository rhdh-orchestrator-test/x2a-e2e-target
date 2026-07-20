# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests, Ansible playbooks, and Chef deployment scripts focused on demonstrating how Chef InSpec can be used alongside Ansible for compliance automation. The migration scope is relatively small, consisting primarily of:

1. Ansible playbooks for configuring HTTPS websites
2. Chef InSpec test profiles for compliance verification
3. Shell scripts for deploying Chef Automate and Chef Infra Server

The migration complexity is low to moderate, with an estimated timeline of 1-2 weeks. The primary focus will be on preserving the compliance testing functionality while consolidating all infrastructure provisioning into Ansible.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **chef-and-ansible**:
    - Description: Collection of Ansible playbooks and Chef InSpec tests for configuring and validating secure web servers
    - Path: chef-and-ansible
    - Technology: Ansible + Chef InSpec
    - Key Features: Apache HTTPS configuration, SSL hardening, compliance testing

- **setup-automate**:
    - Description: Shell scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Shell Scripts
    - Key Features: Chef infrastructure deployment, user and organization setup

### Infrastructure Files

- `chef-and-ansible/website_https.yml`: Ansible playbook that configures Apache with HTTPS, creates self-signed certificates, and deploys a simple website
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook that fixes SSL POODLE vulnerability by disabling older SSL protocols
- `chef-and-ansible/tests/website_https_verify.rb`: Chef InSpec test profile that verifies HTTPS website functionality and security
- `chef-and-ansible/tests/ssh_profile.rb`: Chef InSpec test profile that verifies SSH security configuration
- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and verifying with InSpec
- `chef-and-ansible/index.html`: Sample HTML file used in the website deployment
- `setup-automate/deploy-automate.sh`: Shell script for deploying Chef Automate and Chef Infra Server
- `setup-automate/deploy-chef-server.sh`: Shell script for deploying Chef Infra Server without Automate

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml)
- **Cloud Platform**: Not specified, appears to be platform-agnostic with potential for on-premises or cloud deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible's built-in assert module for basic tests and ansible-lint for static analysis. For more complex compliance testing, consider:
  - Option 1: Continue using InSpec but invoke it from Ansible
  - Option 2: Migrate to Ansible's native testing capabilities with custom modules
  - Option 3: Integrate with other compliance tools like OSCAP or Lynis

- **Test Kitchen**: Replace with Ansible Molecule for testing Ansible roles and playbooks

- **Chef Automate/Infra Server**: Replace with Ansible Automation Platform or open-source alternatives:
  - AWX (open-source version of Ansible Tower)
  - Semaphore (lightweight alternative)
  - GitLab CI/CD with Ansible

### Security Considerations

- **SSL Configuration**: The current implementation hardens Apache against POODLE vulnerability. Migration should:
  - Maintain or improve the SSL/TLS security posture
  - Update to current best practices (TLS 1.3 support)
  - Consider using Let's Encrypt for certificate management instead of self-signed certificates

- **SSH Hardening**: The InSpec profile checks for SSH root login restrictions. Migration should:
  - Preserve these security checks
  - Expand SSH hardening to include additional best practices
  - Implement SSH hardening via Ansible rather than just testing for compliance

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be migrated to Ansible Vault
  - No encrypted data bags or Chef Vault usage detected
  - SSL certificate generation should use Ansible Vault for storing private keys

### Technical Challenges

- **Compliance Testing**: The primary challenge will be replacing Chef InSpec's compliance testing capabilities with Ansible-native solutions
  - Mitigation: Consider using Ansible's assert module for basic tests and integrating with specialized compliance tools for more complex requirements

- **Test Kitchen to Molecule Migration**: Converting the test workflow from Test Kitchen to Molecule
  - Mitigation: Create equivalent Molecule scenarios that match the current Test Kitchen configuration

- **Chef Automate Functionality**: Replacing Chef Automate's compliance reporting and dashboards
  - Mitigation: Evaluate Ansible Automation Platform's compliance capabilities or integrate with third-party compliance reporting tools

### Migration Order

1. **Ansible Playbooks** (chef-and-ansible/website_https.yml, chef-and-ansible/poodle_fix.yml): Low risk as they're already in Ansible format, just need review and potential optimization
2. **InSpec Tests** (chef-and-ansible/tests/website_https_verify.rb, chef-and-ansible/tests/ssh_profile.rb): Moderate complexity, convert to Ansible assertions or continue using InSpec but invoked from Ansible
3. **Chef Deployment Scripts** (setup-automate/deploy-automate.sh, setup-automate/deploy-chef-server.sh): High complexity, replace with Ansible roles for deploying alternative infrastructure

### Assumptions

1. The primary purpose of this repository is to demonstrate Chef InSpec's compliance capabilities alongside Ansible, not to provide production-ready infrastructure
2. The target environment will continue to be Ubuntu 20.04 or compatible Linux distributions
3. The migration will prioritize maintaining the same level of compliance testing while consolidating on Ansible
4. No external dependencies or integrations beyond what's visible in the repository
5. The simple website deployment is for demonstration purposes and doesn't have specific performance or high availability requirements
6. The hardcoded credentials in the deployment scripts are for demonstration only and will be properly secured in the migrated solution